import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { api } from '../../api/client'
import type { CredentialStatus } from '../../api/types'
import { Button, Card, Input } from '../ui'

export function CredentialsPanel({ credentials }: { credentials: CredentialStatus }) {
  const qc = useQueryClient()
  const [form, setForm] = useState<{ llamactl_key?: string; huggingface_token?: string }>({})
  const [message, setMessage] = useState('')

  const save = useMutation({
    mutationFn: () => api.credentialsUpdate(form),
    onSuccess: () => {
      setForm({})
      setMessage('Credentials saved securely on the server.')
      qc.invalidateQueries({ queryKey: ['settings'] })
      qc.invalidateQueries({ queryKey: ['settings-modules'] })
      qc.invalidateQueries({ queryKey: ['setup-status'] })
    },
  })

  return (
    <Card className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary">Credentials</h3>
        <p className="text-sm text-text-secondary mt-1">
          API keys never leave the server or appear in the browser after save.
        </p>
      </div>
      <Input
        label={`llamactl API key${credentials.llamactl_key_set ? ` (${credentials.llamactl_key_preview})` : ''}`}
        value={form.llamactl_key ?? ''}
        onChange={(v) => setForm((p) => ({ ...p, llamactl_key: v }))}
        type="password"
        placeholder={credentials.llamactl_key_set ? 'Enter new key to replace' : 'Required when llamactl URL is set'}
      />
      <Input
        label={`HuggingFace token${credentials.huggingface_token_set ? ` (${credentials.huggingface_token_preview})` : ''}`}
        value={form.huggingface_token ?? ''}
        onChange={(v) => setForm((p) => ({ ...p, huggingface_token: v }))}
        type="password"
        placeholder="hf_… for gated downloads"
      />
      <div className="flex items-center gap-3 flex-wrap">
        <Button onClick={() => save.mutate()} disabled={save.isPending || !Object.keys(form).length}>
          {save.isPending ? 'Saving…' : 'Save credentials'}
        </Button>
        {message && <span className="text-sm text-[var(--status-running-text)]">{message}</span>}
        {save.isError && (
          <span className="text-sm text-[var(--status-error-text)]">
            {save.error instanceof Error ? save.error.message : 'Save failed'}
          </span>
        )}
      </div>
    </Card>
  )
}
