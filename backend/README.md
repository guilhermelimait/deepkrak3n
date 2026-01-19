# DeepKrak3n v3 Backend (Independent)

Minimal FastAPI service for username searches. Uses its own slim site database and does **not** depend on DefenseMon3.

## Run locally
```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Endpoints
- `GET /health`
- `POST /api/search/username?username=alice&limit=20` — JSON results
- `GET /api/search/username/stream?username=alice&limit=20` — SSE stream of hits

## Notes
- CORS allows `http://localhost:3000` and `http://localhost:5173` by default; override with `CORS_ORIGINS` env var (comma-separated).
- Site definitions live in `app/sites_database.py`; add more patterns as needed.

## Proxy / Anonymity (optional)
- Enable with `PROXY_ENABLED=true` and provide `PROXY_LIST` (comma-separated proxy URLs like `http://user:pass@ip:port`).
- Rotation mode: `PROXY_ROTATION_MODE=round_robin` (default) or `random_healthy`.
- Retry tuning: `PROXY_MAX_RETRIES` (default 2), `PROXY_BACKOFF_BASE` (seconds, default 0.5).
- Health: `PROXY_FAILURE_COOLDOWN_SECONDS` (default 120) controls how long a failed proxy is cooled off.
- Fallback: `PROXY_ALLOW_DIRECT_FALLBACK=true` lets the service go direct if no healthy proxies are available.
- Concurrency: override with `MAX_CONCURRENCY` (default 8).
