"""Drive the Intel B70 fleet via systemd, b70-model, and journalctl.

Only one Intel model runs at a time (32GB VRAM); starting one stops the rest,
which is enforced by the existing `b70-model start` helper.
"""
from __future__ import annotations

import asyncio

import httpx

from app.settings.paths import instance_base_url
from app.settings.runtime import get_runtime_settings
from app.intel import registry
from app.schemas import Backend, InstanceStatus, UnifiedInstance


def _service(name: str) -> str:
    return f"{get_runtime_settings().intel_service_prefix}{name}.service"


async def _run(*args: str, timeout: float = 30.0) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise
    return proc.returncode or 0, out.decode(errors="replace")


async def _service_active(name: str) -> bool:
    code, out = await _run("systemctl", "is-active", _service(name))
    return code == 0 and out.strip() == "active"


async def _port_up(port: int) -> bool:
    url = f"{instance_base_url(get_runtime_settings(), port)}/v1/models"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
            return resp.status_code == 200
    except httpx.HTTPError:
        return False


async def _status_for(model: registry.IntelModel) -> InstanceStatus:
    if await _port_up(model.port):
        return InstanceStatus.running
    if await _service_active(model.name):
        return InstanceStatus.starting
    return InstanceStatus.stopped


async def list_instances() -> list[UnifiedInstance]:
    models = registry.list_models()
    statuses = await asyncio.gather(*(_status_for(m) for m in models))
    return [
        UnifiedInstance(
            name=m.name,
            backend=Backend.intel,
            status=status,
            port=m.port,
            model=m.model,
            ctx_size=m.ctx,
            description=m.description,
            options={"extra_args": m.extra_args},
        )
        for m, status in zip(models, statuses)
    ]


async def start(name: str) -> dict:
    if registry.get_model(name) is None:
        raise ValueError(f"unknown intel model '{name}'")
    code, out = await _run(get_runtime_settings().intel_b70_cli, "start", name, timeout=300.0)
    return {"status": "ok" if code == 0 else "error", "output": out}


async def stop(name: str) -> dict:
    code, out = await _run("systemctl", "stop", _service(name))
    return {"status": "ok" if code == 0 else "error", "output": out}


async def restart(name: str) -> dict:
    if registry.get_model(name) is None:
        raise ValueError(f"unknown intel model '{name}'")
    await stop(name)
    return await start(name)


async def logs(name: str, lines: int = 200) -> str:
    _, out = await _run(
        "journalctl", "-u", _service(name), "-n", str(lines), "--no-pager"
    )
    return out
