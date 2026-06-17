interface Option {
  value: string
  label: string
  disabled?: boolean
}

interface Props {
  label: string
  value: string
  onChange: (v: string) => void
  options: string[] | Option[]
  className?: string
}

function normalize(options: string[] | Option[]): Option[] {
  return options.map((o) => (typeof o === 'string' ? { value: o, label: o } : o))
}

export function Select({ label, value, onChange, options, className = '' }: Props) {
  const items = normalize(options)
  const hideLabel = !label

  return (
    <label className={`block ${className}`}>
      <span className={hideLabel ? 'sr-only' : 'text-sm text-text-secondary'}>{label || 'Select'}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`${hideLabel ? '' : 'mt-1.5'} w-full rounded-[var(--radius-control)] bg-surface-elevated border border-separator px-3 py-2.5 text-sm text-text-primary transition-colors duration-200 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20`}
      >
        {items.map((o) => (
          <option key={o.value || 'default'} value={o.value} disabled={o.disabled}>
            {o.label || 'default'}
          </option>
        ))}
      </select>
    </label>
  )
}
