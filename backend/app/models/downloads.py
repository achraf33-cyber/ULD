"""Normalize llamactl download job payloads."""
from __future__ import annotations

from typing import Any


def normalize_jobs(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [_normalize_job(j) for j in raw]
    if isinstance(raw, dict):
        for key in ("jobs", "items", "data"):
            val = raw.get(key)
            if isinstance(val, list):
                return [_normalize_job(j) for j in val]
        if raw.get("id"):
            return [_normalize_job(raw)]
    return []


def _normalize_job(raw: dict[str, Any]) -> dict[str, Any]:
    progress = raw.get("progress") or {}
    repo = str(raw.get("repo") or raw.get("model") or "")
    tag = raw.get("tag")
    if ":" in repo and not tag:
        repo, tag = repo.rsplit(":", 1)
    return {
        "id": str(raw.get("id") or raw.get("job_id") or ""),
        "repo": repo,
        "tag": tag or "",
        "status": str(raw.get("status") or "unknown"),
        "progress": {
            "bytes_downloaded": int(progress.get("bytes_downloaded") or 0),
            "total_bytes": int(progress.get("total_bytes") or 0),
            "current_file": progress.get("current_file"),
        },
        "error": raw.get("error"),
    }
