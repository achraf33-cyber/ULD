import type { InputHTMLAttributes } from 'react'

interface Props extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  label: string
  value: string
  onChange: (v: string) => void
}

export function Input({ label, value, onChange, className = '', ...props }: Props) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-text-secondary">{label}</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`mt-1.5 w-full rounded-[var(--radius-control)] bg-surface-elevated border border-separator px-3 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary transition-all duration-200 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 focus:bg-surface ${className}`}
        {...props}
      />
    </label>
  )
}
