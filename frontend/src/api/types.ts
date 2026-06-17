export type Backend = 'nvidia' | 'intel'
export type GpuVendor = 'nvidia' | 'intel' | 'amd' | 'other'
export type GpuMemKind = 'vram' | 'gtt' | 'system' | 'unknown'
export type InstanceStatus = 'running' | 'stopped' | 'starting' | 'error' | 'unknown'

export interface GpuEngineUtil {
  name: string
  util_percent?: number
}

export interface WizardHardware {
  id: string
  vendor: string
  backend: Backend
  name: string
  pci_slot: string
  driver: string
  cuda_index?: number
  mem_used_mb?: number
  mem_total_mb?: number
  mem_free_mb?: number
  effort_percent?: number
  core_count?: number
  product_family?: string
  creatable: boolean
  note?: string
  available?: boolean
  availability_note?: string
  instances_on_gpu?: string[]
  render_node?: string
  supported_apis?: string[]
  available_compute_backends?: string[]
  compute_backend?: string
  device_id?: string
}

export interface WizardRuntime {
  id: string
  label: string
  stack: string
  vendor: string
  binary: string
  version: string
  supports_turboquant: boolean
  multi_gpu: boolean
  hint: string
  installed: boolean
  cpu_only?: boolean
  compatible_vendors?: string[]
  default?: boolean
}

export interface WizardRuntimesResponse {
  default_runtime_id: string
  runtimes: WizardRuntime[]
}

export interface KvCacheProfile {
  id: string
  label: string
  cache_type_k?: string
  cache_type_v?: string
  hint?: string
}

export interface KvOptions {
  engine_binary: string
  supports_turboquant: boolean
  profiles: KvCacheProfile[]
}

export type GpuPickMode = 'single' | 'multi'

export interface GgufFile {
  path: string
  name: string
  size_mb?: number
}

export interface DownloadJob {
  id: string
  repo: string
  tag?: string
  status: string
  progress?: {
    bytes_downloaded: number
    total_bytes: number
    current_file?: string
  }
  error?: string
}

export interface UnifiedInstance {
  name: string
  backend: Backend
  status: InstanceStatus
  port?: number
  model?: string
  ctx_size?: number
  description?: string
  options?: Record<string, unknown>
}

export interface GpuStats {
  vendor: GpuVendor
  driver: string
  index: number
  card: string
  pci_slot?: string
  render_node?: string
  name: string
  product_family?: string
  mem_kind: GpuMemKind
  util_percent?: number
  mem_util_percent?: number
  mem_used_mb?: number
  mem_total_mb?: number
  gtt_used_mb?: number
  gtt_total_mb?: number
  core_count?: number
  sm_clock_mhz?: number
  mem_clock_mhz?: number
  encoder_util_percent?: number
  decoder_util_percent?: number
  effort_percent?: number
  engines?: GpuEngineUtil[]
  temp_c?: number
  power_w?: number
  freq_mhz?: number
  capabilities?: Record<string, unknown>
}

export interface InstanceThroughput {
  name: string
  backend: Backend
  port: number
  healthy: boolean
  tokens_per_second?: number
  prompt_tokens_per_second?: number
  kv_cache_used_percent?: number
  active_slots?: number
  total_slots?: number
  requests_processing?: number
  requests_deferred?: number
}

export interface ThroughputSample {
  tokens_per_second?: number
  prompt_tokens_per_second?: number
  kv_cache_used_percent?: number
  active_slots?: number
}

export interface LiveSnapshot {
  gpus: GpuStats[]
  instances: UnifiedInstance[]
  throughput?: InstanceThroughput[]
  throughput_history?: Record<string, ThroughputSample[]>
}

export interface ModelLibraryItem {
  path: string
  name: string
  relative_path: string
  root: string
  size_mb?: number
  modified_at?: string
}

export interface LibraryRootStatus {
  path: string
  exists: boolean
  gguf_count: number
}

export interface ModelLibraryResponse {
  configured_dirs: string
  roots: LibraryRootStatus[]
  total: number
  offset: number
  limit: number
  items: ModelLibraryItem[]
}

export interface DownloadJobsResponse {
  jobs: DownloadJob[]
}

export interface CredentialStatus {
  llamactl_key_set: boolean
  llamactl_key_preview: string
  huggingface_token_set: boolean
  huggingface_token_preview: string
}

export interface DashboardSettings {
  host: string
  port: number
  static_dir: string
  lan_ip: string
  metrics_interval_s: number
  library_dirs: string
  effective_library_dirs: string
  library_roots: LibraryRootStatus[]
  model_dirs: string
  hf_home: string
  hf_hub_cache: string
  llama_cache: string
  llamactl_url: string
  llamactl_config: string
  instance_bind_host: string
  runtime_cuda_turboquant: string
  runtime_cuda_standard: string
  runtime_vulkan: string
  runtime_cpu: string
  runtime_sycl: string
  runtime_rocm: string
  intel_default_server: string
  intel_conf: string
  intel_env_dir: string
  intel_b70_cli: string
  intel_service_prefix: string
  install_complete: boolean
  database_path: string
  credentials: CredentialStatus
}

export interface DashboardSettingsUpdate {
  host?: string
  port?: number
  static_dir?: string
  lan_ip?: string
  metrics_interval_s?: number
  library_dirs?: string
  model_dirs?: string
  hf_home?: string
  hf_hub_cache?: string
  llama_cache?: string
  llamactl_url?: string
  llamactl_config?: string
  instance_bind_host?: string
  runtime_cuda_turboquant?: string
  runtime_cuda_standard?: string
  runtime_vulkan?: string
  runtime_cpu?: string
  runtime_sycl?: string
  runtime_rocm?: string
  intel_default_server?: string
  intel_conf?: string
  intel_env_dir?: string
  intel_b70_cli?: string
  intel_service_prefix?: string
  database_path?: string
  install_complete?: string
}

export interface SettingsSaveResponse {
  status: string
  settings: DashboardSettings
  restart_required?: boolean
  restart_command?: string
}

export interface CredentialsUpdate {
  llamactl_key?: string
  huggingface_token?: string
}

export interface FieldStatus {
  state: 'ok' | 'warn' | 'missing' | 'empty'
  message: string
}

export interface ConfigField {
  key: string
  label: string
  hint: string
  type: string
  required: boolean
  value: string
  status: FieldStatus | null
  restart_on_change?: boolean
}

export interface ConfigModule {
  id: string
  title: string
  description: string
  complete: boolean
  fields: ConfigField[]
}

export interface ConfigModuleSummary {
  id: string
  title: string
  complete: boolean
}

export interface SettingsModulesResponse {
  modules: ConfigModule[]
  credentials: ConfigModuleSummary
  library_roots: LibraryRootStatus[]
  database_path: string
  install_complete: boolean
}

export interface SetupStatusResponse {
  configured: boolean
  install_complete: boolean
  modules: ConfigModuleSummary[]
  missing: ConfigModuleSummary[]
}
