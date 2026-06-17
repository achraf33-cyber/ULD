"""Standard multi-vendor GPU telemetry (NVIDIA, Intel, AMD, …)."""
from app.metrics.gpus.aggregate import read_all

__all__ = ["read_all"]
