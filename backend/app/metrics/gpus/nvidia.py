"""NVIDIA GPU telemetry — NVML driver API (no nvidia-smi)."""
from __future__ import annotations

from app.metrics.gpus.discover import DrmDevice
from app.metrics.gpus import effort, nvidia_nvml
from app.metrics.gpus.names import resolve
from app.metrics.gpus.schema import GpuMemKind, GpuStats, GpuVendor


def _normalize_pci(raw: str) -> str:
    raw = raw.strip().lower().replace("00000000:", "0000:")
    if raw and not raw.startswith("0000:"):
        raw = f"0000:{raw}"
    return raw


async def read(devices: list[DrmDevice]) -> list[GpuStats]:
    if not devices:
        return []
    by_pci = {_normalize_pci(d.pci_slot): d for d in devices if d.pci_slot}
    stats: list[GpuStats] = []
    for snap in nvidia_nvml.read_all():
        dev = by_pci.get(_normalize_pci(snap.pci_slot))
        name, family, caps = resolve(dev) if dev else ("NVIDIA GPU", None, {"api": ["cuda"]})
        if snap.name:
            name = snap.name
        caps = {**caps, "telemetry": "nvml", "cores": snap.core_count}
        row = GpuStats(
            vendor=GpuVendor.nvidia,
            driver="nvidia",
            index=dev.index if dev else snap.index,
            card=dev.card if dev else "",
            pci_slot=dev.pci_slot if dev else snap.pci_slot,
            render_node=dev.render_node if dev else None,
            name=name,
            product_family=family,
            mem_kind=GpuMemKind.vram,
            util_percent=snap.gpu_util,
            mem_util_percent=snap.mem_util,
            mem_used_mb=snap.mem_used_mb,
            mem_total_mb=snap.mem_total_mb,
            core_count=snap.core_count,
            sm_clock_mhz=snap.sm_clock_mhz,
            mem_clock_mhz=snap.mem_clock_mhz,
            encoder_util_percent=snap.encoder_util,
            decoder_util_percent=snap.decoder_util,
            temp_c=snap.temp_c,
            power_w=snap.power_w,
            capabilities=caps,
        )
        row.effort_percent = effort.compute(row)
        stats.append(row)
    return stats
