import type { ExecutorClass, TaskStatus, VerificationLevel } from '../types'

export function StatusBadge({ status }: { status: TaskStatus }) {
  return <span className={`badge status status-${status.toLowerCase().replace(' ', '-')}`}><i />{status}</span>
}

export function ExecutorBadge({ executor }: { executor: ExecutorClass }) {
  const icon = executor === 'Deterministic' ? '⌁' : executor === 'Local AI' ? '✦' : '◉'
  return <span className={`badge executor executor-${executor.toLowerCase().replace(' ', '-')}`} aria-label={`${executor} executor`}><b>{icon}</b>{executor}</span>
}

export function VerificationBadge({ level }: { level: VerificationLevel }) {
  return <span className={`badge verification verification-${level.toLowerCase()}`}>Verification · {level}</span>
}
