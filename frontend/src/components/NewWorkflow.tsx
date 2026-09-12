import { useEffect, useState, type FormEvent } from 'react'
import type { NewWorkflowInput } from '../types'
import { api } from '../api'
export function NewWorkflow({onCancel,onStart}:{onCancel:()=>void;onStart:(input:NewWorkflowInput)=>void}) {
 const [objective,setObjective]=useState(''),[name,setName]=useState(''),[workspace,setWorkspace]=useState('')
 const [grants,setGrants]=useState<{id:string;label:string}[]>([]),[files,setFiles]=useState<{id:string;name:string;extractable:boolean}[]>([])
 const [selected,setSelected]=useState<string[]>([]),[error,setError]=useState(''),[loading,setLoading]=useState(true)
 useEffect(()=>{api<{id:string;label:string}[]>('/workspaces').then(v=>{setGrants(v);setWorkspace(v[0]?.id||'')}).catch(e=>{setError(String(e));setLoading(false)})},[])
 useEffect(()=>{if(!workspace)return;setLoading(true);setSelected([]);api<typeof files>(`/workspaces/${workspace}/files`).then(setFiles).catch(e=>setError(String(e))).finally(()=>setLoading(false))},[workspace])
 const submit=(e:FormEvent)=>{e.preventDefault();if(!selected.length){setError('Select at least one authorized file.');return}onStart({name:name.trim()||undefined,objective:objective.trim(),workspace,sourceIds:selected})}
 return <><h1>New workflow</h1><p className="page-description">Start with a goal. Select the materials this workflow may use.</p><form className="new-workflow-form" onSubmit={submit}>
 <label className="form-field"><span>Goal</span><textarea autoFocus required maxLength={4000} rows={4} value={objective} onChange={e=>setObjective(e.target.value)} placeholder="What do you need to work out?"/></label>
 <label className="form-field"><span>Name <em>Optional</em></span><input maxLength={160} value={name} onChange={e=>setName(e.target.value)} placeholder="Use a short, recognizable name"/></label>
 <label className="form-field"><span>Authorized workspace</span><select required value={workspace} onChange={e=>setWorkspace(e.target.value)}>{grants.map(g=><option key={g.id} value={g.id}>{g.label}</option>)}</select><small>Only files in the selected server-authorized workspace are available.</small></label>
 <fieldset className="file-selection"><legend>Materials · select up to 8 files</legend>{loading?<p role="status">Loading available files…</p>:files.filter(f=>f.extractable).map(f=><label key={f.id}><input type="checkbox" checked={selected.includes(f.id)} disabled={selected.length>=8&&!selected.includes(f.id)} onChange={e=>setSelected(old=>e.target.checked?[...old,f.id]:old.filter(x=>x!==f.id))}/><span>{f.name}</span></label>)}{!loading&&!files.length&&<p>No authorized files available.</p>}</fieldset>
 {error&&<p role="alert" className="form-error">{error}</p>}<div className="form-actions"><button type="button" onClick={onCancel}>Cancel</button><button className="primary-action" disabled={loading||!selected.length}>Create workflow</button></div></form></>
}
