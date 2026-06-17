"""Installed llama.cpp runtimes (binaries) for wizard instance creation."""
from __future__ import annotations

import glob
import os
import re
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.settings.paths import runtime_binary_map
from app.settings.runtime import get_runtime_settings

_CUDA_MAJOR = "12"


@dataclass(frozen=True)
class WizardRuntime:
    id: str
    label: str
    stack: str
    vendor: str
    binary: str
    version: str
    supports_turboquant: bool
    multi_gpu: bool
    hint: str
    installed: bool = False
    cpu_only: bool = False
    compatible_vendors: tuple[str, ...] = ("nvidia",)
    default: bool = False


_CATALOG_META: tuple[dict[str, Any], ...] = (
    {
        "id": "cuda-turboquant",
        "label": f"CUDA {_CUDA_MAJOR} TurboQuant llama.cpp (Linux)",
        "stack": "cuda",
        "vendor": "nvidia",
        "supports_turboquant": True,
        "multi_gpu": True,
        "compatible_vendors": ("nvidia",),
        "hint": "Default fleet runtime — TurboQuant KV, multi-GPU layer split",
    },
    {
        "id": "cuda-standard",
        "label": f"CUDA {_CUDA_MAJOR} llama.cpp (Linux)",
        "stack": "cuda",
        "vendor": "nvidia",
        "supports_turboquant": False,
        "multi_gpu": True,
        "compatible_vendors": ("nvidia",),
        "hint": "Standard CUDA build — q8_0 / f16 KV types",
    },
    {
        "id": "vulkan",
        "label": "Vulkan llama.cpp (Linux)",
        "stack": "vulkan",
        "vendor": "any",
        "supports_turboquant": False,
        "multi_gpu": False,
        "compatible_vendors": ("nvidia", "intel", "amd", "any"),
        "hint": "Cross-vendor GPU via Vulkan — requires GGML_VULKAN build",
    },
    {
        "id": "cpu",
        "label": "CPU llama.cpp (Linux)",
        "stack": "cpu",
        "vendor": "any",
        "supports_turboquant": False,
        "multi_gpu": False,
        "cpu_only": True,
        "compatible_vendors": ("nvidia", "intel", "amd", "any"),
        "hint": "Host CPU inference — no GPU layers",
    },
    {
        "id": "sycl-intel",
        "label": "SYCL llama.cpp (Intel Linux)",
        "stack": "sycl",
        "vendor": "intel",
        "supports_turboquant": False,
        "multi_gpu": False,
        "compatible_vendors": ("intel",),
        "hint": "Intel Arc / B-series — one GPU per instance",
    },
    {
        "id": "rocm",
        "label": "ROCm llama.cpp (Linux)",
        "stack": "rocm",
        "vendor": "amd",
        "supports_turboquant": False,
        "multi_gpu": False,
        "compatible_vendors": ("amd",),
        "hint": "AMD HIP/ROCm — requires GGML_HIP build",
    },
)


def _catalog_specs() -> tuple[dict[str, Any], ...]:
    paths = runtime_binary_map(get_runtime_settings())
    return tuple({**meta, "binary": paths.get(str(meta["id"]), "")} for meta in _CATALOG_META)


def _exists(path: str) -> bool:
    return bool(path) and os.path.isfile(path)


def _has_cpu_backend(binary: str) -> bool:
    bindir = os.path.dirname(binary)
    return bool(glob.glob(os.path.join(bindir, "libggml-cpu.so*")))


def _is_installed(spec: dict[str, Any]) -> bool:
    binary = str(spec["binary"])
    if not _exists(binary):
        return False
    if spec.get("cpu_only"):
        return _has_cpu_backend(binary)
    return True


@lru_cache
def _version(binary: str) -> str:
    try:
        out = subprocess.run(
            [binary, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        text = (out.stdout or out.stderr or "").strip()
        match = re.search(r"version:\s*(\S+)", text)
        if match:
            return match.group(1)
        if out.returncode != 0 or "error" in text.lower():
            return "installed"
        return text.splitlines()[0][:40] if text else "unknown"
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"


def _build(spec: dict[str, Any]) -> WizardRuntime:
    binary = str(spec["binary"])
    installed = _is_installed(spec)
    version = _version(binary) if installed else ""
    label = str(spec["label"])
    if installed and version and version != "installed":
        label = f"{label} v{version}"
    return WizardRuntime(
        id=str(spec["id"]),
        label=label,
        stack=str(spec["stack"]),
        vendor=str(spec["vendor"]),
        binary=binary,
        version=version or ("installed" if installed else ""),
        supports_turboquant=bool(spec.get("supports_turboquant")),
        multi_gpu=bool(spec.get("multi_gpu")),
        hint=str(spec.get("hint", "")),
        installed=installed,
        cpu_only=bool(spec.get("cpu_only")),
        compatible_vendors=tuple(spec.get("compatible_vendors", ("nvidia",))),
    )


def list_catalog() -> list[WizardRuntime]:
    return [_build(spec) for spec in _catalog_specs()]


def list_installed() -> list[WizardRuntime]:
    return [rt for rt in list_catalog() if rt.installed]


def for_vendor(vendor: str, multi_gpu: bool = False) -> list[WizardRuntime]:
    filtered: list[WizardRuntime] = []
    for rt in list_installed():
        if vendor not in rt.compatible_vendors and "any" not in rt.compatible_vendors:
            continue
        if multi_gpu and not rt.multi_gpu:
            continue
        filtered.append(rt)
    if not filtered:
        return filtered
    default_id = _default_id(vendor, multi_gpu, filtered)
    return [
        WizardRuntime(**{**rt.__dict__, "default": rt.id == default_id}) for rt in filtered
    ]


def compatible_with_runtime(runtime_id: str, vendor: str) -> bool:
    rt = get(runtime_id)
    if not rt or not rt.installed:
        return False
    return vendor in rt.compatible_vendors or "any" in rt.compatible_vendors


def get(runtime_id: str) -> WizardRuntime | None:
    for rt in list_catalog():
        if rt.id == runtime_id:
            return rt
    return None


def _default_id(vendor: str, multi_gpu: bool, items: list[WizardRuntime]) -> str:
    if vendor == "nvidia":
        prefer = ("cuda-turboquant", "cuda-standard", "cpu")
    elif vendor == "intel":
        prefer = ("sycl-intel", "cpu")
    else:
        prefer = ("cuda-standard", "cpu", "vulkan")
    for pid in prefer:
        for rt in items:
            if rt.id == pid:
                return rt.id
    return items[0].id


def default_catalog_id() -> str:
    for prefer in ("cuda-turboquant", "cuda-standard", "sycl-intel", "cpu"):
        rt = get(prefer)
        if rt and rt.installed:
            return rt.id
    for rt in list_installed():
        return rt.id
    return "cuda-standard"


def resolve(runtime_id: str, vendor: str, multi_gpu: bool) -> WizardRuntime:
    rt = get(runtime_id)
    if not rt or not rt.installed:
        raise ValueError(f"Runtime '{runtime_id}' is not installed on this host")
    if not compatible_with_runtime(runtime_id, vendor):
        raise ValueError(f"Runtime '{runtime_id}' is not compatible with {vendor} GPU")
    if multi_gpu and not rt.multi_gpu:
        raise ValueError(f"Runtime '{runtime_id}' does not support multi-GPU")
    return rt


def default_for(vendor: str, multi_gpu: bool = False) -> WizardRuntime:
    items = for_vendor(vendor, multi_gpu)
    if not items:
        raise ValueError(f"No llama.cpp runtime installed for {vendor}")
    for rt in items:
        if rt.default:
            return rt
    return items[0]


def supports_turboquant(runtime_id: str | None = None) -> bool:
    if runtime_id:
        rt = get(runtime_id)
        return bool(rt and rt.supports_turboquant)
    rt = get("cuda-turboquant")
    return bool(rt and rt.installed)
