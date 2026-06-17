"""Field validation for settings UI."""
from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlparse

from app.settings.registry import SETTING_BY_KEY
from app.settings.detect import llamactl_reachable

_IP_RE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[01]?\d?\d)){3}|::1|localhost)$"
)


def check_field(key: str, value: str) -> dict:
    spec = SETTING_BY_KEY.get(key)
    if not spec:
        return check_path(value)
    kind = spec.field_type
    if kind == "number":
        return _check_number(value, spec.min_value, spec.max_value)
    if kind == "url":
        return _check_url(value)
    if kind == "text" and key in {"lan_ip", "instance_bind_host"}:
        return _check_host(value, required=spec.required)
    if kind == "text":
        return _check_text(value, required=spec.required)
    return check_path(value, kind)


def check_path(value: str, kind: str = "any") -> dict:
    raw = value.strip()
    if not raw:
        return {"state": "empty", "message": "Not configured"}
    if kind == "path-list":
        return _check_list(raw)
    path = Path(raw)
    if kind == "file":
        if path.is_file():
            return {"state": "ok", "message": "File found"}
        if path.exists():
            return {"state": "warn", "message": "Path exists but is not a file"}
        return {"state": "missing", "message": "File not found"}
    if kind == "dir":
        if path.is_dir():
            return {"state": "ok", "message": "Folder found"}
        if path.exists():
            return {"state": "warn", "message": "Path exists but is not a folder"}
        return {"state": "missing", "message": "Folder not found"}
    if path.exists():
        return {"state": "ok", "message": "Path found"}
    return {"state": "missing", "message": "Path not found"}


def _check_number(raw: str, min_v: float | None, max_v: float | None) -> dict:
    text = raw.strip()
    if not text:
        return {"state": "empty", "message": "Not configured"}
    try:
        num = float(text)
    except ValueError:
        return {"state": "missing", "message": "Invalid number"}
    if min_v is not None and num < min_v:
        return {"state": "missing", "message": f"Minimum {min_v}"}
    if max_v is not None and num > max_v:
        return {"state": "missing", "message": f"Maximum {max_v}"}
    return {"state": "ok", "message": "Valid"}


def _check_url(raw: str) -> dict:
    text = raw.strip()
    if not text:
        return {"state": "empty", "message": "Not configured"}
    parsed = urlparse(text)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return {"state": "ok", "message": "Valid URL"}
    return {"state": "missing", "message": "Invalid URL"}


def _check_host(raw: str, *, required: bool) -> dict:
    text = raw.strip()
    if not text:
        return {"state": "empty" if not required else "missing", "message": "Not configured"}
    if text in {"0.0.0.0", "*"} or _IP_RE.match(text):
        return {"state": "ok", "message": "Valid"}
    return {"state": "warn", "message": "Unrecognized host format"}


def _check_text(raw: str, *, required: bool) -> dict:
    text = raw.strip()
    if not text:
        return {"state": "empty" if not required else "missing", "message": "Required" if required else "Not configured"}
    return {"state": "ok", "message": "Set"}


def _check_list(raw: str) -> dict:
    parts = [p.strip() for p in raw.replace(",", ":").split(":") if p.strip()]
    if not parts:
        return {"state": "empty", "message": "Not configured"}
    missing = [p for p in parts if not os.path.isdir(p)]
    if not missing:
        return {"state": "ok", "message": f"{len(parts)} folder(s) found"}
    if len(missing) < len(parts):
        return {"state": "warn", "message": f"{len(missing)} of {len(parts)} missing"}
    return {"state": "missing", "message": "No folders found"}


def library_has_folder(cfg) -> bool:
    raw = (cfg.library_dirs or cfg.model_dirs or "").strip()
    if not raw:
        return False
    parts = [p.strip() for p in raw.replace(",", ":").split(":") if p.strip()]
    return any(os.path.isdir(p) for p in parts)


def has_nvidia_runtime(cfg) -> bool:
    if cfg.runtime_cuda_standard.strip() and os.path.isfile(cfg.runtime_cuda_standard.strip()):
        return True
    if cfg.runtime_cuda_turboquant.strip() and os.path.isfile(cfg.runtime_cuda_turboquant.strip()):
        return True
    url = cfg.llamactl_url.strip()
    if url and llamactl_reachable(url, cfg.llamactl_key):
        return True
    return False


def has_intel_runtime(cfg) -> bool:
    if cfg.runtime_sycl.strip() and os.path.isfile(cfg.runtime_sycl.strip()):
        return True
    if cfg.intel_conf.strip() and os.path.isfile(cfg.intel_conf.strip()):
        return True
    return False
