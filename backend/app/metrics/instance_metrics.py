"""Per-instance inference metrics scraped from each llama-server.

Reads Prometheus `/metrics` when enabled, otherwise falls back to `/slots`
and `/props` for live activity and estimated token rates.
"""
from __future__ import annotations

import asyncio

import httpx

from app.metrics.slot_rates import apply_slot_metrics
from app.settings.paths import instance_base_url
from app.settings.runtime import get_runtime_settings
from app.schemas import InstanceStatus, InstanceThroughput, UnifiedInstance

_PROM_MAP = {
    "llamacpp:predicted_tokens_seconds": "tokens_per_second",
    "llamacpp_predicted_tokens_seconds": "tokens_per_second",
    "llamacpp:prompt_tokens_seconds": "prompt_tokens_per_second",
    "llamacpp_prompt_tokens_seconds": "prompt_tokens_per_second",
    "llamacpp:kv_cache_usage_ratio": "kv_cache_used_percent",
    "llamacpp_kv_cache_usage_ratio": "kv_cache_used_percent",
    "llamacpp:requests_processing": "requests_processing",
    "llamacpp_requests_processing": "requests_processing",
    "llamacpp:requests_deferred": "requests_deferred",
    "llamacpp_requests_deferred": "requests_deferred",
}


def _parse_prometheus(text: str) -> dict[str, float]:
    values: dict[str, float] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        key = parts[0].split("{", 1)[0]
        try:
            values[key] = float(parts[1])
        except ValueError:
            continue
    return values


async def _scrape(client: httpx.AsyncClient, port: int) -> dict[str, float]:
    base = instance_base_url(get_runtime_settings(), port)
    try:
        resp = await client.get(f"{base}/metrics")
        if resp.status_code != 200:
            return {}
        body = resp.text
        if body.lstrip().startswith("{"):
            return {}
        return _parse_prometheus(body)
    except httpx.HTTPError:
        return {}


async def _props(client: httpx.AsyncClient, port: int) -> dict:
    base = instance_base_url(get_runtime_settings(), port)
    try:
        resp = await client.get(f"{base}/props")
        if resp.status_code == 200:
            return resp.json()
    except (httpx.HTTPError, ValueError):
        return {}
    return {}


async def _slots(client: httpx.AsyncClient, port: int) -> list[dict]:
    base = instance_base_url(get_runtime_settings(), port)
    try:
        resp = await client.get(f"{base}/slots")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
    except (httpx.HTTPError, ValueError):
        return []
    return []


def _apply_prom(result: InstanceThroughput, prom: dict[str, float]) -> None:
    for metric, field in _PROM_MAP.items():
        if metric not in prom:
            continue
        value = prom[metric]
        if field == "kv_cache_used_percent":
            value = round(value * 100.0, 1)
        elif field in {"requests_processing", "requests_deferred"}:
            value = int(value)
        setattr(result, field, value)
    if result.requests_processing is not None:
        result.active_slots = result.requests_processing


async def for_instance(inst: UnifiedInstance) -> InstanceThroughput:
    result = InstanceThroughput(
        name=inst.name, backend=inst.backend, port=inst.port or 0
    )
    if not inst.port or inst.status != InstanceStatus.running:
        return result

    async with httpx.AsyncClient(timeout=3.0) as client:
        prom, props, slots = await asyncio.gather(
            _scrape(client, inst.port),
            _props(client, inst.port),
            _slots(client, inst.port),
        )

    if not prom and not props and not slots:
        return result

    result.healthy = True
    _apply_prom(result, prom)
    result.total_slots = props.get("total_slots")
    apply_slot_metrics(result, inst, slots)
    return result


async def for_all(instances: list[UnifiedInstance]) -> list[InstanceThroughput]:
    if not instances:
        return []
    return list(await asyncio.gather(*(for_instance(i) for i in instances)))
