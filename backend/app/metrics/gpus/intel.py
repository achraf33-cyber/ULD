"""Intel GPU telemetry — xe (Arc/B-series/B70 Pro) + i915 (embedded)."""
from __future__ import annotations

import asyncio
import glob
import time

from app.metrics.gpus.discover import DrmDevice
from app.metrics.gpus import effort, fdinfo, intel_vram
from app.metrics.gpus.names import resolve
from app.metrics.gpus.schema import GpuMemKind, GpuStats, GpuVendor
from app.metrics.gpus.sysfs import hwmon_temp_c, read_int


async def read(devices: list[DrmDevice]) -> list[GpuStats]:
    if not devices:
        return []
    samples = [_sample(d.device_path) for d in devices]
    start = time.monotonic()
    await asyncio.sleep(0.25)
    samples2 = [_sample(d.device_path) for d in devices]
    elapsed = time.monotonic() - start

    stats: list[GpuStats] = []
    for dev, (idle0, e0), (idle1, e1) in zip(devices, samples, samples2):
        name, family, caps = resolve(dev)
        mem_used, mem_total = intel_vram.read_vram_mb(dev.device_path, dev.driver)
        mem_kind = GpuMemKind.vram if dev.driver == "xe" else GpuMemKind.system
        agg = fdinfo.aggregate(dev.pci_slot) if dev.pci_slot else fdinfo.FdInfoAggregate()
        gtt_used, gtt_total = fdinfo.gtt_mb(agg)
        engines = fdinfo.engine_utils(agg)
        freq = read_int(f"{dev.device_path}/tile0/gt0/freq0/act_freq")
        if freq is None:
            freq = read_int(f"{dev.device_path}/gt/gt0/rps/cur_freq")
        row = GpuStats(
            vendor=GpuVendor.intel,
            driver=dev.driver,
            index=dev.index,
            card=dev.card,
            pci_slot=dev.pci_slot,
            render_node=dev.render_node,
            name=name,
            product_family=family,
            mem_kind=mem_kind,
            util_percent=_util(idle0, idle1, elapsed),
            mem_util_percent=_active_pct(agg.vram_used_b, agg.vram_total_b),
            mem_used_mb=mem_used,
            mem_total_mb=mem_total,
            gtt_used_mb=gtt_used,
            gtt_total_mb=gtt_total,
            sm_clock_mhz=float(freq) if freq else None,
            engines=engines,
            temp_c=hwmon_temp_c(dev.device_path),
            power_w=_power(e0, e1, elapsed),
            capabilities={**caps, "telemetry": "drm-ioctl+fdinfo"},
        )
        row.effort_percent = effort.compute(row)
        stats.append(row)
    return stats


def _sample(device: str) -> tuple[int | None, int | None]:
    idle = _idle_ms(device)
    energy = _energy_uj(device)
    return idle, energy


def _idle_ms(device: str) -> int | None:
    for path in (
        f"{device}/tile0/gt0/gtidle/idle_residency_ms",
        f"{device}/gt/gt0/gtidle/idle_residency_ms",
    ):
        value = read_int(path)
        if value is not None:
            return value
    return None


def _energy_uj(device: str) -> int | None:
    for path in glob.glob(f"{device}/hwmon/hwmon*/energy1_input"):
        value = read_int(path)
        if value is not None:
            return value
    return None


def _util(idle0: int | None, idle1: int | None, elapsed: float) -> float | None:
    if idle0 is None or idle1 is None or elapsed <= 0:
        return None
    busy = 1.0 - ((idle1 - idle0) / (elapsed * 1000.0))
    return round(max(0.0, min(1.0, busy)) * 100.0, 1)


def _power(e0: int | None, e1: int | None, elapsed: float) -> float | None:
    if e0 is None or e1 is None or elapsed <= 0:
        return None
    return round((e1 - e0) / 1_000_000.0 / elapsed, 1)


def _active_pct(used_b: int, total_b: int) -> float | None:
    if total_b <= 0:
        return None
    return round(min(100.0, (used_b / total_b) * 100.0), 1)
