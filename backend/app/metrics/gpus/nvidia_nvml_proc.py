"""NVML fallback when libnvidia-ml is unavailable."""
from __future__ import annotations

import glob

from app.metrics.gpus.nvidia_nvml_schema import NvmlSnapshot


def from_proc() -> list[NvmlSnapshot]:
    out: list[NvmlSnapshot] = []
    for idx, path in enumerate(sorted(glob.glob("/proc/driver/nvidia/gpus/*"))):
        info = _parse_proc_info(f"{path}/information")
        if not info:
            continue
        out.append(
            NvmlSnapshot(
                index=idx,
                pci_slot=info.get("pci", ""),
                name=info.get("model", "NVIDIA GPU"),
                gpu_util=None,
                mem_util=None,
                mem_used_mb=None,
                mem_total_mb=None,
                core_count=None,
                sm_clock_mhz=None,
                mem_clock_mhz=None,
                temp_c=None,
                power_w=None,
                encoder_util=None,
                decoder_util=None,
            )
        )
    return out


def _parse_proc_info(path: str) -> dict[str, str] | None:
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return None
    info: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        info[key.strip().lower()] = val.strip()
    if "bus location" in info:
        info["pci"] = info["bus location"].lower()
    return info if info.get("pci") else None
