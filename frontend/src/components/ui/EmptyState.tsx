import type { ReactNode } from 'react'
import { Inbox } from 'lucide-react'

interface Props {
  message: string
  className?: string
  action?: ReactNode
}

export function EmptyState({ message, className = '', action }: Props) {
  return (
    <div
      className={`flex flex-col items-center justify-center text-center py-12 px-6 ${className}`}
    >
      <div className="w-12 h-12 rounded-full bg-surface-elevated border border-separator flex items-center justify-center mb-4">
        <Inbox size={22} className="text-text-tertiary" strokeWidth={1.5} />
      </div>
      <p className="text-sm text-text-secondary max-w-sm leading-relaxed">{message}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
