"""Aggregate all GPU providers into one standard telemetry stream."""
from __future__ import annotations

import asyncio

from app.metrics.gpus import amd, generic, intel, nvidia
from app.metrics.gpus.discover import DrmDevice, list_devices
from app.metrics.gpus.names import vendor_for
from app.metrics.gpus.schema import GpuStats, GpuVendor


async def read_all() -> list[GpuStats]:
    devices = list_devices()
    groups = _group(devices)
    nvidia_s, intel_s, amd_s, other_s = await asyncio.gather(
        nvidia.read(groups[GpuVendor.nvidia]),
        intel.read(groups[GpuVendor.intel]),
        amd.read(groups[GpuVendor.amd]),
        generic.read(groups[GpuVendor.other]),
    )
    return _sort(nvidia_s + intel_s + amd_s + other_s)


def _group(devices: list[DrmDevice]) -> dict[GpuVendor, list[DrmDevice]]:
    buckets: dict[GpuVendor, list[DrmDevice]] = {v: [] for v in GpuVendor}
    for dev in devices:
        buckets[vendor_for(dev.vendor_id)].append(dev)
    return buckets


def _sort(stats: list[GpuStats]) -> list[GpuStats]:
    order = {GpuVendor.nvidia: 0, GpuVendor.amd: 1, GpuVendor.intel: 2, GpuVendor.other: 3}
    return sorted(stats, key=lambda g: (order.get(g.vendor, 9), g.index))
