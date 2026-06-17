import type {
  Backend,
  CredentialsUpdate,
  DashboardSettings,
  DashboardSettingsUpdate,
  DownloadJob,
  DownloadJobsResponse,
  GgufFile,
  GpuStats,
  InstanceThroughput,
  KvOptions,
  ModelLibraryResponse,
  SettingsModulesResponse,
  SettingsSaveResponse,
  SetupStatusResponse,
  UnifiedInstance,
  WizardHardware,
  WizardRuntimesResponse,
} from './types'

const json = async <T>(res: Response): Promise<T> => {
  const text = await res.text()
  if (!res.ok) {
    throw new Error(text || res.statusText)
  }
  try {
    return JSON.parse(text) as T
  } catch {
    if (text.trimStart().startsWith('<!')) {
      throw new Error(
        'Server returned HTML instead of JSON. Restart the dashboard: sudo systemctl restart llama-dashboard',
      )
    }
    throw new Error('Invalid JSON response from server')
  }
}

export const api = {
  health: () => fetch('/api/health').then(json),
  instances: () => fetch('/api/instances').then(json<UnifiedInstance[]>),
  gpus: () => fetch('/api/metrics/gpus').then(json<GpuStats[]>),
  wizardHardware: () => fetch('/api/wizard/hardware').then(json<WizardHardware[]>),
  wizardRuntimesCatalog: () =>
    fetch('/api/wizard/runtimes?catalog=true').then(json<WizardRuntimesResponse>),
  wizardRuntimes: (vendor: string, multiGpu: boolean) =>
    fetch(`/api/wizard/runtimes?vendor=${vendor}&multi_gpu=${multiGpu}&catalog=false`).then(
      json<WizardRuntimesResponse>,
    ),
  wizardKvOptions: (backend: Backend, runtimeId?: string) =>
    fetch(
      `/api/wizard/kv-options?backend=${backend}${runtimeId ? `&runtime_id=${encodeURIComponent(runtimeId)}` : ''}`,
    ).then(json<KvOptions>),
  wizardSuggestPort: (backend: Backend) =>
    fetch(`/api/wizard/suggest-port?backend=${backend}`).then(json<{ port: number }>),
  wizardGgufFiles: (q: string) =>
    fetch(`/api/wizard/gguf-files?q=${encodeURIComponent(q)}`).then(json<GgufFile[]>),
  wizardCreate: (payload: Record<string, unknown>) =>
    fetch('/api/wizard/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(json),
  throughput: () => fetch('/api/metrics/throughput').then(json<InstanceThroughput[]>),

  nvidiaStart: (name: string) =>
    fetch(`/api/nvidia/instances/${name}/start`, { method: 'POST' }).then(json),
  nvidiaStop: (name: string) =>
    fetch(`/api/nvidia/instances/${name}/stop`, { method: 'POST' }).then(json),
  nvidiaRestart: (name: string) =>
    fetch(`/api/nvidia/instances/${name}/restart`, { method: 'POST' }).then(json),
  nvidiaCreate: (name: string, options: Record<string, unknown>) =>
    fetch(`/api/nvidia/instances/${name}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(options),
    }).then(json),
  nvidiaDelete: (name: string) =>
    fetch(`/api/nvidia/instances/${name}`, { method: 'DELETE' }).then(json),
  nvidiaDownload: (repo: string, tag: string) =>
    fetch('/api/nvidia/models/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo, tag, format: 'gguf' }),
    }).then(json<{ job_id: string }>),
  nvidiaDownloadJob: (jobId: string) =>
    fetch(`/api/nvidia/models/jobs/${jobId}`).then(json<DownloadJob>),

  modelLibrary: (q = '', limit = 100, offset = 0) =>
    fetch(
      `/api/models/library?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`,
    ).then(json<ModelLibraryResponse>),
  modelDownloads: () => fetch('/api/models/downloads').then(json<DownloadJobsResponse>),
  modelStartDownload: (repo: string, tag: string) =>
    fetch('/api/models/downloads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo, tag, format: 'gguf' }),
    }).then(json<{ job_id: string }>),
  modelCancelDownload: (jobId: string) =>
    fetch(`/api/models/downloads/${jobId}`, { method: 'DELETE' }).then(json),

  settingsGet: () => fetch('/api/settings').then(json<DashboardSettings>),
  settingsModules: () => fetch('/api/settings/modules').then(json<SettingsModulesResponse>),
  setupStatus: () => fetch('/api/setup/status').then(json<SetupStatusResponse>),
  settingsUpdate: (payload: DashboardSettingsUpdate) =>
    fetch('/api/settings', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(json<SettingsSaveResponse>),
  settingsExport: () => fetch('/api/settings/export').then(json),
  settingsImport: (payload: { settings?: Record<string, unknown>; credentials?: Record<string, string>; confirm_overwrite: boolean }) =>
    fetch('/api/settings/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(json),
  credentialsUpdate: (payload: CredentialsUpdate) =>
    fetch('/api/settings/credentials', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(json),

  intelStart: (name: string) =>
    fetch(`/api/intel/instances/${name}/start`, { method: 'POST' }).then(json),
  intelStop: (name: string) =>
    fetch(`/api/intel/instances/${name}/stop`, { method: 'POST' }).then(json),
  intelRestart: (name: string) =>
    fetch(`/api/intel/instances/${name}/restart`, { method: 'POST' }).then(json),
  intelDelete: (name: string) =>
    fetch(`/api/intel/instances/${name}`, { method: 'DELETE' }).then(json),
  intelCreate: (payload: Record<string, unknown>) =>
    fetch('/api/intel/instances', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(json),
}
