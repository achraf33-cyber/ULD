import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { DownloadJob, WizardHardware } from '../../api/types'
import { Button, Card, Input, ProgressBar, SegmentedControl } from '../ui'

interface Props {
  selected?: WizardHardware
  name: string
  model: string
  description: string
  onName: (v: string) => void
  onModel: (v: string) => void
  onDescription: (v: string) => void
}

export function ModelStep({
  selected,
  name,
  model,
  description,
  onName,
  onModel,
  onDescription,
}: Props) {
  const [mode, setMode] = useState<'path' | 'hf'>('path')
  const [ggufQuery, setGgufQuery] = useState('')
  const [hfRepo, setHfRepo] = useState('')
  const [hfTag, setHfTag] = useState('Q4_K_M')
  const [downloadJob, setDownloadJob] = useState<DownloadJob | null>(null)

  const { data: ggufFiles } = useQuery({
    queryKey: ['gguf-files', ggufQuery],
    queryFn: () => api.wizardGgufFiles(ggufQuery),
    enabled: mode === 'path',
  })

  useEffect(() => {
    if (!downloadJob?.id || downloadJob.status === 'completed' || downloadJob.status === 'failed') {
      return
    }
    const timer = setInterval(async () => {
      try {
        const job = await api.nvidiaDownloadJob(downloadJob.id)
        setDownloadJob(job)
        if (job.status === 'completed' && job.progress?.current_file) {
          onModel(job.progress.current_file)
        }
      } catch {
        /* ignore poll errors */
      }
    }, 2000)
    return () => clearInterval(timer)
  }, [downloadJob?.id, downloadJob?.status, onModel])

  const startDownload = async () => {
    if (!hfRepo.trim()) return
    const res = await api.nvidiaDownload(hfRepo.trim(), hfTag.trim())
    const job = await api.nvidiaDownloadJob(res.job_id)
    setDownloadJob(job)
  }

  const downloadPct =
    downloadJob?.progress && downloadJob.progress.total_bytes > 0
      ? Math.round(
          (downloadJob.progress.bytes_downloaded / downloadJob.progress.total_bytes) * 100,
        )
      : 0

  return (
    <div className="space-y-5">
      {selected && (
        <p className="text-sm text-accent">
          Target: {selected.name}
          {selected.cuda_index != null ? ` (CUDA device ${selected.cuda_index})` : ''}
        </p>
      )}
      <Input label="Instance name" value={name} onChange={onName} placeholder="my-model-65k" />

      <SegmentedControl
        options={[
          { value: 'path', label: 'Local GGUF' },
          ...(selected?.backend === 'nvidia'
            ? [{ value: 'hf', label: 'HuggingFace' }]
            : []),
        ]}
        value={mode}
        onChange={(v) => setMode(v as 'path' | 'hf')}
      />

      {mode === 'path' ? (
        <div className="space-y-3">
          <Input
            label="Search local GGUF files"
            value={ggufQuery}
            onChange={setGgufQuery}
            placeholder="qwen, gemma…"
          />
          <Input
            label="Model path"
            value={model}
            onChange={onModel}
            placeholder="/path/to/model.gguf"
          />
          {ggufFiles && ggufFiles.length > 0 && (
            <Card padding="sm" className="max-h-40 overflow-y-auto p-0">
              <ul className="text-xs divide-y divide-separator">
                {ggufFiles.map((f) => (
                  <li key={f.path}>
                    <button
                      type="button"
                      className="w-full text-left px-4 py-2.5 hover:bg-surface-elevated truncate transition-colors duration-150 text-text-primary"
                      onClick={() => onModel(f.path)}
                      title={f.path}
                    >
                      {f.name}
                      {f.size_mb != null ? ` (${f.size_mb} MB)` : ''}
                    </button>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          <Input label="HuggingFace repo" value={hfRepo} onChange={setHfRepo} placeholder="org/model" />
          <Input label="Quant tag" value={hfTag} onChange={setHfTag} placeholder="Q4_K_M" />
          <Button variant="secondary" onClick={startDownload}>
            Start download
          </Button>
          {downloadJob && (
            <Card padding="sm" className="text-sm space-y-3">
              <p>
                Status: <span className="text-text-primary font-medium">{downloadJob.status}</span>
              </p>
              {downloadJob.progress && downloadJob.progress.total_bytes > 0 && (
                <div className="space-y-1.5">
                  <ProgressBar value={downloadPct} />
                  <p className="text-xs text-text-tertiary">{downloadPct}%</p>
                </div>
              )}
              {downloadJob.error && (
                <p className="text-[var(--status-error-text)] text-xs">{downloadJob.error}</p>
              )}
            </Card>
          )}
        </div>
      )}

      {selected?.backend === 'intel' && (
        <Input label="Description" value={description} onChange={onDescription} />
      )}
    </div>
  )
}
