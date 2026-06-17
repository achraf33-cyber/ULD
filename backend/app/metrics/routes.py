"""Aggregated telemetry routes (GPU + per-instance throughput)."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter

from app.intel import control as intel_control
from app.metrics import instance_metrics
from app.metrics.gpus import read_all as read_gpus
from app.nvidia import client as nvidia_client

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/gpus")
async def gpus():
    return await read_gpus()


@router.get("/throughput")
async def throughput():
    nvidia, intel = await asyncio.gather(
        _safe(nvidia_client.list_instances), _safe(intel_control.list_instances)
    )
    instances = [i for i in (nvidia + intel) if i.status.value == "running"]
    metrics = await asyncio.gather(
        *(instance_metrics.for_instance(inst) for inst in instances)
    )
    return list(metrics)


async def _safe(coro_fn):
    try:
        return await coro_fn()
    except Exception:
        return []
