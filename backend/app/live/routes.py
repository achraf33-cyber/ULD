"""SSE endpoint pushing periodic GPU + instance snapshots to the dashboard."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app import aggregate
from app.settings.runtime import get_runtime_settings
from app.live.history import ThroughputHistory
from app.metrics.gpus import read_all as read_gpus
from app.metrics.instance_metrics import for_all as throughput_for_all

router = APIRouter(prefix="/api/live", tags=["live"])
_history = ThroughputHistory()


async def _snapshot() -> dict:
    gpus, instances = await asyncio.gather(_gpus(), aggregate.list_all())
    throughput = await throughput_for_all(instances)
    history = _history.record(throughput)
    return {
        "gpus": [g.model_dump() for g in gpus],
        "instances": [i.model_dump() for i in instances],
        "throughput": [t.model_dump() for t in throughput],
        "throughput_history": history,
    }


async def _gpus():
    return await read_gpus()


@router.get("")
async def live(request: Request):
    interval = get_runtime_settings().metrics_interval_s

    async def publisher():
        while True:
            if await request.is_disconnected():
                break
            try:
                payload = await _snapshot()
            except Exception as exc:  # keep the stream alive on transient errors
                payload = {"error": str(exc)}
            yield {"event": "snapshot", "data": json.dumps(payload)}
            await asyncio.sleep(interval)

    return EventSourceResponse(publisher())
