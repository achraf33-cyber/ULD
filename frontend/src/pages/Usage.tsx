import {
  CartesianGrid,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Link } from 'react-router-dom'
import { Card, EmptyState, PageHeader } from '../components/ui'
import { useElementSize } from '../hooks/useElementSize'
import { useLive } from '../hooks/useLive'
import { chartTheme, useTheme } from '../theme'

export function UsagePage() {
  const { data, connected } = useLive()
  const { resolvedTheme } = useTheme()
  const running = (data?.instances ?? []).filter((i) => i.status === 'running')
  const throughputByKey = new Map(
    (data?.throughput ?? []).map((m) => [`${m.backend}:${m.name}`, m]),
  )
  const metrics = running.map(
    (inst) =>
      throughputByKey.get(`${inst.backend}:${inst.name}`) ?? {
        name: inst.name,
        backend: inst.backend,
        port: inst.port ?? 0,
        healthy: false,
      },
  )
  const hasTokenMetrics = metrics.some(
    (m) => m.tokens_per_second != null || m.prompt_tokens_per_second != null,
  )
  const colors = chartTheme()

  return (
    <div className="space-y-10">
      <PageHeader
        title="Usage"
        description="Live inference metrics from running instances"
        connected={connected}
        connectedLabel="Live SSE"
      />

      {!metrics.length ? (
        <EmptyState
          message="No running instances. Start an instance to see live usage."
          action={
            <Link
              to="/create"
              className="inline-flex items-center rounded-[var(--radius-control)] px-4 py-2.5 text-sm font-medium bg-surface border border-separator text-text-primary hover:bg-surface-elevated"
            >
              Create instance
            </Link>
          }
        />
      ) : (
        <>
          {!hasTokenMetrics && (
            <p className="text-sm text-text-secondary rounded-[var(--radius-control)] bg-surface-elevated px-4 py-3">
              Token rates appear after a few seconds of activity. For Prometheus metrics, start
              llama-server with <span className="font-mono">--metrics</span>.
            </p>
          )}
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {metrics.map((m) => (
              <Card key={`${m.backend}-${m.name}`}>
                <h3 className="font-medium mb-0.5 text-text-primary">{m.name}</h3>
                <p className="text-xs text-text-tertiary mb-4 capitalize">
                  {m.backend} · port {m.port}
                </p>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <Metric label="Tokens/s" value={fmt(m.tokens_per_second)} />
                  <Metric label="Prompt tok/s" value={fmt(m.prompt_tokens_per_second)} />
                  <Metric label="KV cache" value={`${fmt(m.kv_cache_used_percent)}%`} />
                  <Metric
                    label="Active slots"
                    value={`${m.active_slots ?? 0}/${m.total_slots ?? '?'}`}
                  />
                </div>
              </Card>
            ))}
          </div>

          <div className="space-y-4">
            {metrics.map((m) => {
              const key = `${m.backend}:${m.name}`
              const history = data?.throughput_history?.[key] ?? []
              const chartData = history.filter(
                (sample) =>
                  sample.tokens_per_second != null || sample.prompt_tokens_per_second != null,
              ).map((sample, i) => ({
                i,
                tps: sample.tokens_per_second ?? sample.prompt_tokens_per_second ?? 0,
              }))
              if (!chartData.length) return null
              return (
                <ThroughputHistoryChart
                  key={`${key}-${resolvedTheme}`}
                  title={`${m.name} — tokens/s history`}
                  chartData={chartData}
                  colors={colors}
                />
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}

function ThroughputHistoryChart({
  title,
  chartData,
  colors,
}: {
  title: string
  chartData: { i: number; tps: number }[]
  colors: ReturnType<typeof chartTheme>
}) {
  const { ref, width, height } = useElementSize<HTMLDivElement>()
  const ready = width > 0 && height > 0

  return (
    <Card className="flex flex-col">
      <h3 className="text-sm text-text-secondary mb-4 shrink-0">{title}</h3>
      <div ref={ref} className="h-40 w-full">
        {ready ? (
          <LineChart width={width} height={height} data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
            <XAxis dataKey="i" hide />
            <YAxis tick={{ fill: colors.tick, fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                background: colors.tooltipBg,
                border: `1px solid ${colors.tooltipBorder}`,
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Line type="monotone" dataKey="tps" stroke={colors.line} dot={false} />
          </LineChart>
        ) : null}
      </div>
    </Card>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-text-tertiary text-xs mb-0.5">{label}</p>
      <p className="text-text-primary font-medium">{value}</p>
    </div>
  )
}

function fmt(n?: number) {
  if (n == null) return '—'
  return Number.isInteger(n) ? String(n) : n.toFixed(1)
}
