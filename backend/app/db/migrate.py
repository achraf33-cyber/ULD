"""One-time import from legacy JSON config files into SQLite."""
from __future__ import annotations

import json
from pathlib import Path

from app.config import get_settings
from app.db.config_store import count_category, write_category
from app.settings.keys import CREDENTIAL_KEYS, SETTINGS_KEYS


def _load_json(path: str) -> dict[str, str]:
    p = Path(path)
    if not p.is_file():
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def migrate_json_if_needed() -> None:
    cfg = get_settings()
    if count_category("setting") == 0:
        data = _load_json(cfg.settings_file)
        filtered = {k: v for k, v in data.items() if k in SETTINGS_KEYS}
        if filtered:
            write_category("setting", filtered)
    if count_category("credential") == 0:
        data = _load_json(cfg.credentials_file)
        filtered = {k: v for k, v in data.items() if k in CREDENTIAL_KEYS}
        if filtered:
            write_category("credential", filtered)
