"""Popular sites database for username checks.

We load the shared platform catalog from v3/data/platforms.json so the backend
uses the exact list the UI shows. If the file is missing or unreadable, startup
fails to avoid drifting to any old hardcoded set.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent  # v3/backend
PLATFORM_PATH = BASE_DIR.parent / "data" / "platforms.json"


def _load_platform_catalog() -> Optional[List[Dict[str, Any]]]:
    try:
        raw = PLATFORM_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        sites: List[Dict[str, Any]] = []
        for category, entries in data.items():
            for entry in entries:
                name = entry.get("name")
                url = entry.get("url")
                if not name or not url:
                    continue
                sites.append(
                    {
                        "name": name,
                        "url": url,  # may contain {handle}; search_service normalizes both {handle} and {}.
                        "category": category,
                        "positive_keywords": [name.lower()],  # lightweight positive signal
                        "negative_keywords": [],
                        "allow_redirect": False,
                    }
                )
        logger.info("Loaded %d platforms from %s", len(sites), PLATFORM_PATH)
        return sites
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load platform catalog: %s", exc)
        return None


SITES_DB: List[Dict[str, Any]] = _load_platform_catalog() or []
if not SITES_DB:
    raise RuntimeError(f"Failed to load platform catalog from {PLATFORM_PATH}")
