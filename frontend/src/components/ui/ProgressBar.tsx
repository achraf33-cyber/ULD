interface Props {
  value: number
  color?: string
  className?: string
  size?: 'sm' | 'md'
}

export function ProgressBar({ value, color = 'bg-accent', className = '', size = 'md' }: Props) {
  const h = size === 'sm' ? 'h-1.5' : 'h-2'
  const pct = Math.min(100, Math.max(0, value))
  return (
    <div
      className={`${h} rounded-full bg-surface-elevated border border-[var(--border-subtle)] overflow-hidden ${className}`}
    >
      <div
        className={`${h} rounded-full ${color} transition-all duration-500 ease-out`}
        style={{ width: `${pct}%` }}
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
      />
    </div>
  )
}
