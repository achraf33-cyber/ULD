import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/client'
import { useMetricsIntervalMs } from '../../hooks/useDashboardSettings'
import { Badge, Button, Card, EmptyState } from '../ui'

interface Props {
  query: string
}

export function ModelLibrary({ query }: Props) {
  const pollMs = useMetricsIntervalMs(30_000)
  const library = useQuery({
    queryKey: ['model-library', query],
    queryFn: () => api.modelLibrary(query, 200, 0),
    refetchInterval: pollMs,
    retry: 2,
  })

  const settings = useQuery({
    queryKey: ['settings'],
    queryFn: api.settingsGet,
    staleTime: 60_000,
  })

  if (library.isLoading) {
    return <EmptyState message="Scanning model directories…" className="py-4" />
  }

  const items = library.data?.items ?? []
  const configured =
    library.data?.configured_dirs || settings.data?.effective_library_dirs || ''
  const roots = library.data?.roots ?? settings.data?.library_roots ?? []

  return (
    <div className="space-y-4">
      <LibraryRootsPanel configured={configured} roots={roots} />

      {library.isError && (
        <Card className="space-y-3 max-w-xl">
          <p className="text-sm text-[var(--status-error-text)]">
            {library.error instanceof Error ? library.error.message : 'Failed to load library'}
          </p>
          <p className="text-sm text-text-secondary">
            The Models API may be unavailable until the backend is restarted.
          </p>
          <Button onClick={() => library.refetch()}>Retry scan</Button>
        </Card>
      )}

      {!library.isError && !items.length ? (
        <EmptyState
          message="No GGUF files found in the configured folders."
          className="py-4"
          action={
            <Link to="/settings?module=library" className="text-sm text-accent hover:underline">
              Configuration → Model library
            </Link>
          }
        />
      ) : !library.isError ? (
        <Card padding="sm" className="overflow-hidden p-0">
          <p className="px-5 py-3 text-xs text-text-tertiary border-b border-separator">
            {library.data?.total ?? items.length} model{library.data?.total === 1 ? '' : 's'} on disk
          </p>
          <div className="overflow-x-auto max-h-[32rem] overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="text-text-secondary text-left border-b border-separator sticky top-0 bg-surface">
                <tr>
                  <th className="px-5 py-3 font-medium">Name</th>
                  <th className="px-5 py-3 font-medium">Size</th>
                  <th className="px-5 py-3 font-medium">Path</th>
                </tr>
              </thead>
              <tbody>
                {items.map((m) => (
                  <tr
                    key={m.path}
                    className="border-b border-separator last:border-0 hover:bg-surface-elevated/50"
                  >
                    <td className="px-5 py-3 font-medium text-text-primary">{m.name}</td>
                    <td className="px-5 py-3 text-text-secondary whitespace-nowrap">
                      {m.size_mb != null ? `${m.size_mb} MB` : '—'}
                    </td>
                    <td
                      className="px-5 py-3 text-text-tertiary font-mono text-xs truncate max-w-md"
                      title={m.path}
                    >
                      {m.path}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : null}
    </div>
  )
}

function LibraryRootsPanel({
  configured,
  roots,
}: {
  configured: string
  roots: { path: string; exists: boolean; gguf_count: number }[]
}) {
  return (
    <Card padding="sm" className="space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-medium text-text-primary">Scan folders</h3>
          <p className="text-xs text-text-tertiary mt-1">
            Colon-separated paths on the server.             Edit in{' '}
            <Link to="/settings?module=library" className="text-accent hover:underline">
              Configuration → Model library
            </Link>
            .
          </p>
        </div>
      </div>
      {configured ? (
        <p className="text-xs font-mono text-text-secondary break-all">{configured}</p>
      ) : (
        <p className="text-xs text-[var(--status-warning-text)]">
          No library folders configured — set paths in Configuration.
        </p>
      )}
      {roots.length > 0 && (
        <ul className="space-y-2">
          {roots.map((r) => (
            <li key={r.path} className="flex items-center justify-between gap-3 text-xs">
              <span className="font-mono text-text-secondary truncate" title={r.path}>
                {r.path}
              </span>
              <span className="flex items-center gap-2 shrink-0">
                <Badge variant={r.exists ? 'success' : 'error'}>
                  {r.exists ? 'found' : 'missing'}
                </Badge>
                {r.exists && (
                  <span className="text-text-tertiary">{r.gguf_count} gguf</span>
                )}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}
