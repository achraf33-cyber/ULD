"""Shared sysfs / hwmon helpers for GPU providers."""
from __future__ import annotations

import glob


def read_int(path: str) -> int | None:
    try:
        with open(path, encoding="utf-8") as handle:
            return int(handle.read().strip())
    except (OSError, ValueError):
        return None


def read_float(path: str) -> float | None:
    value = read_int(path)
    return float(value) if value is not None else None


def bytes_to_mb(value: int | None) -> float | None:
    return round(value / (1024 * 1024), 1) if value is not None else None


def hwmon_temp_c(device_path: str) -> float | None:
    for path in glob.glob(f"{device_path}/hwmon/hwmon*/temp1_input"):
        value = read_int(path)
        if value is not None:
            return value / 1000.0
    return None


def hwmon_power_w(device_path: str) -> float | None:
    for path in glob.glob(f"{device_path}/hwmon/hwmon*/power1_average"):
        value = read_int(path)
        if value is not None:
            return value / 1_000_000.0
    for path in glob.glob(f"{device_path}/hwmon/hwmon*/energy1_input"):
        return None  # needs delta sampling — handled by caller
    return None
