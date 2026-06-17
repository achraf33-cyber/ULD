"""HTTP routes for the Intel B70 control plane."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.intel import control, registry

router = APIRouter(prefix="/api/intel", tags=["intel"])


class CreateIntelModel(BaseModel):
    name: str
    port: int
    ctx: int
    model: str
    description: str = ""
    extra_args: str = ""


@router.get("/instances")
async def list_instances():
    return await control.list_instances()


@router.get("/registry")
def list_registry():
    return [vars(m) for m in registry.list_models()]


@router.post("/instances")
def create_model(payload: CreateIntelModel):
    try:
        registry.add_model(registry.IntelModel(**payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"status": "created", "name": payload.name}


@router.post("/instances/{name}/start")
async def start_instance(name: str):
    try:
        return await control.start(name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/instances/{name}/stop")
async def stop_instance(name: str):
    return await control.stop(name)


@router.post("/instances/{name}/restart")
async def restart_instance(name: str):
    try:
        return await control.restart(name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/instances/{name}")
async def delete_instance(name: str):
    try:
        registry.remove_model(name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"status": "deleted", "name": name}


@router.get("/instances/{name}/logs")
async def instance_logs(name: str, lines: int = 200):
    return {"logs": await control.logs(name, lines)}
