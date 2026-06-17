import { Play, RotateCcw, Square, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { InstanceThroughput, UnifiedInstance } from '../api/types'
import { Card, EmptyState } from './ui'
import { StatusBadge } from './StatusBadge'

interface Props {
  instances: UnifiedInstance[]
  throughput?: InstanceThroughput[]
  showTokens?: boolean
  showDelete?: boolean
  onAction?: () => void
}

export function InstanceTable({
  instances,
  throughput = [],
  showTokens = false,
  showDelete = false,
  onAction,
}: Props) {
  const [busyKey, setBusyKey] = useState<string | null>(null)
  const [rowError, setRowError] = useState<Record<string, string>>({})

  const tpsMap = new Map(
    throughput.map((t) => [`${t.backend}:${t.name}`, t.tokens_per_second]),
  )

  const rowKey = (inst: UnifiedInstance) => `${inst.backend}:${inst.name}`

  const act = async (inst: UnifiedInstance, verb: 'start' | 'stop' | 'restart') => {
    const key = rowKey(inst)
    setBusyKey(`${key}:${verb}`)
    setRowError((e) => ({ ...e, [key]: '' }))
    try {
      if (inst.backend === 'nvidia') {
        if (verb === 'start') await api.nvidiaStart(inst.name)
        else if (verb === 'stop') await api.nvidiaStop(inst.name)
        else await api.nvidiaRestart(inst.name)
      } else {
        if (verb === 'start') await api.intelStart(inst.name)
        else if (verb === 'stop') await api.intelStop(inst.name)
        else await api.intelRestart(inst.name)
      }
      onAction?.()
    } catch (err) {
      setRowError((e) => ({
        ...e,
        [key]: err instanceof Error ? err.message : 'Action failed',
      }))
    } finally {
      setBusyKey(null)
    }
  }

  const del = async (inst: UnifiedInstance) => {
    if (!confirm(`Delete instance "${inst.name}"?`)) return
    const key = rowKey(inst)
    setBusyKey(`${key}:delete`)
    setRowError((e) => ({ ...e, [key]: '' }))
    try {
      if (inst.backend === 'nvidia') await api.nvidiaDelete(inst.name)
      else await api.intelDelete(inst.name)
      onAction?.()
    } catch (err) {
      setRowError((e) => ({
        ...e,
        [key]: err instanceof Error ? err.message : 'Delete failed',
      }))
    } finally {
      setBusyKey(null)
    }
  }

  if (!instances.length) {
    return (
      <EmptyState
        message="No instances found."
        action={
          <Link
            to="/create"
            className="inline-flex items-center rounded-[var(--radius-control)] px-4 py-2.5 text-sm font-medium bg-surface border border-separator text-text-primary hover:bg-surface-elevated"
          >
            Create instance
          </Link>
        }
      />
    )
  }

  return (
    <Card padding="sm" className="overflow-hidden p-0">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-text-secondary text-left border-b border-separator">
            <tr>
              <th className="px-5 py-3.5 font-medium">Name</th>
              <th className="px-5 py-3.5 font-medium">Backend</th>
              <th className="px-5 py-3.5 font-medium">Status</th>
              <th className="px-5 py-3.5 font-medium">Port</th>
              <th className="px-5 py-3.5 font-medium">Context</th>
              {showTokens && <th className="px-5 py-3.5 font-medium">Tokens/s</th>}
              <th className="px-5 py-3.5 font-medium">Model</th>
              <th className="px-5 py-3.5 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {instances.map((inst, i) => {
              const key = rowKey(inst)
              const tps = tpsMap.get(key)
              const loading = busyKey?.startsWith(`${key}:`) ?? false
              const err = rowError[key]
              return (
                <tr
                  key={key}
                  className={`border-b border-separator last:border-0 transition-colors duration-150 hover:bg-surface-elevated/50 ${
                    i % 2 === 1 ? 'bg-surface-elevated/20' : ''
                  }`}
                >
                  <td className="px-5 py-4 font-medium text-text-primary">
                    <div>{inst.name}</div>
                    {err && <p className="text-xs text-[var(--status-error-text)] mt-1 max-w-xs truncate">{err}</p>}
                  </td>
                  <td className="px-5 py-4 text-xs text-text-secondary capitalize">{inst.backend}</td>
                  <td className="px-5 py-4">
                    <StatusBadge status={inst.status} />
                  </td>
                  <td className="px-5 py-4 text-text-secondary">{inst.port ?? '—'}</td>
                  <td className="px-5 py-4 text-text-secondary">
                    {inst.ctx_size ? inst.ctx_size.toLocaleString() : '—'}
                  </td>
                  {showTokens && (
                    <td className="px-5 py-4 text-accent font-medium">
                      {tps != null ? (Number.isInteger(tps) ? tps : tps.toFixed(1)) : '—'}
                    </td>
                  )}
                  <td
                    className="px-5 py-4 max-w-xs truncate text-text-secondary"
                    title={inst.model}
                  >
                    {inst.model ? inst.model.split('/').pop() : '—'}
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex justify-end gap-0.5">
                      {inst.status !== 'running' && (
                        <ActionBtn
                          icon={Play}
                          label="Start"
                          disabled={loading}
                          onClick={() => act(inst, 'start')}
                        />
                      )}
                      {inst.status === 'running' && (
                        <>
                          <ActionBtn icon={Square} label="Stop" disabled={loading} onClick={() => act(inst, 'stop')} />
                          <ActionBtn
                            icon={RotateCcw}
                            label="Restart"
                            disabled={loading}
                            onClick={() => act(inst, 'restart')}
                          />
                        </>
                      )}
                      {showDelete && (
                        <ActionBtn icon={Trash2} label="Delete" disabled={loading} onClick={() => del(inst)} />
                      )}
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

function ActionBtn({
  icon: Icon,
  label,
  onClick,
  disabled,
}: {
  icon: typeof Play
  label: string
  onClick: () => void
  disabled?: boolean
}) {
  return (
    <button
      type="button"
      title={label}
      disabled={disabled}
      onClick={onClick}
      className="rounded-full p-2 text-text-secondary transition-colors duration-200 hover:bg-surface-elevated hover:text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 disabled:opacity-40"
    >
      <Icon size={15} strokeWidth={1.75} />
    </button>
  )
}
