import type { WorkflowViewModel } from '../types'
import { Icon } from './Icon'

export function AppTopbar({ currentView, onHome, onNew }: { currentView: 'home' | 'detail' | 'new'; onHome: () => void; onNew: () => void }) {
  return (
    <header className="app-topbar">
      <button className="brand" onClick={onHome} aria-label="Open workflow home"><span className="brand-mark"><Icon name="workflow" size={19} /></span><span>Workflow <strong>Governor</strong></span><span className="demo-tag">DEMO</span></button>
      <nav className="app-navigation" aria-label="Application"><button className={currentView === 'home' ? 'active' : ''} onClick={onHome}>Workflows</button><button className={currentView === 'new' ? 'active' : ''} onClick={onNew}>+ New Workflow</button></nav>
      <div className="topbar-meta"><span className="boundary-label"><Icon name="shield" size={14} /> Bounded evidence</span><span className="runtime-pill"><i /> LOCAL <em>live state</em></span></div>
    </header>
  )
}

export function WorkflowHeader({ workflow }: { workflow: WorkflowViewModel }) {
  const complete = workflow.tasks.filter((task) => task.status === 'Completed').length
  const progress = workflow.tasks.length ? (complete / workflow.tasks.length) * 100 : 0
  return (
    <section className="workflow-header">
      <div className="objective-icon"><Icon name="target" size={23} /></div>
      <div className="objective-copy">
        <div className="eyebrow">Active workflow <span>/</span> {workflow.id}</div>
        <h1>{workflow.name}</h1>
        <p>“{workflow.objective}”</p>
      </div>
      <div className="header-stats">
        <div><span>Status</span><strong><i className="pulse-dot" />{workflow.status}</strong></div>
        <div><span>Current stage</span><strong>{workflow.stage}</strong></div>
        <div className="progress-stat"><span>Plan progress</span><strong>{workflow.tasks.length ? `${complete} of ${workflow.tasks.length}` : 'Not started'}</strong><div className="progress-track"><i style={{ width: `${progress}%` }} /></div></div>
      </div>
    </section>
  )
}
