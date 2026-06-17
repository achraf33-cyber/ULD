# Architecture

## Components

```
Browser (:9000)
    └── llama-dashboard (FastAPI + React SPA)
            ├── llamactl API (:8080) → NVIDIA instances
            ├── b70-model / systemd → Intel B70 instances
            └── metrics (NVML, DRM, sysfs, /metrics scrape)
```

## Backends

| Backend | Control | Binary source |
|---------|---------|---------------|
| NVIDIA | llamactl | Per-instance `command_override` or global config |
| Intel | `llama-intel-b70@*.service` | `LLAMA_INTEL_SERVER` in env file |

## Metrics

- **NVIDIA**: NVML (lazy-loaded if `libnvidia-ml` present)
- **Intel xe**: DRM + custom VRAM ioctl
- **AMD**: sysfs (view-only, no create wizard path)
- **Throughput**: per-instance llama-server `/metrics` when running

## Live data

- `GET /api/live` — SSE snapshot (GPUs, instances, throughput history)
- `GET /api/logs/{backend}/{name}/stream` — journal / llamactl logs

## Security

- No authentication on dashboard (LAN-trusted)
- `DASHBOARD_LLAMACTL_KEY` in `.env` — server-side only, never sent to browser

## CI

Gitea Actions (`.gitea/workflows/ci.yml`): `ruff check`, import smoke test, `npm run build`.
