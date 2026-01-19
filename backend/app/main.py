"""Independent FastAPI backend for the v3 app.
Run with: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import asyncio
import os
import logging
from typing import AsyncGenerator
import json

import httpx

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from .search_service import SearchService
from .proxy_manager import ProxyManager
from .profile_analyzer import AnalyzeRequest, analyze_profiles

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="DeepKrak3n v3 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

proxy_manager = ProxyManager()
search_service = SearchService(
    max_concurrency=int(os.getenv("MAX_CONCURRENCY", "8")),
    max_retries=int(os.getenv("PROXY_MAX_RETRIES", "2")),
    backoff_base=float(os.getenv("PROXY_BACKOFF_BASE", "0.5")),
    proxy_manager=proxy_manager,
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/search/username")
async def search_username(
    username: str = Query(..., min_length=1),
    limit: int | None = Query(None),
):
    try:
        return await search_service.search_username(username=username, limit=limit)
    except Exception as e:  # noqa: BLE001
        logger.exception("username search failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/search/username/stream")
async def stream_username(
    username: str = Query(..., min_length=1),
    limit: int | None = Query(None),
):
    async def event_generator() -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue()
        result_data: dict = {}

        async def on_result(site_result):
            await queue.put({"type": "site_result", "result": site_result.__dict__})

        async def run_search():
            nonlocal result_data
            try:
                result_data = await search_service.search_username(
                    username=username,
                    limit=limit,
                    on_result=on_result,
                )
            except Exception as e:  # noqa: BLE001
                await queue.put({"type": "error", "error": str(e)})
            finally:
                await queue.put({"type": "_done"})

        # kick off search task
        asyncio.create_task(run_search())

        while True:
            event = await queue.get()
            if event.get("type") == "_done":
                break
            yield "event: {evt}\ndata: {data}\n\n".format(evt=event.get("type", "message"), data=json.dumps(event))

        if result_data:
            summary = {
                "type": "search_complete",
                "summary": {
                    "total_found": result_data.get("total_found", 0),
                    "total_checked": result_data.get("total_checked", 0),
                },
                "found_profiles": result_data.get("found_profiles", []),
            }
            yield f"event: search_complete\ndata: {json.dumps(summary)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/network/status")
async def network_status():
    direct_ip = None
    proxy_ip = None
    proxy_snapshot = proxy_manager.snapshot()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("https://api.ipify.org?format=json")
            direct_ip = resp.json().get("ip")
    except Exception:  # noqa: BLE001
        direct_ip = None

    if proxy_manager.enabled:
        proxy = await proxy_manager.get_proxy()
        if proxy:
            try:
                async with httpx.AsyncClient(timeout=5.0, proxy=proxy.url) as client:
                    resp = await client.get("https://api.ipify.org?format=json")
                    proxy_ip = resp.json().get("ip")
            except Exception:  # noqa: BLE001
                proxy_ip = None

    return {
        "proxy_enabled": proxy_manager.enabled,
        "proxy": proxy_snapshot,
        "direct_ip": direct_ip,
        "proxy_ip": proxy_ip,
    }


@app.post("/api/proxy/toggle")
async def proxy_toggle(enabled: bool = Query(...)):
    auto_fetch_attempted = False
    if enabled and not proxy_manager.proxies:
        auto_fetch_attempted = True
        await proxy_manager.ensure_proxies()
    if enabled and not proxy_manager.proxies:
        proxy_manager.set_enabled(False)
        return {
            "proxy_enabled": False,
            "proxy_count": 0,
            "auto_fetch_attempted": auto_fetch_attempted,
            "message": "No proxies available; proxy left off. Set PROXY_LIST or keep PROXY_AUTO_FETCH on.",
        }
    proxy_manager.set_enabled(enabled)
    return {
        "proxy_enabled": proxy_manager.enabled,
        "proxy_count": len(proxy_manager.proxies),
        "auto_fetch_attempted": auto_fetch_attempted,
    }


@app.post("/api/profile/analyze")
async def profile_analyze(req: AnalyzeRequest):
    if not req.profiles:
        raise HTTPException(status_code=400, detail="profiles required")
    try:
        return await analyze_profiles(req)
    except Exception as e:  # noqa: BLE001
        logger.exception("profile analysis failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/ollama/models")
async def list_ollama_models(host: str | None = Query(None)):
    """Return available Ollama models for the given host (default localhost)."""
    target_host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
    url = target_host.rstrip("/") + "/api/tags"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json() or {}
            models = [m.get("name") for m in data.get("models", []) if m.get("name")]
            return {"host": target_host, "models": models}
    except Exception as exc:  # noqa: BLE001
        logger.exception("failed to fetch ollama models")
        raise HTTPException(status_code=502, detail=f"Failed to reach Ollama at {target_host}: {exc}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
