import { GpuCards } from '../components/GpuCards'
import { InstanceTable } from '../components/InstanceTable'
import { PageHeader, Section } from '../components/ui'
import { useDashboardBaseUrl } from '../hooks/useDashboardSettings'
import { useLive } from '../hooks/useLive'

export function OverviewPage() {
  const { data, connected } = useLive()
  const baseUrl = useDashboardBaseUrl()

  return (
    <div className="space-y-10">
      <PageHeader
        title="Overview"
        description={
          baseUrl
            ? `Live fleet status · Dashboard at ${baseUrl}`
            : 'Live fleet status across NVIDIA and Intel'
        }
        connected={connected}
      />

      <Section title="GPUs">
        <GpuCards gpus={data?.gpus ?? []} />
      </Section>

      <Section title={`Instances (${data?.instances.length ?? 0})`}>
        <InstanceTable
          instances={data?.instances ?? []}
          throughput={data?.throughput}
          showTokens
        />
      </Section>
    </div>
  )
}
