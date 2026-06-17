"""Intel GPU VRAM telemetry via official kernel interfaces."""
from __future__ import annotations

import glob
import os

from app.metrics.gpus import intel_vram_ioctl as ioctl
from app.metrics.gpus import intel_vram_sysfs as sysfs

_INTEL_VENDOR = "0x8086"


def find_intel_devices() -> list[tuple[str, str]]:
    """Return (device_sysfs_path, driver_name) for each Intel GPU."""
    found: list[tuple[str, str]] = []
    for vendor_file in glob.glob("/sys/class/drm/card*/device/vendor"):
        try:
            with open(vendor_file, encoding="utf-8") as handle:
                if handle.read().strip() != _INTEL_VENDOR:
                    continue
            device = os.path.dirname(vendor_file)
            driver = os.path.basename(os.path.realpath(os.path.join(device, "driver")))
            found.append((device, driver))
        except OSError:
            continue
    return found


def read_vram_mb(device: str, driver: str) -> tuple[float | None, float | None]:
    used, total = ioctl.from_ioctl(device, driver)
    if total:
        return _to_mb(used), _to_mb(total)
    used, total = sysfs.from_debugfs(device, driver)
    if total:
        return _to_mb(used), _to_mb(total)
    used, total = sysfs.from_fdinfo(device)
    if total:
        return _to_mb(used), _to_mb(total)
    return None, None


def _to_mb(value: int | None) -> float | None:
    return round(value / (1024 * 1024), 1) if value is not None else None
