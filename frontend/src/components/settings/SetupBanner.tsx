import { CheckCircle2, Circle, CircleAlert } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { ConfigModuleSummary } from '../../api/types'
import { Card } from '../ui'

interface Props {
  modules: ConfigModuleSummary[]
  onSelect?: (id: string) => void
  compact?: boolean
}

export function SetupBanner({ modules, onSelect, compact = false }: Props) {
  const incomplete = modules.filter((m) => !m.complete)
  if (!incomplete.length) return null

  return (
    <Card
      className={`space-y-3 border-[var(--status-warning-text)]/20 bg-[var(--status-warning-bg)]/30 ${
        compact ? 'p-3' : 'space-y-4'
      }`}
    >
      <div>
        <h3 className={`font-semibold text-text-primary ${compact ? 'text-xs' : 'text-sm'}`}>
          {compact ? 'Setup incomplete' : 'Finish setup'}
        </h3>
        {!compact && (
          <p className="text-sm text-text-secondary mt-1">
            Complete these modules so Models, Usage, and Create work correctly.
          </p>
        )}
      </div>
      <ul className="space-y-1">
        {incomplete.map((m) => (
          <li key={m.id}>
            {onSelect ? (
              <button
                type="button"
                onClick={() => onSelect(m.id)}
                className="flex items-center gap-2 text-sm text-left w-full rounded-[var(--radius-control)] px-2 py-1.5 hover:bg-surface-elevated/80 transition-colors"
              >
                <CircleAlert size={compact ? 14 : 16} className="text-[var(--status-warning-text)] shrink-0" />
                <span className="text-text-primary font-medium truncate">{m.title}</span>
                {!compact && <span className="text-text-tertiary ml-auto text-xs">Configure →</span>}
              </button>
            ) : (
              <Link
                to={`/settings?module=${encodeURIComponent(m.id)}`}
                className="flex items-center gap-2 text-xs text-left w-full rounded-[var(--radius-control)] px-2 py-1.5 hover:bg-surface-elevated/80 transition-colors"
              >
                <CircleAlert size={14} className="text-[var(--status-warning-text)] shrink-0" />
                <span className="text-text-primary font-medium truncate">{m.title}</span>
              </Link>
            )}
          </li>
        ))}
      </ul>
    </Card>
  )
}

export function ModuleNav({
  modules,
  active,
  onSelect,
  credentials,
}: {
  modules: ConfigModuleSummary[]
  active: string
  onSelect: (id: string) => void
  credentials?: ConfigModuleSummary
}) {
  return (
    <nav className="space-y-0.5">
      {modules.map((m) => (
        <button
          key={m.id}
          type="button"
          onClick={() => onSelect(m.id)}
          className={`w-full flex items-center gap-2.5 rounded-[var(--radius-control)] px-3 py-2.5 text-left text-sm transition-colors ${
            active === m.id
              ? 'bg-[var(--nav-active-bg)] text-accent font-medium'
              : 'text-text-secondary hover:bg-surface-elevated hover:text-text-primary'
          }`}
        >
          {m.complete ? (
            <CheckCircle2 size={16} className="text-[var(--status-running-text)] shrink-0" />
          ) : (
            <Circle size={16} className="text-text-tertiary shrink-0" />
          )}
          <span className="truncate">{m.title}</span>
        </button>
      ))}
      {credentials && (
        <button
          type="button"
          onClick={() => onSelect('credentials')}
          className={`w-full flex items-center gap-2.5 rounded-[var(--radius-control)] px-3 py-2.5 text-left text-sm transition-colors mt-2 border-t border-separator pt-3 ${
            active === 'credentials'
              ? 'bg-[var(--nav-active-bg)] text-accent font-medium'
              : 'text-text-secondary hover:bg-surface-elevated hover:text-text-primary'
          }`}
        >
          {credentials.complete ? (
            <CheckCircle2 size={16} className="text-[var(--status-running-text)] shrink-0" />
          ) : (
            <Circle size={16} className="text-text-tertiary shrink-0" />
          )}
          <span className="truncate">{credentials.title}</span>
        </button>
      )}
    </nav>
  )
}
