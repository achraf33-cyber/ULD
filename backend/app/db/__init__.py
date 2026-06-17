"""Dashboard SQLite database — public exports."""
from __future__ import annotations

from app.db.config_store import count_category, patch_category, read_category
from app.db.connection import database_path
from app.db.migrate import migrate_json_if_needed
from app.db.schema import init_schema


def init_db() -> None:
    init_schema()
    migrate_json_if_needed()


__all__ = [
    "count_category",
    "database_path",
    "init_db",
    "patch_category",
    "read_category",
]
