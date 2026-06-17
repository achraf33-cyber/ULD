"""Async log producers for Intel (journalctl -f) and NVIDIA (llamactl poll)."""
from __future__ import annotations

import asyncio
from typing import AsyncIterator

from app.settings.runtime import get_runtime_settings
from app.nvidia import client as nvidia_client


async def stream_intel(name: str, tail: int = 200) -> AsyncIterator[str]:
    service = f"{get_runtime_settings().intel_service_prefix}{name}.service"
    proc = await asyncio.create_subprocess_exec(
        "journalctl", "-u", service, "-n", str(tail), "-f", "--no-pager",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        assert proc.stdout is not None
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            yield line.decode(errors="replace").rstrip("\n")
    finally:
        if proc.returncode is None:
            proc.kill()
            await proc.wait()


async def stream_nvidia(name: str, tail: int = 200) -> AsyncIterator[str]:
    """llamactl has no follow endpoint, so poll and emit only new content."""
    seen = ""
    interval = get_runtime_settings().metrics_interval_s
    while True:
        try:
            current = await nvidia_client.logs(name, tail)
        except Exception as exc:
            yield f"[dashboard] log fetch error: {exc}"
            await asyncio.sleep(interval)
            continue
        delta = _suffix_delta(seen, current)
        if delta:
            for line in delta.splitlines():
                yield line
            seen = current
        await asyncio.sleep(interval)


def _suffix_delta(previous: str, current: str) -> str:
    if not previous:
        return current
    if current.startswith(previous):
        return current[len(previous):]
    return current
