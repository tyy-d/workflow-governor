import { useMemo, useState } from 'react'
import type { WorkflowViewModel } from '../types'

function completedTasks(workflow: WorkflowViewModel) {
  return workflow.tasks.filter((task) => task.status === 'Completed').length
}

export function WorkflowHome({ workflows, onSelect, onNew }: { workflows: WorkflowViewModel[]; onSelect: (id: string) => void; onNew: () => void }) {
  const [query, setQuery] = useState('')
  const visibleWorkflows = useMemo(() => {
    const needle = query.trim().toLowerCase()
    if (!needle) return workflows
    return workflows.filter((workflow) => [workflow.name, workflow.objective, workflow.status].some((value) => value.toLowerCase().includes(needle)))
  }, [query, workflows])

  return (
    <main className="workflow-home">
      <section className="home-hero">
        <div><span className="section-kicker">Local Runtime · Frontend mock state</span><h1>Workflow Governor</h1><p>Choose an inspectable workflow or begin with a sparse objective.</p></div>
        <button className="new-workflow-button" onClick={onNew}>+ New Workflow</button>
      </section>
      <section className="workflow-index" aria-labelledby="recent-workflows-title">
        <div className="index-heading"><div><span className="section-kicker">Workflow navigator</span><h2 id="recent-workflows-title">Recent workflows</h2></div><label className="workflow-search"><span>Search workflows</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Name, objective, or status" /></label></div>
        {visibleWorkflows.length ? <div className="workflow-list">{visibleWorkflows.map((workflow) => {
          const complete = completedTasks(workflow)
          const total = workflow.tasks.length
          const percent = total ? Math.round((complete / total) * 100) : 0
          const humanWaiting = workflow.tasks.filter((task) => task.status === 'Needs Human').length
          return <button className="workflow-list-item" key={workflow.id} onClick={() => onSelect(workflow.id)}>
            <span className="workflow-list-main"><strong>{workflow.name}</strong><q>{workflow.objective}</q><small>{workflow.workspace}</small></span>
            <span className={`workflow-status workflow-status-${workflow.status.toLowerCase().replace(' ', '-')}`}><i />{workflow.status}</span>
            <span className="workflow-stage"><small>Current stage</small><strong>{workflow.stage}</strong><em>Updated {workflow.updatedAt}</em></span>
            <span className="workflow-progress"><small>Task progress</small><strong>{complete} / {total} completed</strong><span><i style={{ width: `${percent}%` }} /></span><em>{percent}%</em></span>
            <span className={`human-attention ${humanWaiting ? 'waiting' : ''}`}>{humanWaiting ? `${humanWaiting} human task${humanWaiting > 1 ? 's' : ''} waiting` : 'No human action waiting'}</span>
            <span className="open-workflow" aria-hidden="true">Open →</span>
          </button>
        })}</div> : <div className="empty-state compact"><h3>No workflows match this search.</h3><p>Try a workflow name, objective, or status.</p></div>}
      </section>
    </main>
  )
}
