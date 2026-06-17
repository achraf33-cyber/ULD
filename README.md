# ULD — Unified LlamaCPP Dashboard

**CyberN Technologie Canada** · PolyForm Noncommercial License

**Release 0.1** — Enterprise-grade unified control panel for **NVIDIA (llamactl)** and **Intel Arc Pro B70 (SYCL)** llama.cpp fleets.

## License

**PolyForm Noncommercial 1.0.0** — free for personal, hobby, research, and nonprofit use. **Commercial use requires prior written permission** from the copyright holder. See [LICENSE](LICENSE) for full terms.

## Documentation

Full docs in [`docs/`](docs/README.md). **Start here:** [GPU & runtime limitations](docs/gpu-runtime-limitations.md) — multi-GPU and multi-vendor rules.

| Guide | Topic |
|-------|--------|
| [Limitations](docs/gpu-runtime-limitations.md) | What GPU/runtime combos work |
| [Wizard](docs/wizard.md) | Create instance flow |
| [Runtimes](docs/runtimes.md) | CUDA, SYCL, Vulkan, CPU binaries |
| [Architecture](docs/architecture.md) | Backends and metrics |
| [Deployment](docs/deployment.md) | Install and systemd |

Gitea wiki: [`wiki/`](wiki/Home.md) (sync to `llama-dashboard.wiki` repo — see [wiki/README.md](wiki/README.md))

## Features

- Live multi-vendor GPU telemetry (NVML, Intel xe DRM, AMD sysfs)
- Unified instance list with start/stop/restart/delete
- Live log streaming (SSE) and live fleet snapshots
- Per-instance throughput and KV-cache metrics
- 4-step create wizard: **runtime → GPU → model → engine params**
- HuggingFace model download (NVIDIA via llamactl)
- No authentication (LAN-trusted deployment)

## Quick start

```bash
./scripts/install.sh   # interactive first install — writes .env + SQLite settings

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend && npm install && npm run build

# Run (serves SPA + API on :9000)
cd ../backend && source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

Open: `http://<host>:9000`

Paths and binaries are **not hardcoded** — set them in `install.sh` or **Settings** after install.

## Systemd

```bash
# Edit deploy/llama-dashboard.service — set WorkingDirectory and paths to your install dir
cp deploy/llama-dashboard.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now llama-dashboard
```

## Architecture

- **NVIDIA**: proxies `llamactl` API at `:8080`
- **Intel B70**: controls `llama-intel-b70@*.service` via `b70-model` + `systemctl`
- **Metrics**: NVML, Intel xe/i915 DRM ioctl, AMD amdgpu sysfs, per-instance `/metrics`

## API

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/instances` | All instances (both backends) |
| `GET /api/live` | SSE live snapshot (GPUs, instances, throughput) |
| `GET /api/metrics/gpus` | GPU telemetry |
| `GET /api/logs/{backend}/{name}/stream` | SSE log stream |
| `GET /api/wizard/runtimes?catalog=true` | Installed + available llama.cpp runtimes |
| `GET /api/wizard/hardware` | Detected GPUs for create wizard |
| `GET /api/wizard/kv-options` | KV cache profiles for runtime |
| `POST /api/wizard/create` | Create instance (runtime + GPU + params) |
| `POST /api/nvidia/models/download` | Start HF download job |
| `GET /api/nvidia/models/jobs/{id}` | Download job status |
