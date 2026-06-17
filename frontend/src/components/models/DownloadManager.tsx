import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Trash2 } from 'lucide-react'
import { useState } from 'react'
import { api } from '../../api/client'
import type { DownloadJob } from '../../api/types'
import { Button, Card, EmptyState, Input, ProgressBar } from '../ui'

export function DownloadManager() {
  const qc = useQueryClient()
  const [repo, setRepo] = useState('')
  const [tag, setTag] = useState('Q4_K_M')
  const [error, setError] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['model-downloads'],
    queryFn: api.modelDownloads,
    refetchInterval: 3000,
  })

  const start = useMutation({
    mutationFn: () => api.modelStartDownload(repo.trim(), tag.trim()),
    onSuccess: () => {
      setError('')
      qc.invalidateQueries({ queryKey: ['model-downloads'] })
    },
    onError: (err) => setError(err instanceof Error ? err.message : 'Download failed'),
  })

  const cancel = useMutation({
    mutationFn: (jobId: string) => api.modelCancelDownload(jobId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['model-downloads'] }),
  })

  const jobs = data?.jobs ?? []

  return (
    <div className="space-y-5">
      <Card className="space-y-4">
        <h3 className="text-sm font-medium text-text-primary">Download from HuggingFace</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          <Input label="Repository" value={repo} onChange={setRepo} placeholder="org/model-name" />
          <Input label="Quant tag" value={tag} onChange={setTag} placeholder="Q4_K_M" />
        </div>
        <Button onClick={() => start.mutate()} disabled={!repo.trim() || start.isPending}>
          {start.isPending ? 'Starting…' : 'Start download'}
        </Button>
        {error && <p className="text-sm text-[var(--status-error-text)]">{error}</p>}
      </Card>

      {isLoading ? (
        <EmptyState message="Loading download jobs…" className="py-4" />
      ) : !jobs.length ? (
        <EmptyState message="No active or recent downloads." className="py-4" />
      ) : (
        <Card padding="sm" className="overflow-hidden p-0 divide-y divide-separator">
          {jobs.map((job) => (
            <JobRow key={job.id} job={job} onCancel={() => cancel.mutate(job.id)} busy={cancel.isPending} />
          ))}
        </Card>
      )}
    </div>
  )
}

function JobRow({
  job,
  onCancel,
  busy,
}: {
  job: DownloadJob
  onCancel: () => void
  busy: boolean
}) {
  const pct =
    job.progress && job.progress.total_bytes > 0
      ? Math.round((job.progress.bytes_downloaded / job.progress.total_bytes) * 100)
      : 0
  const active = !['completed', 'failed', 'cancelled'].includes(job.status)

  return (
    <div className="px-5 py-4 space-y-2">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-medium text-text-primary">
            {job.repo}
            {job.tag ? `:${job.tag}` : ''}
          </p>
          <p className="text-xs text-text-tertiary capitalize mt-0.5">{job.status}</p>
        </div>
        {active && (
          <button
            type="button"
            title="Cancel"
            disabled={busy}
            onClick={onCancel}
            className="rounded-full p-2 text-text-secondary hover:bg-surface-elevated hover:text-[var(--status-error-text)] transition-colors"
          >
            <Trash2 size={15} />
          </button>
        )}
      </div>
      {job.progress && job.progress.total_bytes > 0 && (
        <div className="space-y-1">
          <ProgressBar value={pct} />
          <p className="text-xs text-text-tertiary">{pct}%</p>
        </div>
      )}
      {job.progress?.current_file && (
        <p className="text-xs text-text-secondary truncate" title={job.progress.current_file}>
          {job.progress.current_file}
        </p>
      )}
      {job.error && <p className="text-xs text-[var(--status-error-text)]">{job.error}</p>}
    </div>
  )
}
