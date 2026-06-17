"""Resolve and inspect local GGUF library scan directories."""
from __future__ import annotations

from pathlib import Path

from app.config import Settings


def parse_dir_list(raw: str) -> list[Path]:
    normalized = raw.replace(",", ":")
    return [Path(p.strip()) for p in normalized.split(":") if p.strip()]


def effective_library_dirs(settings: Settings) -> str:
    return settings.library_dirs.strip() or settings.model_dirs.strip()


def library_roots(settings: Settings) -> list[Path]:
    return parse_dir_list(effective_library_dirs(settings))


def roots_status(settings: Settings) -> list[dict]:
    out: list[dict] = []
    for root in library_roots(settings):
        exists = root.is_dir()
        count = 0
        if exists:
            try:
                count = sum(1 for _ in root.rglob("*.gguf"))
            except OSError:
                count = 0
        out.append({"path": str(root), "exists": exists, "gguf_count": count})
    return out
