"""NVIDIA telemetry via NVML (libnvidia-ml) — direct driver API, no nvidia-smi."""
from __future__ import annotations

import ctypes

from app.metrics.gpus import nvidia_nvml_proc as proc_fallback
from app.metrics.gpus.nvidia_nvml_schema import NvmlSnapshot

_NVML = None
_INIT = False

NVML_TEMPERATURE_GPU = 0
NVML_CLOCK_SM = 0
NVML_CLOCK_MEM = 2


def read_all() -> list[NvmlSnapshot]:
    if not _ensure_init():
        return proc_fallback.from_proc()
    count = ctypes.c_uint()
    if _NVML.nvmlDeviceGetCount_v2(ctypes.byref(count)) != 0:
        return proc_fallback.from_proc()
    return [_read_index(i) for i in range(count.value)]


def _ensure_init() -> bool:
    global _INIT, _NVML
    if _INIT:
        return _NVML is not None
    _INIT = True
    try:
        _NVML = ctypes.CDLL("libnvidia-ml.so.1")
        if _NVML.nvmlInit_v2() != 0:
            _NVML = None
            return False
        return True
    except OSError:
        _NVML = None
        return False


def _read_index(index: int) -> NvmlSnapshot:
    assert _NVML is not None
    handle = ctypes.c_void_p()
    _NVML.nvmlDeviceGetHandleByIndex_v2(index, ctypes.byref(handle))
    name = ctypes.create_string_buffer(96)
    _NVML.nvmlDeviceGetName(handle, name, 96)
    pci = _pci_slot(handle)
    util = _utilization(handle)
    mem = _memory(handle)
    return NvmlSnapshot(
        index=index,
        pci_slot=pci,
        name=name.value.decode(errors="replace"),
        gpu_util=util[0],
        mem_util=util[1],
        mem_used_mb=mem[0],
        mem_total_mb=mem[1],
        core_count=_cores(handle),
        sm_clock_mhz=_clock(handle, NVML_CLOCK_SM),
        mem_clock_mhz=_clock(handle, NVML_CLOCK_MEM),
        temp_c=_temp(handle),
        power_w=_power(handle),
        encoder_util=_encdec(handle, True),
        decoder_util=_encdec(handle, False),
    )


def _pci_slot(handle) -> str:
    class Pci(ctypes.Structure):
        _fields_ = [
            ("busId", ctypes.c_char * 32),
            ("domain", ctypes.c_uint),
            ("bus", ctypes.c_uint),
            ("device", ctypes.c_uint),
            ("pciDeviceId", ctypes.c_uint),
            ("pciSubSystemId", ctypes.c_uint),
            ("reserved", ctypes.c_uint * 2),
        ]

    info = Pci()
    if _NVML.nvmlDeviceGetPciInfo_v3(handle, ctypes.byref(info)) != 0:
        return ""
    raw = info.busId.decode(errors="replace").strip().lower()
    return raw.replace("00000000:", "0000:")


def _utilization(handle) -> tuple[float | None, float | None]:
    class Util(ctypes.Structure):
        _fields_ = [("gpu", ctypes.c_uint), ("memory", ctypes.c_uint)]

    u = Util()
    if _NVML.nvmlDeviceGetUtilizationRates(handle, ctypes.byref(u)) != 0:
        return None, None
    return float(u.gpu), float(u.memory)


def _memory(handle) -> tuple[float | None, float | None]:
    class Mem(ctypes.Structure):
        _fields_ = [
            ("total", ctypes.c_ulonglong),
            ("free", ctypes.c_ulonglong),
            ("used", ctypes.c_ulonglong),
        ]

    m = Mem()
    if _NVML.nvmlDeviceGetMemoryInfo(handle, ctypes.byref(m)) != 0:
        return None, None
    return round(m.used / (1024 * 1024), 1), round(m.total / (1024 * 1024), 1)


def _cores(handle) -> int | None:
    cores = ctypes.c_uint()
    if _NVML.nvmlDeviceGetNumGpuCores(handle, ctypes.byref(cores)) != 0:
        return None
    return int(cores.value)


def _clock(handle, kind: int) -> float | None:
    mhz = ctypes.c_uint()
    _NVML.nvmlDeviceGetClockInfo.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
    if _NVML.nvmlDeviceGetClockInfo(handle, kind, ctypes.byref(mhz)) != 0:
        return None
    return float(mhz.value)


def _temp(handle) -> float | None:
    t = ctypes.c_uint()
    if _NVML.nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU, ctypes.byref(t)) != 0:
        return None
    return float(t.value)


def _power(handle) -> float | None:
    mw = ctypes.c_uint()
    if _NVML.nvmlDeviceGetPowerUsage(handle, ctypes.byref(mw)) != 0:
        return None
    return round(mw.value / 1000.0, 1)


def _encdec(handle, encoder: bool) -> float | None:
    util = ctypes.c_uint()
    period = ctypes.c_uint()
    fn = _NVML.nvmlDeviceGetEncoderUtilization if encoder else _NVML.nvmlDeviceGetDecoderUtilization
    if fn(handle, ctypes.byref(util), ctypes.byref(period)) != 0:
        return None
    return float(util.value)
