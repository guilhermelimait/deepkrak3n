"""Username search service with optional proxy support and retries."""
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import httpx

from .sites_database import SITES_DB
from .proxy_manager import ProxyManager, ProxyRecord

logger = logging.getLogger(__name__)


@dataclass
class SiteResult:
    site: str
    url: str
    found: bool
    state: str
    status_code: int
    via_proxy: bool
    proxy_id: str | None
    proxy_url: Optional[str] = None
    latency_ms: float | None = None
    reason: str | None = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None


class SearchService:
    def __init__(
        self,
        timeout: float = 20.0,
        max_concurrency: int = 8,
        max_retries: int = 2,
        backoff_base: float = 0.5,
        proxy_manager: ProxyManager | None = None,
    ):
        self.timeout = timeout
        self.max_concurrency = max_concurrency
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.proxy_manager = proxy_manager

    async def search_username(
        self,
        username: str,
        limit: Optional[int] = None,
        on_result: Optional[callable] = None,
    ) -> Dict[str, Any]:
        sites = SITES_DB[:limit] if limit else SITES_DB
        results: List[SiteResult] = []

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            sem = asyncio.Semaphore(self.max_concurrency)

            async def check_site(site: Dict[str, Any]) -> None:
                url = self._build_url(site.get("url"), username)
                proxy: Optional[ProxyRecord] = None
                proxy_cfg: Dict[str, str] | None = None
                proxy_id: Optional[str] = None
                try:
                    async with sem:
                        proxy, proxy_cfg = await self._choose_proxy()
                        resp, latency_ms, proxy_id = await self._fetch_with_retries(
                            client=client,
                            url=url,
                            proxy_cfg=(proxy, proxy_cfg),
                        )
                    found, state, reason, details = self._analyze_response(resp, username, site)
                    result = SiteResult(
                        site=site.get("name", "Unknown"),
                        url=url,
                        found=found,
                        state=state,
                        status_code=resp.status_code,
                        via_proxy=proxy_id is not None,
                        proxy_id=proxy_id,
                        proxy_url=proxy.url if proxy else None,
                        latency_ms=latency_ms,
                        reason=reason,
                        display_name=details.get("display_name") if details else None,
                        bio=details.get("bio") if details else None,
                        avatar=details.get("avatar") if details else None,
                    )
                    results.append(result)
                    if on_result:
                        await on_result(result)
                except Exception as e:  # noqa: BLE001
                    state, reason = self._state_from_exception(e)
                    result = SiteResult(
                        site=site.get("name", "Unknown"),
                        url=url,
                        found=False,
                        state=state,
                        status_code=0,
                        via_proxy=proxy is not None,
                        proxy_id=proxy.id if proxy else None,
                        proxy_url=proxy.url if proxy else None,
                        latency_ms=None,
                        reason=reason,
                    )
                    results.append(result)
                    if on_result:
                        await on_result(result)

            await asyncio.gather(*(check_site(site) for site in sites))

        total_found = sum(1 for r in results if r.found)
        return {
            "query": username,
            "total_checked": len(results),
            "total_found": total_found,
            "found_profiles": [r.__dict__ for r in results if r.found],
            "all_results": [r.__dict__ for r in results],
        }

    def _build_url(self, template: Optional[str], username: str) -> str:
        if not template:
            return ""
        if "{handle}" in template:
            return template.replace("{handle}", username)
        try:
            return template.format(username)
        except Exception:
            return template

    async def _choose_proxy(self) -> Tuple[Optional[ProxyRecord], Dict[str, str] | None]:
        if not self.proxy_manager or not self.proxy_manager.enabled:
            return None, None
        proxy = await self.proxy_manager.get_proxy()
        if not proxy:
            return None, None
        proxy_cfg = {"http": proxy.url, "https": proxy.url}
        return proxy, proxy_cfg

    async def _fetch_with_retries(
        self,
        client: httpx.AsyncClient,
        url: str,
        proxy_cfg: Tuple[Optional[ProxyRecord], Dict[str, str] | None],
    ) -> Tuple[httpx.Response, float, Optional[str]]:
        proxy_rec, proxies = proxy_cfg
        proxy_id = proxy_rec.id if proxy_rec else None
        attempts = self.max_retries + 1
        last_exc: Exception | None = None

        for attempt in range(attempts):
            start = time.perf_counter()
            try:
                request_kwargs: Dict[str, Any] = {"headers": {"User-Agent": "Mozilla/5.0"}}
                # httpx 0.28 drops per-request `proxies`; use `proxy` instead when provided.
                if proxies:
                    request_kwargs["proxy"] = proxies.get("http") or proxies.get("https")

                resp = await client.get(url, **request_kwargs)
                latency_ms = (time.perf_counter() - start) * 1000
                if proxy_id:
                    await self.proxy_manager.mark_success(proxy_id)
                return resp, latency_ms, proxy_id
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if proxy_id:
                    await self.proxy_manager.mark_failure(proxy_id)
                if attempt < attempts - 1:
                    sleep_for = self.backoff_base * (2**attempt) + random.uniform(0, 0.25)
                    await asyncio.sleep(sleep_for)
                    continue
                raise

        assert last_exc  # for type checkers
        raise last_exc

    def _state_from_exception(self, exc: Exception) -> Tuple[str, str]:
        if isinstance(exc, httpx.TimeoutException):
            return "timeout", "Timeout"
        if isinstance(exc, httpx.RequestError):
            return "network_error", str(exc)
        return "error", str(exc)

    def _extract_profile_details(self, html_text: str) -> Optional[Dict[str, str]]:
        """Lightweight OG meta scraper to enrich profiles without new deps."""
        details: Dict[str, str] = {}
        text = html_text or ""

        def _find_meta(prop_names):
            lowered = text.lower()
            for prop in prop_names:
                marker = f'property="{prop.lower()}"'
                idx = lowered.find(marker)
                if idx != -1:
                    content_idx = lowered.find("content=\"", idx)
                    if content_idx != -1:
                        end_idx = lowered.find("\"", content_idx + 9)
                        if end_idx != -1:
                            return text[content_idx + 9 : end_idx].strip()
            return None

        og_title = _find_meta(["og:title", "twitter:title"])
        og_desc = _find_meta(["og:description", "twitter:description"])
        og_image = _find_meta(["og:image", "twitter:image"])

        if og_title:
            details["display_name"] = og_title
        if og_desc:
            details["bio"] = og_desc
        if og_image:
            details["avatar"] = og_image

        return details if details else None

    def _analyze_response(self, response: httpx.Response, username: str, site: Dict[str, Any]) -> Tuple[bool, str, str, Optional[Dict[str, str]]]:
        text_lower = response.text.lower() if response.text else ""
        positives = [p.lower() for p in site.get("positive_keywords", [])]
        negatives = [n.lower() for n in site.get("negative_keywords", [])]
        username_lower = username.lower()

        if response.status_code == 404:
            return False, "not_found", "Profile not found", None
        if response.status_code == 403:
            return False, "blocked", "Access forbidden", None
        if response.status_code == 429:
            return False, "rate_limited", "Rate limited", None
        if response.status_code >= 500:
            return False, "server_error", "Server error", None
        if response.status_code in (301, 302) and not site.get("allow_redirect", False):
            return False, "redirect", "Redirected", None

        if any(neg in text_lower for neg in negatives):
            return False, "not_found", "Site negative signal", None

        contains_username = username_lower in text_lower
        contains_positive = any(pos in text_lower for pos in positives) if positives else False

        if response.status_code == 200 and contains_positive and contains_username:
            details = self._extract_profile_details(response.text)
            return True, "found", "Positive keyword and username", details

        if response.status_code == 200 and contains_username:
            details = self._extract_profile_details(response.text)
            return True, "found", "Username present", details

        if response.status_code == 200 and contains_positive:
            return False, "unknown", "Positive keyword only", None

        return False, "unknown", "Unable to confirm", None
