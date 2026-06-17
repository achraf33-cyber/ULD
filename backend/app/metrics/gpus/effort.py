"""Composite GPU load score from all available utilization signals."""
from __future__ import annotations

from app.metrics.gpus.schema import GpuStats


def compute(stats: GpuStats) -> float | None:
    parts: list[float] = []
    for value in (
        stats.util_percent,
        stats.mem_util_percent,
        stats.encoder_util_percent,
        stats.decoder_util_percent,
    ):
        if value is not None:
            parts.append(float(value))
    for engine in stats.engines:
        if engine.util_percent is not None:
            parts.append(float(engine.util_percent))
    if stats.mem_total_mb and stats.mem_used_mb:
        parts.append(min(100.0, (stats.mem_used_mb / stats.mem_total_mb) * 100.0))
    if stats.gtt_total_mb and stats.gtt_used_mb:
        parts.append(min(100.0, (stats.gtt_used_mb / stats.gtt_total_mb) * 100.0))
    if not parts:
        return None
    return round(max(parts), 1)
