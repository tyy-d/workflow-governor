import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from . import model, bridge
from .store import STATUSES
from workflow_governor.core.substrate import RetrievedEvidence, WorkspaceGrant
from workflow_governor.core.models import EvidenceRef
from workflow_governor.core.models import ExecutionStatus, PlanStatus
from workflow_governor.execution.runner import HumanHandoff, MinimalTaskRunner, RunState, TaskExecutionState
from workflow_governor.human.contracts import human_response_from_mapping
from workflow_governor.integration.adapters import ArtifactExecutionEventSink
from workflow_governor.integration.human import apply_validated_human_response
from workflow_governor.planning.lifecycle import PlanRecord
from workflow_governor.workspace import WorkspaceScout, DiscoveryLimits


def now():return datetime.now(timezone.utc).isoformat()

def event(w,title,description,kind='system'):
    w['updatedAt']=now()
    w['activity'].append({'id':uuid.uuid4().hex,'time':now(),'title':title,'description':description,'kind':kind})

def validate_plan(plan, sources):
    tasks=plan['tasks'];seen=set();evidence={s['id'] for s in sources}
    for task in tasks:
        import re
        if not re.fullmatch(r'T[1-9][0-9]*',task['id']) or task['id'] in seen:
            raise ValueError('Task IDs must be distinct T1, T2, ...')
        if not set(task['dependencyIds'])<=seen:raise ValueError('Dependencies must reference earlier tasks; cycles are not allowed')
        if not set(task['evidenceIds'])<=evidence:raise ValueError('Task refers to ungranted evidence')
        scope=task.get('requestedDecisionAuthorityScope','NO_DECISION')
        if scope not in ['NO_DECISION','ANALYSIS_OR_RECOMMENDATION','AUTHORITY_DECISION']:
            raise ValueError('Task has an invalid decision-authority scope')
        if scope=='AUTHORITY_DECISION' and not task.get('authorityRequirement'):
            raise ValueError('Authority-decision tasks require an explicit authority requirement')
        seen.add(task['id'])
    if not {'Deterministic','Local AI','Human'} <= {t['executor'] for t in tasks}:
        raise ValueError('The proposed plan must include deterministic, local-model and human review work')
    if tasks[-1]['executor']!='Local AI' or set(tasks[-1]['dependencyIds'])!=seen-{tasks[-1]['id']}:
        raise ValueError('Final synthesis must depend on all other tasks')
    return plan

class Service:
    def __init__(self,store,workspace,*,human_validator=None,human_interactions=None):
        self.store=store;self.workspace=workspace
        # Identity and authority providers are deliberately injected. The web
        # projection must never manufacture either capability.
        self.human_validator=human_validator;self.human_interactions=human_interactions
        for w in store.list():
            if w.get('operation') and not w.get('readOnly'):
                w['error']='Server interrupted the operation. Review state and retry; completed results were preserved.'
                w['operation']=None;w['status']='Blocked'
                for t in w['tasks']:
                    if t['status']=='Running':t['status']='Blocked';t['blockReason']=w['error']
                event(w,'Interrupted operation',w['error']);self.save(w)

    def save(self,w):
        self.refresh(w)
        if w.get('storageVersion')==2 and w.get('planState')=='APPROVED':
            pending=[t for t in w['tasks'] if t['executor']=='Human' and t['status']=='Needs Human' and not t.get('humanHandoff')]
            if pending:
                record=PlanRecord(bridge.shared_plan(w),PlanStatus.APPROVED)
                specs={task.task_id:task for task in record.plan.tasks}
                for task in pending:
                    handoff=MinimalTaskRunner.create_handoff(record,w['id'],specs[task['id']],created_at=w.get('approvedAt') or w['updatedAt'])
                    if self.human_interactions is not None:self.human_interactions.write_handoff(handoff)
                    task['humanHandoff']=handoff.to_dict()
        if not (self.store.directory(w['id'])/'manifest.json').exists():self.store.save(w)
        d=self.store.directory(w['id'])
        if w.get('storageVersion')==2:
            for t in w['tasks']:
                self.store.artifacts.save_task_status(w['id'],t['id'],STATUSES.get(t['status'],t['status']))
            self.store.artifacts.save_final_artifact(w['id'],'summary.json',__import__('json').dumps(w['finalState'],ensure_ascii=False))
            self.store.save(w)
        else:
            # Compatibility writes retain the original legacy schema, without migration.
            for t in w['tasks']:
                self.store.write_json(d/'tasks'/t['id']/'task.json',t)
                if t.get('result'):self.store.write_json(d/'tasks'/t['id']/'result.json',t['result'])
            self.store.write_json(d/'final'/'summary.json',w['finalState'])
            self.store.save(w)

    def refresh(self,w):
        if w['planState']=='APPROVED':
            for t in w['tasks']:
                if t['status']=='Pending' and all(next(x for x in w['tasks'] if x['id']==dep)['status']=='Completed' for dep in t['dependencyIds']):
                    t['status']='Needs Human' if t['executor']=='Human' else 'Ready'
            statuses=[t['status'] for t in w['tasks']]
            w['status']=('Completed' if statuses and all(s=='Completed' for s in statuses) else
                         'In Progress' if 'Running' in statuses else 'Needs Human' if 'Needs Human' in statuses else
                         'In Progress' if 'Ready' in statuses else 'Blocked' if 'Blocked' in statuses else 'Planning')
            w['stage']=next((t['title'] for t in w['tasks'] if t['status']!='Completed'),'Review finalized — external actions not performed')
        final={'findings':[],'blockers':[],'nextActions':[],'authorityDecisions':[]}
        finished=[t for t in w['tasks'] if t.get('result')]
        # Once final task completes its synthesis supersedes intermediate narrative, without removing history.
        results=[finished[-1]] if w['tasks'] and w['tasks'][-1].get('result') else finished
        for t in results:
            r=t['result']
            for f in r.get('findings',[]):
                cites=' '.join(f"[{c['sourceId']}:L{c['line']}]" for c in f.get('citations',[]))
                final['findings'].append(f['statement']+' '+cites)
            for key in ['blockers','nextActions','authorityDecisions']:final[key].extend(r.get(key,[]))
        for t in w['tasks']:
            if t['status']=='Blocked':final['blockers'].append(t['title']+': '+t.get('blockReason','Unresolved'))
            elif t['status']!='Completed':final['nextActions'].append(t['title']+' ('+t['status']+')')
        if w.get('error'):final['blockers'].append(w['error'])
        w['finalState']={k:list(dict.fromkeys(v)) for k,v in final.items()}

    def create(self,data):
        key=data['workspace'];objective=data['objective'].strip()
        if key not in self.workspace.grants or not objective or len(objective)>4000:raise ValueError('Select an authorized workspace and a bounded objective')
        identity=data.get('_identity') or 'WF-'+uuid.uuid4().hex[:12]
        selected=data.get('sourceIds',[])
        if selected:self.workspace.selected(key,selected)
        w={'id':identity,'name':data.get('name') or objective[:65],'objective':objective,'workspace':self.workspace.grants[key]['label'],
           'workspaceKey':key,'status':'Planning','stage':'Discovering authorized evidence','createdAt':now(),'updatedAt':now(),
           'planState':'NOT_PROPOSED','tasks':[],'evidence':[],'sources':[],'activity':[], 'finalState':{},'operation':None,
           'operator':{'id':'local-reviewer','name':'Local reviewer','role':'Review only; corporate authority not verified','evidenceState':'No capability assessment','scaffolding':'Evidence and reasons required'},'error':None}
        if self.store.grants is not None:
            w.update(storageVersion=2,selectedSourceIds=selected,operator=None,status='Draft',stage='Ready to plan')
        with self.store.lock:
            event(w,'Workflow created','Authorized workspace selected; no external systems will be modified.');self.save(w)
        return w if w.get('storageVersion')==2 else self.plan(identity)

    def launch(self,identity,label,work,task_id=None):
        with self.store.lock:
            w=self.store.read(identity)
            if w.get('readOnly'):raise ValueError('Saved artifacts require repair before execution')
            if w.get('operation'):raise ValueError('Another operation is running; wait for it to finish')
            if task_id is not None:
                task=next(t for t in w['tasks'] if t['id']==task_id)
                if w['planState']!='APPROVED' or task['status']!='Ready' or task['executor']=='Human':raise ValueError('Task is not approved and ready')
                task['status']='Running'
                event(w,'Task started',task['title'],'task')
            w['operation']=label;w['runId']='run-'+uuid.uuid4().hex;w['error']=None;event(w,'Operation started',label);self.save(w)
        def run():
            try:work()
            except Exception as e:
                with self.store.lock:
                    w=self.store.read(identity);w['error']=str(e);w['status']='Blocked'
                    for t in w['tasks']:
                        if t['status']=='Running':t['status']='Blocked';t['blockReason']=str(e)
                    event(w,'Operation failed',str(e));self.save(w)
                print('operation_failed',identity,label,str(e),flush=True)
            finally:
                with self.store.lock:
                    w=self.store.read(identity);w['operation']=None
                    self.store.write_json(self.store.directory(identity)/'artifacts'/'runs'/(w['runId']+'.json'),{'runId':w['runId'],'phase':label,'finishedAt':now(),'error':w.get('error'),'planVersion':w.get('planVersion'),'sourceHashes':{s['id']:s.get('sha256') for s in w.get('sources',[])},'model':model.MODEL,'temperature':0,'thinking':False})
                    self.save(w)
        threading.Thread(target=run,daemon=True).start()
        return self.store.read(identity)

    def plan(self,identity):
        w=self.store.read(identity)
        if w['planState'] not in ['NOT_PROPOSED','REVISION_REQUESTED']:
            raise ValueError('Only an unapproved/revision-requested plan may be generated')
        def work():
            w=self.store.read(identity);d=self.store.directory(identity);key=w['workspaceKey']
            version=int(w.get('planNumber',0))+1;logdir=d/'model'/f'plan-{version}-{uuid.uuid4().hex[:6]}'
            inventory=self.workspace.inventory(key)
            self.store.write_json(d/'input'/'workspace-map.json',inventory)
            selection={'sourceIds':w['selectedSourceIds']} if w.get('selectedSourceIds') else model.call('Choose up to 8 relevant available source IDs from filenames and metadata for the objective. Prefer primary status records, required-document evidence, structured checklists, governing transaction artifacts and communications; avoid brochures and duplicate/noise files. Do not guess contents.',
                {'goal':w['objective'],'files':inventory},model.object_schema({'sourceIds':model.arr(model.TEXT,minItems=1,maxItems=8)}),logdir,'discovery',450)
            selected=self.workspace.selected(key,selection['sourceIds'])
            followed=[] if w.get('selectedSourceIds') else self.workspace.referenced_pending(key,selected)
            sources=selected+followed+self.workspace.policies(key)
            if sum(len(s['content']) for s in sources)>44000:raise ValueError('Selected evidence exceeds bounded context budget; narrow the goal')
            self.store.write_json(d/'input'/'sources.json',sources)
            if w.get('storageVersion')==2:
                grant=WorkspaceGrant(key,self.workspace.grants[key]['root'])
                scout=WorkspaceScout(self.store.artifacts.config,grants=(grant,))
                self.store.artifacts.save_workspace_map(identity,scout.discover(grant,DiscoveryLimits(max_preview_chars=0)))
                self.store.artifacts.save_evidence(identity,[RetrievedEvidence(EvidenceRef(s['path'],artifact_id=s['id']),s['sha256'],s['sha256'],'unchanged',s['content'],False,now()) for s in sources])
            with self.store.lock:
                progress=self.store.read(identity);progress['operation']='Generating and validating plan';self.save(progress)
            from .compact_plan import generate
            taskplan=generate(w['objective'],w.get('revisionNote'),sources,logdir)
            validate_plan(taskplan,sources)
            core_plan=bridge.validate_generated(dict(w,planNumber=version),taskplan,sources,inventory)
            plan_dir=d/('artifacts/plans' if w.get('storageVersion')==2 else 'plans')
            self.store.write_json(plan_dir/f'v{version}-core.json',bridge.serial(core_plan))
            with self.store.lock:
                w=self.store.read(identity)
                if w['tasks']:
                    self.store.write_json(plan_dir/f"v{w['planNumber']}-superseded.json",dict(tasks=w['tasks'],state='SUPERSEDED'))
                tasks=[]
                for i,t in enumerate(taskplan['tasks']):
                    tasks.append(dict(t,sequence=i+1,status='Pending',stage=t['title'],
                                      humanRequest=t['objective'] if t['executor']=='Human' else None,
                                      consequenceLabel='Human Decision' if t['executor']=='Human' else None))
                w.update(tasks=tasks,sources=sources,planNumber=version,planVersion=f'v{version}',planState='PROPOSED',status='Planning',stage='Awaiting user plan approval',assumptions=taskplan['assumptions'],questions=taskplan['questions'])
                w['evidence']=[self.evidence_view(s,tasks) for s in sources]
                event(w,'Local model proposed plan',f"{len(tasks)} tasks; {len(selected)+len(followed)}/{len(inventory)} workspace files retrieved ({len(followed)} explicit pending-record references followed), plus {len(self.workspace.grants[key]['policies'])} scoped policies. Model {model.MODEL}. Approval required.")
                self.store.write_json(plan_dir/f'v{version}.json',dict(taskplan,state='PROPOSED'))
                (plan_dir/'plan.md').write_text('# Proposed plan\n\n'+w['objective']+'\n\n'+'\n'.join(f"- {t['id']}: {t['title']} ({t['executor']})" for t in tasks),encoding='utf-8')
                self.store.commit_plan(w,core_plan,'PROPOSED')
                self.save(w)
        return self.launch(identity,'Selecting authorized evidence',work)

    def evidence_view(self,s,tasks):
        kind='Policy' if s.get('policy') else 'Human Input' if s.get('human') else 'Spreadsheet' if s['path'].endswith('.csv') else 'Record' if s['path'].endswith('.json') else 'Document'
        return {'id':s['id'],'title':s['name'],'filename':s['name'],'kind':kind,'status':'Available','source':s['path'],
                'sourceType':'Authorized extract','sourceRole':'Authoritative Policy' if s.get('policy') else 'Human Observation' if s.get('human') else 'Operational Record',
                'summary':'Source content and line references are available below.','preview':s['content'].splitlines(),
                'taskIds':[t['id'] for t in tasks if s['id'] in t['evidenceIds']],
                'metadata':[{'label':'SHA-256','value':s.get('sha256','human input')}],'updatedAt':now()}

    def approve(self,identity):
        with self.store.lock:
            w=self.store.read(identity)
            if w.get('operation') or w['planState']!='PROPOSED':raise ValueError('A finished proposed plan is required')
            core_approval=bridge.approve(w)
            self.store.write_json(self.store.directory(identity)/('artifacts/plans' if w.get('storageVersion')==2 else 'plans')/f"v{w['planNumber']}-core-approval.json",bridge.serial(core_approval))
            self.store.commit_plan(w,bridge.shared_plan(w),'APPROVED')
            w['planState']='APPROVED';w['approvedAt']=now();event(w,'Plan approved','User approved this plan version for local evidence work; not a vendor/PO authorization.','human');self.save(w)
            self.store.write_json(self.store.directory(identity)/('artifacts/plans' if w.get('storageVersion')==2 else 'plans')/f"v{w['planNumber']}-approved.json",dict(tasks=w['tasks'],state='APPROVED',approvedAt=w['approvedAt']))
            return w

    def revise(self,identity,note):
        with self.store.lock:
            w=self.store.read(identity)
            if w.get('operation') or w['planState']!='PROPOSED' or not note.strip():raise ValueError('Only unapproved plans can be revised with a reason')
            if w.get('storageVersion')==2:self.store.artifacts.append_correction(identity,{'kind':'plan_revision','note':note,'planVersion':w.get('planVersion'),'timestamp':now()})
            w['planState']='REVISION_REQUESTED';w['revisionNote']=note.strip();event(w,'Revision requested',note,'correction');self.save(w)
        return self.plan(identity)

    def execute(self,identity,task_id):
        with self.store.lock:
            w=self.store.read(identity);t=next(t for t in w['tasks'] if t['id']==task_id)
            if w.get('operation') or w['planState']!='APPROVED' or t['status']!='Ready' or t['executor']=='Human':raise ValueError('Task is not approved and ready for automatic execution')
        def work():
            w=self.store.read(identity);t=next(t for t in w['tasks'] if t['id']==task_id);d=self.store.directory(identity)/'tasks'/task_id
            previous=[{'taskId':p['id'],'executor':p['executor'],'result':{k:v for k,v in p['result'].items() if k!='facts'}} for p in w['tasks'] if p['id'] in t['dependencyIds'] and p.get('result')]
            inherited={c['sourceId'] for item in previous for f in item['result'].get('findings',[]) for c in f.get('citations',[])}
            sources=[s for s in w['sources'] if s['id'] in set(t['evidenceIds'])|inherited or s.get('policy') or s.get('human')]
            self.store.write_json(d/'context.json',{'instruction':t['objective'],'sources':[s['id'] for s in sources],'previous':previous})
            payload={'goal':w['objective'],'instruction':t['objective'],'sources':[{'id':s['id'],'policy':s.get('policy',False),'content':s['content']} for s in sources],'previousResults':previous}
            result=bridge.execute_bounded(w,t,sources,previous,d/'attempts'/uuid.uuid4().hex[:8],payload,**({'artifact_store':self.store.artifacts} if w.get('storageVersion')==2 else {}))

            with self.store.lock:
                w=self.store.read(identity);t=next(t for t in w['tasks'] if t['id']==task_id)
                t['result']=result;t['status']='Completed';t.pop('blockReason',None)
                event(w,'Task completed',t['title']+' — '+t['executor']+' result saved.','task');self.save(w)
        return self.launch(identity,'Execute '+task_id,work,task_id=task_id)

    def human_handoff(self,identity,task_id):
        """Return the canonical Track C handoff, creating it idempotently."""
        with self.store.lock:
            w=self.store.read(identity);t=next(t for t in w['tasks'] if t['id']==task_id)
            if w.get('storageVersion')!=2:raise ValueError('Canonical handoffs require the current storage format')
            if w.get('operation') or w['planState']!='APPROVED' or t['executor']!='Human' or t['status']!='Needs Human':
                raise ValueError('Human task is not ready')
            record=PlanRecord(bridge.shared_plan(w),PlanStatus.APPROVED)
            task=next(item for item in record.plan.tasks if item.task_id==task_id)
            if t.get('humanHandoff'):
                stored=HumanHandoff.from_dict(t['humanHandoff'])
                expected=MinimalTaskRunner.create_handoff(record,identity,task,created_at=stored.created_at)
                if stored!=expected:raise ValueError('Persisted human handoff does not match the approved plan')
                return stored
            handoff=MinimalTaskRunner.create_handoff(record,identity,task,created_at=w.get('approvedAt') or w['updatedAt'])
            if self.human_interactions is not None:self.human_interactions.write_handoff(handoff)
            t['humanHandoff']=handoff.to_dict();self.save(w)
            return handoff

    def human(self,identity,task_id,data,*,session_id=''):
        if self.store.read(identity).get('storageVersion')==2:
            if self.human_validator is None or self.human_interactions is None:
                raise ValueError('Authorized human routing is not connected. This task remains waiting; no operator identity or decision is fabricated.')
            # Parse strictly before any runtime mutation. Valid but rejected
            # submissions are retained for audit while the task stays pending.
            try:response=human_response_from_mapping(data)
            except (KeyError,TypeError,ValueError) as exc:raise ValueError('Malformed canonical human response') from exc
            handoff=self.human_handoff(identity,task_id)
            self.human_interactions.write_submission(response)
            validation=self.human_validator.validate(handoff,response,session_id=session_id)
            self.human_interactions.write_validation(response,validation)
            with self.store.lock:
                w=self.store.read(identity);t=next(t for t in w['tasks'] if t['id']==task_id)
                record=PlanRecord(bridge.shared_plan(w),PlanStatus.APPROVED)
                state=RunState(identity,{task_id:TaskExecutionState(task_id,status=ExecutionStatus.PENDING_HUMAN,human_handoff=handoff)},mock_assisted=False)
                applied=apply_validated_human_response(MinimalTaskRunner({}),record,state,validation,ArtifactExecutionEventSink(self.store.artifacts))
                if not applied:return w
                result=state.task_states[task_id].result
                t['status']='Completed';t['humanResponse']=response.response_id;t['humanState']=response.response_disposition.value
                t['result']={'summary':result.rationale or 'Human response accepted','findings':[],
                             'blockers':list(result.unresolved),'nextActions':list(result.unresolved),
                             'authorityDecisions':[json.dumps(result.output.get('decision'),ensure_ascii=False)]}
                event(w,'Validated human response applied',response.response_id+' completed '+task_id,'human');self.save(w);return w
        with self.store.lock:
            w=self.store.read(identity);t=next(t for t in w['tasks'] if t['id']==task_id)
            if w.get('operation') or w['planState']!='APPROVED' or t['executor']!='Human' or t['status']!='Needs Human':raise ValueError('Human task is not ready')
            action=data.get('action');judgment=data.get('judgment','').strip();reason=data.get('reason','').strip()
            # Legacy snapshots predate Track C and retain their original local
            # review field for read/write compatibility only.
            operator=((w.get('operator') or {}).get('name') or data.get('operator','')).strip()
            if action not in ['Complete','Ask Clarification','Partial','Narrow Task','Request Reassignment','Decline Authority'] or not judgment or not reason or not operator:
                raise ValueError('A bound operator, judgment and reason are required')
            if max(len(judgment),len(reason),len(operator))>8000:raise ValueError('Human input too long')
            record={'action':action,'judgment':judgment,'reason':reason,'operator':operator,'timestamp':now(),'authorityVerified':False}
            self.store.write_json(self.store.directory(identity)/'artifacts'/'human'/f'{task_id}-{uuid.uuid4().hex[:8]}.json',record)
            t['humanResponse']=record;t['humanState']=action
            if action=='Complete':
                sid='H-'+task_id
                lines=[{'line':1,'text':'Operator: '+operator},{'line':2,'text':'Judgment: '+judgment},{'line':3,'text':'Reason: '+reason},{'line':4,'text':'Corporate authority is not verified. This is review input, not an external authorization.'}]
                s={'id':sid,'path':f'artifacts/human/{task_id}','name':'Human review '+task_id,'lines':lines,'content':'\n'.join(f"L{x['line']}: {x['text']}" for x in lines),'human':True,'policy':False}
                w['sources'].append(s);w['evidence'].append(self.evidence_view(s,w['tasks']))
                t['result']={'summary':judgment,'findings':[{'statement':judgment+' Reason: '+reason,'citations':[{'sourceId':sid,'line':2,'quote':judgment}]}], 'blockers':[],'nextActions':[],'authorityDecisions':['Human review recorded; no external corporate authorization was verified.']}
                t['status']='Completed'
            else:t['status']='Blocked';t['blockReason']=action+': '+judgment+' — '+reason
            event(w,'Human response saved',operator+': '+action+' — '+judgment+'; '+reason,'human');self.save(w);return w

    def resume(self,identity,task_id,note):
        with self.store.lock:
            w=self.store.read(identity);t=next(t for t in w['tasks'] if t['id']==task_id)
            if w.get('operation') or t['status']!='Blocked' or not note.strip():raise ValueError('Blocked task and recovery reason required')
            t['status']='Pending';t.pop('blockReason',None);w['error']=None
            event(w,'Task resumed',t['title']+': '+note,'correction');self.save(w);return w

    def evidence_action(self,identity,eid,action):
        with self.store.lock:
            w=self.store.read(identity)
            if w.get('operation'):raise ValueError('Wait for current operation')
            e=next(e for e in w['evidence'] if e['id']==eid)
            if action=='Mark Reviewed':e['inspected']=True
            elif action=='Flag Conflict':e['status']='Conflicting';e['conflictNote']='User flagged possible conflict. This observation requires reconciliation.'
            else:raise ValueError('External evidence request delivery is not connected')
            event(w,'Evidence annotation',eid+': '+action,'correction');self.save(w);return w
