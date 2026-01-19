# deepkrak3n (v3)

<p align="center">
	<span style="display:inline-block; position:relative;">
		<img src="./deepkrak3nlogo.png" alt="deepkrak3n logo" width="140" style="animation: logo-glitch 2.8s ease-in-out infinite 1s; border-radius: 12px;" />
	</span>
</p>

deepkrak3n is a local-first OSINT playground. Enter a username or email, scan 100+ public platforms, turn hits into profile cards, link identities on a mind map, run heuristic or LLM analysis, and export what you select.

## Features
- Live availability scan over SSE across ~100 public platforms with per-site status.
- Profile cards with display name, bio, avatar, category, and latency/proxy info.
- Mind map linking by username, email, or profile name, with overlap controls.
- Heuristic analysis plus optional LLM (Ollama or OpenAI-compatible) summary.
- Export JSON or HTML preview; settings stored locally in the browser.
- Proxy toggle/status surfaced in UI; backend handles proxy rotation and retries.

## Architecture
- Frontend: Next.js App Router; main flow in [app/page.tsx](app/page.tsx), layout/theming in [app/layout.tsx](app/layout.tsx), Tailwind config in [tailwind.config.ts](tailwind.config.ts). Platform catalog lives in [data/platforms.json](data/platforms.json).
- Backend: FastAPI service in [backend/app/main.py](backend/app/main.py); username search in [backend/app/search_service.py](backend/app/search_service.py) with site definitions in [backend/app/sites_database.py](backend/app/sites_database.py); proxy pool in [backend/app/proxy_manager.py](backend/app/proxy_manager.py); heuristic/LLM analyzer in [backend/app/profile_analyzer.py](backend/app/profile_analyzer.py).

## Run locally
Prereqs: Node 18+ and Python 3.11+.

Backend (FastAPI):
```
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend (Next.js):
```
npm install
npm run dev
```

Open http://localhost:3000 and set `NEXT_PUBLIC_API_BASE` if your backend is not on the default http://localhost:8000.

## Configuration knobs
- `NEXT_PUBLIC_API_BASE`: backend URL (used by the frontend).
- LLM (local): run Ollama (default http://localhost:11434) and pull a model, e.g., `ollama pull smollm:latest`; click Connect to list models.
- LLM (OpenAI-compatible): set API mode to `openai` in Settings and point to your compatible endpoint/key (proxied via your backend if needed).
- Proxy envs (optional, backend): `PROXY_ENABLED`, `PROXY_LIST`, `PROXY_ROTATION_MODE`, `PROXY_MAX_RETRIES`, `PROXY_BACKOFF_BASE`, `PROXY_FAILURE_COOLDOWN_SECONDS`, `PROXY_ALLOW_DIRECT_FALLBACK`.

## Customization
- Platforms: edit [data/platforms.json](data/platforms.json) (category keys with `{ "name": "Site", "url": "https://site.com/{handle}" }`). Dev server hot-reloads; rebuild for production.
- Analyzer prompt: update in Settings → Analyzer prompt; base logic in [backend/app/profile_analyzer.py](backend/app/profile_analyzer.py).

## Do not upload
Everything in [DONOTUPLOAD](DONOTUPLOAD) is non-runtime and should stay out of version control: builds ([DONOTUPLOAD/.next](DONOTUPLOAD/.next), [DONOTUPLOAD/out](DONOTUPLOAD/out)), dependencies ([DONOTUPLOAD/node_modules](DONOTUPLOAD/node_modules)), backups ([DONOTUPLOAD/backup_20260117_114547](DONOTUPLOAD/backup_20260117_114547)), tooling caches ([DONOTUPLOAD/.bolt](DONOTUPLOAD/.bolt)), unused UI kit ([DONOTUPLOAD/components](DONOTUPLOAD/components), [DONOTUPLOAD/hooks/use-toast.ts](DONOTUPLOAD/hooks/use-toast.ts), [DONOTUPLOAD/lib/utils.ts](DONOTUPLOAD/lib/utils.ts)), helper scripts/docs ([DONOTUPLOAD/backend/scripts/fetch_proxies.py](DONOTUPLOAD/backend/scripts/fetch_proxies.py), [DONOTUPLOAD/components.json](DONOTUPLOAD/components.json), [DONOTUPLOAD/PROXY_ANON_PLAN.md](DONOTUPLOAD/PROXY_ANON_PLAN.md)).

## Troubleshooting
- Backend not responding: ensure uvicorn is running and `NEXT_PUBLIC_API_BASE` matches.
- Ollama test fails: confirm Ollama is reachable and at least one model is pulled; use the Test Ollama button in Settings.
- Empty results: platforms may throttle; retry with proxy on (if configured) or wait.

## Educational note
For educational OSINT only. Respect platform terms, rate limits, and privacy. Exports happen only when you choose to export.
