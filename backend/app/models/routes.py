"""Unified model library and download management routes."""
from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models import downloads, library
from app.nvidia import client as nvidia_client

router = APIRouter(prefix="/api/models", tags=["models"])


class StartDownloadBody(BaseModel):
    repo: str
    tag: str = ""
    format: str = "gguf"


@router.get("/library")
@router.get("/library/")
async def model_library(q: str = "", limit: int = 100, offset: int = 0):
    return library.list_library(q, limit, offset)


@router.get("/downloads")
async def list_downloads():
    try:
        raw = await nvidia_client.list_download_jobs()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    return {"jobs": downloads.normalize_jobs(raw)}


@router.post("/downloads")
async def start_download(body: StartDownloadBody):
    try:
        return await nvidia_client.start_download(body.repo, body.tag, body.format)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


@router.get("/downloads/{job_id}")
async def get_download(job_id: str):
    try:
        raw = await nvidia_client.get_download_job(job_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    jobs = downloads.normalize_jobs(raw if isinstance(raw, dict) else {"items": [raw]})
    return jobs[0] if jobs else raw


@router.delete("/downloads/{job_id}")
async def cancel_download(job_id: str):
    try:
        await nvidia_client.delete_download_job(job_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    return {"status": "deleted"}
