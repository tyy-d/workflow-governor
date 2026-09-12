import type { WorkflowViewModel } from '../types'

export function PlanningEmptyState({ workflow }: { workflow: WorkflowViewModel }) {
  return <main className="planning-console"><section className="empty-state planning-empty"><span className="section-kicker">Plan state · {workflow.planState}</span><h2>No plan has been proposed yet.</h2><p>The runtime will inspect the authorized workspace and propose the work required once connected.</p><dl><div><dt>Evidence</dt><dd>No evidence has been collected yet. Once the runtime is connected, Workflow Governor will inspect the authorized workspace and surface relevant evidence here.</dd></div><div><dt>Activity</dt><dd>No execution activity has occurred.</dd></div><div><dt>Final result</dt><dd>No final state is available while planning has not begun.</dd></div></dl><span className="mock-notice">Frontend-only planning state · no runtime execution</span></section></main>
}
