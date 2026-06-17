"""Settings HTTP routes — SQLite persistence for config and credentials."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db import database_path
from app.library_paths import effective_library_dirs, roots_status
from app.settings import runtime, store
from app.settings.modules import build_modules, credentials_module_status
from app.settings.registry import CREDENTIAL_KEYS, NUMERIC_KEYS, RESTART_KEYS, SETTINGS_KEYS
from app.settings.schema import (
    CredentialsUpdate,
    CredentialStatus,
    DashboardSettingsPublic,
    DashboardSettingsUpdate,
    LibraryRootStatus,
    SettingsExport,
    SettingsImportBody,
)

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _public() -> DashboardSettingsPublic:
    cfg = runtime.get_runtime_settings()
    creds = store.read_credentials_db()
    effective = effective_library_dirs(cfg)
    return DashboardSettingsPublic(
        host=str(cfg.host),
        port=int(cfg.port),
        static_dir=str(cfg.static_dir),
        lan_ip=cfg.lan_ip,
        metrics_interval_s=float(cfg.metrics_interval_s),
        library_dirs=cfg.library_dirs,
        effective_library_dirs=effective,
        library_roots=[LibraryRootStatus(**r) for r in roots_status(cfg)],
        model_dirs=cfg.model_dirs,
        hf_home=cfg.hf_home,
        hf_hub_cache=cfg.hf_hub_cache,
        llama_cache=cfg.llama_cache,
        llamactl_url=cfg.llamactl_url,
        llamactl_config=cfg.llamactl_config,
        instance_bind_host=cfg.instance_bind_host,
        runtime_cuda_turboquant=cfg.runtime_cuda_turboquant,
        runtime_cuda_standard=cfg.runtime_cuda_standard,
        runtime_vulkan=cfg.runtime_vulkan,
        runtime_cpu=cfg.runtime_cpu,
        runtime_sycl=cfg.runtime_sycl,
        runtime_rocm=cfg.runtime_rocm,
        intel_default_server=cfg.intel_default_server,
        intel_conf=cfg.intel_conf,
        intel_env_dir=cfg.intel_env_dir,
        intel_b70_cli=cfg.intel_b70_cli,
        intel_service_prefix=cfg.intel_service_prefix,
        install_complete=bool(cfg.install_complete),
        database_path=str(database_path()),
        credentials=CredentialStatus(
            llamactl_key_set=bool(cfg.llamactl_key),
            llamactl_key_preview=store.mask(cfg.llamactl_key),
            huggingface_token_set=bool(creds.get("huggingface_token")),
            huggingface_token_preview=store.mask(str(creds.get("huggingface_token", ""))),
        ),
    )


def _needs_restart(patch: dict) -> bool:
    return any(key in RESTART_KEYS for key in patch)


@router.get("")
@router.get("/")
async def get_dashboard_settings():
    return _public()


@router.get("/modules")
async def get_settings_modules():
    cfg = runtime.get_runtime_settings()
    modules = build_modules(cfg)
    cred = credentials_module_status(cfg)
    return {
        "modules": modules,
        "credentials": cred,
        "library_roots": [LibraryRootStatus(**r) for r in roots_status(cfg)],
        "database_path": str(database_path()),
        "install_complete": bool(cfg.install_complete),
    }


@router.patch("")
async def patch_dashboard_settings(body: DashboardSettingsUpdate):
    patch = body.model_dump(exclude_none=True)
    for key in NUMERIC_KEYS:
        if key in patch and patch[key] is not None:
            patch[key] = str(patch[key])
    store.save_settings_patch(patch)
    runtime.reload_runtime_settings()
    return {
        "status": "saved",
        "settings": _public(),
        "restart_required": _needs_restart(patch),
        "restart_command": "sudo systemctl restart llama-dashboard",
    }


@router.patch("/credentials")
async def patch_credentials(body: CredentialsUpdate):
    patch = body.model_dump(exclude_none=True)
    store.save_credentials_patch(patch)
    runtime.reload_runtime_settings()
    return {
        "status": "saved",
        "credentials": _public().credentials,
        "message": "Credentials saved to SQLite on the server.",
    }


@router.get("/export")
async def export_settings():
    cfg = runtime.get_runtime_settings()
    creds = store.read_credentials_db()
    settings = {key: getattr(cfg, key) for key in SETTINGS_KEYS}
    masked = {key: store.mask(str(creds.get(key, ""))) for key in CREDENTIAL_KEYS}
    return SettingsExport(settings=settings, credentials=masked)


@router.post("/import")
async def import_settings(body: SettingsImportBody):
    if not body.confirm_overwrite:
        raise HTTPException(400, "Set confirm_overwrite=true to apply import")
    if body.settings:
        normalized = {k: str(v) for k, v in body.settings.items() if k in SETTINGS_KEYS}
        store.save_settings_patch(normalized)
    if body.credentials:
        cred_patch = {
            k: v
            for k, v in body.credentials.items()
            if k in CREDENTIAL_KEYS and v and "****" not in v
        }
        if cred_patch:
            store.save_credentials_patch(cred_patch)
    runtime.reload_runtime_settings()
    return {"status": "imported", "settings": _public()}
