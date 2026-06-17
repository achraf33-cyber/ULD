"""Create llama.cpp instances on the wizard-selected GPU(s)."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from app.intel import control, registry
from app.nvidia import client as nvidia_client
from app.schemas import Backend
from app.settings.runtime import get_runtime_settings
from app.wizard.hardware import list_hardware
from app.wizard.kv_cache import intel_extra_cache_flags, resolve_types
from app.wizard.runtimes import default_for, resolve as resolve_runtime
from app.wizard.schema import WizardHardware


async def create(payload: dict[str, Any]) -> dict[str, Any]:
    hw_list = await _resolve_many(_hardware_ids(payload))
    primary = hw_list[0]
    if not all(h.creatable for h in hw_list):
        bad = next(h for h in hw_list if not h.creatable)
        raise HTTPException(status_code=400, detail=bad.note or "Hardware not creatable")

    name = payload["name"]
    model = payload["model"]
    port = int(payload.get("port") or await suggest_port(primary.backend))
    ctx = int(payload.get("ctx", 65536))
    start = bool(payload.get("start", True))
    cache_k, cache_v = _resolve_kv(payload, primary.backend.value)
    runtime = _resolve_runtime_obj(hw_list, payload)

    if primary.backend == Backend.nvidia:
        result = await _create_nvidia(
            hw_list, name, model, port, ctx, payload, cache_k, cache_v, runtime
        )
        if start:
            await nvidia_client.action(name, "start")
        return result

    result = await _create_intel(primary, name, model, port, ctx, payload, cache_k, cache_v, runtime)
    if start:
        await control.start(name)
    return result


def _hardware_ids(payload: dict[str, Any]) -> list[str]:
    if payload.get("hardware_ids"):
        return list(payload["hardware_ids"])
    if payload.get("hardware_id"):
        return [str(payload["hardware_id"])]
    raise HTTPException(status_code=422, detail="hardware_ids required")


def _resolve_kv(payload: dict[str, Any], backend: str) -> tuple[str, str]:
    profile = str(payload.get("kv_cache_profile") or "normal")
    variant = str(payload.get("kv_cache_variant") or "turbo4")
    custom_k = str(payload.get("cache_type_k") or "")
    custom_v = str(payload.get("cache_type_v") or "")
    runtime_id = payload.get("runtime_id")
    try:
        return resolve_types(profile, variant, custom_k, custom_v, runtime_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _resolve_runtime_obj(hw_list: list[WizardHardware], payload: dict[str, Any]):
    vendor = hw_list[0].vendor
    multi = len(hw_list) > 1
    runtime_id = payload.get("runtime_id")
    try:
        if runtime_id:
            return resolve_runtime(str(runtime_id), vendor, multi)
        return default_for(vendor, multi)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def suggest_port(backend: Backend) -> int:
    used = await _used_ports(backend)
    if backend == Backend.intel:
        for port in range(8086, 8099):
            if port not in used:
                return port
        return 8099
    for port in range(10012, 11000):
        if port not in used:
            return port
    raise HTTPException(status_code=409, detail="No free port in range")


async def _used_ports(backend: Backend) -> set[int]:
    from app import aggregate

    ports: set[int] = set()
    for inst in await aggregate.list_all():
        if inst.backend != backend or not inst.port:
            continue
        ports.add(inst.port)
    return ports


async def _resolve_many(hardware_ids: list[str]) -> list[WizardHardware]:
    if not hardware_ids:
        raise HTTPException(status_code=422, detail="Select at least one GPU")
    all_hw = await list_hardware()
    by_id = {h.id: h for h in all_hw}
    resolved: list[WizardHardware] = []
    for hid in hardware_ids:
        item = by_id.get(hid)
        if not item:
            raise HTTPException(status_code=404, detail=f"Unknown hardware id: {hid}")
        resolved.append(item)
    vendors = {h.vendor for h in resolved}
    if len(vendors) > 1:
        raise HTTPException(status_code=400, detail="Cannot mix GPU vendors in one instance")
    if len(resolved) > 1 and resolved[0].vendor != "nvidia":
        raise HTTPException(status_code=400, detail="Multi-GPU only supported for NVIDIA")
    return resolved


def _stack(hw: WizardHardware, payload: dict[str, Any]) -> str:
    chosen = payload.get("compute_backend")
    if chosen:
        if chosen not in hw.available_compute_backends:
            raise HTTPException(
                status_code=400,
                detail=f"Compute backend '{chosen}' not available for this GPU",
            )
        return str(chosen)
    return hw.compute_backend


def _device(hw: WizardHardware, payload: dict[str, Any]) -> str:
    return str(payload.get("device_id") or hw.device_id or "CUDA0")


async def _create_nvidia(
    hw_list: list[WizardHardware],
    name: str,
    model: str,
    port: int,
    ctx: int,
    payload: dict,
    cache_k: str,
    cache_v: str,
    runtime,
) -> dict:
    hw = hw_list[0]
    gpu_layers = "0" if runtime.cpu_only else str(payload.get("gpu_layers", "auto"))
    parallel = int(payload.get("parallel", 1))
    reasoning = str(payload.get("reasoning") or "auto")
    reasoning_format = str(payload.get("reasoning_format") or "")
    budget = payload.get("reasoning_budget")
    device_id = _device(hw, payload)

    cfg = get_runtime_settings()
    env: dict[str, str] = {
        "HF_HOME": cfg.hf_home,
        "HF_HUB_CACHE": cfg.hf_hub_cache,
        "LLAMA_CACHE": cfg.llama_cache,
    }
    indices = sorted(h.cuda_index for h in hw_list if h.cuda_index is not None)
    if indices and not runtime.cpu_only:
        env["CUDA_VISIBLE_DEVICES"] = ",".join(str(i) for i in indices)

    extra_args: dict[str, Any] = {"n-gpu-layers": gpu_layers, "reasoning": reasoning}
    if runtime.cpu_only:
        extra_args["device"] = "CPU0"
    elif runtime.stack == "vulkan":
        extra_args["device"] = str(payload.get("device_id") or "Vulkan0")
    elif device_id:
        extra_args["device"] = device_id

    backend_opts: dict[str, Any] = {
        "model": model,
        "port": port,
        "ctx_size": ctx,
        "host": "0.0.0.0",
        "jinja": True,
        "parallel": parallel,
        "flash_attn": "auto",
        "metrics": True,
        "extra_args": extra_args,
    }
    if len(indices) > 1 and not runtime.cpu_only:
        backend_opts["split_mode"] = "layer"
    if cache_k:
        backend_opts["cache_type_k"] = cache_k
    if cache_v:
        backend_opts["cache_type_v"] = cache_v
    if reasoning_format:
        backend_opts["reasoning_format"] = reasoning_format
    if budget is not None:
        backend_opts["reasoning_budget"] = int(budget)

    options = {
        "backend_type": "llama_cpp",
        "backend_options": backend_opts,
        "environment": env,
        "group": "chat",
        "on_demand_start": False,
        "idle_timeout": 60,
        "auto_restart": True,
        "command_override": runtime.binary,
    }
    return await nvidia_client.create_instance(name, options)


async def _create_intel(
    hw: WizardHardware,
    name: str,
    model: str,
    port: int,
    ctx: int,
    payload: dict,
    cache_k: str,
    cache_v: str,
    runtime,
) -> dict:
    _stack(hw, payload)
    desc = payload.get("description") or hw.product_family or hw.name
    device = str(payload.get("device_id") or hw.device_id or "SYCL0")
    reasoning = str(payload.get("reasoning") or "auto")
    reasoning_format = str(payload.get("reasoning_format") or "")
    budget = payload.get("reasoning_budget")

    parts = [intel_extra_cache_flags(cache_k, cache_v), f"--reasoning {reasoning}"]
    if reasoning_format:
        parts.append(f"--reasoning-format {reasoning_format}")
    if budget is not None:
        parts.append(f"--reasoning-budget {int(budget)}")
    extra = " ".join(p for p in parts if p).strip()
    if payload.get("extra_args"):
        extra = f"{extra} {payload['extra_args']}".strip()

    registry.add_model(
        registry.IntelModel(name, port, ctx, model, desc, extra, device, runtime.binary)
    )
    return {
        "status": "created",
        "hardware": hw.id,
        "hardware_ids": [hw.id],
        "name": name,
        "port": port,
        "device_id": device,
        "runtime_id": runtime.id,
        "runtime_binary": runtime.binary,
    }
