import type { GpuPickMode, WizardHardware, WizardRuntime } from '../api/types'
import { gpuMatchesRuntime } from '../components/wizard/runtimeUtils'

export function resolveRuntimeId(
  runtimeId: string,
  runtimes?: { default_runtime_id?: string; runtimes: WizardRuntime[] },
) {
  if (!runtimes) return runtimeId
  const valid = Boolean(
    runtimeId && runtimes.runtimes.some((rt) => rt.id === runtimeId && rt.installed),
  )
  return valid ? runtimeId : (runtimes.default_runtime_id ?? runtimeId)
}

export function normalizeHardwareIds(
  ids: string[],
  creatable: WizardHardware[],
  gpuMode: GpuPickMode,
  runtime?: WizardRuntime,
): string[] {
  let result = ids.filter((id) => {
    const gpu = creatable.find((h) => h.id === id)
    return gpu && gpuMatchesRuntime(gpu.vendor, runtime)
  })

  if (!result.length && creatable.length) {
    const match = creatable.find((h) => gpuMatchesRuntime(h.vendor, runtime))
    const firstNvidia = creatable.find((h) => h.vendor === 'nvidia')
    result = [match?.id ?? firstNvidia?.id ?? creatable[0].id]
  }

  if (gpuMode === 'single' && result.length > 1) return [result[0]]
  if (gpuMode === 'multi') {
    return result.filter((id) => creatable.find((h) => h.id === id)?.vendor === 'nvidia')
  }
  return result
}

export function resolveKvProfile(kvProfile: string, runtimeId: string) {
  if (kvProfile === 'turbo' && runtimeId && runtimeId !== 'cuda-turboquant') return 'normal'
  return kvProfile
}
