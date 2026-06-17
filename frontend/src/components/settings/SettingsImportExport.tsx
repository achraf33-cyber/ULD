import { Download, Upload } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { api } from '../../api/client'
import { Button } from '../ui'

export function SettingsImportExport() {
  const qc = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)
  const [message, setMessage] = useState('')

  const exportMut = useMutation({
    mutationFn: api.settingsExport,
    onSuccess: (data) => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'uld-settings-export.json'
      a.click()
      URL.revokeObjectURL(url)
      setMessage('Export downloaded.')
    },
  })

  const importMut = useMutation({
    mutationFn: (payload: Parameters<typeof api.settingsImport>[0]) => api.settingsImport(payload),
    onSuccess: () => {
      setMessage('Settings imported.')
      qc.invalidateQueries({ queryKey: ['settings'] })
      qc.invalidateQueries({ queryKey: ['settings-modules'] })
      qc.invalidateQueries({ queryKey: ['setup-status'] })
    },
  })

  const onFile = (file: File) => {
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result))
        if (!confirm('Import will overwrite matching settings. Continue?')) return
        importMut.mutate({
          settings: parsed.settings,
          credentials: parsed.credentials,
          confirm_overwrite: true,
        })
      } catch {
        setMessage('Invalid JSON file.')
      }
    }
    reader.readAsText(file)
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <Button variant="secondary" onClick={() => exportMut.mutate()} disabled={exportMut.isPending}>
        <Download size={14} className="mr-1.5" />
        Export
      </Button>
      <Button
        variant="secondary"
        onClick={() => fileRef.current?.click()}
        disabled={importMut.isPending}
      >
        <Upload size={14} className="mr-1.5" />
        Import
      </Button>
      <input
        ref={fileRef}
        type="file"
        accept="application/json,.json"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0]
          if (f) onFile(f)
          e.target.value = ''
        }}
      />
      {message && <span className="text-xs text-text-tertiary">{message}</span>}
      {importMut.isError && (
        <span className="text-xs text-[var(--status-error-text)]">
          {importMut.error instanceof Error ? importMut.error.message : 'Import failed'}
        </span>
      )}
    </div>
  )
}
