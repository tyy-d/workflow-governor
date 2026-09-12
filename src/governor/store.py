"""Web projection over Track A storage; legacy snapshots stay in their original format."""
import json
import re
import threading
from pathlib import Path
from workflow_governor.artifacts import ArtifactStore, WorkflowStateLoader
from workflow_governor.artifacts.store import atomic_write
from workflow_governor.core.config import RuntimeConfig, confined
from workflow_governor.core.models import PlanStatus
from workflow_governor.core.substrate import WorkspaceGrant

STATUSES = {'Pending':'PENDING','Ready':'READY','Running':'RUNNING','Needs Human':'PENDING_HUMAN','Completed':'COMPLETED','Blocked':'BLOCKED'}

class Store:
    def __init__(self, root, repo=None, grants=None):
        self.root=Path(root).absolute();self.root.mkdir(parents=True,exist_ok=True)
        self.lock=threading.RLock();self.grants=grants
        self.artifacts=ArtifactStore(RuntimeConfig(Path(repo or Path.cwd()), self.root.parent))
        self.loader=WorkflowStateLoader(self.artifacts)

    def directory(self, identity):
        if not re.fullmatch(r'WF-[a-f0-9]{12}',identity):
            raise ValueError('Invalid workflow identity')
        return confined(self.root,identity)

    def read(self, identity):
        with self.lock:
            manifest=json.loads(confined(self.directory(identity),'manifest.json').read_text())
            if 'id' in manifest:
                if self.grants is not None:manifest['readOnly']='Historical format. Preserved without migration; create a new workflow to run again.'
                return manifest
            state=self.artifacts.load_final_state(identity).payload
            # Never infer business completion from an unavailable or inconsistent artifact.
            if not state.get('operation'):
                snapshot=self.loader.load(identity)
                if snapshot.diagnostics:
                    state['readOnly']='Some saved artifacts need repair. Original files have been retained.'
                    state['error']='; '.join(f'{d.message} ({d.path or d.code})' for d in snapshot.diagnostics)
                    state['status']='Blocked'
                    for task in state.get('tasks',[]):
                        if task['id'] not in snapshot.results and task['status']=='Completed':
                            task['status']='Blocked';task['blockReason']='Saved result is unavailable; review required.'
            return state

    def write_json(self, path, value):
        path=Path(path)
        path=confined(self.root,path.relative_to(self.root).as_posix())
        atomic_write(path,json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False).encode())

    def save(self, value):
        with self.lock:
            if value.get('storageVersion')==2:
                identity=value['id']
                if not (self.directory(identity)/'manifest.json').exists():
                    grant=self.grants[value['workspaceKey']]
                    self.artifacts.create_workflow(identity,value['objective'],(WorkspaceGrant(value['workspaceKey'],grant['root']),))
                self.artifacts.save_final_state(identity,value)
            else:
                self.write_json(self.directory(value['id'])/'manifest.json',value)

    def commit_plan(self,w,plan,status):
        if w.get('storageVersion')==2:
            self.artifacts.save_plan(w['id'],plan,status=PlanStatus(status))
            for task in plan.tasks:self.artifacts.save_task(w['id'],task)

    def list(self):
        with self.lock:
            values=[]
            for p in self.root.glob('WF-*/manifest.json'):
                try:values.append(self.read(p.parent.name))
                except Exception:
                    values.append({'id':p.parent.name,'name':'Saved workflow needs repair','objective':'Its files remain on disk. Restore or repair in a separate directory.','status':'Blocked','createdAt':'1970-01-01T00:00:00Z','updatedAt':'1970-01-01T00:00:00Z','workspace':'Unavailable','planState':'NOT_PROPOSED','tasks':[],'evidence':[],'activity':[],'finalState':{},'readOnly':'The saved workflow could not be decoded.'})
            return sorted(values,key=lambda x:x.get('updatedAt',x['createdAt']),reverse=True)
