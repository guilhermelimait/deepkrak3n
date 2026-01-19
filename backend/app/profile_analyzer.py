from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProfileInput(BaseModel):
    platform: str
    url: str | None = None
    display_name: str | None = None
    bio: str | None = None
    avatar: str | None = None
    category: str | None = None


class AnalyzeRequest(BaseModel):
    profiles: List[ProfileInput]
    use_llm: bool = False
    llm_model: str | None = None
    ollama_host: str | None = None
    api_mode: str | None = None  # "ollama" (generate) or "openai" (chat)
    username: str | None = None
    email: str | None = None
    prompt: str | None = None


def _heuristic_analysis(profiles: List[ProfileInput]) -> Dict[str, Any]:
    total = len(profiles)
    platforms = [p.platform.lower() for p in profiles]
    bios = [p.bio for p in profiles if p.bio]

    traits: List[str] = []
    risks: List[str] = []

    if any("github" in p or "gitlab" in p or "bitbucket" in p for p in platforms):
        traits.append("developer/tech footprint")
    if any("linkedin" in p for p in platforms):
        traits.append("professional identity")
    if any("instagram" in p or "facebook" in p or "tiktok" in p for p in platforms):
        traits.append("social presence")
    if any("patreon" in p or "ko-fi" in p or "venmo" in p or "cash app" in p for p in platforms):
        traits.append("creator/monetization signals")
    if any(len(b or "") > 240 for b in bios):
        traits.append("long-form bio detected")

    if len(set(platforms)) <= 2 and total >= 3:
        risks.append("identity reuse across few platforms")
    if any("vpn" in (b or "").lower() or "proxy" in (b or "").lower() for b in bios):
        risks.append("privacy tooling mentioned")

    summary = (
        f"Found {total} profiles across {len(set(platforms))} platforms. "
        "Signals combined into high-level traits and risks."
    )

    return {
        "summary": summary,
        "traits": traits,
        "risks": risks,
        "mode": "heuristic",
        "llm_used": False,
    }


async def _ollama_analysis(
    profiles: List[ProfileInput],
    model: str,
    host: str,
    api_mode: str = "ollama",
    username: str | None = None,
    email: str | None = None,
    prompt_override: str | None = None,
) -> tuple[str, str]:
    prompt_lines = [
        prompt_override.strip()
    ] if prompt_override and prompt_override.strip() else [
        "You are a concise profile analyst.",
        "Given multi-platform profile hits, infer persona, interests, and risk signals.",
        "Keep it under 140 words.",
    ]
    if username:
        prompt_lines.append(f"Username pivot: {username}")
    if email:
        prompt_lines.append(f"Email pivot: {email}")
    prompt_lines.append("Profiles:")
    for p in profiles:
        line = f"- {p.platform}: {p.display_name or ''} | {p.url or ''}"
        if p.bio:
            line += f" | bio: {p.bio[:220]}"
        prompt_lines.append(line)
    prompt = "\n".join(prompt_lines)

    async def _call_generate() -> str:
        payload = {"model": model, "prompt": prompt, "stream": False}
        url = host.rstrip("/") + "/api/generate"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response") or data.get("data") or ""
            return text.strip()

    async def _call_chat() -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a concise profile analyst."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        url = host.rstrip("/") + "/v1/chat/completions"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            choice = (data.get("choices") or [{}])[0]
            message = choice.get("message") or {}
            text = message.get("content") or ""
            return text.strip()

    # Try preferred mode, fallback to the other if 404/Not Found
    if api_mode == "openai":
        try:
            return await _call_chat(), "openai"
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 404:
                raise
        # fallback
        return await _call_generate(), "ollama"
    else:
        try:
            return await _call_generate(), "ollama"
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 404:
                raise
        # fallback
        return await _call_chat(), "openai"


async def analyze_profiles(req: AnalyzeRequest) -> Dict[str, Any]:
    base = _heuristic_analysis(req.profiles)

    if not req.use_llm:
        return base

    model = req.llm_model or os.getenv("OLLAMA_MODEL", "llama3")
    host = req.ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
    api_mode = (req.api_mode or os.getenv("OLLAMA_API_MODE", "ollama")).lower()

    try:
        llm_summary, used_mode = await _ollama_analysis(
            req.profiles,
            model,
            host,
            api_mode,
            username=req.username,
            email=req.email,
            prompt_override=req.prompt,
        )
        base.update(
            {
                "summary": llm_summary or base["summary"],
                "mode": used_mode,
                "llm_used": True,
                "llm_model": model,
                "llm_error": None,
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("ollama analysis failed")
        base.update(
            {
                "mode": "heuristic_fallback",
                "llm_used": False,
                "llm_model": model,
                "llm_error": str(exc),
            }
        )

    return base
