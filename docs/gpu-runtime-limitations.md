# GPU and runtime limitations

This document defines **hard limits** for the create-instance wizard and llama.cpp on the fleet host. These are engine constraints, not dashboard bugs.

## One runtime per instance

Each llama-server process uses **one GGML backend** (CUDA, SYCL, Vulkan, CPU, or ROCm). The wizard binds **one runtime** + **one or more GPUs** per new instance.

You **cannot** run CUDA TurboQuant and SYCL in the same process.

## Multi-GPU matrix

| Goal | Supported? | Runtime | Method |
|------|------------|---------|--------|
| 1× RTX 3060 | Yes | CUDA TurboQuant or CUDA 12 | Single GPU → `CUDA_VISIBLE_DEVICES=0` or `1` |
| 2× RTX 3060 (both) | Yes | CUDA TurboQuant or CUDA 12 | Multi-GPU → `CUDA_VISIBLE_DEVICES=0,1` + `split_mode: layer` |
| 1× Intel B70 | Yes | SYCL | `--device SYCL0`, one model at a time |
| NVIDIA + Intel in **one** instance | **No** | — | Different binaries/drivers; use **two instances** |
| All 3 GPUs in **one** instance | **No** | — | Not supported on this fleet |

## Cross-vendor multi-GPU

| Runtime | Same vendor multi-GPU | Mixed vendor (e.g. RTX + B70) |
|---------|----------------------|-------------------------------|
| **CUDA TurboQuant** | Yes (NVIDIA only) | No |
| **CUDA 12** | Yes (NVIDIA only) | No |
| **SYCL** | No (single B70) | No |
| **Vulkan** | Experimental in llama.cpp | **Theoretically possible** — not enabled in wizard |
| **CPU** | N/A | N/A |
| **ROCm** | AMD only (not installed) | No |

### Vulkan note

**Vulkan llama.cpp** is the only engine that *could* address NVIDIA and Intel GPUs through one binary (different Vulkan ICDs). On this host:

- Vulkan is installed at `/opt/llama.cpp/build-vulkan/bin/llama-server`
- Intel B70 is normally served by **SYCL**, not Vulkan
- The wizard **blocks** mixed vendors regardless of runtime
- Cross-vendor Vulkan multi-GPU is **untested** and **not recommended** for production

## Recommended patterns

### Large model on both RTX 3060s

1. Runtime: **CUDA 12 TurboQuant llama.cpp**
2. Mode: **Multi-GPU (NVIDIA)**
3. Select both RTX 3060 cards
4. KV: TurboQuant `turbo4` or Normal `q8_0`

### Model on Intel B70

1. Runtime: **SYCL llama.cpp (Intel)**
2. Mode: **Single GPU**
3. Select Intel Arc Pro B70
4. KV: Normal `q8_0` (TurboQuant not available on SYCL)

### Need both NVIDIA and Intel

Create **two instances**:

| Instance | Runtime | GPU | Control plane |
|----------|---------|-----|---------------|
| Chat / large model | CUDA TurboQuant | 2× RTX 3060 | llamactl |
| Intel workload | SYCL | B70 | `b70-model` + systemd |

Route clients via your existing router or port map.

## Wizard enforcement

The backend rejects invalid combinations:

- `Cannot mix GPU vendors in one instance` — NVIDIA + Intel in one create payload
- `Multi-GPU only supported for NVIDIA` — multi-select with Intel
- `Runtime '…' is not installed` — e.g. ROCm when no build exists
- `Runtime '…' is not compatible with … GPU` — e.g. SYCL runtime + NVIDIA GPU

Busy GPUs show a **warning only** — selection is still allowed.

## Control plane vs compute stack

| Layer | Meaning |
|-------|---------|
| **Control plane** | How the dashboard starts the instance (llamactl vs `b70-model`) |
| **GGML compute stack** | Which GPU API llama-server uses (CUDA, SYCL, Vulkan, …) |

NVIDIA instances are created via **llamactl** with optional `command_override` per runtime binary. Intel instances use **models.conf** + `LLAMA_INTEL_SERVER` in the launcher env.

## Out of scope

- Migrating existing instances to a different runtime (manual llamactl/registry edit + restart)
- Mixing turboquant and standard CUDA in one process
- AMD instance creation until ROCm build exists
