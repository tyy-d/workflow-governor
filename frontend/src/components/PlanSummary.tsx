import { useState, type FormEvent } from 'react'
import type { WorkflowViewModel } from '../types'

function planStateLabel(state: WorkflowViewModel['planState']) {
  return state === 'NOT_PROPOSED' ? 'Not proposed' : state.split('_').map((word) => word[0] + word.slice(1).toLowerCase()).join(' ')
}

interface Props {
  workflow: WorkflowViewModel
  onApprove: () => void
  onRequestRevision: (note: string) => void
}

export function PlanSummary({ workflow, onApprove, onRequestRevision }: Props) {
  const [showRevision, setShowRevision] = useState(false)
  const [note, setNote] = useState('')
  const [error, setError] = useState('')
  const complete = workflow.tasks.filter((task) => task.status === 'Completed').length
  const blocked = workflow.tasks.filter((task) => task.status === 'Blocked').length
  const human = workflow.tasks.filter((task) => task.status === 'Needs Human').length

  const submitRevision = (event: FormEvent) => {
    event.preventDefault()
    if (!note.trim()) {
      setError('Describe what the plan should reconsider.')
      return
    }
    onRequestRevision(note)
    setShowRevision(false)
    setNote('')
  }

  return (
    <section className={`plan-summary plan-summary-${workflow.planState.toLowerCase().replace('_', '-')}`} aria-label="Plan summary">
      <div className="plan-summary-title">
        <span className="section-kicker">Operational plan {workflow.planVersion && `· ${workflow.planVersion}`}</span>
        <h2>{planStateLabel(workflow.planState)}</h2>
      </div>
      <dl className="plan-metrics">
        <div><dt>Tasks</dt><dd>{workflow.tasks.length}</dd></div>
        <div><dt>Completed</dt><dd>{complete}</dd></div>
        <div><dt>Blocked</dt><dd>{blocked}</dd></div>
        <div><dt>Human attention</dt><dd>{human}</dd></div>
        <div><dt>Current stage</dt><dd>{workflow.stage}</dd></div>
      </dl>
      {workflow.planState === 'PROPOSED' && <div className="plan-actions">
        <button className="primary-action" onClick={onApprove}>Approve Plan</button>
        <button onClick={() => { setShowRevision((value) => !value); setError('') }}>Request Revision</button>
      </div>}
      {workflow.planState === 'REVISION_REQUESTED' && <div className="plan-pause"><strong>Execution paused</strong><span>The local model is preparing a revised proposal.</span></div>}
      {showRevision && <form className="revision-form" onSubmit={submitRevision}>
        <label htmlFor="revision-note">What should the plan reconsider?</label>
        <textarea id="revision-note" autoFocus value={note} onChange={(event) => { setNote(event.target.value); setError('') }} placeholder="The insurance review should happen before commercial readiness." />
        {error && <p role="alert">{error}</p>}
        <div><button type="button" onClick={() => setShowRevision(false)}>Cancel</button><button className="primary-action" type="submit">Submit Request</button></div>
      </form>}
      {Boolean(workflow.assumptions?.length || workflow.questions?.length) && <details><summary>Assumptions and unresolved questions</summary>{workflow.assumptions?.map((s,i)=><p key={`a${i}`}>Assumption: {s}</p>)}{workflow.questions?.map((s,i)=><p key={`q${i}`}>Question: {s}</p>)}</details>}
      {workflow.revisionNote && <div className="revision-note"><strong>Requested change</strong><span>{workflow.revisionNote}</span></div>}
    </section>
  )
}
