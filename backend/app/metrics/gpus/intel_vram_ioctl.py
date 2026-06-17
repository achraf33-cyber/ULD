"""Intel GPU VRAM ioctl helpers (xe + i915 DRM)."""
from __future__ import annotations

import ctypes
import fcntl
import glob
import os

_IOC_READWRITE = 3
_IOC_NRSHIFT, _IOC_TYPESHIFT, _IOC_SIZESHIFT, _IOC_DIRSHIFT = 0, 8, 16, 30


def _ioc(nr: int, size: int) -> int:
    return (_IOC_READWRITE << _IOC_DIRSHIFT) | (ord("d") << _IOC_TYPESHIFT) | (nr << _IOC_NRSHIFT) | (size << _IOC_SIZESHIFT)


class _XeQuery(ctypes.Structure):
    _fields_ = [
        ("extensions", ctypes.c_uint64),
        ("query", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("data", ctypes.c_uint64),
        ("reserved", ctypes.c_uint64 * 2),
    ]


class _XeMemRegion(ctypes.Structure):
    _fields_ = [
        ("mem_class", ctypes.c_uint16),
        ("instance", ctypes.c_uint16),
        ("min_page_size", ctypes.c_uint32),
        ("total_size", ctypes.c_uint64),
        ("used", ctypes.c_uint64),
        ("cpu_visible_size", ctypes.c_uint64),
        ("cpu_visible_used", ctypes.c_uint64),
        ("reserved", ctypes.c_uint64 * 6),
    ]


class _XeHeader(ctypes.Structure):
    _fields_ = [("num_mem_regions", ctypes.c_uint32), ("pad", ctypes.c_uint32)]


class _I915Query(ctypes.Structure):
    _fields_ = [("num_items", ctypes.c_uint32), ("flags", ctypes.c_uint32), ("items_ptr", ctypes.c_uint64)]


class _I915QueryItem(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint64),
        ("length", ctypes.c_int32),
        ("flags", ctypes.c_uint32),
        ("data_ptr", ctypes.c_uint64),
    ]


class _I915RegionInfo(ctypes.Structure):
    _fields_ = [
        ("region_class", ctypes.c_uint16),
        ("region_instance", ctypes.c_uint16),
        ("rsvd0", ctypes.c_uint32),
        ("probed_size", ctypes.c_uint64),
        ("unallocated_size", ctypes.c_uint64),
        ("rsvd1", ctypes.c_uint64 * 8),
    ]


class _I915RegionsHeader(ctypes.Structure):
    _fields_ = [("num_regions", ctypes.c_uint32), ("rsvd", ctypes.c_uint32 * 3)]


def render_node(device: str) -> str | None:
    for node in glob.glob("/sys/class/drm/renderD*"):
        dev = os.path.join(node, "device")
        if os.path.realpath(dev) == os.path.realpath(device):
            return f"/dev/dri/{os.path.basename(node)}"
    return None


def from_ioctl(device: str, driver: str) -> tuple[int | None, int | None]:
    node = render_node(device)
    if not node:
        return None, None
    try:
        fd = os.open(node, os.O_RDWR)
    except OSError:
        return None, None
    try:
        if driver == "xe":
            return _xe_ioctl(fd)
        if driver == "i915":
            return _i915_ioctl(fd)
    finally:
        os.close(fd)
    return None, None


def _xe_ioctl(fd: int) -> tuple[int | None, int | None]:
    ioctl_nr = _ioc(0x40, ctypes.sizeof(_XeQuery))
    probe = _XeQuery(query=1, size=0, data=0)
    fcntl.ioctl(fd, ioctl_nr, probe)
    buf = ctypes.create_string_buffer(probe.size)
    req = _XeQuery(query=1, size=probe.size, data=ctypes.addressof(buf))
    fcntl.ioctl(fd, ioctl_nr, req)
    hdr = _XeHeader.from_buffer_copy(buf)
    offset = ctypes.sizeof(_XeHeader)
    vram_used = vram_total = sys_used = sys_total = 0
    for _ in range(hdr.num_mem_regions):
        reg = _XeMemRegion.from_buffer_copy(buf, offset)
        offset += ctypes.sizeof(_XeMemRegion)
        if reg.mem_class == 1 and reg.total_size:
            vram_used, vram_total = reg.used, reg.total_size
        elif reg.mem_class == 0 and reg.total_size:
            sys_used, sys_total = reg.used, reg.total_size
    if vram_total:
        return vram_used or 0, vram_total
    if sys_total:
        return sys_used or 0, sys_total
    return None, None


def _i915_ioctl(fd: int) -> tuple[int | None, int | None]:
    ioctl_nr = _ioc(0x79, ctypes.sizeof(_I915Query))
    item = _I915QueryItem(query_id=4, length=0, data_ptr=0)
    query = _I915Query(num_items=1, items_ptr=ctypes.addressof(item))
    fcntl.ioctl(fd, ioctl_nr, query)
    buf = ctypes.create_string_buffer(item.length)
    item.data_ptr = ctypes.addressof(buf)
    item.length = len(buf)
    fcntl.ioctl(fd, ioctl_nr, query)
    hdr = _I915RegionsHeader.from_buffer_copy(buf)
    offset = ctypes.sizeof(_I915RegionsHeader)
    device_used = device_total = sys_used = sys_total = 0
    for _ in range(hdr.num_regions):
        reg = _I915RegionInfo.from_buffer_copy(buf, offset)
        offset += ctypes.sizeof(_I915RegionInfo)
        used = reg.probed_size - reg.unallocated_size
        if reg.region_class == 1 and reg.probed_size:
            device_used, device_total = used, reg.probed_size
        elif reg.region_class == 0 and reg.probed_size:
            sys_used, sys_total = used, reg.probed_size
    if device_total:
        return device_used, device_total
    if sys_total:
        return sys_used, sys_total
    return None, None
