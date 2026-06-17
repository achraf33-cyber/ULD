"""Combine both control planes into one instance list."""
from __future__ import annotations

import asyncio

from app.intel import control as intel_control
from app.nvidia import client as nvidia_client
from app.schemas import UnifiedInstance


async def _safe(coro_fn) -> list[UnifiedInstance]:
    try:
        return await coro_fn()
    except Exception:
        return []


async def list_all() -> list[UnifiedInstance]:
    nvidia, intel = await asyncio.gather(
        _safe(nvidia_client.list_instances),
        _safe(intel_control.list_instances),
    )
    return nvidia + intel
