"""Auto-detect llamactl and runtime paths from the local filesystem."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

from app.config import Settings

_LLAMACTL_CONFIGS = (
    "/opt/llamactl/config.yaml",
    "/etc/llamactl/config.yaml",
)

_CUDA_BINARIES = (
    "/opt/llama-turboquant/build/bin/llama-server",
    "/opt/llama.cpp/build/bin/llama-server",
    "/usr/local/bin/llama-server",
)

_INTEL_CONF = (
    "/etc/llama-intel-b70/models.conf",
)

_SYCL_BINARIES = (
    "/opt/llama.cpp/build-sycl/bin/llama-server",
    "/opt/llama-sycl/build/bin/llama-server",
)

_INTEL_CLI = (
    "/usr/local/bin/b70-model",
)


@dataclass(frozen=True)
class DetectedPaths:
    llamactl_url: str = ""
    llamactl_config: str = ""
    runtime_cuda_standard: str = ""
    runtime_cuda_turboquant: str = ""
    runtime_sycl: str = ""
    intel_conf: str = ""
    intel_env_dir: str = ""
    intel_b70_cli: str = ""


def _first_file(paths: tuple[str, ...]) -> str:
    for path in paths:
        if os.path.isfile(path):
            return path
    return ""


def _binary_from_llamactl_config(config_path: str) -> str:
    if not config_path or not os.path.isfile(config_path):
        return ""
    try:
        with open(config_path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return str(data.get("backends", {}).get("llama-cpp", {}).get("command", "")).strip()
    except OSError:
        return ""


def _llamactl_port_from_config(config_path: str) -> int | None:
    if not config_path or not os.path.isfile(config_path):
        return None
    try:
        with open(config_path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        port = data.get("server", {}).get("port")
        return int(port) if port else None
    except (OSError, TypeError, ValueError):
        return None


def detect_paths(cfg: Settings) -> DetectedPaths:
    config = cfg.llamactl_config.strip() or _first_file(_LLAMACTL_CONFIGS)
    binary = _binary_from_llamactl_config(config)
    turbo = ""
    standard = ""
    if binary:
        if "turbo" in binary.lower():
            turbo = binary
        else:
            standard = binary
    if not standard and not turbo:
        for path in _CUDA_BINARIES:
            if os.path.isfile(path):
                if "turbo" in path.lower():
                    turbo = turbo or path
                else:
                    standard = standard or path
    intel_conf = cfg.intel_conf.strip() or _first_file(_INTEL_CONF)
    intel_env = cfg.intel_env_dir.strip()
    if not intel_env and intel_conf:
        intel_env = str(Path(intel_conf).parent)
    return DetectedPaths(
        llamactl_url=_detect_llamactl_url(cfg, config),
        llamactl_config=config,
        runtime_cuda_standard=standard,
        runtime_cuda_turboquant=turbo,
        runtime_sycl=cfg.runtime_sycl.strip() or _first_file(_SYCL_BINARIES),
        intel_conf=intel_conf,
        intel_env_dir=intel_env,
        intel_b70_cli=cfg.intel_b70_cli.strip() or _first_file(_INTEL_CLI),
    )


def _detect_llamactl_url(cfg: Settings, config_path: str) -> str:
    if cfg.llamactl_url.strip():
        return ""
    port = _llamactl_port_from_config(config_path) or 8080
    if llamactl_reachable(f"http://127.0.0.1:{port}", cfg.llamactl_key):
        return f"http://127.0.0.1:{port}"
    return ""


def llamactl_reachable(url: str, key: str = "") -> bool:
    base = url.rstrip("/")
    if not base:
        return False
    req = Request(f"{base}/api/v1/instances", method="GET")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    try:
        with urlopen(req, timeout=2) as resp:
            return resp.status < 500
    except HTTPError as exc:
        return exc.code in {200, 401, 403}
    except (URLError, OSError, ValueError):
        return False


def enrich(cfg: Settings) -> Settings:
    """Fill empty settings from local autodetection (in-memory only)."""
    detected = detect_paths(cfg)
    data = cfg.model_dump()
    for key in (
        "llamactl_url",
        "llamactl_config",
        "runtime_cuda_standard",
        "runtime_cuda_turboquant",
        "runtime_sycl",
        "intel_conf",
        "intel_env_dir",
        "intel_b70_cli",
    ):
        if not str(data.get(key, "")).strip():
            val = getattr(detected, key, "")
            if val:
                data[key] = val
    return Settings.model_validate(data)


def autodetect_keys(cfg: Settings) -> frozenset[str]:
    """Setting keys whose effective value comes from autodetection."""
    detected = detect_paths(cfg)
    keys: set[str] = set()
    for key in (
        "llamactl_url",
        "llamactl_config",
        "runtime_cuda_standard",
        "runtime_cuda_turboquant",
        "runtime_sycl",
        "intel_conf",
        "intel_env_dir",
        "intel_b70_cli",
    ):
        if not str(getattr(cfg, key, "")).strip() and getattr(detected, key, ""):
            keys.add(key)
    return frozenset(keys)
