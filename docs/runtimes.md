# Installed runtimes (fleet host)

Paths and roles for llama-server binaries detected by the wizard.

| Runtime ID | Label | Binary | Stack | Multi-GPU |
|------------|-------|--------|-------|-----------|
| `cuda-turboquant` | CUDA 12 TurboQuant | `/opt/llama-turboquant/build/bin/llama-server` | CUDA | Yes |
| `cuda-standard` | CUDA 12 standard | `/opt/llama.cpp/build/bin/llama-server` | CUDA | Yes |
| `vulkan` | Vulkan | `/opt/llama.cpp/build-vulkan/bin/llama-server` | Vulkan | Experimental |
| `cpu` | CPU | `/opt/llama.cpp/build/bin/llama-server` | CPU | No |
| `sycl-intel` | SYCL Intel | `/opt/llama.cpp/build-sycl/bin/llama-server` | SYCL | No |
| `rocm` | ROCm | `/opt/llama.cpp/build-rocm/bin/llama-server` | ROCm | Not installed |

## llamactl default

Global config `/opt/llamactl/config.yaml`:

```yaml
backends:
  llama-cpp:
    command: /opt/llama-turboquant/build/bin/llama-server
```

Wizard creates override per instance via `command_override` when a different NVIDIA runtime is selected.

## Intel launcher

- Registry: `/etc/llama-intel-b70/models.conf`
- Env: `/etc/llama-intel-b70/<name>.env` with `LLAMA_INTEL_SERVER`, `LLAMA_INTEL_DEVICE`
- Script: `/usr/local/bin/llama-intel-b70.sh`

## Building Vulkan

```bash
apt-get install -y glslc libshaderc-dev spirv-headers libvulkan-dev
cmake -S /opt/llama.cpp -B /opt/llama.cpp/build-vulkan \
  -DCMAKE_BUILD_TYPE=Release -DGGML_VULKAN=ON -DGGML_CUDA=OFF \
  -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_TESTS=OFF
cmake --build /opt/llama.cpp/build-vulkan --target llama-server -j$(nproc)
```

Restart `llama-dashboard` after adding binaries so the catalog refreshes.
