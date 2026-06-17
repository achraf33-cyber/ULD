import type { InstanceStatus } from '../api/types'
import { Badge } from './ui'

const variants: Record<InstanceStatus, 'success' | 'neutral' | 'warning' | 'error'> = {
  running: 'success',
  stopped: 'neutral',
  starting: 'warning',
  error: 'error',
  unknown: 'neutral',
}

export function StatusBadge({ status }: { status: InstanceStatus }) {
  return <Badge variant={variants[status]}>{status}</Badge>
}
