import type { ActivityEvent, WorkflowViewModel } from '../types'
import { Icon } from './Icon'

function Timeline({ activity }: { activity: ActivityEvent[] }) {
  return <div className="timeline">{activity.map((event) => <div className={`timeline-item ${event.kind}`} key={event.id}><span className="timeline-time">{new Date(event.time).toLocaleTimeString()}</span><i /><div><strong>{event.kind === 'correction' && <em>Correction</em>}{event.title}</strong><p>{event.description}</p></div></div>)}</div>
}

function FinalState({ finalState, onEvidenceSelect }: { finalState: WorkflowViewModel['finalState']; onEvidenceSelect: (id:string)=>void }) {
  const groups = [
    ['Findings', finalState.findings], ['Remaining blockers', finalState.blockers],
    ['Recommended next actions', finalState.nextActions], ['Unresolved authority', finalState.authorityDecisions],
  ] as const
  return <div className="final-grid">{groups.map(([title, items]) => <section key={title}><span>{title}</span>{items.map((item) => <p key={item}>{item.split(/(\[[EPH]-[^\]]+:L\d+\])/g).map((part,i)=>part.startsWith('[')?<button key={i} onClick={()=>onEvidenceSelect(part.slice(1,part.indexOf(':')))}>{part}</button>:part)}</p>)}</section>)}</div>
}

export function BottomDrawer({ workflow, expanded, onToggle, onEvidenceSelect }: { workflow: WorkflowViewModel; expanded: boolean; onToggle: () => void; onEvidenceSelect: (id:string)=>void }) {
  const corrections = workflow.activity.filter((event) => event.kind === 'correction').length
  return (
    <section className={`bottom-drawer ${expanded ? 'expanded' : ''}`}>
      <button className="drawer-toggle" onClick={onToggle} aria-expanded={expanded}>
        <div><Icon name="clock" size={17} /><span>Workflow activity</span><b>{workflow.activity.length} events</b>{corrections > 0 && <span className="correction-count">{corrections} correction{corrections > 1 ? 's' : ''} retained</span>}</div>
        <div><span>Final-state preview</span><Icon name="chevron" size={17} /></div>
      </button>
      {expanded && <div className="drawer-content"><Timeline activity={workflow.activity} /><FinalState finalState={workflow.finalState} onEvidenceSelect={onEvidenceSelect} /></div>}
    </section>
  )
}
