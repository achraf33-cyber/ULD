"""Wizard API — hardware discovery and native instance creation."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.wizard import create, hardware, kv_cache, runtimes

router = APIRouter(prefix="/api/wizard", tags=["wizard"])


class WizardCreateBody(BaseModel):
    hardware_id: str = ""
    hardware_ids: list[str] = Field(default_factory=list)
    name: str
    model: str
    port: int | None = None
    ctx: int = 65536
    gpu_layers: str = "auto"
    parallel: int = 1
    kv_cache_profile: str = "normal"
    kv_cache_variant: str = "turbo4"
    cache_type_k: str = ""
    cache_type_v: str = ""
    compute_backend: str | None = None
    runtime_id: str | None = None
    device_id: str | None = None
    reasoning: str = "auto"
    reasoning_format: str = ""
    reasoning_budget: int | None = None
    description: str = ""
    extra_args: str = ""
    start: bool = True


@router.get("/hardware")
async def list_hardware():
    return await hardware.list_hardware()


@router.get("/runtimes")
async def list_runtimes(vendor: str = "", multi_gpu: bool = False, catalog: bool = True):
    if catalog and not vendor:
        items = runtimes.list_catalog()
        default_id = runtimes.default_catalog_id()
        return {
            "default_runtime_id": default_id,
            "runtimes": [rt.__dict__ for rt in items],
        }
    items = runtimes.for_vendor(vendor or "nvidia", multi_gpu)
    default_id = next((rt.id for rt in items if rt.default), items[0].id if items else "")
    return {
        "default_runtime_id": default_id,
        "runtimes": [rt.__dict__ for rt in items],
    }


@router.get("/kv-options")
async def kv_options(backend: str = "nvidia", runtime_id: str | None = None):
    rt = runtime_id or None
    return {
        "engine_binary": kv_cache.engine_binary(),
        "supports_turboquant": kv_cache.supports_turboquant(rt),
        "profiles": kv_cache.list_profiles(backend, rt),
    }


@router.get("/gguf-files")
async def gguf_files(q: str = "", limit: int = 50):
    from app.wizard import gguf_files

    return gguf_files.list_gguf_files(q, min(limit, 100))


@router.get("/suggest-port")
async def suggest_port(backend: str):
    from app.schemas import Backend

    b = Backend.nvidia if backend == "nvidia" else Backend.intel
    return {"port": await create.suggest_port(b)}


@router.post("/create")
async def create_instance(body: WizardCreateBody):
    try:
        return await create.create(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
