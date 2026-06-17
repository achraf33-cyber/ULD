"""Token rate estimation from /slots when Prometheus /metrics is disabled."""
from __future__ import annotations

import time

from app.schemas import InstanceThroughput, UnifiedInstance

_prev: dict[str, tuple[float, int, int]] = {}


def apply_slot_metrics(
    result: InstanceThroughput,
    inst: UnifiedInstance,
    slots: list[dict],
) -> None:
    if not slots:
        return

    busy = sum(1 for slot in slots if slot.get("is_processing"))
    if busy:
        result.active_slots = busy
    result.total_slots = result.total_slots or len(slots)

    n_decoded = 0
    for slot in slots:
        next_token = slot.get("next_token") or []
        if next_token:
            n_decoded += int(next_token[0].get("n_decoded") or 0)
    n_prompt_done = sum(int(slot.get("n_prompt_tokens_processed") or 0) for slot in slots)

    key = f"{inst.backend.value}:{inst.name}"
    now = time.monotonic()
    prev = _prev.get(key)
    _prev[key] = (now, n_decoded, n_prompt_done)
    if not prev or result.tokens_per_second is not None:
        return

    dt = now - prev[0]
    if dt <= 0:
        return
    if n_decoded > prev[1]:
        result.tokens_per_second = round((n_decoded - prev[1]) / dt, 1)
    elif n_prompt_done > prev[2]:
        result.prompt_tokens_per_second = round((n_prompt_done - prev[2]) / dt, 1)
