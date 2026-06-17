"""Pydantic schemas for dashboard settings API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CredentialStatus(BaseModel):
    llamactl_key_set: bool = False
    llamactl_key_preview: str = ""
    huggingface_token_set: bool = False
    huggingface_token_preview: str = ""


class LibraryRootStatus(BaseModel):
    path: str
    exists: bool
    gguf_count: int = 0


class DashboardSettingsPublic(BaseModel):
    host: str
    port: int
    static_dir: str
    lan_ip: str
    metrics_interval_s: float
    library_dirs: str
    effective_library_dirs: str
    library_roots: list[LibraryRootStatus]
    model_dirs: str
    hf_home: str
    hf_hub_cache: str
    llama_cache: str
    llamactl_url: str
    llamactl_config: str
    instance_bind_host: str
    runtime_cuda_turboquant: str
    runtime_cuda_standard: str
    runtime_vulkan: str
    runtime_cpu: str
    runtime_sycl: str
    runtime_rocm: str
    intel_default_server: str
    intel_conf: str
    intel_env_dir: str
    intel_b70_cli: str
    intel_service_prefix: str
    install_complete: bool
    database_path: str
    credentials: CredentialStatus


class DashboardSettingsUpdate(BaseModel):
    host: str | None = None
    port: int | None = None
    static_dir: str | None = None
    lan_ip: str | None = None
    metrics_interval_s: float | None = None
    library_dirs: str | None = None
    model_dirs: str | None = None
    hf_home: str | None = None
    hf_hub_cache: str | None = None
    llama_cache: str | None = None
    llamactl_url: str | None = None
    llamactl_config: str | None = None
    instance_bind_host: str | None = None
    runtime_cuda_turboquant: str | None = None
    runtime_cuda_standard: str | None = None
    runtime_vulkan: str | None = None
    runtime_cpu: str | None = None
    runtime_sycl: str | None = None
    runtime_rocm: str | None = None
    intel_default_server: str | None = None
    intel_conf: str | None = None
    intel_env_dir: str | None = None
    intel_b70_cli: str | None = None
    intel_service_prefix: str | None = None
    database_path: str | None = None
    install_complete: str | None = None


class CredentialsUpdate(BaseModel):
    llamactl_key: str | None = Field(default=None, description="Empty string clears override")
    huggingface_token: str | None = Field(default=None, description="Empty string clears override")


class SettingsExport(BaseModel):
    version: int = 1
    settings: dict[str, str | float | int]
    credentials: dict[str, str]


class SettingsImportBody(BaseModel):
    settings: dict[str, str | float | int] | None = None
    credentials: dict[str, str] | None = None
    confirm_overwrite: bool = False
