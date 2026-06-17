"""GPU telemetry schema — vendor-agnostic, works for any DRM GPU."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.metrics.gpus.engine import GpuEngineUtil


class GpuVendor(str, Enum):
    nvidia = "nvidia"
    intel = "intel"
    amd = "amd"
    other = "other"


class GpuMemKind(str, Enum):
    vram = "vram"
    gtt = "gtt"
    system = "system"
    unknown = "unknown"


class GpuStats(BaseModel):
    """Standard telemetry block for any GPU (NVIDIA, Intel Arc/B-series, AMD, …)."""

    vendor: GpuVendor
    driver: str = "unknown"
    index: int = 0
    card: str = ""
    pci_slot: Optional[str] = None
    render_node: Optional[str] = None
    name: str = "GPU"
    product_family: Optional[str] = None
    mem_kind: GpuMemKind = GpuMemKind.vram
    util_percent: Optional[float] = None
    mem_util_percent: Optional[float] = None
    mem_used_mb: Optional[float] = None
    mem_total_mb: Optional[float] = None
    gtt_used_mb: Optional[float] = None
    gtt_total_mb: Optional[float] = None
    core_count: Optional[int] = None
    sm_clock_mhz: Optional[float] = None
    mem_clock_mhz: Optional[float] = None
    encoder_util_percent: Optional[float] = None
    decoder_util_percent: Optional[float] = None
    effort_percent: Optional[float] = None
    engines: list[GpuEngineUtil] = Field(default_factory=list)
    temp_c: Optional[float] = None
    power_w: Optional[float] = None
    freq_mhz: Optional[float] = None
    capabilities: dict = Field(default_factory=dict)
