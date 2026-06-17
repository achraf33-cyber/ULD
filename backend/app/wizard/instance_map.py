"""Map running instances to physical GPU indices."""
from __future__ import annotations

from app.nvidia import client as nvidia_client
from app.schemas import Backend


async def nvidia_cuda_to_names() -> dict[int, list[str]]:
    """CUDA index -> instance names bound to that GPU."""
    by_index: dict[int, list[str]] = {}
    all_indices: set[int] = set()
    try:
        raw = await nvidia_client.list_instances()
    except Exception:
        return by_index

    for inst in raw:
        opts = inst.options or {}
        env = opts.get("environment", {}) if isinstance(opts, dict) else {}
        cuda = str(env.get("CUDA_VISIBLE_DEVICES", "") or "").strip()
        if not cuda:
            for i in range(8):
                all_indices.add(i)
                by_index.setdefault(i, []).append(inst.name)
            continue
        for part in cuda.split(","):
            part = part.strip()
            if not part.isdigit():
                continue
            idx = int(part)
            all_indices.add(idx)
            by_index.setdefault(idx, []).append(inst.name)
    return by_index


async def intel_instance_names() -> list[str]:
    from app import aggregate

    names: list[str] = []
    for inst in await aggregate.list_all():
        if inst.backend == Backend.intel:
            names.append(inst.name)
    return names
