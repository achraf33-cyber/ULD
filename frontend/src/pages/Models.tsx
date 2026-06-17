import { useState } from 'react'
import { DownloadManager } from '../components/models/DownloadManager'
import { ModelLibrary } from '../components/models/ModelLibrary'
import { Input, PageHeader, SegmentedControl } from '../components/ui'

const TABS = [
  { value: 'library', label: 'Local library' },
  { value: 'downloads', label: 'Downloads' },
]

export function ModelsPage() {
  const [tab, setTab] = useState('library')
  const [query, setQuery] = useState('')

  return (
    <div className="space-y-8">
      <PageHeader
        title="Models"
        description="Browse local GGUF files and manage HuggingFace downloads"
      />

      <SegmentedControl options={TABS} value={tab} onChange={setTab} />

      {tab === 'library' ? (
        <div className="space-y-4">
          <Input
            label="Search models"
            value={query}
            onChange={setQuery}
            placeholder="Filter by name or path…"
          />
          <ModelLibrary query={query} />
        </div>
      ) : (
        <DownloadManager />
      )}
    </div>
  )
}
