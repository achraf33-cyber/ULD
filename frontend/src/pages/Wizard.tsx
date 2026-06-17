import { useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { GpuPickMode } from '../api/types'
import { HardwareStep } from '../components/wizard/HardwareStep'
import { ModelStep } from '../components/wizard/ModelStep'
import { ParamsStep } from '../components/wizard/ParamsStep'
import { gpuMatchesRuntime } from '../components/wizard/runtimeUtils'
import { ReviewStep } from '../components/wizard/ReviewStep'
import { Button, PageHeader, StepIndicator } from '../components/ui'
import {
  normalizeHardwareIds,
  resolveKvProfile,
  resolveRuntimeId,
} from '../hooks/useWizardSelection'

const STEPS = ['Hardware', 'Model', 'Parameters', 'Review']

export function WizardPage() {
  const navigate = useNavigate()
  const { data: hardware, isLoading } = useQuery({
    queryKey: ['wizard-hardware'],
    queryFn: api.wizardHardware,
    refetchInterval: 5000,
  })

  const [step, setStep] = useState(0)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [gpuMode, setGpuMode] = useState<GpuPickMode>('single')
  const [hardwareIds, setHardwareIds] = useState<string[]>([])
  const [name, setName] = useState('')
  const [model, setModel] = useState('')
  const [port, setPort] = useState(10012)
  const [ctx, setCtx] = useState(65536)
  const [gpuLayers, setGpuLayers] = useState('auto')
  const [parallel, setParallel] = useState(1)
  const [kvProfile, setKvProfile] = useState('normal')
  const [kvVariant, setKvVariant] = useState('turbo4')
  const [cacheTypeK, setCacheTypeK] = useState('')
  const [cacheTypeV, setCacheTypeV] = useState('')
  const [runtimeId, setRuntimeId] = useState('')
  const [computeBackend, setComputeBackend] = useState('')
  const [reasoning, setReasoning] = useState('auto')
  const [reasoningFormat, setReasoningFormat] = useState('')
  const [reasoningBudget, setReasoningBudget] = useState('')
  const [description, setDescription] = useState('')
  const [extraArgs, setExtraArgs] = useState('')

  const { data: runtimesCatalog } = useQuery({
    queryKey: ['wizard-runtimes-catalog'],
    queryFn: api.wizardRuntimesCatalog,
  })

  const creatable = useMemo(() => (hardware ?? []).filter((h) => h.creatable), [hardware])
  const effectiveRuntimeId = useMemo(
    () => resolveRuntimeId(runtimeId, runtimesCatalog),
    [runtimeId, runtimesCatalog],
  )
  const activeRuntime = runtimesCatalog?.runtimes.find((r) => r.id === effectiveRuntimeId)
  const effectiveHardwareIds = useMemo(
    () => normalizeHardwareIds(hardwareIds, creatable, gpuMode, activeRuntime),
    [hardwareIds, creatable, gpuMode, activeRuntime],
  )
  const effectiveKvProfile = resolveKvProfile(kvProfile, effectiveRuntimeId)
  const selectedAll = creatable.filter((h) => effectiveHardwareIds.includes(h.id))
  const selected = selectedAll[0]
  const multiGpu = gpuMode === 'multi' && effectiveHardwareIds.length > 1

  useEffect(() => {
    if (!selected) return
    api.wizardSuggestPort(selected.backend).then((r) => setPort(r.port)).catch(() => {})
  }, [selected])

  const handleRuntime = (id: string) => {
    setRuntimeId(id)
    const rt = runtimesCatalog?.runtimes.find((r) => r.id === id)
    if (!rt) return
    setHardwareIds((ids) =>
      ids.filter((hid) => {
        const gpu = creatable.find((h) => h.id === hid)
        return gpu && gpuMatchesRuntime(gpu.vendor, rt)
      }),
    )
    if (!rt.multi_gpu && gpuMode === 'multi') setGpuMode('single')
  }

  const handleGpuMode = (mode: GpuPickMode) => {
    setGpuMode(mode)
    setHardwareIds((ids) => {
      if (mode === 'single' && ids.length > 1) return [ids[0]]
      if (mode === 'multi') {
        return ids.filter((id) => creatable.find((h) => h.id === id)?.vendor === 'nvidia')
      }
      return ids
    })
  }

  const create = async () => {
    if (!selected) return
    setBusy(true)
    setError('')
    try {
      const payload: Record<string, unknown> = {
        hardware_ids: effectiveHardwareIds,
        name,
        model,
        port,
        ctx,
        gpu_layers: gpuLayers,
        parallel,
        kv_cache_profile: effectiveKvProfile,
        kv_cache_variant: kvVariant,
        cache_type_k: cacheTypeK,
        cache_type_v: cacheTypeV,
        reasoning,
        description,
        extra_args: extraArgs,
        runtime_id: effectiveRuntimeId,
        start: true,
      }
      if (computeBackend) payload.compute_backend = computeBackend
      if (reasoningFormat) payload.reasoning_format = reasoningFormat
      if (reasoningBudget !== '') payload.reasoning_budget = Number(reasoningBudget)
      await api.wizardCreate(payload)
      navigate('/instances')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Create failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-8">
      <PageHeader
        title="Create Instance"
        description={`Step ${step + 1} of ${STEPS.length} — ${STEPS[step]}`}
      />

      <StepIndicator steps={STEPS} current={step} />

      {step === 0 && (
        <HardwareStep
          hardware={hardware}
          isLoading={isLoading}
          mode={gpuMode}
          hardwareIds={effectiveHardwareIds}
          multiGpu={multiGpu}
          runtimeId={effectiveRuntimeId}
          runtimes={runtimesCatalog?.runtimes}
          onMode={handleGpuMode}
          onSelect={setHardwareIds}
          onRuntime={handleRuntime}
        />
      )}

      {step === 1 && (
        <ModelStep
          selected={selected}
          name={name}
          model={model}
          description={description}
          onName={setName}
          onModel={setModel}
          onDescription={setDescription}
        />
      )}

      {step === 2 && (
        <ParamsStep
          selected={selected}
          multiGpu={multiGpu}
          runtimeId={effectiveRuntimeId}
          port={port}
          ctx={ctx}
          gpuLayers={gpuLayers}
          parallel={parallel}
          kvProfile={effectiveKvProfile}
          kvVariant={kvVariant}
          cacheTypeK={cacheTypeK}
          cacheTypeV={cacheTypeV}
          computeBackend={computeBackend}
          reasoning={reasoning}
          reasoningFormat={reasoningFormat}
          reasoningBudget={reasoningBudget}
          extraArgs={extraArgs}
          onPort={setPort}
          onCtx={setCtx}
          onGpuLayers={setGpuLayers}
          onParallel={setParallel}
          onKvProfile={setKvProfile}
          onKvVariant={setKvVariant}
          onCacheTypeK={setCacheTypeK}
          onCacheTypeV={setCacheTypeV}
          onComputeBackend={setComputeBackend}
          onReasoning={setReasoning}
          onReasoningFormat={setReasoningFormat}
          onReasoningBudget={setReasoningBudget}
          onExtraArgs={setExtraArgs}
        />
      )}

      {step === 3 && selected && (
        <ReviewStep
          selected={selected}
          selectedAll={selectedAll}
          mode={gpuMode}
          name={name}
          model={model}
          port={port}
          ctx={ctx}
          gpuLayers={gpuLayers}
          parallel={parallel}
          kvProfile={effectiveKvProfile}
          kvVariant={kvVariant}
          cacheTypeK={cacheTypeK}
          cacheTypeV={cacheTypeV}
          runtimeId={effectiveRuntimeId}
          computeBackend={computeBackend}
          reasoning={reasoning}
          reasoningFormat={reasoningFormat}
          reasoningBudget={reasoningBudget}
          extraArgs={extraArgs}
        />
      )}

      {error && <p className="text-[var(--status-error-text)] text-sm">{error}</p>}

      <div className="flex gap-3 pt-2">
        {step > 0 && (
          <Button variant="secondary" onClick={() => setStep((s) => s - 1)}>
            Back
          </Button>
        )}
        {step < STEPS.length - 1 ? (
          <Button
            onClick={() => setStep((s) => s + 1)}
            disabled={!canNext(step, effectiveHardwareIds, name, model, gpuMode, effectiveRuntimeId)}
          >
            Next
          </Button>
        ) : (
          <Button onClick={create} disabled={busy || !selected}>
            {busy ? 'Creating…' : 'Create & Start'}
          </Button>
        )}
      </div>
    </div>
  )
}

function canNext(
  step: number,
  hardwareIds: string[],
  name: string,
  model: string,
  mode: GpuPickMode,
  runtimeId: string,
) {
  if (step === 0) {
    if (!hardwareIds.length) return false
    if (mode === 'multi' && hardwareIds.length < 2) return false
    if (!runtimeId) return false
    return true
  }
  if (step === 1) return Boolean(name && model)
  if (step === 2) return Boolean(runtimeId)
  return true
}
