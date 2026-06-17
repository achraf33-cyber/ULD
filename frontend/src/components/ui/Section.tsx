import type { ReactNode } from 'react'

interface Props {
  title: string
  description?: string
  children: ReactNode
}

export function Section({ title, description, children }: Props) {
  return (
    <section className="space-y-4">
      <div className="flex items-baseline justify-between gap-4">
        <div>
          <h3 className="text-[15px] font-semibold text-text-primary tracking-tight">{title}</h3>
          {description && (
            <p className="text-sm text-text-tertiary mt-0.5">{description}</p>
          )}
        </div>
      </div>
      {children}
    </section>
  )
}
