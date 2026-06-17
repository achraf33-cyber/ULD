import type { WizardRuntime } from '../../api/types'

export function runtimeLabel(runtimes: WizardRuntime[] | undefined, id: string) {
  return runtimes?.find((r) => r.id === id)?.label ?? id
}

export function gpuMatchesRuntime(gpuVendor: string, runtime?: WizardRuntime) {
  if (!runtime?.installed) return false
  if (runtime.cpu_only) return true
  return (
    runtime.compatible_vendors?.includes(gpuVendor) ||
    runtime.compatible_vendors?.includes('any') ||
    false
  )
}
