"""Resolved install paths from runtime settings."""
from __future__ import annotations

from app.config import Settings


def runtime_binary_map(settings: Settings) -> dict[str, str]:
    cpu = settings.runtime_cpu.strip() or settings.runtime_cuda_standard.strip()
    return {
        "cuda-turboquant": settings.runtime_cuda_turboquant.strip(),
        "cuda-standard": settings.runtime_cuda_standard.strip(),
        "vulkan": settings.runtime_vulkan.strip(),
        "cpu": cpu,
        "sycl-intel": settings.runtime_sycl.strip(),
        "rocm": settings.runtime_rocm.strip(),
    }


def intel_server_default(settings: Settings) -> str:
    return (
        settings.intel_default_server.strip()
        or settings.runtime_sycl.strip()
        or ""
    )


def instance_base_url(settings: Settings, port: int) -> str:
    host = settings.instance_bind_host.strip() or "127.0.0.1"
    return f"http://{host}:{port}"
