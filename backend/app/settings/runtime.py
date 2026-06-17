"""Effective runtime configuration (env + SQLite overrides)."""
from __future__ import annotations

from functools import lru_cache

from app.config import Settings, get_settings
from app.settings import store
from app.settings.detect import enrich


@lru_cache
def get_runtime_settings() -> Settings:
    merged = store.merge_runtime(get_settings())
    return enrich(merged)


def reload_runtime_settings() -> Settings:
    get_runtime_settings.cache_clear()
    _clear_path_caches()
    return get_runtime_settings()


def _clear_path_caches() -> None:
    from app.wizard import compute_backends, kv_cache

    compute_backends.installed_backends.cache_clear()
    kv_cache.engine_binary.cache_clear()
