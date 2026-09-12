import { useEffect, useState } from 'react'
import { api } from './api'
import type { EvidenceAction, HumanAction, HumanInput, NewWorkflowInput, WorkflowViewModel } from './types'
import { AppTopbar, WorkflowHeader } from './components/WorkflowHeader'
import { PlanPanel } from './components/PlanPanel'
import { TaskWorkspace } from './components/TaskWorkspace'
import { EvidencePanel } from './components/EvidencePanel'
import { BottomDrawer } from './components/BottomDrawer'
import { WorkflowHome } from './components/WorkflowHome'
import { NewWorkflow } from './components/NewWorkflow'
import { PlanningEmptyState } from './components/PlanningEmptyState'
import { PlanSummary } from './components/PlanSummary'

export function App() {
  const initial = window.location.hash.slice(1)
  const [view, setView] = useState<'home'|'detail'|'new'>(initial ? 'detail' : 'home')
  const [workflows, setWorkflows] = useState<WorkflowViewModel[]>([])
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(initial)
  const [selectedTaskId, setSelectedTaskId] = useState('')
  const [selectedEvidenceId, setSelectedEvidenceId] = useState('')
  const [drawerExpanded, setDrawerExpanded] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [connected, setConnected] = useState(false)
  const workflow = workflows.find(w => w.id === selectedWorkflowId)
  const task = workflow?.tasks.find(t => t.id === selectedTaskId) ?? workflow?.tasks[0]
  const reload = async () => { const values = await api<WorkflowViewModel[]>('/workflows'); setWorkflows(values); setConnected(true) }
  useEffect(() => {
    const update = () => { reload().catch(e => { setConnected(false); setError(String(e)) }) }
    update(); const timer = setInterval(update, 2500); return () => clearInterval(timer)
  }, [])
  const home = () => { setView('home'); window.location.hash = '' }
  const open = (id: string) => { setSelectedWorkflowId(id); setSelectedTaskId(''); setSelectedEvidenceId(''); setView('detail'); window.location.hash = id }
  const act = async (path: string, data: unknown = {}) => {
    setBusy(true); setError('')
    try { const w = await api<WorkflowViewModel>(path, data); setWorkflows(old => [w, ...old.filter(x => x.id !== w.id)]); return w }
    catch(e) { setError(e instanceof Error ? e.message : String(e)) }
    finally { setBusy(false) }
  }
  const start = async (input: NewWorkflowInput) => { const w = await act('/workflows', input); if(w) open(w.id) }
  const selectTask = (id: string, keepEvidence=false) => { setSelectedTaskId(id); if(!keepEvidence) setSelectedEvidenceId(workflow?.tasks.find(t=>t.id===id)?.evidenceIds[0] ?? '') }
  const human = (action: HumanAction, input: HumanInput) => { if(workflow && task) void act(`/workflows/${workflow.id}/tasks/${task.id}/human`, {action,...input}) }
  const evidenceAction = (action: EvidenceAction) => { if(workflow) void act(`/workflows/${workflow.id}/evidence/${selectedEvidenceId || task?.evidenceIds[0] || workflow.evidence[0]?.id}`, {action}) }
  const locked = busy || Boolean(workflow?.operation)
  return <div className="app-shell">
    <AppTopbar currentView={view} onHome={home} onNew={()=>setView('new')} />
    <div className="runtime-banner" role="status">{connected ? 'GB10 · Local Qwen · persistent workflow state' : 'Connecting to local backend…'}{workflow?.operation && ` · ${workflow.operation} — processing; you can refresh safely`}</div>
    {error && <div className="runtime-error" role="alert">{error}<button onClick={()=>setError('')}>Dismiss</button></div>}
    {view==='home' && <WorkflowHome workflows={workflows} onSelect={open} onNew={()=>setView('new')} />}
    {view==='new' && <fieldset className="runtime-fieldset" disabled={busy}><NewWorkflow onCancel={home} onStart={start} /></fieldset>}
    {view==='detail' && workflow && <>
      <nav className="workflow-breadcrumb"><button onClick={home}>← Workflows</button><strong>{workflow.name}</strong><span>LOCAL EXECUTION</span></nav>
      <WorkflowHeader workflow={workflow}/>
      {workflow.error && <div className="runtime-error" role="alert">{workflow.error}</div>}
      {task && workflow.operator ? <>
        <fieldset className="runtime-fieldset" disabled={locked}>
          <PlanSummary workflow={workflow} onApprove={()=>void act(`/workflows/${workflow.id}/approve`)} onRequestRevision={note=>void act(`/workflows/${workflow.id}/revise`,{note})}/>
        </fieldset>
        <div className="workspace-grid">
          <PlanPanel tasks={workflow.tasks} selectedTaskId={task.id} planState={workflow.planState} onSelect={selectTask}/>
          <TaskWorkspace key={`${workflow.id}-${task.id}`} task={task} tasks={workflow.tasks} evidence={workflow.evidence} operator={workflow.operator} planState={workflow.planState==='NOT_PROPOSED'?'PROPOSED':workflow.planState} busy={locked} onEvidenceSelect={setSelectedEvidenceId} onHumanAction={human} onExecute={()=>void act(`/workflows/${workflow.id}/tasks/${task.id}/execute`)} onResume={note=>void act(`/workflows/${workflow.id}/tasks/${task.id}/resume`,{note})}/>
          <EvidencePanel evidence={workflow.evidence} tasks={workflow.tasks} selectedId={selectedEvidenceId || task.evidenceIds[0]} selectedTaskId={task.id} usedIds={task.evidenceIds} operator={workflow.operator} onSelect={setSelectedEvidenceId} onTaskSelect={id=>selectTask(id,true)} onAction={evidenceAction}/>
        </div>
        <BottomDrawer workflow={workflow} expanded={drawerExpanded} onToggle={()=>setDrawerExpanded(x=>!x)} onEvidenceSelect={setSelectedEvidenceId}/>
      </> : <PlanningEmptyState workflow={workflow} onRetry={()=>void act(`/workflows/${workflow.id}/plan`)}/>}
    </>}
  </div>
}
