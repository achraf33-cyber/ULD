"""KV cache profile presets for wizard instance creation."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml

from app.settings.runtime import get_runtime_settings
from app.wizard import runtimes as wizard_runtimes

_PROFILES: dict[str, dict[str, str]] = {
    "turbo4": {"cache_type_k": "turbo4", "cache_type_v": "turbo4"},
    "turbo3": {"cache_type_k": "turbo3", "cache_type_v": "turbo3"},
    "mixed": {"cache_type_k": "q8_0", "cache_type_v": "turbo3"},
    "normal": {"cache_type_k": "q8_0", "cache_type_v": "q8_0"},
    "full": {"cache_type_k": "f16", "cache_type_v": "f16"},
}


@lru_cache
def engine_binary() -> str:
    path = get_runtime_settings().llamactl_config.strip()
    if not path:
        return ""
    try:
        with open(path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return str(data.get("backends", {}).get("llama-cpp", {}).get("command", ""))
    except OSError:
        return ""


def supports_turboquant(runtime_id: str | None = None) -> bool:
    return wizard_runtimes.supports_turboquant(runtime_id)


def list_profiles(backend: str, runtime_id: str | None = None) -> list[dict[str, Any]]:
    turbo = supports_turboquant(runtime_id) and backend == "nvidia"
    items: list[dict[str, Any]] = [
        {"id": "normal", "label": "Normal (q8_0)", **_PROFILES["normal"], "hint": "Balanced VRAM/quality"},
        {"id": "full", "label": "Full precision (f16)", **_PROFILES["full"], "hint": "Highest KV quality"},
    ]
    if turbo:
        items.insert(
            0,
            {"id": "turbo", "label": "TurboQuant", "hint": "Lowest KV VRAM (turboquant binary)"},
        )
    items.append({"id": "custom", "label": "Custom", "cache_type_k": "", "cache_type_v": "", "hint": "Expert"})
    return items


def resolve_types(
    profile: str,
    variant: str = "turbo4",
    custom_k: str = "",
    custom_v: str = "",
    runtime_id: str | None = None,
) -> tuple[str, str]:
    if profile == "custom":
        return custom_k, custom_v
    if profile == "turbo":
        if not supports_turboquant(runtime_id):
            raise ValueError("TurboQuant KV requires the TurboQuant runtime")
        key = variant if variant in _PROFILES else "turbo4"
        p = _PROFILES[key]
        return p["cache_type_k"], p["cache_type_v"]
    if profile in _PROFILES:
        p = _PROFILES[profile]
        return p["cache_type_k"], p["cache_type_v"]
    return custom_k, custom_v


def intel_extra_cache_flags(cache_k: str, cache_v: str) -> str:
    parts: list[str] = []
    if cache_k:
        parts.append(f"--cache-type-k {cache_k}")
    if cache_v:
        parts.append(f"--cache-type-v {cache_v}")
    return " ".join(parts)
