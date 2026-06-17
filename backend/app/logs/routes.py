"""SSE log routes for both control planes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from app.logs import streams

router = APIRouter(prefix="/api/logs", tags=["logs"])

_PRODUCERS = {"nvidia": streams.stream_nvidia, "intel": streams.stream_intel}


@router.get("/{backend}/{name}/stream")
async def stream(backend: str, name: str, request: Request, tail: int = 200):
    producer = _PRODUCERS.get(backend)
    if producer is None:
        raise HTTPException(status_code=404, detail="unknown backend")

    async def publisher():
        async for line in producer(name, tail):
            if await request.is_disconnected():
                break
            yield {"event": "log", "data": line}

    return EventSourceResponse(publisher())
