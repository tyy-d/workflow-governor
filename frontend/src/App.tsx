import { useState } from 'react'
import { mockWorkflows } from './mock/workflow'
import type { EvidenceAction, HumanAction, NewWorkflowInput, WorkflowViewModel } from './types'
import { AppTopbar, WorkflowHeader } from './components/WorkflowHeader'
import { PlanPanel } from './components/PlanPanel'
import { TaskWorkspace } from './components/TaskWorkspace'
import { EvidencePanel } from './components/EvidencePanel'
import { BottomDrawer } from './components/BottomDrawer'
import { WorkflowHome } from './components/WorkflowHome'
import { NewWorkflow } from './components/NewWorkflow'
import { PlanningEmptyState } from './components/PlanningEmptyState'
import { PlanSummary } from './components/PlanSummary'
import { approvePlan, requestPlanRevision, updateEvidence, updateHumanTask, updateTaskStatus, type TaskTransition } from './workflowState'

type AppView = 'home' | 'detail' | 'new'

function titleFromObjective(objective: string) {
  const words = objective.replace(/[?.!]+$/, '').split(/\s+/).filter(Boolean)
  const title = words.slice(0, 6).join(' ')
  return title ? title.charAt(0).toUpperCase() + title.slice(1) : 'Untitled Workflow'
}

function createLocalWorkflow(input: NewWorkflowInput, sequence: number): WorkflowViewModel {
  return {
    id: `LOCAL-${String(sequence).padStart(3, '0')}`,
    name: input.name || titleFromObjective(input.objective),
    objective: input.objective,
    status: 'Planning',
    stage: 'Awaiting plan proposal',
    workspace: input.workspace,
    createdAt: 'Just now',
    updatedAt: 'just now',
    planState: 'NOT_PROPOSED',
    tasks: [], evidence: [], activity: [],
    finalState: { findings: [], blockers: [], nextActions: [], authorityDecisions: [] },
  }
}

export function App() {
  const [view, setView] = useState<AppView>('home')
  const [workflows, setWorkflows] = useState<WorkflowViewModel[]>(mockWorkflows)
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(mockWorkflows[0].id)
  const [selectedTaskId, setSelectedTaskId] = useState(mockWorkflows[0].tasks[0].id)
  const [selectedEvidenceId, setSelectedEvidenceId] = useState(mockWorkflows[0].evidence[0].id)
  const [drawerExpanded, setDrawerExpanded] = useState(false)
  const workflow = workflows.find((item) => item.id === selectedWorkflowId) ?? workflows[0]
  const selectedTask = workflow?.tasks.find((task) => task.id === selectedTaskId) ?? workflow?.tasks[0]

  const openWorkflow = (id: string) => {
    const next = workflows.find((item) => item.id === id)
    if (!next) return
    setSelectedWorkflowId(id)
    setSelectedTaskId(next.tasks[0]?.id ?? '')
    setSelectedEvidenceId(next.tasks[0]?.evidenceIds[0] ?? next.evidence[0]?.id ?? '')
    setDrawerExpanded(false)
    setView('detail')
  }

  const selectTask = (id: string, keepEvidence = false) => {
    setSelectedTaskId(id)
    const task = workflow.tasks.find((item) => item.id === id)
    if (!keepEvidence && task?.evidenceIds[0]) setSelectedEvidenceId(task.evidenceIds[0])
  }

  const startWorkflow = (input: NewWorkflowInput) => {
    const created = createLocalWorkflow(input, workflows.length + 1)
    setWorkflows((current) => [created, ...current])
    setSelectedWorkflowId(created.id)
    setSelectedTaskId('')
    setSelectedEvidenceId('')
    setDrawerExpanded(false)
    setView('detail')
  }

  const updateSelectedWorkflow = (update: (current: WorkflowViewModel) => WorkflowViewModel) => {
    setWorkflows((current) => current.map((item) => item.id === selectedWorkflowId ? update(item) : item))
  }

  const handleHumanAction = (action: HumanAction) => {
    if (!selectedTask) return
    updateSelectedWorkflow((current) => updateHumanTask(current, selectedTask.id, action))
  }

  const handleTaskTransition = (status: TaskTransition) => {
    if (!selectedTask) return
    updateSelectedWorkflow((current) => updateTaskStatus(current, selectedTask.id, status))
  }

  const handleEvidenceAction = (action: EvidenceAction) => {
    if (!selectedEvidenceId) return
    updateSelectedWorkflow((current) => updateEvidence(current, selectedEvidenceId, action))
  }

  return (
    <div className="app-shell">
      <AppTopbar currentView={view} onHome={() => setView('home')} onNew={() => setView('new')} />
      {view === 'home' && <WorkflowHome workflows={workflows} onSelect={openWorkflow} onNew={() => setView('new')} />}
      {view === 'new' && <NewWorkflow onCancel={() => setView('home')} onStart={startWorkflow} />}
      {view === 'detail' && workflow && <>
        <nav className="workflow-breadcrumb" aria-label="Workflow navigation"><button onClick={() => setView('home')}>← Workflows</button><span aria-hidden="true">/</span><strong>{workflow.name}</strong><span className="frontend-state-label">FRONTEND MOCK</span></nav>
        <WorkflowHeader workflow={workflow} />
        {selectedTask && workflow.operator ? <>
          <PlanSummary workflow={workflow} onApprove={() => updateSelectedWorkflow(approvePlan)} onRequestRevision={(note) => updateSelectedWorkflow((current) => requestPlanRevision(current, note))} />
          <div className="workspace-grid">
            <PlanPanel tasks={workflow.tasks} selectedTaskId={selectedTask.id} planState={workflow.planState} onSelect={(id) => selectTask(id)} />
            <TaskWorkspace task={selectedTask} tasks={workflow.tasks} evidence={workflow.evidence} operator={workflow.operator} planState={workflow.planState === 'NOT_PROPOSED' ? 'PROPOSED' : workflow.planState} onEvidenceSelect={setSelectedEvidenceId} onHumanAction={handleHumanAction} onTaskTransition={handleTaskTransition} />
            <EvidencePanel key={workflow.id} evidence={workflow.evidence} tasks={workflow.tasks} selectedId={selectedEvidenceId} selectedTaskId={selectedTask.id} usedIds={selectedTask.evidenceIds} operator={workflow.operator} onSelect={setSelectedEvidenceId} onTaskSelect={(id) => selectTask(id, true)} onAction={handleEvidenceAction} />
          </div>
          <BottomDrawer workflow={workflow} expanded={drawerExpanded} onToggle={() => setDrawerExpanded((value) => !value)} />
        </> : <PlanningEmptyState workflow={workflow} />}
      </>}
    </div>
  )
}
