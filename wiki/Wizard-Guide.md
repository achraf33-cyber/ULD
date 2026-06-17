# Create-instance wizard

Four steps: **Hardware → Model → Parameters → Review**.

## Step 1 — Hardware (runtime first)

### Runtime (top of page)

Pick the llama.cpp engine **before** GPUs. Options include:

- CUDA 12 TurboQuant (NVIDIA, default fleet)
- CUDA 12 standard
- Vulkan (cross-vendor capable in theory)
- CPU (no GPU layers)
- SYCL (Intel)
- ROCm (shown as not installed until built)

Unavailable runtimes appear as **not installed** in the list.

### GPU mode

| Mode | Behavior |
|------|----------|
| **Single GPU** | One card — NVIDIA or Intel |
| **Multi-GPU (NVIDIA)** | Checkboxes on RTX cards only; layer split |

GPU list **filters by runtime**. Incompatible cards are disabled.

See [GPU & runtime limitations](gpu-runtime-limitations.md) for what combinations work.

## Step 2 — Model

- Instance name, GGUF path (browser), optional description
- HuggingFace download available for NVIDIA path via llamactl

## Step 3 — Parameters

- **KV cache profile**: TurboQuant (NVIDIA turboquant only), Normal `q8_0`, Full `f16`, Custom
- **Reasoning**: `auto` / `on` / `off`, format, budget
- Port, context, GPU layers, parallel (NVIDIA)

Runtime is shown read-only; change on Hardware step.

## Step 4 — Review

Confirms runtime, GPU binding, KV profile, and reasoning flags before create.

## API

```http
GET /api/wizard/runtimes?catalog=true
GET /api/wizard/hardware
GET /api/wizard/kv-options?backend=nvidia&runtime_id=cuda-turboquant
POST /api/wizard/create
```

Create body includes `hardware_ids[]`, `runtime_id`, `kv_cache_profile`, `reasoning`, etc.
