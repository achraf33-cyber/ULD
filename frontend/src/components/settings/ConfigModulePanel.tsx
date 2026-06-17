import { Badge, Button, Card, Input } from '../ui'
import type { ConfigField, ConfigModule } from '../../api/types'
import { useConfigSave } from './useConfigSave'
import { useEffect, useState } from 'react'

const STATUS_VARIANT = {
  ok: 'success',
  warn: 'warning',
  missing: 'error',
  empty: 'neutral',
} as const

interface Props {
  module: ConfigModule
  libraryRoots?: { path: string; exists: boolean; gguf_count: number }[]
  databasePath?: string
  onDirtyChange?: (dirty: boolean) => void
  onNavigateAway?: (next: () => void) => void
}

export function ConfigModulePanel({
  module,
  libraryRoots,
  databasePath,
  onDirtyChange,
}: Props) {
  const [draft, setDraft] = useState<Record<string, string>>({})
  const [message, setMessage] = useState('')
  const [restartHint, setRestartHint] = useState('')
  const save = useConfigSave((res) => {
    setDraft({})
    setMessage('Saved.')
    if (res.restart_required) {
      setRestartHint(res.restart_command ?? 'sudo systemctl restart llama-dashboard')
    }
  })

  const dirty = Object.keys(draft).length > 0

  useEffect(() => {
    onDirtyChange?.(dirty)
  }, [dirty, onDirtyChange])

  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (dirty) e.preventDefault()
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [dirty])

  const valueFor = (field: ConfigField) => {
    if (field.key in draft) return draft[field.key]
    if (field.type === 'path-list') return field.value.replace(/:/g, '\n')
    return field.value
  }

  const setField = (field: ConfigField, raw: string) => {
    const val =
      field.type === 'path-list'
        ? raw
            .split('\n')
            .map((l) => l.trim())
            .filter(Boolean)
            .join(':')
        : raw
    setDraft((prev) => ({ ...prev, [field.key]: val }))
    setMessage('')
  }

  const handleSave = () => {
    const payload: Record<string, string | number> = {}
    for (const [key, val] of Object.entries(draft)) {
      payload[key] = key === 'metrics_interval_s' || key === 'port' ? Number(val) : val
    }
    if (dirty && !module.complete) {
      payload.install_complete = '1'
    }
    save.mutate(payload)
  }

  return (
    <Card className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary">{module.title}</h3>
        <p className="text-sm text-text-secondary mt-1">{module.description}</p>
      </div>

      {restartHint && (
        <div className="rounded-[var(--radius-control)] border border-[var(--status-warning-text)]/30 bg-[var(--status-warning-bg)]/40 px-4 py-3 text-sm">
          <p className="text-text-primary font-medium">Restart required</p>
          <p className="text-text-secondary mt-1">
            Server bind settings changed. Run:{' '}
            <code className="font-mono text-xs bg-surface-elevated px-1.5 py-0.5 rounded">{restartHint}</code>
          </p>
        </div>
      )}

      {module.id === 'library' && libraryRoots && libraryRoots.length > 0 && (
        <LibraryStatus roots={libraryRoots} />
      )}

      <div className="space-y-5">
        {module.fields.map((field) => (
          <FieldRow
            key={field.key}
            field={field}
            value={valueFor(field)}
            onChange={(v) => setField(field, v)}
          />
        ))}
      </div>

      {databasePath && module.id === 'server' && (
        <p className="text-xs text-text-tertiary">
          Bootstrap overrides may still apply from <span className="font-mono">.env</span> until saved here.
        </p>
      )}

      {databasePath && module.id !== 'server' && (
        <p className="text-xs text-text-tertiary">
          Stored in SQLite · <span className="font-mono">{databasePath}</span>
        </p>
      )}

      <div className="flex items-center gap-3 pt-1 flex-wrap">
        <Button onClick={handleSave} disabled={save.isPending || !dirty}>
          {save.isPending ? 'Saving…' : 'Save module'}
        </Button>
        {message && <span className="text-sm text-[var(--status-running-text)]">{message}</span>}
        {save.isError && (
          <span className="text-sm text-[var(--status-error-text)]">
            {save.error instanceof Error ? save.error.message : 'Save failed'}
          </span>
        )}
      </div>
    </Card>
  )
}

function FieldRow({
  field,
  value,
  onChange,
}: {
  field: ConfigField
  value: string
  onChange: (v: string) => void
}) {
  const status = field.status
  const isPathList = field.type === 'path-list'

  if (isPathList) {
    return (
      <div>
        <label className="block">
          <span className="text-sm font-medium text-text-secondary flex items-center gap-2 flex-wrap">
            {field.label}
            {field.required && <span className="text-accent text-xs">Required</span>}
            {status && <FieldStatus status={status} />}
          </span>
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            rows={4}
            placeholder="/path/to/models&#10;/path/to/hub"
            className="mt-1.5 w-full rounded-[var(--radius-control)] bg-surface-elevated border border-separator px-3 py-2.5 text-sm font-mono text-text-primary placeholder:text-text-tertiary focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
          />
        </label>
        {field.hint && <p className="text-xs text-text-tertiary mt-1">{field.hint}</p>}
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-0.5">
        {status && <FieldStatus status={status} />}
        {field.restart_on_change && (
          <span className="text-[10px] text-text-tertiary uppercase tracking-wide">Restart on save</span>
        )}
      </div>
      <Input
        label={`${field.label}${field.required ? ' *' : ''}`}
        value={value}
        onChange={onChange}
        type={field.type === 'number' ? 'number' : 'text'}
        placeholder={field.hint.slice(0, 60)}
      />
      {field.hint && <p className="text-xs text-text-tertiary mt-1">{field.hint}</p>}
    </div>
  )
}

function FieldStatus({ status }: { status: NonNullable<ConfigField['status']> }) {
  const variant = STATUS_VARIANT[status.state as keyof typeof STATUS_VARIANT] ?? 'neutral'
  return (
    <Badge variant={variant} className="ml-auto">
      {status.message}
    </Badge>
  )
}

function LibraryStatus({
  roots,
}: {
  roots: { path: string; exists: boolean; gguf_count: number }[]
}) {
  return (
    <div className="rounded-[var(--radius-control)] bg-surface-elevated border border-separator p-3 space-y-2">
      <p className="text-xs font-medium text-text-secondary">Scan preview</p>
      {roots.map((r) => (
        <div key={r.path} className="flex justify-between gap-2 text-xs">
          <span className="font-mono text-text-tertiary truncate">{r.path}</span>
          <span className={r.exists ? 'text-[var(--status-running-text)]' : 'text-[var(--status-error-text)]'}>
            {r.exists ? `${r.gguf_count} gguf` : 'missing'}
          </span>
        </div>
      ))}
    </div>
  )
}
