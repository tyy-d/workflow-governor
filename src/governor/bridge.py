"""Adapters to Thomas's shared contracts; no changes to his owned modules.
The web API schedules one task at a time. Full plans are validated first, then
MinimalTaskRunner receives a one-task projection plus durable predecessor states.
"""
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from workflow_governor.core.models import (EvidenceRef,EvidenceContent,FileRecord,WorkspaceMap,TaskSpec,TaskContext,TaskResult,WorkflowPlan,ExecutorType,ExecutionStatus,PlanStatus)
from workflow_governor.planning.planner import Planner,PlanningRequest
from workflow_governor.planning.validation import PlanValidator
from workflow_governor.planning.lifecycle import PlanLifecycle,PlanRecord
from workflow_governor.model.local import LocalModelExecutor,ModelContextBuilder
from workflow_governor.execution.runner import MinimalTaskRunner,RunState,TaskExecutionState

EXECUTORS={'Deterministic':ExecutorType.DETERMINISTIC,'Local AI':ExecutorType.LOCAL_MODEL,'Human':ExecutorType.HUMAN}

def serial(value):
    if hasattr(value,'__dataclass_fields__'):return serial(asdict(value))
    if isinstance(value,dict):return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [serial(v) for v in value]
    if isinstance(value,datetime):return value.isoformat()
    if isinstance(value,Enum):return value.value
    return value

def spec(t,sources):
    selected=[s for s in sources if s['id'] in t['evidenceIds']]
    return TaskSpec(t['id'],t['title'],t['objective'],EXECUTORS[t['executor']],tuple(t['dependencyIds']),
        tuple(EvidenceRef(s['path'],artifact_id=s['id']) for s in selected if not s.get('policy')),
        tuple(EvidenceRef(s['path'],artifact_id=s['id']) for s in selected if s.get('policy')),
        (t['expectedOutput'],),authority_requirement='Local review only. External corporate authority is not verified.',
        operation='inspect_records' if t['executor']=='Deterministic' else None)

def shared_plan(w,draft=None,sources=None):
    sources=sources if sources is not None else w['sources'];tasks=draft['tasks'] if draft else w['tasks']
    return WorkflowPlan(w['id'],w.get('planNumber',1),w['objective'],tuple(spec(t,sources) for t in tasks),
        tuple((draft or w).get('assumptions',[])),tuple((draft or w).get('questions',[])))

def validate_generated(w,draft,sources,inventory):
    class GeneratedDraftAdapter:
        def create_plan(self,request):return shared_plan(w,draft,sources)
    evidence=tuple(EvidenceContent(EvidenceRef(s['path']),s['content'],not s.get('policy')) for s in sources if not s.get('policy'))
    policy=tuple(EvidenceContent(EvidenceRef(s['path']),s['content'],False) for s in sources if s.get('policy'))
    request=PlanningRequest(w['objective'],WorkspaceMap(w['workspaceKey'],tuple(FileRecord(x['path'],x['name'],size=x['size']) for x in inventory)),evidence,policy)
    return Planner(GeneratedDraftAdapter(),PlanValidator(allowed_evidence_sources=[s['path'] for s in sources],supported_operations=['inspect_records'])).plan(request)

def approve(w):
    return PlanLifecycle().approve(PlanRecord(shared_plan(w),PlanStatus.PROPOSED),actor='local-reviewer')

def execute_bounded(w,t,sources,previous,directory,payload=None,artifact_store=None):
    from . import model
    from .deterministic import inspect_records
    details={}
    task=spec(t,w['sources'])
    context=TaskContext(task.task_id,
        evidence=tuple(EvidenceContent(EvidenceRef(s['path'],artifact_id=s['id']),s['content']) for s in sources if not s.get('policy')),
        policy=tuple(EvidenceContent(EvidenceRef(s['path'],artifact_id=s['id']),s['content'],False) for s in sources if s.get('policy')),
        workflow_state={'goal':w['objective'],'previousResults':previous},granted_sources=tuple(s['path'] for s in sources))
    class Adapter:
        def generate(self,request):
            details.update(model.call('Execute the bounded task. Cite only sourceId and line from the supplied numbered extracts. The server resolves the exact original quotation; do not generate a quote field. Reflect actual prior results and human judgment. Preserve business blockers; never claim external activation or PO transmission. Use 3-4 concise findings. Cite the line containing the factual support, not a blank line. Include source ID and line references in blocker/action/authority strings when applicable.',payload,model.RESULT_SCHEMA,directory,'execution',1800))
            model.validate_citations(details,sources)
            mapping={s['id']:s['path'] for s in sources}
            return {'findings':[f['statement'] for f in details['findings']],
                    'evidence_refs':[{'source':mapping[c['sourceId']]} for f in details['findings'] for c in f['citations']],
                    'conclusions':[details['summary']], 'assumptions':[], 'unresolved':details['blockers'],'rationale':'Evidence-grounded local Qwen execution; exact citations checked by integration adapter.'}
    class RecordExecutor:
        def execute(self,task,context):
            details.update(inspect_records(sources))
            return TaskResult(task.task_id,ExecutionStatus.COMPLETED,task.executor_type,
                findings=tuple(f['statement'] for f in details['findings']),evidence_refs=task.evidence_requirements,
                rationale=details['summary'],output=details)
    executor=RecordExecutor() if t['executor']=='Deterministic' else LocalModelExecutor(Adapter(),context_builder=ModelContextBuilder(max_files=14,max_characters=48000),malformed_retries=0)
    class ContextProvider:
        def get_context(self,task,run_state):return context
    class Sink:
        def __init__(self):self.events=[]
        def record(self,event):self.events.append(serial(event))
    sink=Sink()
    state=RunState(w['id'],mock_assisted=False)
    for dep in t['dependencyIds']:
        actual=next(x for x in w['tasks'] if x['id']==dep)
        if actual['status']!='Completed':raise ValueError('Predecessor is not complete')
        state.task_states[dep]=TaskExecutionState(dep,status=ExecutionStatus.COMPLETED)
    projection=WorkflowPlan(w['id'],w['planNumber'],w['objective'],(task,))
    MinimalTaskRunner({task.executor_type:executor}).run(PlanRecord(projection,PlanStatus.APPROVED),state,ContextProvider(),sink,None)
    result=state.task_states[t['id']].result
    from pathlib import Path
    import json
    Path(directory).mkdir(parents=True,exist_ok=True)
    Path(directory,'core-execution.json').write_text(json.dumps({'runner':'MinimalTaskRunner','mock_assisted':False,'events':sink.events,'result':serial(result)},ensure_ascii=False,indent=2))
    if artifact_store is not None:
        artifact_store.save_context(w['id'],context)
        if result is not None and result.status==ExecutionStatus.COMPLETED:artifact_store.save_result(w['id'],result)
    if result is None or result.status!=ExecutionStatus.COMPLETED:raise ValueError(result.error or '; '.join(result.unresolved) if result else 'Missing core result')
    return details
