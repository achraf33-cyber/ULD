"""Discover DRM GPUs on the host (standard Linux sysfs layout)."""
from __future__ import annotations

import glob
import os
from dataclasses import dataclass

_SKIP_VENDORS = {"0x1a03"}  # ASPEED BMC — not a compute GPU


@dataclass(frozen=True)
class DrmDevice:
    card: str
    index: int
    vendor_id: str
    device_id: str
    pci_slot: str
    driver: str
    device_path: str
    render_node: str | None


def list_devices() -> list[DrmDevice]:
    devices: list[DrmDevice] = []
    idx = 0
    for vendor_file in sorted(glob.glob("/sys/class/drm/card[0-9]/device/vendor")):
        device_path = os.path.dirname(vendor_file)
        card = os.path.basename(os.path.dirname(device_path))
        vendor_id = _read(vendor_file)
        if not vendor_id or vendor_id in _SKIP_VENDORS:
            continue
        device_id = _read(f"{device_path}/device") or ""
        pci_slot = _read(f"{device_path}/uevent", key="PCI_SLOT_NAME") or ""
        driver = os.path.basename(os.path.realpath(f"{device_path}/driver"))
        devices.append(
            DrmDevice(
                card=card,
                index=idx,
                vendor_id=vendor_id,
                device_id=device_id,
                pci_slot=pci_slot,
                driver=driver,
                device_path=device_path,
                render_node=_render_node(device_path),
            )
        )
        idx += 1
    return devices


def _render_node(device_path: str) -> str | None:
    real = os.path.realpath(device_path)
    for node in glob.glob("/sys/class/drm/renderD*"):
        if os.path.realpath(os.path.join(node, "device")) == real:
            return f"/dev/dri/{os.path.basename(node)}"
    return None


def _read(path: str, key: str | None = None) -> str | None:
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read().strip()
    except OSError:
        return None
    if key is None:
        return text
    for line in text.splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1]
    return None
