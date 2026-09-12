export const TASK_STATUSES = [
  'Pending',
  'Ready',
  'Running',
  'Needs Human',
  'Completed',
  'Blocked',
] as const

export const EXECUTOR_CLASSES = ['Deterministic', 'Local AI', 'Human'] as const

export const PLAN_STATES = ['PROPOSED', 'APPROVED', 'REVISION_REQUESTED', 'SUPERSEDED'] as const

export const VERIFICATION_LEVELS = ['Normal', 'Enhanced', 'Mandatory'] as const

export const WORKFLOW_STATUSES = [
  'Draft',
  'Planning',
  'In Progress',
  'Needs Human',
  'Blocked',
  'Completed',
] as const

export const EVIDENCE_KINDS = [
  'Document',
  'Spreadsheet',
  'Record',
  'Policy',
  'Email',
  'Calculation',
  'Human Input',
  'System Result',
] as const

export const EVIDENCE_STATUSES = [
  'Available',
  'In Use',
  'Needs Review',
  'Superseded',
  'Conflicting',
  'Missing',
] as const

export const EVIDENCE_SOURCE_ROLES = [
  'Authoritative Policy',
  'Operational Record',
  'Vendor-Submitted',
  'Human Observation',
  'Derived Calculation',
  'Model Summary',
] as const

export type TaskStatus = (typeof TASK_STATUSES)[number]
export type ExecutorClass = (typeof EXECUTOR_CLASSES)[number]
export type PlanState = (typeof PLAN_STATES)[number]
export type VerificationLevel = (typeof VERIFICATION_LEVELS)[number]
export type WorkflowStatus = (typeof WORKFLOW_STATUSES)[number]
export type HumanAction = 'Complete' | 'Ask Clarification' | 'Narrow Task' | 'Request Reassignment' | 'Decline Authority'
export type EvidenceKind = (typeof EVIDENCE_KINDS)[number]
export type EvidenceStatus = (typeof EVIDENCE_STATUSES)[number]
export type EvidenceSourceRole = (typeof EVIDENCE_SOURCE_ROLES)[number]
export type EvidenceAction = 'Mark Reviewed' | 'Request Evidence' | 'Flag Conflict'

export interface EvidenceMetadata {
  label: string
  value: string
}

export interface EvidenceViewModel {
  id: string
  title: string
  filename?: string
  kind: EvidenceKind
  status: EvidenceStatus
  source: string
  sourceType: string
  sourceRole: EvidenceSourceRole
  summary: string
  preview: string[]
  taskIds: string[]
  metadata: EvidenceMetadata[]
  version?: string
  createdAt?: string
  updatedAt: string
  supersedesId?: string
  supersededById?: string
  conflictsWithIds?: string[]
  conflictNote?: string
  derivedFromIds?: string[]
  inspected?: boolean
  requestState?: 'Not requested' | 'Requested'
}

export interface HumanInput { operator: string; judgment: string; reason: string }
export interface TaskResultView { summary: string; findings: { statement: string; citations: { sourceId: string; line: number; quote: string }[] }[] }

export interface TaskViewModel {
  result?: TaskResultView
  humanResponse?: HumanInput & { action: string; timestamp: string }
  id: string
  sequence: number
  title: string
  objective: string
  status: TaskStatus
  executor: ExecutorClass
  stage: string
  rationale: string
  expectedOutput: string
  dependencyIds: string[]
  evidenceIds: string[]
  assignedOperator?: string
  verificationLevel?: VerificationLevel
  scaffoldingLevel?: string
  blockReason?: string
  consequenceLabel?: 'Authorization Required' | 'Human Decision' | 'Mandatory Verification'
  humanRequest?: string
  humanState?: string
}

export interface OperatorViewModel {
  id: string
  name: string
  role: string
  evidenceState: string
  scaffolding: string
}

export interface ActivityEvent {
  id: string
  time: string
  title: string
  description: string
  kind: 'system' | 'task' | 'human' | 'correction'
}

export interface WorkflowViewModel {
  assumptions?: string[]
  questions?: string[]
  operation?: string | null
  error?: string | null
  id: string
  name: string
  objective: string
  status: WorkflowStatus
  stage: string
  workspace: string
  createdAt: string
  updatedAt: string
  planState: PlanState | 'NOT_PROPOSED'
  planVersion?: string
  revisionNote?: string
  tasks: TaskViewModel[]
  evidence: EvidenceViewModel[]
  operator?: OperatorViewModel
  activity: ActivityEvent[]
  finalState: {
    findings: string[]
    blockers: string[]
    nextActions: string[]
    authorityDecisions: string[]
  }
}


export interface NewWorkflowInput {
  name?: string
  objective: string
  workspace: string
}
