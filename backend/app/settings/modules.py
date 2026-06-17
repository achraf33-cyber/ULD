"""Modular configuration groups for the Settings UI."""
from __future__ import annotations

from app.config import Settings, get_settings
from app.settings.registry import MODULE_DEFS, SETTING_DEFS
from app.settings.detect import autodetect_keys
from app.settings import store
from app.settings.validate import (
    check_field,
    has_intel_runtime,
    has_nvidia_runtime,
    library_has_folder,
)


def _value(cfg: Settings, key: str) -> str:
    raw = getattr(cfg, key, "")
    if key in {"metrics_interval_s", "port"}:
        return str(raw)
    return str(raw or "")


def _module_complete(cfg: Settings, module_id: str) -> bool:
    if module_id == "library":
        if not (cfg.library_dirs.strip() or cfg.model_dirs.strip()):
            return False
        return library_has_folder(cfg)
    if module_id == "nvidia":
        return has_nvidia_runtime(cfg)
    if module_id == "intel":
        return has_intel_runtime(cfg)
    if module_id == "server":
        host = str(cfg.host or "").strip()
        port = str(cfg.port or "").strip()
        if not host or not port:
            return False
        if check_field("host", host)["state"] == "missing":
            return False
        if check_field("port", port)["state"] == "missing":
            return False
        static = str(cfg.static_dir or "").strip()
        if static and check_field("static_dir", static)["state"] == "missing":
            return False
        return True
    if module_id == "credentials":
        if cfg.llamactl_url.strip() and not cfg.llamactl_key.strip():
            return False
        return True
    fields = [s for s in SETTING_DEFS if s.module_id == module_id and not s.ui_hidden and not s.credential]
    for spec in fields:
        if not spec.required:
            continue
        val = _value(cfg, spec.key)
        if not val.strip():
            return False
        status = check_field(spec.key, val)
        if status["state"] in {"missing", "empty"}:
            return False
    return True


def blocking_modules(cfg: Settings) -> list[dict[str, str]]:
    """Modules that block fleet operations until configured."""
    raw = store.merge_runtime(get_settings())
    out: list[dict[str, str]] = []
    if not _module_complete(cfg, "library"):
        mod = next(m for m in MODULE_DEFS if m.id == "library")
        out.append({"id": "library", "title": mod.title})
    if _nvidia_expected(raw) and not _module_complete(cfg, "nvidia"):
        mod = next(m for m in MODULE_DEFS if m.id == "nvidia")
        out.append({"id": mod.id, "title": mod.title})
    return out


def _nvidia_expected(raw: Settings) -> bool:
    if raw.llamactl_url.strip():
        return True
    try:
        from app.metrics.gpus.discover import list_devices
        from app.metrics.gpus.schema import GpuVendor

        return any(d.vendor == GpuVendor.nvidia for d in list_devices())
    except OSError:
        return False


def build_modules(cfg: Settings) -> list[dict]:
    raw = store.merge_runtime(get_settings())
    detected = autodetect_keys(raw)
    out: list[dict] = []
    for mod in MODULE_DEFS:
        if mod.id == "credentials":
            continue
        fields = []
        for spec in SETTING_DEFS:
            if spec.module_id != mod.id or spec.ui_hidden or spec.credential:
                continue
            val = _value(cfg, spec.key)
            status = None
            if spec.field_type in {"file", "dir", "path-list", "number", "url", "text"}:
                status = check_field(spec.key, val)
            if spec.key in detected and val.strip():
                status = {"state": "ok", "message": "Auto-detected"}
            fields.append(
                {
                    "key": spec.key,
                    "label": spec.label,
                    "hint": spec.hint,
                    "type": spec.field_type,
                    "required": spec.required,
                    "value": val,
                    "status": status,
                    "restart_on_change": spec.restart_on_change,
                }
            )
        out.append(
            {
                "id": mod.id,
                "title": mod.title,
                "description": mod.description,
                "complete": _module_complete(cfg, mod.id),
                "fields": fields,
            }
        )
    return out


def credentials_module_status(cfg: Settings) -> dict:
    complete = _module_complete(cfg, "credentials")
    return {"id": "credentials", "title": "Credentials", "complete": complete}
