import { useQuery } from '@tanstack/react-query'
import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { ConfigModuleSummary } from '../api/types'
import { api } from '../api/client'
import { ConfigModulePanel } from '../components/settings/ConfigModulePanel'
import { CredentialsPanel } from '../components/settings/CredentialsPanel'
import { ModuleNav, SetupBanner } from '../components/settings/SetupBanner'
import { SettingsImportExport } from '../components/settings/SettingsImportExport'
import { Button, Card, PageHeader } from '../components/ui'

export function SettingsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initial = searchParams.get('module') ?? 'general'
  const [active, setActiveState] = useState(initial)
  const [panelDirty, setPanelDirty] = useState(false)

  const modulesQuery = useQuery({
    queryKey: ['settings-modules'],
    queryFn: api.settingsModules,
  })
  const settingsQuery = useQuery({
    queryKey: ['settings'],
    queryFn: api.settingsGet,
  })
  const setupQuery = useQuery({
    queryKey: ['setup-status'],
    queryFn: api.setupStatus,
  })

  const setActive = useCallback(
    (id: string) => {
      if (panelDirty && id !== active && !confirm('You have unsaved changes. Discard them?')) {
        return
      }
      setActiveState(id)
      setSearchParams({ module: id }, { replace: true })
    },
    [active, panelDirty, setSearchParams],
  )

  useEffect(() => {
    const mod = searchParams.get('module')
    if (mod && mod !== active) setActiveState(mod)
  }, [searchParams])

  const loading = modulesQuery.isLoading || settingsQuery.isLoading

  if (loading) {
    return (
      <div className="space-y-8">
        <PageHeader title="Configuration" description="Modular setup for your deployment" />
        <p className="text-sm text-text-tertiary">Loading modules…</p>
      </div>
    )
  }

  if (modulesQuery.isError || !modulesQuery.data) {
    return (
      <div className="space-y-8">
        <PageHeader title="Configuration" description="Modular setup for your deployment" />
        <Card className="space-y-4 max-w-xl">
          <p className="text-sm text-[var(--status-error-text)]">Could not load configuration modules.</p>
          <Button onClick={() => modulesQuery.refetch()}>Retry</Button>
        </Card>
      </div>
    )
  }

  const { modules, library_roots, database_path, credentials } = modulesQuery.data
  const module = modules.find((m) => m.id === active) ?? modules[0]
  const navItems: ConfigModuleSummary[] = modules.map((m) => ({
    id: m.id,
    title: m.title,
    complete: m.complete,
  }))
  const setupModules = setupQuery.data?.modules ?? navItems

  return (
    <div className="space-y-8">
      <PageHeader
        title="Configuration"
        description="Organized by module — save each section independently. Changes apply immediately."
        actions={<SettingsImportExport />}
      />

      <SetupBanner modules={setupModules} onSelect={setActive} />

      <div className="grid gap-8 lg:grid-cols-[220px_1fr]">
        <Card padding="sm" className="h-fit space-y-1 p-2">
          <ModuleNav
            modules={navItems}
            active={active}
            onSelect={setActive}
            credentials={credentials}
          />
        </Card>

        <div className="min-w-0">
          {active === 'credentials' && settingsQuery.data ? (
            <CredentialsPanel credentials={settingsQuery.data.credentials} />
          ) : module ? (
            <ConfigModulePanel
              module={module}
              libraryRoots={library_roots}
              databasePath={database_path}
              onDirtyChange={setPanelDirty}
            />
          ) : null}
        </div>
      </div>
    </div>
  )
}
