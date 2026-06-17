"""Unified data model spanning both NVIDIA and Intel backends."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Backend(str, Enum):
    nvidia = "nvidia"
    intel = "intel"


class InstanceStatus(str, Enum):
    running = "running"
    stopped = "stopped"
    starting = "starting"
    error = "error"
    unknown = "unknown"


class UnifiedInstance(BaseModel):
    """A single llama-server instance from either control plane."""

    name: str
    backend: Backend
    status: InstanceStatus = InstanceStatus.unknown
    port: Optional[int] = None
    model: Optional[str] = None
    ctx_size: Optional[int] = None
    description: Optional[str] = None
    options: dict = {}


class InstanceThroughput(BaseModel):
    """Per-instance inference metrics derived from llama-server."""

    name: str
    backend: Backend
    port: int
    healthy: bool = False
    tokens_per_second: Optional[float] = None
    prompt_tokens_per_second: Optional[float] = None
    kv_cache_used_percent: Optional[float] = None
    active_slots: Optional[int] = None
    total_slots: Optional[int] = None
    requests_processing: Optional[int] = None
    requests_deferred: Optional[int] = None
