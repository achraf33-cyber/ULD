import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  children: ReactNode
}

const styles: Record<Variant, string> = {
  primary:
    'bg-accent text-white shadow-sm hover:bg-accent-hover active:scale-[0.98] disabled:opacity-50',
  secondary:
    'bg-surface border border-separator text-text-primary hover:bg-surface-elevated active:scale-[0.98]',
  ghost:
    'text-text-secondary hover:bg-surface-elevated hover:text-text-primary active:scale-[0.98]',
}

export function Button({ variant = 'primary', className = '', children, ...props }: Props) {
  return (
    <button
      type="button"
      className={`inline-flex items-center justify-center rounded-[var(--radius-control)] px-4 py-2.5 text-sm font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 focus-visible:ring-offset-2 focus-visible:ring-offset-bg disabled:cursor-not-allowed disabled:active:scale-100 ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
