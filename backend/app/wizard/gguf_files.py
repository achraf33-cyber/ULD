"""Local GGUF file discovery for the create wizard."""
from __future__ import annotations

from pathlib import Path

from app.library_paths import library_roots
from app.settings.runtime import get_runtime_settings

_MAX_RESULTS = 100


def list_gguf_files(query: str = "", limit: int = _MAX_RESULTS) -> list[dict[str, str | float | None]]:
    """Return matching .gguf paths under configured library directories."""
    needle = query.strip().lower()
    hits: list[dict[str, str | float | None]] = []
    for root in library_roots(get_runtime_settings()):
        if not root.is_dir():
            continue
        for entry in root.rglob("*.gguf"):
            path = str(entry)
            name = entry.name
            if needle and needle not in path.lower() and needle not in name.lower():
                continue
            hits.append({"path": path, "name": name, "size_mb": _size_mb(entry)})
            if len(hits) >= limit:
                return hits
    return hits


def _size_mb(path: Path) -> float | None:
    try:
        return round(path.stat().st_size / (1024 * 1024), 1)
    except OSError:
        return None
