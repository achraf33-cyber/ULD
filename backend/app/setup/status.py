"""First-install / configuration status."""
from __future__ import annotations

from fastapi import APIRouter

from app.settings.modules import blocking_modules, build_modules, credentials_module_status
from app.settings.runtime import get_runtime_settings

router = APIRouter(prefix="/api/setup", tags=["setup"])


@router.get("/status")
async def setup_status():
    cfg = get_runtime_settings()
    modules = build_modules(cfg)
    cred = credentials_module_status(cfg)
    all_modules = [{"id": m["id"], "title": m["title"], "complete": m["complete"]} for m in modules]
    all_modules.append({"id": cred["id"], "title": cred["title"], "complete": cred["complete"]})
    blocking = blocking_modules(cfg)
    return {
        "configured": not blocking,
        "install_complete": bool(cfg.install_complete),
        "modules": all_modules,
        "missing": blocking,
    }
