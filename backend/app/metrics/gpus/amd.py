"""AMD GPU telemetry — amdgpu sysfs (kernel.org standard) + rocm-smi fallback."""
from __future__ import annotations

import asyncio
import json

from app.metrics.gpus import effort, fdinfo
from app.metrics.gpus.discover import DrmDevice
from app.metrics.gpus.names import resolve
from app.metrics.gpus.schema import GpuMemKind, GpuStats, GpuVendor
from app.metrics.gpus.sysfs import bytes_to_mb, hwmon_power_w, hwmon_temp_c, read_int


async def read(devices: list[DrmDevice]) -> list[GpuStats]:
    if not devices:
        return []
    rocm = await _rocm_map()
    stats: list[GpuStats] = []
    for dev in devices:
        name, family, caps = resolve(dev)
        used_b = read_int(f"{dev.device_path}/mem_info_vram_used")
        total_b = read_int(f"{dev.device_path}/mem_info_vram_total")
        mem_kind = GpuMemKind.vram
        if not total_b:
            used_b = read_int(f"{dev.device_path}/mem_info_gtt_used")
            total_b = read_int(f"{dev.device_path}/mem_info_gtt_total")
            mem_kind = GpuMemKind.gtt
        rocm_row = rocm.get(dev.pci_slot) or rocm.get(dev.index)
        agg = fdinfo.aggregate(dev.pci_slot) if dev.pci_slot else fdinfo.FdInfoAggregate()
        gtt_used, gtt_total = fdinfo.gtt_mb(agg)
        row = GpuStats(
            vendor=GpuVendor.amd,
            driver=dev.driver,
            index=dev.index,
            card=dev.card,
            pci_slot=dev.pci_slot,
            render_node=dev.render_node,
            name=rocm_row.get("name", name) if rocm_row else name,
            product_family=family,
            mem_kind=mem_kind,
            util_percent=_pct(f"{dev.device_path}/gpu_busy_percent")
            or (rocm_row.get("util") if rocm_row else None),
            mem_util_percent=_pct(f"{dev.device_path}/mem_busy_percent")
            or _active_pct(used_b, total_b),
            mem_used_mb=bytes_to_mb(used_b),
            mem_total_mb=bytes_to_mb(total_b),
            gtt_used_mb=gtt_used,
            gtt_total_mb=gtt_total,
            engines=fdinfo.engine_utils(agg),
            temp_c=hwmon_temp_c(dev.device_path)
            or (rocm_row.get("temp") if rocm_row else None),
            power_w=hwmon_power_w(dev.device_path)
            or (rocm_row.get("power") if rocm_row else None),
            capabilities={**caps, "telemetry": "amdgpu-sysfs+fdinfo"},
        )
        row.effort_percent = effort.compute(row)
        stats.append(row)
    return stats


def _pct(path: str) -> float | None:
    value = read_int(path)
    return float(value) if value is not None else None


def _active_pct(used_b: int | None, total_b: int | None) -> float | None:
    if not used_b or not total_b:
        return None
    return round(min(100.0, (used_b / total_b) * 100.0), 1)


async def _rocm_map() -> dict:
    try:
        proc = await asyncio.create_subprocess_exec(
            "rocm-smi",
            "--showuse",
            "--showmeminfo",
            "vram",
            "--showtemp",
            "--showpower",
            "--json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        data = json.loads(out.decode())
    except (FileNotFoundError, asyncio.TimeoutError, json.JSONDecodeError):
        return {}
    result: dict = {}
    for key, row in data.items():
        if not isinstance(row, dict):
            continue
        idx = _parse_index(key)
        result[idx] = {
            "name": row.get("Card series", row.get("Card model")),
            "util": _json_float(row.get("GPU use (%)")),
            "temp": _json_float(row.get("Temperature (Edge)")),
            "power": _json_float(row.get("Average Graphics Package Power (W)")),
        }
    return result


def _parse_index(key: str) -> int:
    digits = "".join(c for c in key if c.isdigit())
    return int(digits) if digits else 0


def _json_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).replace("%", "").strip())
    except ValueError:
        return None
