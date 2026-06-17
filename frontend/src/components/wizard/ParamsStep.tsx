import { useQuery } from '@tanstack/react-query'
import type { WizardHardware } from '../../api/types'
import { api } from '../../api/client'
import { Card, Input, SegmentedControl, Select } from '../ui'
import { runtimeLabel } from './runtimeUtils'

interface Props {
  selected?: WizardHardware
  multiGpu: boolean
  runtimeId: string
  port: number
  ctx: number
  gpuLayers: string
  parallel: number
  kvProfile: string
  kvVariant: string
  cacheTypeK: string
  cacheTypeV: string
  computeBackend: string
  reasoning: string
  reasoningFormat: string
  reasoningBudget: string
  extraArgs: string
  onPort: (v: number) => void
  onCtx: (v: number) => void
  onGpuLayers: (v: string) => void
  onParallel: (v: number) => void
  onKvProfile: (v: string) => void
  onKvVariant: (v: string) => void
  onCacheTypeK: (v: string) => void
  onCacheTypeV: (v: string) => void
  onComputeBackend: (v: string) => void
  onReasoning: (v: string) => void
  onReasoningFormat: (v: string) => void
  onReasoningBudget: (v: string) => void
  onExtraArgs: (v: string) => void
}

export function ParamsStep(props: Props) {
  const { selected } = props
  const nvidia = selected?.backend === 'nvidia'
  const backends = selected?.available_compute_backends ?? []
  const showStack = backends.length > 1

  const { data: kvOptions } = useQuery({
    queryKey: ['wizard-kv', selected?.backend, props.runtimeId],
    queryFn: () => api.wizardKvOptions(selected!.backend, props.runtimeId || undefined),
    enabled: Boolean(selected?.backend),
  })

  const profiles = kvOptions?.profiles ?? []
  const showTurbo = props.kvProfile === 'turbo' && kvOptions?.supports_turboquant

  const { data: runtimesData } = useQuery({
    queryKey: ['wizard-runtimes-catalog'],
    queryFn: api.wizardRuntimesCatalog,
  })

  return (
    <div className="space-y-5">
      {props.runtimeId && (
        <Card padding="sm" className="text-sm">
          <span className="text-text-tertiary">Runtime · </span>
          <span className="text-text-primary">{runtimeLabel(runtimesData?.runtimes, props.runtimeId)}</span>
          <span className="text-text-tertiary text-xs block mt-1">Change on the Hardware step</span>
        </Card>
      )}

      <Input label="Port" value={String(props.port)} onChange={(v) => props.onPort(Number(v))} type="number" />
      <Input label="Context size" value={String(props.ctx)} onChange={(v) => props.onCtx(Number(v))} type="number" />

      <fieldset className="space-y-3">
        <legend className="text-sm text-text-secondary">KV cache profile</legend>
        <SegmentedControl
          options={profiles.map((p) => ({ value: p.id, label: p.label }))}
          value={props.kvProfile}
          onChange={props.onKvProfile}
          className="flex flex-wrap"
        />
        {showTurbo && (
          <SegmentedControl
            options={(['turbo4', 'turbo3', 'mixed'] as const).map((v) => ({ value: v, label: v }))}
            value={props.kvVariant}
            onChange={props.onKvVariant}
          />
        )}
        {props.kvProfile === 'custom' && (
          <div className="grid grid-cols-2 gap-3">
            <Input label="cache_type_k" value={props.cacheTypeK} onChange={props.onCacheTypeK} />
            <Input label="cache_type_v" value={props.cacheTypeV} onChange={props.onCacheTypeV} />
          </div>
        )}
        <p className="text-xs text-text-tertiary">
          TurboQuant requires the turboquant llama-server (NVIDIA). Intel uses normal KV only.
        </p>
      </fieldset>

      <fieldset className="space-y-3">
        <legend className="text-sm text-text-secondary">Reasoning / thinking</legend>
        <Select label="Reasoning" value={props.reasoning} onChange={props.onReasoning} options={['auto', 'on', 'off']} />
        <Select
          label="Reasoning format"
          value={props.reasoningFormat}
          onChange={props.onReasoningFormat}
          options={['', 'none', 'deepseek', 'deepseek-legacy']}
        />
        <Input
          label="Reasoning budget (-1 unlimited, 0 off)"
          value={props.reasoningBudget}
          onChange={props.onReasoningBudget}
          placeholder="leave empty for default"
        />
      </fieldset>

      {nvidia && (
        <>
          <Input label="GPU layers" value={props.gpuLayers} onChange={props.onGpuLayers} placeholder="auto" />
          <Input
            label="Parallel slots"
            value={String(props.parallel)}
            onChange={(v) => props.onParallel(Number(v))}
            type="number"
          />
        </>
      )}

      {!nvidia && (
        <Input label="Extra args" value={props.extraArgs} onChange={props.onExtraArgs} placeholder="optional flags" />
      )}

      {showStack && (
        <details className="rounded-[var(--radius-card)] border border-separator bg-surface p-4">
          <summary className="text-sm text-text-secondary cursor-pointer">Advanced compute stack</summary>
          <p className="text-xs text-text-tertiary mt-2 mb-3">
            Auto-selected from your GPU. Vulkan/ROCm appear only when a matching build is installed.
          </p>
          <Select
            label="Compute backend"
            value={props.computeBackend || selected?.compute_backend || ''}
            onChange={props.onComputeBackend}
            options={['', ...backends]}
          />
        </details>
      )}
    </div>
  )
}
