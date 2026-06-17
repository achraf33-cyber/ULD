import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { InstancesPage } from './pages/Instances'
import { LogsPage } from './pages/Logs'
import { ModelsPage } from './pages/Models'
import { OverviewPage } from './pages/Overview'
import { SettingsPage } from './pages/Settings'
import { UsagePage } from './pages/Usage'
import { WizardPage } from './pages/Wizard'

const client = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={client}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<OverviewPage />} />
            <Route path="instances" element={<InstancesPage />} />
            <Route path="usage" element={<UsagePage />} />
            <Route path="logs" element={<LogsPage />} />
            <Route path="models" element={<ModelsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="create" element={<WizardPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
