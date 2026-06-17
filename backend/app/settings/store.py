"""SQLite-backed dashboard settings and credentials store."""
from __future__ import annotations

from app.config import Settings
from app.db import patch_category, read_category
from app.settings.keys import CREDENTIAL_KEYS, SETTINGS_KEYS


def mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return f"{value[:2]}****{value[-2:]}"


def read_settings_db() -> dict:
    return read_category("setting")


def read_credentials_db() -> dict:
    return read_category("credential")


def save_settings_patch(patch: dict) -> dict:
    filtered = {k: str(v) for k, v in patch.items() if k in SETTINGS_KEYS and v is not None}
    if "library_dirs" in filtered and "model_dirs" not in filtered:
        filtered["model_dirs"] = filtered["library_dirs"]
    return patch_category("setting", filtered)


def save_credentials_patch(patch: dict) -> dict:
    filtered: dict[str, str | None] = {}
    for key, val in patch.items():
        if key in CREDENTIAL_KEYS and val is not None:
            filtered[key] = val
    return patch_category("credential", filtered)


def merge_runtime(base: Settings) -> Settings:
    """Merge env defaults with SQLite overrides."""
    data = base.model_dump()
    db_settings = read_settings_db()
    db_creds = read_credentials_db()
    for key in SETTINGS_KEYS:
        if key in db_settings:
            data[key] = db_settings[key]
    for key in CREDENTIAL_KEYS:
        if key in db_creds:
            data[key] = db_creds[key]
    return Settings.model_validate(data)
