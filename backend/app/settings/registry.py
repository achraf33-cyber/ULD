"""Single source of truth for dashboard configuration fields and modules."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SettingDef:
    key: str
    label: str
    hint: str
    field_type: str  # text | number | url | file | dir | path-list
    module_id: str
    required: bool = False
    credential: bool = False
    restart_on_change: bool = False
    ui_hidden: bool = False
    min_value: float | None = None
    max_value: float | None = None


@dataclass(frozen=True)
class ModuleDef:
    id: str
    title: str
    description: str


MODULE_DEFS: tuple[ModuleDef, ...] = (
    ModuleDef("server", "Server", "How the dashboard binds and serves the UI."),
    ModuleDef("general", "General", "How the dashboard identifies itself and polls metrics."),
    ModuleDef("library", "Model library", "Folders scanned for local .gguf files."),
    ModuleDef("huggingface", "HuggingFace & cache", "Download and cache locations."),
    ModuleDef("nvidia", "NVIDIA / llamactl", "Control plane for NVIDIA instances."),
    ModuleDef("intel", "Intel B70", "Systemd fleet and SYCL runtime for Intel Arc Pro B70."),
    ModuleDef("credentials", "Credentials", "API keys stored securely on the server."),
)


SETTING_DEFS: tuple[SettingDef, ...] = (
    SettingDef("host", "Bind host", "Address the dashboard listens on.", "text", "server", required=True, restart_on_change=True),
    SettingDef("port", "Port", "HTTP port for the dashboard.", "number", "server", required=True, restart_on_change=True, min_value=1, max_value=65535),
    SettingDef("static_dir", "Static files", "Built frontend assets directory.", "dir", "server", restart_on_change=True),
    SettingDef("database_path", "Database path", "SQLite file for settings persistence.", "file", "server"),
    SettingDef("lan_ip", "Dashboard LAN IP", "Shown in links to this host.", "text", "general"),
    SettingDef("metrics_interval_s", "Refresh interval (seconds)", "Live GPU and usage poll rate.", "number", "general", min_value=0.5, max_value=60),
    SettingDef("instance_bind_host", "Instance metrics host", "Host where llama-server listens.", "text", "general"),
    SettingDef("library_dirs", "Library folders", "Colon-separated paths on this server.", "path-list", "library", required=True),
    SettingDef("model_dirs", "", "", "path-list", "library", ui_hidden=True),
    SettingDef("hf_home", "HuggingFace home", "Root HF config and cache.", "dir", "huggingface"),
    SettingDef("hf_hub_cache", "Hub cache", "Downloaded model snapshots.", "dir", "huggingface"),
    SettingDef("llama_cache", "Llama cache", "Optional llama.cpp cache directory.", "dir", "huggingface"),
    SettingDef("llamactl_url", "llamactl API URL", "e.g. http://127.0.0.1:8080", "url", "nvidia"),
    SettingDef("llamactl_config", "llamactl config file", "Path to config.yaml.", "file", "nvidia"),
    SettingDef("runtime_cuda_turboquant", "CUDA TurboQuant binary", "llama-server with TurboQuant KV.", "file", "nvidia"),
    SettingDef("runtime_cuda_standard", "CUDA standard binary", "Standard CUDA llama-server build.", "file", "nvidia"),
    SettingDef("runtime_vulkan", "Vulkan binary", "Optional cross-vendor GPU build.", "file", "nvidia"),
    SettingDef("runtime_cpu", "CPU binary", "Leave empty to reuse CUDA standard.", "file", "nvidia"),
    SettingDef("runtime_rocm", "ROCm binary", "Optional AMD HIP build.", "file", "nvidia"),
    SettingDef("runtime_sycl", "SYCL llama-server", "Intel GPU binary.", "file", "intel"),
    SettingDef("intel_default_server", "Default Intel server binary", "When registry lines omit a server path.", "file", "intel"),
    SettingDef("intel_conf", "Models registry", "models.conf path.", "file", "intel"),
    SettingDef("intel_env_dir", "Env files directory", "Per-instance .env files.", "dir", "intel"),
    SettingDef("intel_b70_cli", "b70-model CLI", "Start/stop helper script.", "file", "intel"),
    SettingDef("intel_service_prefix", "Systemd unit prefix", "e.g. llama-intel-b70@", "text", "intel"),
    SettingDef("install_complete", "", "", "text", "general", ui_hidden=True),
    SettingDef("llamactl_key", "llamactl API key", "Required for NVIDIA control.", "text", "credentials", credential=True),
    SettingDef("huggingface_token", "HuggingFace token", "For gated model downloads.", "text", "credentials", credential=True),
)

SETTINGS_KEYS: tuple[str, ...] = tuple(s.key for s in SETTING_DEFS if not s.credential)
CREDENTIAL_KEYS: tuple[str, ...] = tuple(s.key for s in SETTING_DEFS if s.credential)
RESTART_KEYS: frozenset[str] = frozenset(s.key for s in SETTING_DEFS if s.restart_on_change)

SETTING_BY_KEY: dict[str, SettingDef] = {s.key: s for s in SETTING_DEFS}
MODULE_BY_ID: dict[str, ModuleDef] = {m.id: m for m in MODULE_DEFS}

NUMERIC_KEYS: frozenset[str] = frozenset(
    s.key for s in SETTING_DEFS if s.field_type == "number" and not s.credential
)
