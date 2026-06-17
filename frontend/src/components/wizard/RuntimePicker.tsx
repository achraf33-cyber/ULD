import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import type { WizardRuntime } from '../../api/types'
import { Card, Select } from '../ui'

export function RuntimePicker({
  runtimeId,
  multiGpu,
  onRuntime,
}: {
  runtimeId: string
  multiGpu: boolean
  onRuntime: (id: string) => void
}) {
  const { data, isLoading } = useQuery({
    queryKey: ['wizard-runtimes-catalog'],
    queryFn: api.wizardRuntimesCatalog,
  })

  const runtimes = data?.runtimes ?? []
  const selected = runtimes.find((r) => r.id === runtimeId)

  return (
    <Card className="space-y-4">
      <div>
        <h3 className="text-sm font-medium text-text-primary">Runtime</h3>
        <p className="text-xs text-text-tertiary mt-1">
          Choose the llama.cpp engine first — CUDA, Vulkan, CPU, or SYCL. GPU options below filter to
          match.
        </p>
      </div>

      {isLoading ? (
        <p className="text-sm text-text-tertiary">Loading runtimes…</p>
      ) : (
        <>
          <Select
            label="Runtime"
            value={runtimeId || data?.default_runtime_id || ''}
            onChange={onRuntime}
            options={runtimes.map((rt) => ({
              value: rt.id,
              label: rt.installed ? rt.label : `${rt.label} — not installed`,
              disabled: !rt.installed,
            }))}
          />

          {selected && <RuntimeDetail runtime={selected} multiGpu={multiGpu} />}

          <div className="grid gap-1 pt-1">
            {runtimes.map((rt) => (
              <RuntimeRow
                key={rt.id}
                runtime={rt}
                active={runtimeId === rt.id}
                onSelect={() => rt.installed && onRuntime(rt.id)}
              />
            ))}
          </div>
        </>
      )}
    </Card>
  )
}

function RuntimeDetail({ runtime, multiGpu }: { runtime: WizardRuntime; multiGpu: boolean }) {
  const warnMulti = multiGpu && !runtime.multi_gpu
  return (
    <Card padding="sm" className="text-xs text-text-secondary bg-surface-elevated">
      <p>{runtime.hint}</p>
      {warnMulti && (
        <p className="text-[var(--status-warning-text)] mt-1">
          This runtime does not support multi-GPU layer split.
        </p>
      )}
      {!runtime.installed && (
        <p className="text-[var(--status-warning-text)] mt-1">
          Build not found on this host at {runtime.binary}
        </p>
      )}
    </Card>
  )
}

function RuntimeRow({
  runtime,
  active,
  onSelect,
}: {
  runtime: WizardRuntime
  active: boolean
  onSelect: () => void
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={!runtime.installed}
      className={`flex items-center justify-between rounded-[var(--radius-control)] px-3 py-2 text-left text-xs transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 ${
        !runtime.installed
          ? 'opacity-40 cursor-not-allowed text-text-tertiary'
          : active
            ? 'bg-accent/12 text-accent font-medium'
            : 'text-text-secondary hover:bg-surface-elevated'
      }`}
    >
      <span>{runtime.label}</span>
      <span className="shrink-0 ml-2">
        {runtime.installed ? (
          <span className="text-[var(--status-running-text)]">installed</span>
        ) : (
          <span className="text-text-tertiary">not installed</span>
        )}
      </span>
    </button>
  )
}
