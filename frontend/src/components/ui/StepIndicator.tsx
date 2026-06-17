interface Props {
  steps: string[]
  current: number
}

export function StepIndicator({ steps, current }: Props) {
  return (
    <div className="flex items-center gap-0">
      {steps.map((label, i) => (
        <div key={label} className="flex items-center flex-1 last:flex-none">
          <div className="flex flex-col items-center gap-1.5">
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-colors duration-200 ${
                i < current
                  ? 'bg-accent text-white'
                  : i === current
                    ? 'bg-accent text-white ring-4 ring-accent/20'
                    : 'bg-surface-elevated text-text-tertiary'
              }`}
            >
              {i < current ? '✓' : i + 1}
            </div>
            <span
              className={`text-xs hidden sm:block ${
                i <= current ? 'text-text-primary font-medium' : 'text-text-tertiary'
              }`}
            >
              {label}
            </span>
          </div>
          {i < steps.length - 1 && (
            <div
              className={`h-0.5 flex-1 mx-2 mb-5 sm:mb-0 transition-colors duration-200 ${
                i < current ? 'bg-accent' : 'bg-separator'
              }`}
            />
          )}
        </div>
      ))}
    </div>
  )
}
