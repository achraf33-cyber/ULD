"""Local model library scanning."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.library_paths import effective_library_dirs, library_roots, roots_status
from app.settings.runtime import get_runtime_settings

_MAX_LIMIT = 500


def list_library(query: str = "", limit: int = 100, offset: int = 0) -> dict:
    cfg = get_runtime_settings()
    roots = library_roots(cfg)
    needle = query.strip().lower()
    cap = min(max(limit, 1), _MAX_LIMIT)
    hits: list[dict] = []

    for root in roots:
        if not root.is_dir():
            continue
        for entry in root.rglob("*.gguf"):
            path = str(entry)
            name = entry.name
            if needle and needle not in path.lower() and needle not in name.lower():
                continue
            hits.append(_entry(entry, root))

    hits.sort(key=lambda x: x["name"].lower())
    total = len(hits)
    page = hits[offset : offset + cap]
    return {
        "configured_dirs": effective_library_dirs(cfg),
        "roots": roots_status(cfg),
        "total": total,
        "offset": offset,
        "limit": cap,
        "items": page,
    }


def _entry(entry: Path, root: Path) -> dict:
    rel = str(entry.relative_to(root)) if entry.is_relative_to(root) else entry.name
    modified = None
    size_mb = None
    try:
        stat = entry.stat()
        size_mb = round(stat.st_size / (1024 * 1024), 1)
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    except OSError:
        pass
    return {
        "path": str(entry),
        "name": entry.name,
        "relative_path": rel,
        "root": str(root),
        "size_mb": size_mb,
        "modified_at": modified,
    }
