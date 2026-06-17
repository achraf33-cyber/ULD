import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

/** Base URL for links to this dashboard (uses configured LAN IP when set). */
export function useDashboardBaseUrl() {
  const { data } = useQuery({
    queryKey: ['settings'],
    queryFn: api.settingsGet,
    staleTime: 60_000,
  })
  if (typeof window === 'undefined') return ''
  if (data?.lan_ip?.trim()) {
    const port = data.port || window.location.port || '9000'
    return `http://${data.lan_ip.trim()}:${port}`
  }
  return window.location.origin
}

export function useMetricsIntervalMs(fallbackMs = 2000) {
  const { data } = useQuery({
    queryKey: ['settings'],
    queryFn: api.settingsGet,
    staleTime: 60_000,
  })
  const sec = data?.metrics_interval_s
  if (sec == null || sec <= 0) return fallbackMs
  return Math.max(500, Math.round(sec * 1000))
}
