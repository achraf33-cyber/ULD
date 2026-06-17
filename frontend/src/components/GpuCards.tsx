import { Link } from 'react-router-dom'
import type { GpuStats, GpuVendor } from '../api/types'
import { Card, EmptyState, ProgressBar } from './ui'

const VENDOR_COLOR: Record<GpuVendor, string> = {
  nvidia: 'bg-green-500',
  intel: 'bg-blue-500',
  amd: 'bg-red-500',
  other: 'bg-text-tertiary',
}

const VENDOR_TEXT: Record<GpuVendor, string> = {
  nvidia: 'text-green-600 dark:text-green-400',
  intel: 'text-blue-600 dark:text-blue-400',
  amd: 'text-red-600 dark:text-red-400',
  other: 'text-text-tertiary',
}

function bar(used?: number, total?: number) {
  if (!used || !total) return 0
  return Math.min(100, Math.round((used / total) * 100))
}

function memLabel(kind: string) {
  if (kind === 'system') return 'Shared memory'
  if (kind === 'gtt') return 'GTT'
  return 'VRAM'
}

export function GpuCards({ gpus }: { gpus: GpuStats[] }) {
  if (!gpus.length) {
    return (
      <EmptyState
        message="No GPU telemetry available."
        className="py-4"
        action={
          <Link
            to="/settings?module=nvidia"
            className="text-sm text-accent hover:underline"
          >
            Configure NVIDIA / llamactl →
          </Link>
        }
      />
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {gpus.map((gpu) => (
        <Card key={`${gpu.vendor}-${gpu.card}-${gpu.index}`}>
          <div className="flex items-center justify-between mb-3">
            <span className={`text-xs font-medium capitalize ${VENDOR_TEXT[gpu.vendor]}`}>
              {gpu.vendor}
            </span>
            <span className="text-xs text-text-tertiary">{gpu.driver}</span>
          </div>
          <h3 className="font-medium text-sm mb-0.5 truncate text-text-primary" title={gpu.name}>
            {gpu.name}
          </h3>
          {gpu.product_family && (
            <p className="text-xs text-text-tertiary mb-3">{gpu.product_family}</p>
          )}

          {gpu.effort_percent != null && (
            <div className="mb-4">
              <div className="flex justify-between text-xs text-text-secondary mb-1.5">
                <span>Effort</span>
                <span className="text-text-primary font-medium">{gpu.effort_percent}%</span>
              </div>
              <ProgressBar value={gpu.effort_percent} color={VENDOR_COLOR[gpu.vendor]} />
            </div>
          )}

          <div className="space-y-2 text-sm">
            {gpu.core_count != null && (
              <Row label="CUDA cores" value={gpu.core_count.toLocaleString()} />
            )}
            <Row label="GPU util" value={pct(gpu.util_percent)} />
            <Row label="Mem util" value={pct(gpu.mem_util_percent)} />
            {gpu.mem_total_mb ? (
              <>
                <Row
                  label={memLabel(gpu.mem_kind)}
                  value={`${Math.round(gpu.mem_used_mb ?? 0)} / ${Math.round(gpu.mem_total_mb)} MB`}
                />
                <ProgressBar
                  value={bar(gpu.mem_used_mb, gpu.mem_total_mb)}
                  color={VENDOR_COLOR[gpu.vendor]}
                  size="sm"
                />
              </>
            ) : null}
            {gpu.gtt_total_mb ? (
              <Row
                label="GTT"
                value={`${Math.round(gpu.gtt_used_mb ?? 0)} / ${Math.round(gpu.gtt_total_mb)} MB`}
              />
            ) : null}
            {(gpu.sm_clock_mhz != null || gpu.mem_clock_mhz != null) && (
              <Row
                label="Clocks"
                value={`SM ${gpu.sm_clock_mhz ?? '—'} / Mem ${gpu.mem_clock_mhz ?? '—'} MHz`}
              />
            )}
            {gpu.encoder_util_percent != null && (
              <Row label="Encoder" value={pct(gpu.encoder_util_percent)} />
            )}
            {gpu.decoder_util_percent != null && (
              <Row label="Decoder" value={pct(gpu.decoder_util_percent)} />
            )}
            {gpu.engines && gpu.engines.length > 0 && (
              <div className="pt-2 border-t border-separator">
                <p className="text-xs text-text-tertiary mb-1.5">Engines</p>
                {gpu.engines.map((e) => (
                  <Row key={e.name} label={e.name} value={pct(e.util_percent)} />
                ))}
              </div>
            )}
            <Row label="Temp" value={gpu.temp_c != null ? `${gpu.temp_c}°C` : '—'} />
            <Row label="Power" value={gpu.power_w != null ? `${gpu.power_w} W` : '—'} />
            {gpu.pci_slot && <Row label="PCI" value={gpu.pci_slot} mono />}
          </div>
        </Card>
      ))}
    </div>
  )
}

function pct(n?: number) {
  return n != null ? `${n}%` : '—'
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex justify-between text-text-secondary gap-2">
      <span>{label}</span>
      <span
        className={`text-text-primary truncate ${mono ? 'font-mono text-xs' : ''}`}
        title={value}
      >
        {value}
      </span>
    </div>
  )
}
