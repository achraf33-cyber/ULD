"""Detect installed GGML compute backends from configured binary paths."""
from __future__ import annotations

import glob
import os
from functools import lru_cache

from app.metrics.gpus.schema import GpuVendor
from app.settings.paths import runtime_binary_map
from app.settings.runtime import get_runtime_settings


@lru_cache
def installed_backends() -> frozenset[str]:
    paths = runtime_binary_map(get_runtime_settings())
    found: set[str] = set()
    cuda = paths.get("cuda-standard", "")
    if cuda and os.path.isfile(cuda):
        bindir = os.path.dirname(cuda)
        if glob.glob(os.path.join(bindir, "libggml-cuda.so*")):
            found.add("cuda")
    for key, stack in (
        ("sycl-intel", "sycl"),
        ("vulkan", "vulkan"),
        ("rocm", "rocm"),
    ):
        if paths.get(key) and os.path.isfile(paths[key]):
            found.add(stack)
    return frozenset(found)


def available_for_apis(supported_apis: list[str]) -> list[str]:
    installed = installed_backends()
    order = ("cuda", "sycl", "rocm", "vulkan", "opencl", "level_zero")
    return [key for key in order if key in supported_apis and key in installed]


def default_stack(vendor: GpuVendor, driver: str) -> str:
    if vendor == GpuVendor.nvidia:
        return "cuda"
    if vendor == GpuVendor.intel and driver == "xe":
        return "sycl"
    if vendor == GpuVendor.amd:
        return "rocm" if "rocm" in installed_backends() else "vulkan"
    return "vulkan"


def default_device_id(stack: str, cuda_index: int | None) -> str:
    if stack == "cuda":
        return "CUDA0" if cuda_index is not None else "CUDA0"
    if stack == "sycl":
        return "SYCL0"
    if stack == "rocm":
        return "HIP0"
    if stack == "vulkan":
        return "Vulkan0"
    return "GPU0"
