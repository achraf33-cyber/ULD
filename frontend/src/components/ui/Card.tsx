import type { ReactNode } from 'react'

interface Props {
  children: ReactNode
  className?: string
  padding?: 'sm' | 'md' | 'none'
  hover?: boolean
}

export function Card({ children, className = '', padding = 'md', hover = false }: Props) {
  const pad =
    padding === 'none' ? '' : padding === 'sm' ? 'p-3.5' : 'p-5'
  return (
    <div
      className={`rounded-[var(--radius-card)] bg-surface border border-[var(--border-subtle)] shadow-[var(--shadow-card)] ${pad} ${
        hover ? 'transition-shadow duration-200 hover:shadow-[var(--shadow-elevated)]' : ''
      } ${className}`}
    >
      {children}
    </div>
  )
}
