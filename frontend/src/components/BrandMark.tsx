interface Props {
  size?: number
  className?: string
}

export function BrandMark({ size = 36, className = '' }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      aria-hidden
    >
      <rect width="32" height="32" rx="8" fill="url(#uld-brand)" />
      <path
        fill="#fff"
        d="M9 10h4.2c3.4 0 5.6 2 5.6 5.1 0 3-2.2 5.1-5.6 5.1H12.4V22H9V10zm3.4 7.5c1.6 0 2.5-.9 2.5-2.4s-.9-2.4-2.5-2.4h-1v4.8h1zM18.2 10h3.3l4.5 12h-3.4l-.8-2.2h-4.5l-.8 2.2h-3.3l4.5-12zm2.2 7.3-1.4-3.8-1.4 3.8h2.8z"
      />
      <defs>
        <linearGradient id="uld-brand" x1="4" y1="4" x2="28" y2="28">
          <stop stopColor="var(--accent)" />
          <stop offset="1" stopColor="var(--accent-hover)" />
        </linearGradient>
      </defs>
    </svg>
  )
}
