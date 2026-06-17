# llama-dashboard documentation

Enterprise control panel for **NVIDIA (llamactl)** and **Intel Arc Pro B70 (SYCL)** llama.cpp fleets on a single host.

## Guides

| Document | Description |
|----------|-------------|
| [GPU & runtime limitations](gpu-runtime-limitations.md) | **Required reading** — what multi-GPU and multi-vendor combinations work |
| [Wizard](wizard.md) | Create-instance wizard: runtime, GPU, KV cache, reasoning |
| [Runtimes](runtimes.md) | Installed llama.cpp engines on the fleet host |
| [Architecture](architecture.md) | Backends, metrics, API overview |
| [Deployment](deployment.md) | Install, systemd, CI |

## Wiki mirror

The `wiki/` directory at the repo root contains the same pages in [Gitea wiki](http://192.168.10.14/achraf/llama-dashboard/wiki) format. See [wiki/README.md](../wiki/README.md) for sync instructions.

## Quick links

- Dashboard: `http://192.168.10.100:9000`
- Gitea repo: `http://192.168.10.14/achraf/llama-dashboard`
- llamactl API: `http://127.0.0.1:8080`
