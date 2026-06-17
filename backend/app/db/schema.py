"""SQLite schema initialization."""
from __future__ import annotations

from app.db.connection import SCHEMA_VERSION, connect


def init_schema() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS config_entries (
                category TEXT NOT NULL CHECK (category IN ('setting', 'credential')),
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (category, key)
            );

            CREATE INDEX IF NOT EXISTS idx_config_category
                ON config_entries (category);
            """
        )
        row = conn.execute(
            "SELECT value FROM schema_meta WHERE key = 'version'",
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO schema_meta (key, value) VALUES ('version', ?)",
                (str(SCHEMA_VERSION),),
            )
