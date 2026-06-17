"""SQLite database path and connection helpers."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.config import _PROJECT_ROOT, get_settings

SCHEMA_VERSION = 1


def database_path() -> Path:
    raw = get_settings().database_path
    path = Path(raw)
    if not path.is_absolute():
        path = _PROJECT_ROOT / path
    return path


@contextmanager
def connect():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
