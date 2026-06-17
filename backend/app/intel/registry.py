"""Read/write the Intel B70 model registry (models.conf)."""
from __future__ import annotations

import os
from dataclasses import dataclass

from app.settings.paths import intel_server_default
from app.settings.runtime import get_runtime_settings


@dataclass
class IntelModel:
    name: str
    port: int
    ctx: int
    model: str
    description: str = ""
    extra_args: str = ""
    device: str = "SYCL0"
    server: str = ""

    def to_line(self) -> str:
        server = self.server or intel_server_default(get_runtime_settings())
        return "|".join(
            [
                self.name,
                str(self.port),
                str(self.ctx),
                self.model,
                self.description,
                self.extra_args,
                self.device,
                server,
            ]
        )


def _conf_path() -> str:
    return get_runtime_settings().intel_conf


def _parse_line(line: str) -> IntelModel | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    parts = line.rstrip("\n").split("|")
    if len(parts) < 4:
        return None
    name, port, ctx, model = parts[0], parts[1], parts[2], parts[3]
    desc = parts[4] if len(parts) > 4 else ""
    extra = parts[5] if len(parts) > 5 else ""
    device = parts[6].strip() if len(parts) > 6 else "SYCL0"
    fallback = intel_server_default(get_runtime_settings())
    server = parts[7].strip() if len(parts) > 7 else fallback
    try:
        return IntelModel(name.strip(), int(port), int(ctx), model.strip(), desc, extra, device, server)
    except ValueError:
        return None


def list_models() -> list[IntelModel]:
    path = _conf_path()
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as handle:
        return [m for m in (_parse_line(line) for line in handle) if m is not None]


def get_model(name: str) -> IntelModel | None:
    return next((m for m in list_models() if m.name == name), None)


def used_ports() -> set[int]:
    return {m.port for m in list_models()}


def add_model(model: IntelModel) -> None:
    if get_model(model.name) is not None:
        raise ValueError(f"model '{model.name}' already exists")
    path = _conf_path()
    if not path:
        raise ValueError("intel_conf path is not configured")
    needs_nl = False
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "rb") as handle:
            handle.seek(-1, os.SEEK_END)
            needs_nl = handle.read(1) != b"\n"
    with open(path, "a", encoding="utf-8") as handle:
        if needs_nl:
            handle.write("\n")
        handle.write(model.to_line() + "\n")


def remove_model(name: str) -> None:
    path = _conf_path()
    if not path or not os.path.exists(path):
        raise ValueError(f"model '{name}' not found")
    kept: list[str] = []
    found = False
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            model = _parse_line(line)
            if model and model.name == name:
                found = True
                continue
            kept.append(line.rstrip("\n"))
    if not found:
        raise ValueError(f"model '{name}' not found")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(kept))
        if kept:
            handle.write("\n")
