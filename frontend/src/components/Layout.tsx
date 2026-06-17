import { useQuery } from '@tanstack/react-query'
import { NavLink, Outlet } from 'react-router-dom'
import {
  Activity,
  Box,
  Cpu,
  FileText,
  LayoutDashboard,
  Monitor,
  Moon,
  PlusCircle,
  Settings,
  Sun,
} from 'lucide-react'
import { BrandMark } from './BrandMark'
import { SetupBanner } from './settings/SetupBanner'
import { SegmentedControl } from './ui'
import { api } from '../api/client'
import { useTheme, type ThemeMode } from '../theme'

const links = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/instances', label: 'Instances', icon: Cpu },
  { to: '/models', label: 'Models', icon: Box },
  { to: '/usage', label: 'Usage', icon: Activity },
  { to: '/logs', label: 'Logs', icon: FileText },
  { to: '/create', label: 'Create', icon: PlusCircle },
  { to: '/settings', label: 'Configuration', icon: Settings },
]

const themeOptions = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'Auto' },
]

export function Layout() {
  const { theme, setTheme } = useTheme()
  const setupQuery = useQuery({
    queryKey: ['setup-status'],
    queryFn: api.setupStatus,
    refetchInterval: 30_000,
  })

  const missing = setupQuery.data?.missing ?? []
  const showSetup = setupQuery.data && !setupQuery.data.configured

  return (
    <div className="min-h-screen flex bg-bg">
      <aside
        className="w-64 shrink-0 flex flex-col border-r border-separator sticky top-0 h-screen backdrop-blur-2xl backdrop-saturate-150"
        style={{ backgroundColor: 'var(--sidebar-bg)' }}
      >
        <div className="p-5 pb-6">
          <div className="flex items-center gap-3 px-1">
            <BrandMark size={40} className="shrink-0 shadow-sm rounded-lg" />
            <div className="min-w-0">
              <h1 className="text-base font-semibold tracking-tight text-text-primary">ULD</h1>
              <p className="text-[11px] text-text-tertiary leading-tight truncate">
                Unified LlamaCPP Dashboard
              </p>
            </div>
          </div>
        </div>

        {showSetup && missing.length > 0 && (
          <div className="px-3 pb-3">
            <SetupBanner modules={missing} compact />
          </div>
        )}

        <nav className="flex-1 px-3 space-y-0.5 overflow-y-auto">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `group relative flex items-center gap-2.5 rounded-[var(--radius-control)] px-3 py-2.5 text-[13px] font-medium transition-all duration-200 ${
                  isActive
                    ? 'text-accent'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated/80'
                }`
              }
              style={({ isActive }) =>
                isActive ? { backgroundColor: 'var(--nav-active-bg)' } : undefined
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-accent" />
                  )}
                  <Icon size={17} strokeWidth={isActive ? 2.25 : 1.75} className="shrink-0" />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-separator space-y-3 mt-auto">
          <div>
            <p className="text-[11px] text-text-tertiary px-1 mb-2 flex items-center gap-1.5 uppercase tracking-wide">
              <ThemeIcon mode={theme} size={12} />
              Appearance
            </p>
            <SegmentedControl
              options={themeOptions}
              value={theme}
              onChange={(v) => setTheme(v as ThemeMode)}
              className="w-full flex"
            />
          </div>
          <p className="text-[10px] text-text-tertiary px-1 leading-relaxed">
            © {new Date().getFullYear()} CyberN Technologie Canada
          </p>
        </div>
      </aside>

      <main className="flex-1 min-w-0 overflow-auto">
        <div className="max-w-6xl mx-auto px-8 py-10 page-enter">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

function ThemeIcon({ mode, size }: { mode: ThemeMode; size: number }) {
  if (mode === 'light') return <Sun size={size} />
  if (mode === 'dark') return <Moon size={size} />
  return <Monitor size={size} />
}
