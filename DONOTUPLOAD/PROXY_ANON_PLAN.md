# Proxy & Anonymity Implementation Plan

## Objectives
- Add outbound proxy/anonymity for the FastAPI OSINT checker without depending on DefenseMon3.
- Keep requests reliable (rotation, health checks, retry/backoff) while respecting per-site limits.
- Keep the Next.js frontend unchanged except for config/env wiring.

## Current Baseline
- Frontend (Next.js 13 app router) calls the FastAPI backend via `NEXT_PUBLIC_API_BASE`.
- Backend endpoints: `/health`, `/api/search/username`, `/api/search/username/stream` using `httpx.AsyncClient` with simple heuristics.
- Sites DB: GitHub, Twitter/X, Reddit, YouTube, TikTok, Instagram, LinkedIn, Facebook.
- No proxy/anonymity yet; direct outbound requests only.

## Approach (phased)
1) **Pluggable proxy client**: wrap `httpx.AsyncClient` with optional per-request proxy assignment; toggle via env.
2) **Rotation & health**: maintain a small in-memory pool with last-failure timestamps; prefer healthy proxies; fall back to direct only if allowed.
3) **Per-site policies**: configurable concurrency caps and small jittered backoffs to avoid bursts.
4) **Observability**: structured logs (proxy id, target host, status, latency) without logging full URLs or usernames.
5) **Config-only rollout**: ship code with proxy disabled by default; enable via env after smoke tests.

## Configuration (new env vars)
- `PROXY_ENABLED=true|false` (default `false`).
- `PROXY_LIST` (comma-separated proxy URLs, e.g., `http://user:pass@ip:port`), or `PROXY_PROVIDER_URL` + `PROXY_API_KEY` if fetching dynamically.
- `PROXY_ROTATION_MODE` (`round_robin` | `random_healthy`).
- `PROXY_FAILURE_COOLDOWN_SECONDS` (e.g., 120) and `PROXY_MAX_RETRIES` (e.g., 2).
- `MAX_CONCURRENCY_PER_SITE` (default keep existing semaphore; allow override per site map if needed).

## Backend Changes (FastAPI)
- Add `proxy_manager.py`:
  - Parse env, load proxies, expose `get_proxy()` with rotation + cooldown.
  - Track health: on failure mark proxy as down until `cooldown` expires.
- Update `search_service.py` request path:
  - When `PROXY_ENABLED`, choose a proxy for each request, pass to `httpx.AsyncClient` via `proxies` option.
  - Add lightweight jittered backoff and limited retries per site.
  - Keep timeouts tight; surface proxy errors distinctly in response metadata (e.g., `source="proxy"`).
- Add minimal logging hooks (structured JSON) for proxy id, host, latency, outcome; guard PII (no full URL/username).
- Add a `/health` extension or debug flag to surface proxy pool status when `DEBUG=true`.

## Frontend Notes
- No UI changes required; ensure `.env.local` still points to backend. Consider exposing a banner chip when backend reports proxy mode active (optional nice-to-have).

## Testing Plan
- Unit: proxy manager rotation/cooldown; retry/backoff logic with fake client.
- Integration: run backend with `PROXY_ENABLED=true` and a local test proxy (or `http://localhost:8888`) to verify requests route and failures cool down.
- Smoke: hit `/api/search/username` against a low-sensitivity username and confirm responses return with proxy metadata.

## Rollout Steps
1) Implement `proxy_manager.py` + wire into `search_service.py` (behind env flag).
2) Add configuration defaults and docs to `backend/README.md`.
3) Add structured logging to make failures debuggable.
4) Manual smoke test with a test proxy; validate cooldown/rotation.
5) Enable in prod config by setting `PROXY_ENABLED=true` and providing `PROXY_LIST`.

## Open Considerations
- If a managed rotating provider is used, add a thin fetcher to refresh the pool periodically.
- If target sites add TLS/device fingerprinting, consider a headless option later; keep current scope to HTTP fetches only.
- Keep rate limits conservative; adjust per-site caps if blocks appear in logs.
