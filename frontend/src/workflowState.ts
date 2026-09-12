import type { ActivityEvent, EvidenceAction, HumanAction, TaskStatus, WorkflowStatus, WorkflowViewModel } from './types'

export type TaskTransition = Extract<TaskStatus, 'Running' | 'Completed' | 'Blocked'>

function eventTime() {
  return new Intl.DateTimeFormat('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date())
}

function addActivity(workflow: WorkflowViewModel, title: string, description: string, kind: ActivityEvent['kind'] = 'task') {
  return [...workflow.activity, { id: `local-${Date.now()}-${workflow.activity.length}`, time: eventTime(), title, description, kind }]
}

export function dependenciesComplete(taskId: string, tasks: WorkflowViewModel['tasks']) {
  const task = tasks.find((item) => item.id === taskId)
  return Boolean(task && task.dependencyIds.every((id) => tasks.find((item) => item.id === id)?.status === 'Completed'))
}

function refreshReadiness(tasks: WorkflowViewModel['tasks']) {
  return tasks.map((task) => {
    if (task.status !== 'Pending' && !(task.status === 'Blocked' && task.blockReason?.startsWith('Waiting for'))) return task
    if (!dependenciesComplete(task.id, tasks)) return task
    return { ...task, status: task.executor === 'Human' ? 'Needs Human' as const : 'Ready' as const, blockReason: undefined, humanState: task.executor === 'Human' ? 'Awaiting response' : task.humanState }
  })
}

export function deriveCurrentStage(tasks: WorkflowViewModel['tasks']) {
  return tasks.find((task) => task.status !== 'Completed')?.stage ?? 'Finalized'
}

function deriveWorkflowStatus(tasks: WorkflowViewModel['tasks']): WorkflowStatus {
  if (tasks.length > 0 && tasks.every((task) => task.status === 'Completed')) return 'Completed'
  if (tasks.some((task) => task.status === 'Running')) return 'In Progress'
  if (tasks.some((task) => task.status === 'Needs Human')) return 'Needs Human'
  if (tasks.some((task) => task.status === 'Ready')) return 'In Progress'
  if (tasks.some((task) => task.status === 'Blocked')) return 'Blocked'
  return 'Planning'
}

export function updateTaskStatus(workflow: WorkflowViewModel, taskId: string, status: TaskTransition): WorkflowViewModel {
  const task = workflow.tasks.find((item) => item.id === taskId)
  if (!task || workflow.planState !== 'APPROVED') return workflow
  if (status === 'Running' && (task.status !== 'Ready' || !dependenciesComplete(taskId, workflow.tasks))) return workflow
  if (status === 'Completed' && task.status !== 'Running') return workflow
  if (status === 'Blocked' && !['Ready', 'Running'].includes(task.status)) return workflow

  let tasks = workflow.tasks.map((item) => item.id === taskId ? {
    ...item,
    status,
    blockReason: status === 'Blocked' ? 'Marked blocked during review; resolution is required before work can resume.' : undefined,
  } : item)
  tasks = refreshReadiness(tasks)
  const verb = status === 'Running' ? 'started' : status === 'Completed' ? 'completed' : 'blocked'
  return {
    ...workflow,
    tasks,
    status: deriveWorkflowStatus(tasks),
    stage: deriveCurrentStage(tasks),
    updatedAt: 'just now',
    activity: addActivity(workflow, `Task ${verb}`, `${task.title} was marked ${status.toLowerCase()} in the frontend demo.`),
  }
}

export function updateHumanTask(workflow: WorkflowViewModel, taskId: string, action: HumanAction): WorkflowViewModel {
  const task = workflow.tasks.find((item) => item.id === taskId)
  if (!task || task.executor !== 'Human' || workflow.planState !== 'APPROVED') return workflow
  const states: Record<HumanAction, string> = {
    Complete: 'Completed locally',
    'Ask Clarification': 'Clarification requested',
    'Narrow Task': 'Narrowing requested',
    'Request Reassignment': 'Reassignment requested',
    'Decline Authority': 'Authority declined',
  }
  let tasks = workflow.tasks.map((item) => item.id === taskId ? {
    ...item,
    status: action === 'Complete' ? 'Completed' as const : 'Needs Human' as const,
    humanState: states[action],
  } : item)
  tasks = refreshReadiness(tasks)
  const title = action === 'Complete' ? 'Human task completed' : `Human task: ${action.toLowerCase()}`
  return {
    ...workflow,
    tasks,
    status: deriveWorkflowStatus(tasks),
    stage: deriveCurrentStage(tasks),
    updatedAt: 'just now',
    activity: addActivity(workflow, title, `${task.title}: ${states[action]}.`, 'human'),
  }
}

export function approvePlan(workflow: WorkflowViewModel): WorkflowViewModel {
  if (workflow.planState !== 'PROPOSED') return workflow
  const tasks = refreshReadiness(workflow.tasks)
  return {
    ...workflow,
    planState: 'APPROVED',
    tasks,
    status: deriveWorkflowStatus(tasks),
    stage: deriveCurrentStage(tasks),
    updatedAt: 'just now',
    activity: addActivity(workflow, 'Plan approved', `${workflow.planVersion ?? 'Current plan'} approved for local demo interaction.`),
  }
}

export function requestPlanRevision(workflow: WorkflowViewModel, note: string): WorkflowViewModel {
  if (workflow.planState !== 'PROPOSED' || !note.trim()) return workflow
  return {
    ...workflow,
    planState: 'REVISION_REQUESTED',
    revisionNote: note.trim(),
    status: 'Planning',
    stage: 'Awaiting plan revision',
    updatedAt: 'just now',
    activity: addActivity(workflow, 'Plan revision requested', note.trim()),
  }
}

export function updateEvidence(workflow: WorkflowViewModel, evidenceId: string, action: EvidenceAction): WorkflowViewModel {
  const evidence = workflow.evidence.find((item) => item.id === evidenceId)
  if (!evidence) return workflow

  const nextEvidence = workflow.evidence.map((item) => {
    if (item.id !== evidenceId) return item
    if (action === 'Mark Reviewed') return { ...item, inspected: true }
    if (action === 'Request Evidence' && item.status === 'Missing') return { ...item, requestState: 'Requested' as const }
    if (action === 'Flag Conflict') return {
      ...item,
      status: 'Conflicting' as const,
      conflictNote: item.conflictNote ?? 'This item was flagged for reconciliation with another workflow source.',
    }
    return item
  })

  const activity = action === 'Mark Reviewed'
    ? ['Evidence reviewed', `${evidence.title} marked reviewed.`] as const
    : action === 'Request Evidence'
      ? ['Evidence requested', `${evidence.title} requested in the frontend demo.`] as const
      : ['Conflict flagged', `${evidence.title} flagged for evidence reconciliation.`] as const

  return {
    ...workflow,
    evidence: nextEvidence,
    updatedAt: 'just now',
    activity: addActivity(workflow, activity[0], activity[1], action === 'Flag Conflict' ? 'correction' : 'task'),
  }
}
