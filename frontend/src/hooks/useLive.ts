import { useEffect, useState } from 'react'
import type { LiveSnapshot } from '../api/types'

export function useLive() {
  const [data, setData] = useState<LiveSnapshot | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const source = new EventSource('/api/live')
    source.onopen = () => setConnected(true)
    source.onerror = () => setConnected(false)
    source.addEventListener('snapshot', (ev) => {
      try {
        setData(JSON.parse(ev.data))
      } catch {
        /* ignore malformed frames */
      }
    })
    return () => source.close()
  }, [])

  return { data, connected }
}
