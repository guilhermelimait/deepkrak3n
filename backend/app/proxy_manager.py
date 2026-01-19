"""Lightweight proxy pool with rotation and cooldown.
This stays opt-in via env so the service can run without proxies.
"""
from __future__ import annotations

import asyncio
import os
import random
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional

import httpx


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}


@dataclass
class ProxyRecord:
    url: str
    id: str
    last_failure_ts: float = field(default=0.0)
    success_count: int = field(default=0)
    failure_count: int = field(default=0)

    @property
    def is_healthy(self) -> bool:
        return self.last_failure_ts == 0.0


class ProxyManager:
    def __init__(self) -> None:
        self.enabled = _env_bool("PROXY_ENABLED", False)
        raw_list = os.getenv("PROXY_LIST", "").strip()
        self.rotation_mode = os.getenv("PROXY_ROTATION_MODE", "round_robin")
        self.failure_cooldown = float(os.getenv("PROXY_FAILURE_COOLDOWN_SECONDS", "120"))
        self.allow_direct_fallback = _env_bool("PROXY_ALLOW_DIRECT_FALLBACK", True)
        self.auto_fetch_if_missing = _env_bool("PROXY_AUTO_FETCH", True)
        self._lock = asyncio.Lock()
        self._index = 0
        self.proxies: List[ProxyRecord] = []

        if raw_list:
            items = [p.strip() for p in raw_list.split(",") if p.strip()]
            self.proxies = [ProxyRecord(url=p, id=f"proxy-{idx}") for idx, p in enumerate(items, 1)]

    def _parse_html_for_proxies(self, html: str, max_results: int = 10) -> List[str]:
        pattern = re.compile(r"document\.write\(([^)]*)\).*?<td[^>]*>(\d+)</td>", re.DOTALL)
        proxies: List[str] = []
        for ip_expr, port in pattern.findall(html):
            cleaned = re.sub(r"[\s\+\'\"]", "", ip_expr)
            cleaned = cleaned.replace("document.write(", "").replace(")", "")
            if cleaned.endswith("."):
                cleaned = cleaned[:-1]
            if re.match(r"^\d+\.\d+\.\d+\.\d+$", cleaned):
                proxies.append(f"http://{cleaned}:{port}")
            if len(proxies) >= max_results:
                break
        return proxies

    async def _auto_fetch_proxies(self) -> List[str]:
        if not self.auto_fetch_if_missing:
            return []
        try:
            async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"}) as client:
                resp = await client.get("https://www.proxynova.com/proxy-server-list/")
                resp.raise_for_status()
                html = resp.text
        except Exception:
            return []
        return self._parse_html_for_proxies(html)

    async def ensure_proxies(self) -> None:
        if self.proxies:
            return
        proxies = await self._auto_fetch_proxies()
        if proxies:
            self.proxies = [ProxyRecord(url=p, id=f"proxy-{idx}") for idx, p in enumerate(proxies, 1)]

    def _healthy_pool(self) -> List[ProxyRecord]:
        now = time.time()
        healthy: List[ProxyRecord] = []
        for p in self.proxies:
            if p.last_failure_ts == 0.0:
                healthy.append(p)
            elif now - p.last_failure_ts >= self.failure_cooldown:
                p.last_failure_ts = 0.0
                healthy.append(p)
        return healthy

    async def get_proxy(self) -> Optional[ProxyRecord]:
        if not self.enabled or not self.proxies:
            return None
        async with self._lock:
            pool = self._healthy_pool()
            if not pool:
                return None if self.allow_direct_fallback else None
            if self.rotation_mode == "random_healthy":
                choice = random.choice(pool)
            else:
                # round robin
                choice = pool[self._index % len(pool)]
                self._index = (self._index + 1) % max(len(pool), 1)
            return choice

    async def mark_failure(self, proxy_id: str) -> None:
        async with self._lock:
            for p in self.proxies:
                if p.id == proxy_id:
                    p.last_failure_ts = time.time()
                    p.failure_count += 1
                    break

    async def mark_success(self, proxy_id: str) -> None:
        async with self._lock:
            for p in self.proxies:
                if p.id == proxy_id:
                    p.success_count += 1
                    break

    def snapshot(self) -> dict:
        return {
            "enabled": self.enabled,
            "count": len(self.proxies),
            "rotation": self.rotation_mode,
            "cooldown_seconds": self.failure_cooldown,
            "allow_direct_fallback": self.allow_direct_fallback,
            "proxies": [
                {
                    "id": p.id,
                    "healthy": p.is_healthy,
                    "last_failure_ts": p.last_failure_ts,
                    "success_count": p.success_count,
                    "failure_count": p.failure_count,
                }
                for p in self.proxies
            ],
        }

    def set_enabled(self, enabled: bool) -> None:
        # Simple toggle; proxies still require PROXY_LIST configured
        self.enabled = enabled and bool(self.proxies)
