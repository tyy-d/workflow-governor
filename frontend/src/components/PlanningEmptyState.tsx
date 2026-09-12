import type { WorkflowViewModel } from '../types'
export function PlanningEmptyState({workflow,onRetry}:{workflow:WorkflowViewModel;onRetry:()=>void}) {
 return <main className="planning-console"><section className="empty-state planning-empty"><h2>{workflow.operation?'Planning with local Qwen…':'Planning needs attention'}</h2><p>Only the selected authorized workspace and scoped policies are supplied to the local model. The proposed plan requires your approval.</p><p>Progress is saved on the server. Refreshing this page will not cancel it.</p>{!workflow.operation&&<button onClick={onRetry}>Retry Planning</button>}{workflow.activity.map(e=><p key={e.id}>{e.time} · {e.title}: {e.description}</p>)}</section></main>
}
