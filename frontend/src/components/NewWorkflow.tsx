import { useState, type FormEvent } from 'react'
import type { NewWorkflowInput } from '../types'

const WORKSPACES = [
  'Northstar — Vendor Activation',
  'Northstar — OTIF Exception',
  'Northstar — Freshness Review',
  'Northstar — Invoice Review',
  'Demo Workspace',
]

export function NewWorkflow({ onCancel, onStart }: { onCancel: () => void; onStart: (input: NewWorkflowInput) => void }) {
  const [objective, setObjective] = useState('')
  const [name, setName] = useState('')
  const [workspace, setWorkspace] = useState(WORKSPACES[0])
  const [error, setError] = useState('')

  const submit = (event: FormEvent) => {
    event.preventDefault()
    if (!objective.trim()) {
      setError('Enter an objective before starting the workflow.')
      return
    }
    onStart({ name: name.trim() || undefined, objective: objective.trim(), workspace })
  }

  return (
    <main className="new-workflow-page">
      <button className="back-link" type="button" onClick={onCancel}>← Workflows</button>
      <section className="new-workflow-intro"><span className="section-kicker">New local workflow</span><h1>What do you need done?</h1><p>Start with a sparse objective. This demo creates frontend state only and does not inspect the selected workspace.</p></section>
      <form className="new-workflow-form" onSubmit={submit} noValidate>
        <label className="form-field"><span>Objective <b>Required</b></span><textarea autoFocus rows={5} value={objective} onChange={(event) => { setObjective(event.target.value); setError('') }} placeholder="Can you figure out what we need to do to get this vendor live by Friday?" aria-describedby={error ? 'objective-error' : undefined} aria-invalid={Boolean(error)} /></label>
        {error && <p className="form-error" id="objective-error" role="alert">{error}</p>}
        <div className="form-grid">
          <label className="form-field"><span>Workspace / Context Source <b>Required</b></span><select value={workspace} onChange={(event) => setWorkspace(event.target.value)}>{WORKSPACES.map((item) => <option key={item}>{item}</option>)}</select><small>Mock selection · no filesystem access occurs.</small></label>
          <label className="form-field"><span>Workflow name <em>Optional</em></span><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Generated from the objective if blank" /></label>
        </div>
        <div className="form-actions"><button type="button" onClick={onCancel}>Cancel</button><button className="primary-action" type="submit">Start Workflow</button></div>
      </form>
    </main>
  )
}
