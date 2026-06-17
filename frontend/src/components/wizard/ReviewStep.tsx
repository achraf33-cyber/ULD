import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import type { WizardHardware } from '../../api/types'
import { Card } from '../ui'
import { runtimeLabel } from './runtimeUtils'

export function ReviewStep({
  selected,
  selectedAll,
  mode,
  name,
  model,
  port,
  ctx,
  gpuLayers,
  parallel,
  kvProfile,
  kvVariant,
  cacheTypeK,
  cacheTypeV,
  runtimeId,
  computeBackend,
  reasoning,
  reasoningFormat,
  reasoningBudget,
  extraArgs,
}: {
  selected: WizardHardware
  selectedAll: WizardHardware[]
  mode: string
  name: string
  model: string
  port: number
  ctx: number
  gpuLayers: string
  parallel: number
  kvProfile: string
  kvVariant: string
  cacheTypeK: string
  cacheTypeV: string
  runtimeId: string
  computeBackend: string
  reasoning: string
  reasoningFormat: string
  reasoningBudget: string
  extraArgs: string
}) {
  const multiGpu = mode === 'multi' && selectedAll.length > 1
  const { data: runtimesData } = useQuery({
    queryKey: ['wizard-runtimes-catalog'],
    queryFn: api.wizardRuntimesCatalog,
  })
  const stack = computeBackend || selected.compute_backend || selected.backend
  const devices = selectedAll
    .map((g) => (g.cuda_index != null ? String(g.cuda_index) : g.device_id))
    .filter(Boolean)
    .join(', ')

  const rows: { k: string; v: string }[] = [
    { k: 'GPU(s)', v: selectedAll.map((g) => g.name).join(', ') },
    ...(devices ? [{ k: 'CUDA devices', v: devices }] : []),
    ...(multiGpu ? [{ k: 'Split mode', v: 'layer' }] : []),
    { k: 'Runtime', v: runtimeLabel(runtimesData?.runtimes, runtimeId) },
    { k: 'Compute stack', v: stack },
    { k: 'Device ID', v: selected.device_id ?? '—' },
    { k: 'Name', v: name },
    { k: 'Model', v: model },
    { k: 'Port', v: String(port) },
    { k: 'Context', v: ctx.toLocaleString() },
    { k: 'KV profile', v: kvProfile === 'turbo' ? `turbo (${kvVariant})` : kvProfile },
    ...(kvProfile === 'custom'
      ? [
          { k: 'cache_type_k', v: cacheTypeK || '—' },
          { k: 'cache_type_v', v: cacheTypeV || '—' },
        ]
      : []),
    { k: 'Reasoning', v: reasoning },
    ...(reasoningFormat ? [{ k: 'Reasoning format', v: reasoningFormat }] : []),
    ...(reasoningBudget ? [{ k: 'Reasoning budget', v: reasoningBudget }] : []),
    ...(selected.backend === 'nvidia'
      ? [
          { k: 'GPU layers', v: gpuLayers },
          { k: 'Parallel', v: String(parallel) },
        ]
      : [{ k: 'Extra args', v: extraArgs || '—' }]),
  ]

  return (
    <Card className="divide-y divide-separator p-0 overflow-hidden">
      {rows.map(({ k, v }) => (
        <Row key={k} k={k} v={v} />
      ))}
    </Card>
  )
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-4 px-5 py-3.5 text-sm">
      <span className="text-text-secondary shrink-0">{k}</span>
      <span className="text-text-primary truncate text-right font-medium" title={v}>
        {v}
      </span>
    </div>
  )
}
