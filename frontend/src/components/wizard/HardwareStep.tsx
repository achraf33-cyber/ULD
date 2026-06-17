import type { ReactNode } from 'react'
import type { GpuPickMode, WizardHardware, WizardRuntime } from '../../api/types'
import { Card, EmptyState, SegmentedControl } from '../ui'
import { RuntimePicker } from './RuntimePicker'
import { gpuMatchesRuntime, runtimeLabel } from './runtimeUtils'

export function HardwareStep({
  hardware,
  isLoading,
  mode,
  hardwareIds,
  multiGpu,
  runtimeId,
  runtimes,
  onMode,
  onSelect,
  onRuntime,
}: {
  hardware?: WizardHardware[]
  isLoading: boolean
  mode: GpuPickMode
  hardwareIds: string[]
  multiGpu: boolean
  runtimeId: string
  runtimes?: WizardRuntime[]
  onMode: (m: GpuPickMode) => void
  onSelect: (ids: string[]) => void
  onRuntime: (id: string) => void
}) {
  const creatable = (hardware ?? []).filter((h) => h.creatable)
  const runtime = runtimes?.find((r) => r.id === runtimeId)
  const nvidia = creatable.filter((h) => h.vendor === 'nvidia')
  const intel = creatable.filter((h) => h.vendor === 'intel')
  const selected = creatable.filter((h) => hardwareIds.includes(h.id))
  const busy = selected.some(isBusy)

  const toggle = (gpu: WizardHardware) => {
    if (!gpuMatchesRuntime(gpu.vendor, runtime)) return
    if (mode === 'single') {
      onSelect([gpu.id])
      return
    }
    if (gpu.vendor !== 'nvidia') return
    const nvidiaIds = hardwareIds.filter(
      (id) => creatable.find((h) => h.id === id)?.vendor === 'nvidia',
    )
    if (hardwareIds.includes(gpu.id)) {
      onSelect(nvidiaIds.filter((id) => id !== gpu.id))
    } else {
      onSelect([...nvidiaIds, gpu.id])
    }
  }

  const gpuDisabled = (gpu: WizardHardware) => {
    if (mode === 'multi' && gpu.vendor !== 'nvidia') return true
    if (!runtime?.installed) return true
    return !gpuMatchesRuntime(gpu.vendor, runtime)
  }

  return (
    <div className="space-y-5">
      <RuntimePicker runtimeId={runtimeId} multiGpu={multiGpu} onRuntime={onRuntime} />

      <SegmentedControl
        options={[
          { value: 'single', label: 'Single GPU' },
          {
            value: 'multi',
            label: 'Multi-GPU',
            disabled: Boolean(runtime && !runtime.multi_gpu),
          },
        ]}
        value={mode}
        onChange={(v) => onMode(v as GpuPickMode)}
      />

      {runtime && !runtime.multi_gpu && mode === 'multi' && (
        <p className="text-xs text-[var(--status-warning-text)]">
          Selected runtime does not support multi-GPU.
        </p>
      )}

      {selected.length > 0 && (
        <Card padding="sm" className="text-sm text-text-secondary">
          {summary(selected, mode, runtimeId, runtimes)}
        </Card>
      )}

      {busy && (
        <Card padding="sm" className="text-sm text-[var(--status-warning-text)] bg-[var(--status-warning-bg)]">
          Selected GPU(s) are busy or low on VRAM — you can still proceed.
        </Card>
      )}

      <p className="text-text-secondary text-sm">
        {runtime?.cpu_only
          ? 'CPU runtime — GPU pick is optional (used for host affinity only).'
          : 'Pick GPU(s) compatible with the runtime above. One vendor per instance.'}
      </p>

      {isLoading ? (
        <EmptyState message="Scanning hardware…" className="py-4" />
      ) : !creatable.length ? (
        <EmptyState message="No creatable GPUs found." className="py-4" />
      ) : (
        <>
          {nvidia.length > 0 && (
            <GpuSection title="NVIDIA GPUs" hint="CUDA / Vulkan runtimes">
              {nvidia.map((gpu) => (
                <HardwareCard
                  key={gpu.id}
                  gpu={gpu}
                  mode={mode}
                  active={hardwareIds.includes(gpu.id)}
                  disabled={gpuDisabled(gpu)}
                  onToggle={() => toggle(gpu)}
                />
              ))}
            </GpuSection>
          )}
          {intel.length > 0 && (
            <GpuSection title="Intel GPUs" hint="SYCL runtime">
              {intel.map((gpu) => (
                <HardwareCard
                  key={gpu.id}
                  gpu={gpu}
                  mode={mode}
                  active={hardwareIds.includes(gpu.id)}
                  disabled={gpuDisabled(gpu)}
                  onToggle={() => toggle(gpu)}
                />
              ))}
            </GpuSection>
          )}
        </>
      )}

      {mode === 'multi' && nvidia.length < 2 && (
        <p className="text-xs text-text-tertiary">
          Only one NVIDIA GPU detected — multi mode needs two RTX cards.
        </p>
      )}

      {(hardware ?? [])
        .filter((h) => !h.creatable)
        .map((gpu) => (
          <Card key={gpu.id} padding="sm" className="text-xs text-text-tertiary">
            {gpu.name} — {gpu.note}
          </Card>
        ))}
    </div>
  )
}

function GpuSection({
  title,
  hint,
  children,
}: {
  title: string
  hint: string
  children: ReactNode
}) {
  return (
    <section className="space-y-3">
      <div>
        <h3 className="text-sm font-medium text-text-primary">{title}</h3>
        <p className="text-xs text-text-tertiary">{hint}</p>
      </div>
      <div className="space-y-2">{children}</div>
    </section>
  )
}

function summary(
  selected: WizardHardware[],
  mode: GpuPickMode,
  runtimeId: string,
  runtimes?: WizardRuntime[],
) {
  const devices = selected
    .map((g) => (g.cuda_index != null ? String(g.cuda_index) : g.device_id ?? ''))
    .filter(Boolean)
    .join(', ')
  const split = mode === 'multi' && selected.length > 1 ? ' · layer split' : ''
  const rt = runtimeLabel(runtimes, runtimeId)
  const gpuPart =
    selected.length > 0
      ? `${selected.length} GPU${selected.length > 1 ? 's' : ''}${devices ? ` (${devices})` : ''}`
      : 'No GPU'
  return `${rt || 'Runtime'} · ${gpuPart}${split}`
}

function isBusy(gpu: WizardHardware) {
  const lowVram = gpu.mem_free_mb != null && gpu.mem_free_mb < 2048
  const highLoad = gpu.effort_percent != null && gpu.effort_percent > 85
  return lowVram || highLoad || gpu.available === false
}

function availBadge(gpu: WizardHardware) {
  if (!gpu.available || (gpu.effort_percent ?? 0) >= 95)
    return { label: 'Critical', cls: 'text-[var(--status-error-text)]' }
  if (isBusy(gpu)) return { label: 'Busy', cls: 'text-[var(--status-warning-text)]' }
  return { label: 'Available', cls: 'text-[var(--status-running-text)]' }
}

function HardwareCard({
  gpu,
  mode,
  active,
  disabled,
  onToggle,
}: {
  gpu: WizardHardware
  mode: GpuPickMode
  active: boolean
  disabled: boolean
  onToggle: () => void
}) {
  const badge = availBadge(gpu)
  const vram =
    gpu.mem_total_mb != null
      ? `${Math.round(gpu.mem_used_mb ?? 0)} / ${Math.round(gpu.mem_total_mb)} MB VRAM`
      : ''
  const free = gpu.mem_free_mb != null ? `${Math.round(gpu.mem_free_mb)} MB free` : ''
  const stack = gpu.compute_backend?.toUpperCase() ?? gpu.backend.toUpperCase()
  const device = gpu.device_id ?? (gpu.cuda_index != null ? `CUDA${gpu.cuda_index}` : '')

  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={disabled}
      className={`w-full text-left rounded-[var(--radius-card)] border p-4 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 ${
        disabled
          ? 'border-separator opacity-50 cursor-not-allowed'
          : active
            ? 'border-accent bg-accent/8 ring-1 ring-accent/20'
            : 'border-separator bg-surface hover:border-accent/40 hover:shadow-sm'
      }`}
    >
      <div className="flex justify-between items-start gap-2">
        <div>
          <h3 className="font-medium text-text-primary">{gpu.name}</h3>
          <p className="text-text-secondary text-sm mt-1 capitalize">
            {gpu.vendor} · {gpu.driver}
            {gpu.cuda_index != null ? ` · NVML ${gpu.cuda_index}` : ''}
          </p>
        </div>
        <div className="text-right space-y-1">
          <span className={`text-xs block font-medium ${badge.cls}`}>{badge.label}</span>
          {gpu.effort_percent != null && (
            <span className="text-xs text-text-tertiary block">{gpu.effort_percent}% load</span>
          )}
        </div>
      </div>
      <p className="text-xs text-text-tertiary mt-2">
        {[stack, device && `device ${device}`, vram, free].filter(Boolean).join(' · ')}
      </p>
      {gpu.instances_on_gpu && gpu.instances_on_gpu.length > 0 && (
        <p className="text-xs text-text-tertiary mt-1 truncate" title={gpu.instances_on_gpu.join(', ')}>
          Instances: {gpu.instances_on_gpu.slice(0, 3).join(', ')}
          {gpu.instances_on_gpu.length > 3 ? ` +${gpu.instances_on_gpu.length - 3}` : ''}
        </p>
      )}
      {disabled && (
        <p className="text-xs text-[var(--status-warning-text)] mt-1">
          Not compatible with selected runtime
        </p>
      )}
      {gpu.note && !disabled && <p className="text-xs text-text-tertiary mt-1">{gpu.note}</p>}
      <div className="mt-2">
        {mode === 'multi' && gpu.vendor === 'nvidia' ? (
          <span className={`text-xs ${active ? 'text-accent font-medium' : 'text-text-tertiary'}`}>
            {active ? 'Selected' : 'Tap to select'}
          </span>
        ) : mode === 'single' ? (
          <span className={`text-xs ${active ? 'text-accent font-medium' : 'text-text-tertiary'}`}>
            {active ? 'Selected' : 'Tap to select'}
          </span>
        ) : null}
      </div>
    </button>
  )
}
