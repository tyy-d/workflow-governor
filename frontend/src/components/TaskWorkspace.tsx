import { useEffect, useState } from 'react'
import type { EvidenceViewModel, HumanAction, HumanInput, OperatorViewModel, PlanState, TaskViewModel } from '../types'
import { ExecutorBadge, StatusBadge } from './Badges'
interface Props {
 task:TaskViewModel; tasks:TaskViewModel[]; evidence:EvidenceViewModel[]; operator:OperatorViewModel; planState:PlanState; busy:boolean;
 onEvidenceSelect:(id:string,line?:number)=>void; onHumanAction:(action:HumanAction,input:HumanInput)=>void; onExecute:()=>void; onResume:(note:string)=>void
}
export function TaskWorkspace({task,tasks,evidence,operator,planState,busy,onEvidenceSelect,onHumanAction,onExecute,onResume}:Props) {
 const draftKey=`human-draft:${window.location.hash}:${task.id}`
 const [input,setInput]=useState<HumanInput>(()=>{try{return JSON.parse(localStorage.getItem(draftKey)||'null')||{operator:'',judgment:'',reason:''}}catch{return {operator:'',judgment:'',reason:''}}})
 const [note,setNote]=useState('')
 useEffect(()=>{localStorage.setItem(draftKey,JSON.stringify(input))},[draftKey,input])
 const ready=planState==='APPROVED'&&!busy
 const actions:HumanAction[]=['Complete','Ask Clarification','Narrow Task','Request Reassignment','Decline Authority']
 return <main className="panel task-workspace">
  <div className="panel-heading task-heading"><div><span className="section-kicker">Task {task.id}</span><h2>{task.title}</h2></div><div className="task-heading-badges"><StatusBadge status={task.status}/><ExecutorBadge executor={task.executor}/></div></div>
  <div className="task-objective"><label>Task objective</label><p>{task.objective}</p></div>
  <section className="routing-rationale"><div><label>Why this executor</label><p>{task.rationale}</p></div></section>
  <section className="input-list"><label>Granted evidence</label>{task.evidenceIds.map(id=><button key={id} onClick={()=>onEvidenceSelect(id)}>{id} · {evidence.find(e=>e.id===id)?.title}</button>)}</section>
  <section className="output-card"><label>Expected output</label><p>{task.expectedOutput}</p></section>
  <div className="dependency-section"><label>Dependencies</label>{task.dependencyIds.length?task.dependencyIds.map(id=><p key={id}>{id} · {tasks.find(t=>t.id===id)?.status}</p>):<p>None</p>}</div>
  {!ready&&planState!=='APPROVED'&&<p>Approve this plan before execution.</p>}
  {task.executor!=='Human'&&task.status==='Ready'&&<button className="primary-action" disabled={!ready} onClick={onExecute}>Execute Task</button>}
  {task.status==='Running'&&<p role="status">Executing on this GB10. Real results will appear when complete.</p>}
  {task.status==='Blocked'&&<section className="human-card"><h3>Blocked — recovery required</h3><p>{task.blockReason}</p><label className="form-field">Recovery reason<textarea value={note} onChange={e=>setNote(e.target.value)} placeholder="What changed or why should this task be retried?"/></label><button disabled={!ready||!note.trim()} onClick={()=>onResume(note)}>Resume Task</button></section>}
  {task.executor==='Human'&&!operator&&<section className="notice"><h3>Waiting for an authorized operator</h3><p>Human assignment and authority verification are not connected. This task stays pending. No decision has been recorded.</p></section>}
  {task.executor==='Human'&&operator&&<section className="human-card"><h3>Human judgment and rationale</h3><p>Record your bounded review. This does not activate a vendor or transmit a purchase order.</p>
   <label className="form-field">Reviewer name<input aria-label="Reviewer name" value={input.operator} onChange={e=>setInput({...input,operator:e.target.value})}/></label>
   <label className="form-field">Judgment<textarea aria-label="Judgment" value={input.judgment} onChange={e=>setInput({...input,judgment:e.target.value})}/></label>
   <label className="form-field">Reason and evidence references<textarea aria-label="Reason and evidence references" value={input.reason} onChange={e=>setInput({...input,reason:e.target.value})}/></label>
   <div className="human-actions">{actions.map(action=><button key={action} className={action==='Complete'?'primary-action':''} disabled={!ready||task.status!=='Needs Human'||!input.operator.trim()||!input.judgment.trim()||!input.reason.trim()} onClick={()=>onHumanAction(action,input)}>{action}</button>)}</div>
   {task.humanResponse&&<pre className="actual-result">{JSON.stringify(task.humanResponse,null,2)}</pre>}
  </section>}
  {task.result&&<section className="actual-result"><h3>Saved execution result</h3><p>{task.result.summary}</p>{task.result.findings.map((f,i)=><div key={i}><p>{f.statement}</p>{f.citations.map((c,j)=><button key={j} onClick={()=>onEvidenceSelect(c.sourceId,c.line)}>{c.sourceId}:L{c.line}</button>)}</div>)}</section>}
 </main>
}
