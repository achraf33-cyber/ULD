"""HTTP routes for the NVIDIA (llamactl) control plane."""
from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from app.nvidia import client

router = APIRouter(prefix="/api/nvidia", tags=["nvidia"])


def _wrap_upstream(exc: httpx.HTTPStatusError) -> HTTPException:
    detail: Any
    try:
        detail = exc.response.json()
    except ValueError:
        detail = exc.response.text
    return HTTPException(status_code=exc.response.status_code, detail=detail)


@router.get("/instances")
async def list_instances():
    return await client.list_instances()


@router.get("/instances/{name}")
async def get_instance(name: str):
    try:
        return await client.get_instance(name)
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)


@router.post("/instances/{name}")
async def create_instance(name: str, options: dict[str, Any] = Body(...)):
    try:
        return await client.create_instance(name, options)
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)


@router.delete("/instances/{name}")
async def delete_instance(name: str):
    try:
        await client.delete_instance(name)
        return {"status": "deleted"}
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)


@router.post("/instances/{name}/{verb}")
async def instance_action(name: str, verb: str):
    if verb not in {"start", "stop", "restart"}:
        raise HTTPException(status_code=400, detail="invalid action")
    try:
        return await client.action(name, verb)
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)


@router.get("/instances/{name}/logs")
async def instance_logs(name: str, lines: int = 200):
    try:
        return {"logs": await client.logs(name, lines)}
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)


@router.get("/devices")
async def list_devices():
    try:
        return await client.devices()
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)


class DownloadBody(BaseModel):
    repo: str
    tag: str = ""
    format: str = "gguf"


@router.post("/models/download")
async def start_download(body: DownloadBody):
    try:
        return await client.start_download(body.repo, body.tag, body.format)
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)


@router.get("/models/jobs")
async def list_download_jobs():
    try:
        return await client.list_download_jobs()
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)


@router.get("/models/jobs/{job_id}")
async def get_download_job(job_id: str):
    try:
        return await client.get_download_job(job_id)
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)


@router.delete("/models/jobs/{job_id}")
async def delete_download_job(job_id: str):
    try:
        await client.delete_download_job(job_id)
        return {"status": "deleted"}
    except httpx.HTTPStatusError as exc:
        raise _wrap_upstream(exc)
