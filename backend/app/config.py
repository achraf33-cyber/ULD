"""Runtime configuration loaded from environment.

Paths and binaries have no code defaults — set them on first install via
`scripts/install.sh` or Settings. Secrets stay server-side only.
"""
from __future__ import annotations

from functools import lru_cache

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DASHBOARD_",
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
    )

    host: str = "0.0.0.0"
    port: int = 9000
    lan_ip: str = ""
    instance_bind_host: str = "127.0.0.1"

    llamactl_url: str = ""
    llamactl_key: str = ""
    huggingface_token: str = ""
    llamactl_config: str = ""

    library_dirs: str = ""
    model_dirs: str = ""
    hf_home: str = ""
    hf_hub_cache: str = ""
    llama_cache: str = ""

    runtime_cuda_turboquant: str = ""
    runtime_cuda_standard: str = ""
    runtime_vulkan: str = ""
    runtime_cpu: str = ""
    runtime_sycl: str = ""
    runtime_rocm: str = ""
    intel_default_server: str = ""

    database_path: str = "data/dashboard.db"
    settings_file: str = "data/settings.json"
    credentials_file: str = "data/credentials.json"

    intel_conf: str = ""
    intel_env_dir: str = ""
    intel_b70_cli: str = ""
    intel_service_prefix: str = ""

    static_dir: str = "frontend_dist"
    metrics_interval_s: float = 2.0
    install_complete: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
