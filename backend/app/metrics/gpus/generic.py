"""Generic DRM GPU — minimal stats when no vendor-specific provider exists."""
from __future__ import annotations

from app.metrics.gpus.discover import DrmDevice
from app.metrics.gpus.names import resolve
from app.metrics.gpus.schema import GpuMemKind, GpuStats, GpuVendor
from app.metrics.gpus.sysfs import hwmon_temp_c


async def read(devices: list[DrmDevice]) -> list[GpuStats]:
    return [
        GpuStats(
            vendor=GpuVendor.other,
            driver=dev.driver,
            index=dev.index,
            card=dev.card,
            pci_slot=dev.pci_slot,
            render_node=dev.render_node,
            name=resolve(dev)[0],
            product_family=resolve(dev)[1],
            mem_kind=GpuMemKind.unknown,
            temp_c=hwmon_temp_c(dev.device_path),
            capabilities=resolve(dev)[2],
        )
        for dev in devices
    ]
