"""Intel GPU VRAM fallbacks via debugfs and fdinfo."""
from __future__ import annotations

import glob
import os
import re


def card_num(device: str) -> str | None:
    card = os.path.basename(os.path.dirname(device))
    return card[4:] if card.startswith("card") else None


def from_debugfs(device: str, driver: str) -> tuple[int | None, int | None]:
    num = card_num(device)
    if not num:
        return None, None
    if driver == "xe":
        return _parse_vram_mm(f"/sys/kernel/debug/dri/{num}/tile0/vram_mm")
    if driver == "i915":
        base = f"/sys/kernel/debug/dri/{num}/gt/gt0/s_meminfo"
        return _parse_lmem(f"{base}/lmem_used", f"{base}/lmem_total")
    return None, None


def from_fdinfo(device: str) -> tuple[int | None, int | None]:
    pdev = os.path.basename(os.path.realpath(device))
    vram = stolen = 0
    for path in glob.glob("/proc/[0-9]*/fdinfo/*"):
        try:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            continue
        if f"drm-pdev:\t{pdev}" not in text and f"drm-pdev: {pdev}" not in text:
            continue
        vram += _parse_kib(text, "drm-resident-vram0")
        stolen += _parse_kib(text, "drm-resident-stolen")
    num = card_num(device)
    if num:
        _, total = _parse_vram_mm(f"/sys/kernel/debug/dri/{num}/tile0/vram_mm")
        if vram and total:
            return vram, total
    if stolen:
        return stolen, stolen
    return None, None


def _parse_vram_mm(path: str) -> tuple[int | None, int | None]:
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return None, None
    size_b = usage_b = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("size:"):
            size_b = int(line.split(":", 1)[1].strip())
        elif line.startswith("usage:"):
            usage_b = int(line.split(":", 1)[1].strip())
    if size_b is None:
        return None, None
    return usage_b or 0, size_b


def _parse_lmem(used_path: str, total_path: str) -> tuple[int | None, int | None]:
    try:
        with open(used_path, encoding="utf-8") as u, open(total_path, encoding="utf-8") as t:
            return int(u.read().strip()), int(t.read().strip())
    except (OSError, ValueError):
        return None, None


def _parse_kib(text: str, key: str) -> int:
    match = re.search(rf"{key}:\s*(\d+)\s*KiB", text)
    return int(match.group(1)) * 1024 if match else 0
