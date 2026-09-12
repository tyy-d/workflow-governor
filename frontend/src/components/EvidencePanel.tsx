import { useMemo, useState } from 'react'
import type { EvidenceAction, EvidenceKind, EvidenceViewModel, OperatorViewModel, TaskViewModel } from '../types'
import { Icon } from './Icon'

type EvidenceFilter = 'All' | 'Documents' | 'Policy' | 'Human' | 'Derived' | 'Conflicts' | 'Missing'

interface Props {
  evidence: EvidenceViewModel[]
  tasks: TaskViewModel[]
  selectedId: string
  selectedTaskId: string
  usedIds: string[]
  operator: OperatorViewModel
  onSelect: (id: string) => void
  onTaskSelect: (id: string) => void
  onAction: (action: EvidenceAction) => void
}

const FILTERS: EvidenceFilter[] = ['All', 'Documents', 'Policy', 'Human', 'Derived', 'Conflicts', 'Missing']

function matchesFilter(item: EvidenceViewModel, filter: EvidenceFilter) {
  if (filter === 'All') return true
  if (filter === 'Documents') return ['Document', 'Spreadsheet', 'Email'].includes(item.kind)
  if (filter === 'Policy') return item.kind === 'Policy'
  if (filter === 'Human') return item.kind === 'Human Input'
  if (filter === 'Derived') return ['Calculation', 'System Result'].includes(item.kind) || Boolean(item.derivedFromIds?.length)
  if (filter === 'Conflicts') return item.status === 'Conflicting'
  return item.status === 'Missing'
}

function kindCode(kind: EvidenceKind) {
  const codes: Record<EvidenceKind, string> = { Document: 'DOC', Spreadsheet: 'XLS', Record: 'REC', Policy: 'POL', Email: 'EML', Calculation: 'CAL', 'Human Input': 'HUM', 'System Result': 'SYS' }
  return codes[kind]
}

function EvidencePreview({ item }: { item: EvidenceViewModel }) {
  if (item.kind === 'Spreadsheet') {
    return <div className="mock-sheet" role="table" aria-label={`${item.title} mock preview`}>{item.preview.map((line) => { const [label, ...value] = line.split(': '); return <div role="row" key={line}><span role="cell">{label}</span><strong role="cell">{value.join(': ')}</strong></div> })}</div>
  }
  return <dl className="preview-fields">{item.preview.map((line) => { const [term, ...value] = line.split(': '); return <div key={line}><dt>{term}</dt><dd>{value.join(': ') || '—'}</dd></div> })}</dl>
}

function RelationButton({ item, label, onSelect }: { item?: EvidenceViewModel; label: string; onSelect: (id: string) => void }) {
  if (!item) return null
  return <button className="relationship-link" onClick={() => onSelect(item.id)}><span>{label}</span><strong>{item.title}</strong><Icon name="chevron" size={13} /></button>
}

export function EvidencePanel({ evidence, tasks, selectedId, selectedTaskId, usedIds, operator, onSelect, onTaskSelect, onAction }: Props) {
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState<EvidenceFilter>('All')
  const [relevantOnly, setRelevantOnly] = useState(false)
  const selected = evidence.find((item) => item.id === selectedId) ?? evidence[0]
  const normalizedQuery = query.trim().toLowerCase()
  const filtered = useMemo(() => evidence.filter((item) => {
    const searchable = [item.title, item.source, item.sourceType, item.kind, item.summary].join(' ').toLowerCase()
    return (!normalizedQuery || searchable.includes(normalizedQuery)) && matchesFilter(item, filter) && (!relevantOnly || usedIds.includes(item.id))
  }), [evidence, filter, normalizedQuery, relevantOnly, usedIds])

  const related = selected ? evidence.filter((item) => selected.conflictsWithIds?.includes(item.id) || item.id === selected.supersedesId || item.id === selected.supersededById) : []
  const derivedInputs = selected?.derivedFromIds?.map((id) => evidence.find((item) => item.id === id)).filter((item): item is EvidenceViewModel => Boolean(item)) ?? []
  const usedBy = selected ? selected.taskIds.map((id) => tasks.find((task) => task.id === id)).filter((task): task is TaskViewModel => Boolean(task)) : []

  return (
    <aside className="right-column">
      <section className="panel evidence-panel">
        <div className="panel-heading evidence-heading"><div><span className="section-kicker">Evidence workspace</span><h2>Evidence {evidence.length}</h2></div><span className="scope-chip"><Icon name="shield" size={12} /> Mock · scoped</span></div>
        <div className="evidence-toolbar">
          <label className="evidence-search"><span className="sr-only">Search evidence</span><Icon name="search" size={15} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search evidence" aria-label="Search evidence" /></label>
          <div className="evidence-filter-row" aria-label="Evidence filters">{FILTERS.map((item) => <button key={item} className={filter === item ? 'active' : ''} aria-pressed={filter === item} onClick={() => setFilter(item)}>{item}</button>)}</div>
          <label className="relevant-toggle"><input type="checkbox" checked={relevantOnly} onChange={(event) => setRelevantOnly(event.target.checked)} disabled={!selectedTaskId} /><span>Relevant to selected task</span></label>
          <p className="evidence-count">Showing {filtered.length} of {evidence.length} · linked items stay highlighted</p>
        </div>
        <div className="evidence-list" aria-label="Workflow evidence">
          {filtered.length ? filtered.map((item) => {
            const relevant = usedIds.includes(item.id)
            return <button key={item.id} className={`${item.id === selectedId ? 'selected' : ''} ${relevant ? 'task-relevant' : ''} ${item.status === 'Superseded' ? 'superseded' : ''}`} onClick={() => onSelect(item.id)} aria-pressed={item.id === selectedId}>
              <span className={`file-kind kind-${item.kind.toLowerCase().replaceAll(' ', '-')}`}>{kindCode(item.kind)}</span>
              <span className="evidence-row-main"><strong>{item.title}</strong><small>{item.kind} · {item.source}</small><span className={`evidence-status status-${item.status.toLowerCase().replaceAll(' ', '-')}`}>{item.status}</span>{item.version && <em>{item.version}</em>}</span>
              <span className="task-use">{relevant ? <><i className="used-dot" />Used</> : `${item.taskIds.length} task${item.taskIds.length === 1 ? '' : 's'}`}</span>
            </button>
          }) : <div className="evidence-empty"><strong>No evidence matches</strong><p>Clear the search or change the filter to inspect other workflow evidence.</p></div>}
        </div>
        {selected ? <div className={`evidence-inspector inspector-${selected.status.toLowerCase().replaceAll(' ', '-')}`}>
          <div className="inspector-head"><div><span className="section-kicker">Selected evidence</span><h3>{selected.title}</h3><div className="inspector-badges"><span>{selected.kind}</span><span className={`evidence-status status-${selected.status.toLowerCase().replaceAll(' ', '-')}`}>{selected.status}</span><span>{selected.inspected ? 'Inspected' : 'Not inspected'}</span></div></div><span className="mock-label">MOCK PREVIEW</span></div>
          {selected.status === 'Missing' && <div className="evidence-alert missing-alert"><strong>Missing evidence</strong><p>{selected.summary}</p><span>{selected.requestState ?? 'Not requested'}</span></div>}
          {selected.status === 'Conflicting' && <div className="evidence-alert conflict-alert"><strong>Conflict detected</strong><p>{selected.conflictNote}</p></div>}
          <div className="inspector-summary"><label>What this evidence supports</label><p>{selected.summary}</p></div>
          <div className="preview-surface"><div className="preview-title"><span>{selected.filename ?? selected.sourceType}</span><small>Read-only fixture</small></div><EvidencePreview item={selected} /></div>
          <dl className="evidence-facts"><div><dt>Source</dt><dd>{selected.source}</dd></div><div><dt>Source type</dt><dd>{selected.sourceType}</dd></div><div><dt>Source role</dt><dd>{selected.sourceRole}</dd></div><div><dt>Version</dt><dd>{selected.version ?? 'Not versioned'}</dd></div><div><dt>Updated</dt><dd>{selected.updatedAt}</dd></div>{selected.metadata.map((fact) => <div key={fact.label}><dt>{fact.label}</dt><dd>{fact.value}</dd></div>)}</dl>
          {derivedInputs.length > 0 && <section className="lineage-section"><label>Evidence lineage</label><div className="lineage-inputs">{derivedInputs.map((item) => <button key={item.id} onClick={() => onSelect(item.id)}>{item.title}</button>)}</div><div className="lineage-arrow">↓</div><strong>{selected.title}</strong></section>}
          {(related.length > 0 || selected.supersedesId || selected.supersededById) && <section className="relationship-section"><label>Related evidence</label>{selected.supersedesId && <RelationButton item={evidence.find((item) => item.id === selected.supersedesId)} label="Supersedes" onSelect={onSelect} />}{selected.supersededById && <RelationButton item={evidence.find((item) => item.id === selected.supersededById)} label="Current replacement" onSelect={onSelect} />}{related.filter((item) => selected.conflictsWithIds?.includes(item.id)).map((item) => <RelationButton key={item.id} item={item} label="Conflicts with" onSelect={onSelect} />)}</section>}
          <section className="used-by-section"><label>Used by tasks</label>{usedBy.length ? usedBy.map((task) => <button key={task.id} className={task.id === selectedTaskId ? 'current' : ''} onClick={() => onTaskSelect(task.id)}><span>{task.id === selectedTaskId ? '✓' : '○'}</span><strong>{task.title}</strong><small>{task.status}</small></button>) : <p>Not linked to a task yet.</p>}</section>
          <div className="evidence-actions"><button disabled={selected.inspected || selected.status === 'Missing'} onClick={() => onAction('Mark Reviewed')}>{selected.inspected ? 'Reviewed' : 'Mark Reviewed'}</button>{selected.status === 'Missing' && <button className="primary-action" disabled={selected.requestState === 'Requested'} onClick={() => onAction('Request Evidence')}>{selected.requestState === 'Requested' ? 'Requested' : 'Request Evidence'}</button>}{selected.status !== 'Missing' && selected.status !== 'Conflicting' && <button onClick={() => onAction('Flag Conflict')}>Flag Conflict</button>}</div>
        </div> : <div className="evidence-empty evidence-empty-workflow"><strong>No evidence has been collected yet.</strong><p>Once the runtime is connected, Workflow Governor will inspect the authorized workspace and surface relevant evidence here.</p></div>}
      </section>
      <section className="panel operator-card"><div className="operator-avatar">{operator.name.split(' ').map((part) => part[0]).join('').slice(0, 2)}</div><div className="operator-main"><span className="section-kicker">Current operator</span><h3>{operator.name}</h3><p>{operator.id} · {operator.role}</p></div><div className="operator-facts"><div><span>Evidence</span><strong>{operator.evidenceState}</strong></div><div><span>Scaffolding</span><strong>{operator.scaffolding}</strong></div></div></section>
    </aside>
  )
}
