type Variant = 'default' | 'success' | 'warning' | 'error' | 'neutral' | 'accent'

interface Props {
  children: React.ReactNode
  variant?: Variant
  pulse?: boolean
  className?: string
}

const styles: Record<Variant, string> = {
  default: 'bg-surface-elevated text-text-secondary border border-separator',
  success: 'bg-[var(--status-running-bg)] text-[var(--status-running-text)]',
  warning: 'bg-[var(--status-warning-bg)] text-[var(--status-warning-text)]',
  error: 'bg-[var(--status-error-bg)] text-[var(--status-error-text)]',
  neutral: 'bg-[var(--status-stopped-bg)] text-[var(--status-stopped-text)]',
  accent: 'bg-accent/15 text-accent',
}

export function Badge({ children, variant = 'default', pulse = false, className = '' }: Props) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${styles[variant]} ${className}`}
    >
      {pulse && (
        <span className="live-dot w-1.5 h-1.5 rounded-full bg-current shrink-0" aria-hidden />
      )}
      {children}
    </span>
  )
}
