import type { EvidenceViewModel, HumanAction, OperatorViewModel, PlanState, TaskViewModel } from '../types'
import type { TaskTransition } from '../workflowState'
import { ExecutorBadge, StatusBadge, VerificationBadge } from './Badges'
import { Icon } from './Icon'

interface Props {
  task: TaskViewModel
  tasks: TaskViewModel[]
  evidence: EvidenceViewModel[]
  operator: OperatorViewModel
  planState: PlanState
  onEvidenceSelect: (id: string) => void
  onHumanAction: (action: HumanAction) => void
  onTaskTransition: (status: TaskTransition) => void
}

function HumanTaskCard({ task, operator, state, disabled, onAction }: { task: TaskViewModel; operator: OperatorViewModel; state: string; disabled: boolean; onAction: (action: HumanAction) => void }) {
  const actions: HumanAction[] = ['Complete', 'Ask Clarification', 'Narrow Task', 'Request Reassignment']
  return (
    <section className="human-card">
      <div className="human-card-title"><div className="human-symbol"><Icon name="person" size={20} /></div><div><span>Bounded human work</span><h3>{operator.name} · {operator.id}</h3></div><span className="human-state">{state}</span></div>
      <div className="human-grid">
        <div><label>Task request</label><p>{task.humanRequest}</p></div>
        <div><label>Context provided</label><p>{task.evidenceIds.length} granted items · task objective · authority boundary</p></div>
        <div><label>Expected response</label><p>{task.expectedOutput}</p></div>
      </div>
      <div className="human-actions">
        {actions.map((action) => <button key={action} disabled={disabled || task.status === 'Completed'} className={action === 'Complete' ? 'primary-action' : ''} onClick={() => onAction(action)}>{action === 'Complete' && <Icon name="check" size={14} />}{action}</button>)}
      </div>
      <p className="local-only-note">Demo interaction only · updates local interface state</p>
    </section>
  )
}

export function TaskWorkspace({ task, tasks, evidence, operator, planState, onEvidenceSelect, onHumanAction, onTaskTransition }: Props) {
  const dependencies = task.dependencyIds.map((id) => tasks.find((item) => item.id === id)).filter((item): item is TaskViewModel => Boolean(item))
  const inputs = task.evidenceIds.map((id) => evidence.find((item) => item.id === id)).filter((item): item is EvidenceViewModel => Boolean(item))
  const canInteract = planState === 'APPROVED'
  const actions: { label: string; status: TaskTransition }[] = task.status === 'Ready'
    ? [{ label: 'Mark Running', status: 'Running' }, { label: 'Mark Blocked', status: 'Blocked' }]
    : task.status === 'Running' && task.executor !== 'Human'
      ? [{ label: 'Mark Completed', status: 'Completed' }, { label: 'Mark Blocked', status: 'Blocked' }]
      : []
  return (
    <main className="panel task-workspace">
      <div className="panel-heading task-heading">
        <div><span className="section-kicker">Task {String(task.sequence).padStart(2, '0')} · Current work area</span><h2>{task.title}</h2></div>
        <div className="task-heading-badges"><StatusBadge status={task.status} /><ExecutorBadge executor={task.executor} />{task.verificationLevel && <VerificationBadge level={task.verificationLevel} />}</div>
      </div>
      {task.consequenceLabel && <div className="consequence-banner"><span>{task.consequenceLabel}</span><p>This task preserves its verification and authority boundary in the mock workflow.</p></div>}
      <div className="task-objective"><label>Task objective</label><p>{task.objective}</p></div>
      <section className="routing-rationale">
        <div className="rationale-icon">↳</div>
        <div><label>Why this executor</label><p>{task.rationale}</p></div>
      </section>
      <div className="detail-grid">
        <section>
          <label>Evidence used by this task</label>
          <div className="input-list">
            {inputs.map((item) => <button key={item.id} className={item.status === 'Missing' ? 'missing-input' : ''} onClick={() => onEvidenceSelect(item.id)}><Icon name="file" size={15} /><span><strong>{item.status === 'Missing' ? '○' : '✓'} {item.title}</strong><small>{item.kind} · {item.status} · {item.source}</small></span><Icon name="chevron" size={14} /></button>)}
          </div>
        </section>
        <section className="output-card"><label>Expected output</label><p>{task.expectedOutput}</p><span>Result schema · bounded summary</span></section>
      </div>
      <div className="dependency-section"><label>Depends on</label>{dependencies.length ? <div className="dependency-list">{dependencies.map((dependency) => <span className={dependency.status === 'Completed' ? 'complete' : ''} key={dependency.id}><b>{dependency.status === 'Completed' ? '✓' : '○'}</b><span>{dependency.title}<small>{dependency.status}</small></span></span>)}</div> : <p>None · this task can proceed independently once the plan is approved.</p>}</div>
      {task.blockReason && <div className="block-reason"><strong>Blocked by</strong><span>{task.blockReason}</span></div>}
      {task.assignedOperator && <div className="task-assignment"><span><label>Assigned operator</label><strong>{task.assignedOperator}</strong></span>{task.scaffoldingLevel && <span><label>Scaffolding</label><strong>{task.scaffoldingLevel}</strong></span>}</div>}
      {actions.length > 0 && <div className="task-controls"><div><label>Mock task controls</label><p>Local state only · every change is added to workflow activity.</p></div><div>{actions.map((action) => <button className={action.status === 'Completed' || action.status === 'Running' ? 'primary-action' : ''} disabled={!canInteract} key={action.status} onClick={() => onTaskTransition(action.status)}>{action.label}</button>)}</div></div>}
      {!canInteract && actions.length > 0 && <p className="interaction-paused">Approve the proposed plan before starting task work.</p>}
      {task.executor === 'Human' && <HumanTaskCard task={task} operator={operator} state={task.humanState ?? 'Awaiting response'} disabled={!canInteract || !['Needs Human', 'Running'].includes(task.status)} onAction={onHumanAction} />}
    </main>
  )
}
