import type { TaskViewModel } from '../types'
import { ExecutorBadge, StatusBadge } from './Badges'
import { Icon } from './Icon'

interface PlanPanelProps {
  tasks: TaskViewModel[]
  selectedTaskId: string
  planState: string
  onSelect: (id: string) => void
}

export function PlanPanel({ tasks, selectedTaskId, planState, onSelect }: PlanPanelProps) {
  const stages = Array.from(new Set(tasks.map((task) => task.stage)))
  return (
    <aside className="panel plan-panel" aria-label="Workflow plan">
      <div className="panel-heading">
        <div><span className="section-kicker">Workflow plan</span><h2>{tasks.length} coordinated tasks</h2></div>
        <span className="plan-state">{planState}</span>
      </div>
      <div className="task-list">
        {stages.map((stage) => {
          const stageTasks = tasks.filter((task) => task.stage === stage)
          return <section className="task-stage" key={stage}>
            <div className="task-stage-heading"><span>{stage}</span>{stageTasks.length > 1 && <small>{stageTasks.length} parallel tasks</small>}</div>
            {stageTasks.map((task) => (
          <button className={`task-row ${task.id === selectedTaskId ? 'selected' : ''}`} key={task.id} onClick={() => onSelect(task.id)} aria-pressed={task.id === selectedTaskId}>
            <div className="task-rail"><span>{String(task.sequence).padStart(2, '0')}</span></div>
            <div className="task-row-content">
              <strong>{task.title}</strong>
              <div className="task-badges"><StatusBadge status={task.status} /><ExecutorBadge executor={task.executor} /></div>
              {task.dependencyIds.length > 0 && <small><Icon name="workflow" size={12} /> Depends on {task.dependencyIds.length} task{task.dependencyIds.length > 1 ? 's' : ''}</small>}
              {task.blockReason && <small className="row-block-reason">Blocked by: {task.blockReason}</small>}
            </div>
            <Icon name="chevron" size={16} />
          </button>
            ))}
          </section>
        })}
      </div>
      <div className="plan-legend"><span><i className="legend-line complete" /> Completed</span><span><i className="legend-line active" /> Active path</span><span><i className="legend-line waiting" /> Waiting</span></div>
      <div className="status-key"><span><b>Pending</b> Not started; prerequisites may remain.</span><span><b>Blocked</b> Cannot proceed until an explicit condition is resolved.</span></div>
    </aside>
  )
}
