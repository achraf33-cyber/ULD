"""Aggregate DRM fdinfo stats per GPU (kernel standard — xe/i915/amdgpu)."""
from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass, field

from app.metrics.gpus.engine import GpuEngineUtil
from app.metrics.gpus.sysfs import bytes_to_mb


@dataclass
class FdInfoAggregate:
    vram_used_b: int = 0
    vram_total_b: int = 0
    gtt_used_b: int = 0
    gtt_total_b: int = 0
    stolen_used_b: int = 0
    engines: dict[str, tuple[int, int]] = field(default_factory=dict)


_ENGINE_KEYS = ("rcs", "bcs", "vcs", "vecs", "ccs", "compute", "render", "copy", "video")


def aggregate(pci_slot: str) -> FdInfoAggregate:
    pdev = os.path.basename(os.path.realpath(f"/sys/bus/pci/devices/{pci_slot}"))
    agg = FdInfoAggregate()
    for path in glob.glob("/proc/[0-9]*/fdinfo/*"):
        try:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            continue
        if f"drm-pdev:\t{pdev}" not in text and f"drm-pdev: {pdev}" not in text:
            continue
        _merge(agg, text)
    return agg


def engine_utils(agg: FdInfoAggregate) -> list[GpuEngineUtil]:
    out: list[GpuEngineUtil] = []
    for key, (cycles, total) in agg.engines.items():
        if total <= 0:
            continue
        pct = round(min(100.0, (cycles / total) * 100.0), 1)
        if pct > 0:
            out.append(GpuEngineUtil(name=key.upper(), util_percent=pct))
    return out


def _merge(agg: FdInfoAggregate, text: str) -> None:
    agg.vram_used_b += _kib(text, "drm-active-vram0") or _kib(text, "drm-resident-vram0")
    agg.vram_total_b += _kib(text, "drm-total-vram0")
    agg.gtt_used_b += _kib(text, "drm-active-gtt") or _kib(text, "drm-resident-gtt")
    agg.gtt_total_b += _kib(text, "drm-total-gtt")
    agg.stolen_used_b += _kib(text, "drm-resident-stolen")
    for key in _ENGINE_KEYS:
        cycles = _int_key(text, f"drm-cycles-{key}")
        total = _int_key(text, f"drm-total-cycles-{key}")
        if cycles is None or total is None:
            continue
        prev_c, prev_t = agg.engines.get(key, (0, 0))
        agg.engines[key] = (prev_c + cycles, max(prev_t, total))


def _kib(text: str, key: str) -> int:
    match = re.search(rf"{key}:\s*(\d+)\s*KiB", text)
    return int(match.group(1)) * 1024 if match else 0


def _int_key(text: str, key: str) -> int | None:
    match = re.search(rf"{key}:\s*(\d+)", text)
    return int(match.group(1)) if match else None


def gtt_mb(agg: FdInfoAggregate) -> tuple[float | None, float | None]:
    return bytes_to_mb(agg.gtt_used_b or None), bytes_to_mb(agg.gtt_total_b or None)
