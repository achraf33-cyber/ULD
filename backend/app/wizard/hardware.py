"""Detect creatable GPUs for the wizard (native DRM + NVML/intel probes)."""
from __future__ import annotations

from app.metrics.gpus import aggregate, nvidia_nvml
from app.metrics.gpus.discover import list_devices
from app.metrics.gpus.names import resolve, vendor_for
from app.metrics.gpus.schema import GpuVendor
from app.schemas import Backend
from app.wizard import compute_backends, instance_map
from app.wizard.schema import WizardHardware


async def list_hardware() -> list[WizardHardware]:
    devices = list_devices()
    stats = await aggregate.read_all()
    by_pci = {g.pci_slot: g for g in stats if g.pci_slot}
    nvml_by_pci = {s.pci_slot: s for s in nvidia_nvml.read_all() if s.pci_slot}
    cuda_names = await instance_map.nvidia_cuda_to_names()
    intel_names = await instance_map.intel_instance_names()
    out: list[WizardHardware] = []

    for dev in devices:
        vendor = vendor_for(dev.vendor_id)
        stat = by_pci.get(dev.pci_slot)
        name, family, caps = resolve(dev)
        if stat and stat.name:
            name = stat.name
        apis = list(caps.get("api", []))
        stack = compute_backends.default_stack(vendor, dev.driver)
        avail_backends = compute_backends.available_for_apis(apis)
        if stack not in avail_backends and avail_backends:
            stack = avail_backends[0]
        cuda_idx = _cuda_index(vendor, dev.pci_slot, nvml_by_pci)
        on_gpu = _instances(vendor, cuda_idx, cuda_names, intel_names)
        free = _free_mb(stat)
        effort = stat.effort_percent if stat else None
        out.append(
            WizardHardware(
                id=_hid(vendor, dev.pci_slot),
                vendor=vendor.value,
                backend=_backend(vendor),
                name=name,
                pci_slot=dev.pci_slot,
                driver=dev.driver,
                cuda_index=cuda_idx,
                mem_used_mb=stat.mem_used_mb if stat else None,
                mem_total_mb=stat.mem_total_mb if stat else None,
                mem_free_mb=free,
                effort_percent=effort,
                core_count=stat.core_count if stat else None,
                product_family=family or (stat.product_family if stat else family),
                creatable=_creatable(vendor, dev.driver),
                note=_note(vendor, dev.driver),
                available=_available(free, effort),
                availability_note=_avail_note(free, effort, on_gpu),
                instances_on_gpu=on_gpu,
                render_node=dev.render_node,
                supported_apis=apis,
                available_compute_backends=avail_backends,
                compute_backend=stack,
                device_id=compute_backends.default_device_id(stack, cuda_idx),
            )
        )
    return _sort(out)


def _instances(
    vendor: GpuVendor,
    cuda_idx: int | None,
    cuda_map: dict[int, list[str]],
    intel_names: list[str],
) -> list[str]:
    if vendor == GpuVendor.intel:
        return list(intel_names)
    if cuda_idx is None:
        return []
    return list(dict.fromkeys(cuda_map.get(cuda_idx, [])))


def _available(free: float | None, effort: float | None) -> bool:
    if free is not None and free > 1024:
        return True
    if effort is not None and effort < 95:
        return True
    return False


def _avail_note(free: float | None, effort: float | None, names: list[str]) -> str | None:
    parts: list[str] = []
    if effort is not None:
        parts.append(f"{effort:.0f}% load")
    if free is not None:
        parts.append(f"{free / 1024:.1f} GB free")
    if names:
        parts.append(f"{len(names)} instance{'s' if len(names) != 1 else ''}")
    return " · ".join(parts) if parts else None


def _sort(items: list[WizardHardware]) -> list[WizardHardware]:
    def key(h: WizardHardware) -> tuple:
        vendor_rank = 0 if h.vendor == "nvidia" else 1
        avail_rank = 0 if h.available else 1
        free = h.mem_free_mb or 0
        return (vendor_rank, avail_rank, -free)

    return sorted(items, key=key)


def _hid(vendor: GpuVendor, pci: str) -> str:
    return f"{vendor.value}:{pci}"


def _backend(vendor: GpuVendor) -> Backend:
    if vendor == GpuVendor.intel:
        return Backend.intel
    return Backend.nvidia


def _cuda_index(vendor: GpuVendor, pci: str, nvml: dict) -> int | None:
    if vendor != GpuVendor.nvidia:
        return None
    snap = nvml.get(pci)
    return snap.index if snap else None


def _creatable(vendor: GpuVendor, driver: str) -> bool:
    if vendor == GpuVendor.nvidia and driver == "nvidia":
        return True
    if vendor == GpuVendor.intel and driver in {"xe", "i915"}:
        return True
    return False


def _note(vendor: GpuVendor, driver: str) -> str | None:
    if vendor == GpuVendor.amd:
        return "AMD detected — view metrics only; instance creation coming soon"
    if vendor == GpuVendor.nvidia and driver != "nvidia":
        return f"Driver {driver} — use proprietary NVIDIA driver for CUDA instances"
    if vendor == GpuVendor.intel and driver == "i915":
        return "Embedded Intel — SYCL via i915; one instance recommended"
    if vendor == GpuVendor.intel and driver == "xe":
        return "Intel Arc/B-series — one active llama model at a time on B70"
    return None


def _free_mb(stat) -> float | None:
    if not stat or stat.mem_total_mb is None:
        return None
    used = stat.mem_used_mb or 0
    return round(max(0.0, stat.mem_total_mb - used), 1)
