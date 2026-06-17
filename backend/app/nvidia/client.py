"""Thin async client for the llamactl management API.

The llamactl bearer key is injected here, server-side only, so the browser
never has to hold it.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.settings.runtime import get_runtime_settings
from app.schemas import Backend, InstanceStatus, UnifiedInstance

_API = "/api/v1"


def _headers() -> dict[str, str]:
    key = get_runtime_settings().llamactl_key
    return {"Authorization": f"Bearer {key}"} if key else {}


def _client(timeout: float = 30.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=get_runtime_settings().llamactl_url,
        headers=_headers(),
        timeout=timeout,
    )


def _to_unified(raw: dict[str, Any]) -> UnifiedInstance:
    options = raw.get("options", {}) or {}
    backend_opts = options.get("backend_options", {}) or {}
    status = str(raw.get("status", "unknown")).lower()
    return UnifiedInstance(
        name=raw.get("name", "?"),
        backend=Backend.nvidia,
        status=_map_status(status),
        port=backend_opts.get("port"),
        model=backend_opts.get("model"),
        ctx_size=backend_opts.get("ctx_size"),
        description=options.get("group"),
        options=options,
    )


def _map_status(status: str) -> InstanceStatus:
    try:
        return InstanceStatus(status)
    except ValueError:
        return InstanceStatus.unknown


async def list_instances() -> list[UnifiedInstance]:
    async with _client() as client:
        resp = await client.get(f"{_API}/instances")
        resp.raise_for_status()
        return [_to_unified(item) for item in resp.json()]


async def get_instance(name: str) -> dict[str, Any]:
    async with _client() as client:
        resp = await client.get(f"{_API}/instances/{name}")
        resp.raise_for_status()
        return resp.json()


async def create_instance(name: str, options: dict[str, Any]) -> dict[str, Any]:
    async with _client(timeout=120.0) as client:
        resp = await client.post(f"{_API}/instances/{name}", json=options)
        resp.raise_for_status()
        return resp.json()


async def delete_instance(name: str) -> None:
    async with _client() as client:
        resp = await client.delete(f"{_API}/instances/{name}")
        resp.raise_for_status()


async def action(name: str, verb: str) -> dict[str, Any]:
    """verb in {start, stop, restart}."""
    async with _client(timeout=180.0) as client:
        resp = await client.post(f"{_API}/instances/{name}/{verb}")
        resp.raise_for_status()
        return resp.json() if resp.content else {"status": "ok"}


async def logs(name: str, lines: int = 200) -> str:
    async with _client() as client:
        resp = await client.get(f"{_API}/instances/{name}/logs", params={"lines": lines})
        resp.raise_for_status()
        return resp.text


async def devices() -> Any:
    async with _client() as client:
        resp = await client.get(f"{_API}/backends/llama-cpp/devices")
        resp.raise_for_status()
        return resp.json()


async def start_download(repo: str, tag: str = "", fmt: str = "gguf") -> dict[str, Any]:
    """Start a HuggingFace GGUF download via llamactl."""
    spec = f"{repo}:{tag}" if tag else repo
    body: dict[str, Any] = {"repo": spec, "format": fmt}
    token = get_runtime_settings().huggingface_token.strip()
    if token:
        body["hf_token"] = token
    async with _client(timeout=120.0) as client:
        resp = await client.post(f"{_API}/models/download", json=body)
        resp.raise_for_status()
        return resp.json()


async def get_download_job(job_id: str) -> dict[str, Any]:
    async with _client() as client:
        resp = await client.get(f"{_API}/models/jobs/{job_id}")
        resp.raise_for_status()
        return resp.json()


async def list_download_jobs() -> dict[str, Any]:
    async with _client() as client:
        resp = await client.get(f"{_API}/models/jobs")
        resp.raise_for_status()
        return resp.json()


async def delete_download_job(job_id: str) -> None:
    async with _client() as client:
        resp = await client.delete(f"{_API}/models/jobs/{job_id}")
        resp.raise_for_status()
