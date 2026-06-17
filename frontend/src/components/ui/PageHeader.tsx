import type { ReactNode } from 'react'
import { Badge } from './Badge'

interface Props {
  title: string
  description?: string
  connected?: boolean
  connectedLabel?: string
  disconnectedLabel?: string
  actions?: ReactNode
}

export function PageHeader({
  title,
  description,
  connected,
  connectedLabel = 'Live',
  disconnectedLabel = 'Disconnected',
  actions,
}: Props) {
  return (
    <header className="flex items-start justify-between gap-6 mb-2">
      <div className="min-w-0">
        <h2 className="text-[1.75rem] font-semibold tracking-tight text-text-primary leading-tight">
          {title}
        </h2>
        {description && (
          <p className="text-text-secondary text-sm mt-1.5 max-w-2xl leading-relaxed">
            {description}
          </p>
        )}
      </div>
      <div className="flex items-center gap-3 shrink-0 mt-1">
        {actions}
        {connected !== undefined && (
          <Badge variant={connected ? 'success' : 'error'} pulse={connected}>
            {connected ? connectedLabel : disconnectedLabel}
          </Badge>
        )}
      </div>
    </header>
  )
}
