"""Key-value config persistence in SQLite."""
from __future__ import annotations

from datetime import datetime, timezone

from app.db.connection import connect

Category = str


def read_category(category: Category) -> dict[str, str]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT key, value FROM config_entries WHERE category = ? ORDER BY key",
            (category,),
        ).fetchall()
    return {str(r["key"]): str(r["value"]) for r in rows}


def write_category(category: Category, data: dict[str, str]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        for key, value in data.items():
            conn.execute(
                """
                INSERT INTO config_entries (category, key, value, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(category, key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (category, key, value, now),
            )


def patch_category(category: Category, patch: dict[str, str | None]) -> dict[str, str]:
    current = read_category(category)
    for key, val in patch.items():
        if val is None:
            continue
        if val == "":
            current.pop(key, None)
            _delete_key(category, key)
        else:
            current[key] = val
    write_category(category, current)
    return current


def _delete_key(category: Category, key: str) -> None:
    with connect() as conn:
        conn.execute(
            "DELETE FROM config_entries WHERE category = ? AND key = ?",
            (category, key),
        )


def count_category(category: Category) -> int:
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM config_entries WHERE category = ?",
            (category,),
        ).fetchone()
    return int(row["n"]) if row else 0
