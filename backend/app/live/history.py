"""SSE throughput history for the Usage page."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from app.schemas import InstanceThroughput

_HISTORY_LEN = 60


@dataclass
class ThroughputHistory:
    """Ring buffer of recent throughput samples keyed by instance."""

    _samples: dict[str, deque[dict]] = field(default_factory=dict)

    def record(self, metrics: list[InstanceThroughput]) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}
        for item in metrics:
            if not item.healthy:
                continue
            key = f"{item.backend.value}:{item.name}"
            buf = self._samples.setdefault(key, deque(maxlen=_HISTORY_LEN))
            sample = {
                "tokens_per_second": item.tokens_per_second,
                "prompt_tokens_per_second": item.prompt_tokens_per_second,
                "kv_cache_used_percent": item.kv_cache_used_percent,
                "active_slots": item.active_slots,
            }
            buf.append(sample)
            out[key] = list(buf)
        return out
