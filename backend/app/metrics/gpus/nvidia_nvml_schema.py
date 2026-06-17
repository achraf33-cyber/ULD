"""NVML snapshot schema."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NvmlSnapshot:
    index: int
    pci_slot: str
    name: str
    gpu_util: float | None
    mem_util: float | None
    mem_used_mb: float | None
    mem_total_mb: float | None
    core_count: int | None
    sm_clock_mhz: float | None
    mem_clock_mhz: float | None
    temp_c: float | None
    power_w: float | None
    encoder_util: float | None
    decoder_util: float | None
