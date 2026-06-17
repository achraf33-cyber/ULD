interface Option {
  value: string
  label: string
  disabled?: boolean
}

interface Props {
  options: Option[]
  value: string
  onChange: (value: string) => void
  className?: string
}

export function SegmentedControl({ options, value, onChange, className = '' }: Props) {
  return (
    <div
      className={`inline-flex rounded-[var(--radius-control)] bg-surface-elevated/80 border border-separator p-0.5 gap-0.5 ${className}`}
      role="tablist"
    >
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          role="tab"
          aria-selected={value === opt.value}
          disabled={opt.disabled}
          onClick={() => onChange(opt.value)}
          className={`flex-1 rounded-[calc(var(--radius-control)-2px)] px-3 py-1.5 text-xs font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 disabled:opacity-40 disabled:cursor-not-allowed ${
            value === opt.value
              ? 'bg-surface text-text-primary shadow-sm'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}
