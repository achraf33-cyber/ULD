"""Per-engine utilization block (compute, video, copy, …)."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class GpuEngineUtil(BaseModel):
    name: str
    util_percent: Optional[float] = None
