import { useEffect, useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Backend } from '../api/types'
import { Card, PageHeader, Select } from '../components/ui'

export function LogsPage() {
  const { data: instances } = useQuery({ queryKey: ['instances'], queryFn: api.instances })
  const [backend, setBackend] = useState<Backend>('nvidia')
  const [name, setName] = useState('')

  const filtered = useMemo(
    () => (instances ?? []).filter((i) => i.backend === backend),
    [instances, backend],
  )

  const activeName = useMemo(() => {
    if (name && filtered.some((i) => i.name === name)) return name
    return filtered[0]?.name ?? ''
  }, [name, filtered])

  const handleBackend = (value: Backend) => {
    setBackend(value)
    setName('')
  }

  return (
    <div className="space-y-6 h-[calc(100vh-5rem)] flex flex-col">
      <PageHeader title="Live Logs" description="Streaming instance output" />

      <div className="flex gap-3">
        <Select
          label="Backend"
          value={backend}
          onChange={(v) => handleBackend(v as Backend)}
          options={[
            { value: 'nvidia', label: 'NVIDIA' },
            { value: 'intel', label: 'Intel B70' },
          ]}
          className="w-44"
        />
        <Select
          label="Instance"
          value={activeName}
          onChange={setName}
          options={filtered.map((i) => i.name)}
          className="flex-1"
        />
      </div>

      <Card padding="sm" className="flex-1 overflow-hidden p-0">
        {activeName ? (
          <LogStream key={`${backend}-${activeName}`} backend={backend} name={activeName} />
        ) : (
          <pre
            className="h-full overflow-auto p-5 text-xs font-mono text-text-secondary leading-relaxed"
            style={{ backgroundColor: 'var(--terminal-bg)' }}
          >
            No instances available for this backend.
          </pre>
        )}
      </Card>
    </div>
  )
}

function LogStream({ backend, name }: { backend: Backend; name: string }) {
  const [lines, setLines] = useState<string[]>([])
  const bottom = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const source = new EventSource(`/api/logs/${backend}/${name}/stream?tail=200`)
    source.addEventListener('log', (ev) => {
      setLines((prev) => [...prev.slice(-500), ev.data])
    })
    return () => source.close()
  }, [backend, name])

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth' })
  }, [lines])

  return (
    <pre
      className="h-full overflow-auto p-5 text-xs font-mono text-text-secondary leading-relaxed"
      style={{ backgroundColor: 'var(--terminal-bg)' }}
    >
      {lines.length ? lines.join('\n') : 'Waiting for logs…'}
      <div ref={bottom} />
    </pre>
  )
}
