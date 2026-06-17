import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../../api/client'
import type { DashboardSettingsUpdate, SettingsSaveResponse } from '../../api/types'

export function useConfigSave(onSuccess?: (res: SettingsSaveResponse) => void) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: DashboardSettingsUpdate) => api.settingsUpdate(payload),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['settings'] })
      qc.invalidateQueries({ queryKey: ['settings-modules'] })
      qc.invalidateQueries({ queryKey: ['setup-status'] })
      qc.invalidateQueries({ queryKey: ['model-library'] })
      onSuccess?.(res)
    },
  })
}
