import { useState } from 'react'
import type { TaskViewModel, WorkflowViewModel } from '../types'
import { Icon } from './Icon'

type Section = 'tasks' | 'evidence' | 'results' | 'history'
type OpenWorkflow = (id: string, section?: Section, taskId?: string, evidenceId?: string, line?: number) => void

const ownerLabel = (task: TaskViewModel) => ({Deterministic:'Automated checks','Local AI':'Qwen analysis',Human:'Human judgment'}[task.executor])
const statusLabel = (status: string) => ({Completed:'Done',Ready:'Ready to run',Running:'In progress','Needs Human':'Needs a reviewer',Pending:'Waiting',Blocked:'Needs attention'}[status] || status)
const readable = (text: string) => text
 .replace(/\s*\((?:E|P)-[a-f\d]+ L\d+\)/g, '')
 .replace(/\s*\[(?:E|P)-[a-f\d]+:L\d+\]/g, '')
 .replaceAll('commercial_po_eligible', 'purchase-order eligibility')

export function BusinessDashboard({workflows,onOpen,onNew,onAll}:{workflows:WorkflowViewModel[];onOpen:OpenWorkflow;onNew:()=>void;onAll:()=>void}) {
 const [selected,setSelected]=useState('')
 // Historical acceptance runs are inspectable elsewhere, not business performance totals.
 const current=workflows.filter(w=>!w.readOnly)
 const preferred=current.find(w=>w.tasks.some(t=>t.executor==='Local AI'&&t.status==='Completed'&&t.result)) || current.find(w=>w.tasks.length) || current[0]
 const workflow=current.find(w=>w.id===selected)||preferred
 const completed=workflow?.tasks.filter(t=>t.status==='Completed'&&t.result) || []
 const analysis=[...completed].reverse().find(t=>t.executor==='Local AI')
 const findings=analysis?.result?.findings || []
 const blockers=analysis?.result?.blockers || []
 const nextActions=analysis?.result?.nextActions || []
 const waiting=workflow?.tasks.find(t=>t.status==='Needs Human')
 const timestamp=workflow?new Date(workflow.updatedAt).toLocaleString([],{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}):''
 return <div className="business-dashboard">
  <div className="dashboard-heading"><div className="overview-title"><span className="overview-icon"><Icon name="panel" size={25}/></span><h1>Overview</h1></div><button className="primary-action" onClick={onNew}>+ New workflow</button></div>
  <section className="live-case" aria-labelledby="live-case-title">

   {!workflow?<div className="empty"><h2>No saved work yet</h2><p>Create a workflow to begin.</p><button onClick={onNew}>New workflow</button></div>:<>
    <div className="case-heading"><div><h2 id="live-case-title">{workflow.name}</h2><p>{workflow.workspace} <span>· Updated {timestamp}</span></p></div><label className="case-picker"><select aria-label="Featured workflow" value={workflow.id} onChange={e=>setSelected(e.target.value)}>{current.map(w=><option key={w.id} value={w.id}>{w.name}</option>)}</select></label></div>
    <div className="case-summary"><div><p>{workflow.objective.split(/(?<=[.!?])\s/)[0]}</p></div><button className="primary-action" onClick={()=>onOpen(workflow.id)}>Open workflow <span aria-hidden="true">↗</span></button></div>
    <dl className="run-facts"><div><dt>Tasks done</dt><dd>{completed.length}<span> / {workflow.tasks.length} tasks</span></dd></div><div><dt>Sources</dt><dd>{workflow.evidence.length}</dd></div><div><dt>Cited findings</dt><dd>{findings.filter(f=>f.citations.length>0).length}</dd></div></dl>
    {workflow.error&&<div className="notice danger" role="alert"><strong>This run needs attention</strong><p>{workflow.error}</p><button onClick={()=>onOpen(workflow.id)}>Review and retry</button></div>}
    {workflow.operation&&<div className="notice" role="status"><span className="spinner"/>{workflow.operation}. Saved results will update when the work finishes.</div>}
    <div className="business-grid">
     <section className="business-analysis"><div className="dashboard-section-heading"><h3>Key findings</h3>{analysis&&<button onClick={()=>onOpen(workflow.id,'tasks',analysis.id)}>Full analysis ↗</button>}</div>
      {analysis?.result?<><p className="executive-takeaway">{readable(analysis.result.summary)}</p><div className="business-findings">{findings.map((f,i)=><details className="finding-entry" key={i}><summary><span>{readable(f.statement)}</span><small>{f.citations.length} sources</small></summary><div><p>{readable(f.statement)}</p><div className="business-citations">{f.citations.map((c,j)=>{const source=workflow.evidence.find(e=>e.id===c.sourceId);return <button key={j} title={source?.filename||source?.title} aria-label={`Inspect source for finding ${i+1}, line ${c.line}`} onClick={()=>onOpen(workflow.id,'evidence',undefined,c.sourceId,c.line)}><Icon name="file" size={12}/>{source?.kind||'Source'} · line {c.line}</button>})}</div></div></details>)}</div></>:<div className="empty"><h3>{workflow.operation?'Analysis is in progress':'Ready to put the plan to work'}</h3><p>{workflow.tasks.length?'Open the workflow to approve the plan and run its ready tasks.':'Generate a plan from the selected documents to begin.'}</p><button onClick={()=>onOpen(workflow.id)}>Continue workflow</button></div>}
     </section>
     <section className="business-allocation"><div className="dashboard-section-heading"><h3>Plan</h3></div><ol>{workflow.tasks.map((task,i)=><li key={task.id}><button onClick={()=>onOpen(workflow.id,'tasks',task.id)}><span className={`allocation-marker ${task.status==='Completed'?'allocation-done':''}`}>{task.status==='Completed'?<Icon name="check" size={13}/>:i+1}</span><span className="allocation-content"><strong>{task.title}</strong><small>{ownerLabel(task)}</small><span className={`status-text status-${task.status.toLowerCase().replaceAll(' ','-')}`}>{statusLabel(task.status)}</span></span><span className="allocation-arrow" aria-hidden="true">↗</span></button></li>)}</ol>{!workflow.tasks.length&&<p className="muted">The plan will show each task and who handles it.</p>}</section>
    </div>
    <section className="decision-brief"><div className="decision-title"><Icon name="person"/><div><h3>{waiting?'Review needed':blockers.length?'Open issues':'Next step'}</h3></div></div><details className="decision-details"><summary>{blockers.length} open issues · {nextActions.length} next steps</summary><div className="decision-columns"><div><h4>Open issues</h4>{blockers.length?blockers.map((b,i)=><p key={i}>{readable(b)}</p>):<p className="muted">{analysis?'No blockers were recorded in this analysis.':'No analysis has been saved yet.'}</p>}</div><div><h4>Suggested follow-up</h4>{nextActions.length?nextActions.map((a,i)=><p key={i}>{readable(a)}</p>):<p className="muted">{workflow.planState==='PROPOSED'?'Review and approve the proposed plan.':'Open the workflow to see its next available step.'}</p>}</div></div></details>{waiting&&<p className="human-availability">Reviewer assignment unavailable</p>}<button onClick={()=>onOpen(workflow.id,waiting?'tasks':'results',waiting?.id)}>{waiting?'Open handoff':'Next steps'} ↗</button></section>
    <div className="dashboard-footer"><span>Updated {timestamp}</span><div><button onClick={()=>onOpen(workflow.id,'evidence')}>Evidence</button><button onClick={()=>onOpen(workflow.id,'history')}>Activity</button></div></div>
   </>}
  </section>
  <div className="dashboard-bottom"><button onClick={onAll}>All workflows ↗</button></div>
 </div>
}
