"""Friendly GPU names and capability tags from PCI IDs."""
from __future__ import annotations

from app.metrics.gpus.discover import DrmDevice
from app.metrics.gpus.schema import GpuVendor

# Intel Arc / Battlemage B-series (xe) — extend as new SKUs ship
_INTEL_DEVICES: dict[str, tuple[str, str]] = {
    "0xe223": ("Intel Arc Pro B70", "arc-pro-b70"),  # Battlemage G31
    "0xe20b": ("Intel Arc B580", "arc-b580"),
    "0x7d55": ("Intel Arc A770", "arc-a770"),
    "0x56a0": ("Intel Data Center GPU Max", "pvc"),
}

_AMD_SERIES = {
    "gfx1100": "rdna3",
    "gfx1030": "rdna2",
    "gfx1010": "rdna1",
}


def resolve(dev: DrmDevice) -> tuple[str, str | None, dict]:
    """Return (display_name, product_family, capabilities)."""
    vendor = vendor_for(dev.vendor_id)
    caps: dict = {"vendor_slug": vendor.value, "driver": dev.driver}
    if vendor == GpuVendor.intel:
        return _intel_name(dev, caps)
    if vendor == GpuVendor.amd:
        return _amd_name(dev, caps)
    if vendor == GpuVendor.nvidia:
        caps["api"] = ["cuda", "vulkan"]
        return f"NVIDIA GPU [{dev.device_id}]", None, caps
    caps["api"] = ["vulkan"]
    return f"GPU [{dev.vendor_id}:{dev.device_id}]", None, caps


def vendor_for(vendor_id: str) -> GpuVendor:
    vid = vendor_id.lower()
    if vid == "0x10de":
        return GpuVendor.nvidia
    if vid == "0x8086":
        return GpuVendor.intel
    if vid == "0x1002":
        return GpuVendor.amd
    return GpuVendor.other


def _intel_name(dev: DrmDevice, caps: dict) -> tuple[str, str | None, dict]:
    did = dev.device_id.lower()
    family, series = _INTEL_DEVICES.get(did, (None, None))
    if dev.driver == "xe":
        caps["api"] = ["level_zero", "opencl", "sycl", "vulkan"]
        caps["stack"] = "oneapi-xe"
    else:
        caps["api"] = ["opencl", "vulkan"]
        caps["stack"] = "i915"
    if series:
        caps["series"] = series
    if family:
        return family, series, caps
    return f"Intel Graphics [{did}]", None, caps


def _amd_name(dev: DrmDevice, caps: dict) -> tuple[str, str | None, dict]:
    caps["api"] = ["rocm", "opencl", "vulkan"]
    caps["stack"] = "amdgpu"
    ip = _read_ip(dev.device_path)
    if ip:
        caps["ip_block"] = ip
        caps["series"] = _AMD_SERIES.get(ip, ip)
    return f"AMD GPU [{dev.device_id}]", caps.get("series"), caps


def _read_ip(device_path: str) -> str | None:
    try:
        with open(f"{device_path}/ip_discovery/die/0/name", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return None
