"""FastAPI entrypoint for the unified llama.cpp dashboard.

Intentionally unauthenticated (per requirements). All privileged credentials
(llamactl key) and host control (systemctl/journalctl) live server-side.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import __version__, aggregate
from app.db import init_db
from app.settings.runtime import get_runtime_settings
from app.intel import router as intel_router
from app.live import router as live_router
from app.logs import router as logs_router
from app.metrics import router as metrics_router
from app.models import router as models_router
from app.nvidia import router as nvidia_router
from app.settings import router as settings_router
from app.setup import router as setup_router
from app.wizard import router as wizard_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="ULD — Unified LlamaCPP Dashboard",
    version=__version__,
    description="CyberN Technologie Canada",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for module_router in (
    nvidia_router,
    intel_router,
    metrics_router,
    logs_router,
    live_router,
    wizard_router,
    models_router,
    settings_router,
    setup_router,
):
    app.include_router(module_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": __version__}


@app.get("/api/instances")
async def instances():
    return await aggregate.list_all()


def _mount_spa() -> None:
    init_db()
    static_dir = get_runtime_settings().static_dir
    if not os.path.isdir(static_dir):
        return
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")))

    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            from fastapi.responses import JSONResponse

            return JSONResponse({"detail": "Not Found"}, status_code=404)
        return FileResponse(
            os.path.join(static_dir, "index.html"),
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )


_mount_spa()
