import { useQuery } from '@tanstack/react-query'
import { InstanceTable } from '../components/InstanceTable'
import { EmptyState, PageHeader } from '../components/ui'
import { api } from '../api/client'
import { useMetricsIntervalMs } from '../hooks/useDashboardSettings'

export function InstancesPage() {
  const pollMs = useMetricsIntervalMs(3000)
  const { data, refetch, isLoading } = useQuery({
    queryKey: ['instances'],
    queryFn: api.instances,
    refetchInterval: pollMs,
  })

  return (
    <div className="space-y-8">
      <PageHeader title="Instances" description="Manage all llama.cpp instances" />
      {isLoading ? (
        <EmptyState message="Loading…" />
      ) : (
        <InstanceTable instances={data ?? []} showDelete onAction={() => refetch()} />
      )}
    </div>
  )
}
