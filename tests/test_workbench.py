"""Integration checks for the web projection over shared durable storage."""
import json
import time
from pathlib import Path
from unittest.mock import patch
import pytest
from governor.store import Store
from governor.workspace import Workspace
from governor.service import Service
from governor import model

@pytest.fixture
def app(tmp_path):
    (tmp_path/'workspace').mkdir()
    (tmp_path/'workspace'/'status.json').write_text('{"status":"Pending"}')
    grants={'selected':{'root':'workspace','label':'Selected workspace','policies':[]}}
    store=Store(tmp_path/'runtime'/'workflows',tmp_path,grants)
    return Service(store,Workspace(tmp_path,grants))

def create(app):
    return app.create({'workspace':'selected','objective':'Review selected evidence','sourceIds':[app.workspace.inventory('selected')[0]['id']]})

def settle(app,w):
    for _ in range(200):
        current=app.store.read(w['id'])
        if not current.get('operation'):return current
        time.sleep(.01)
    pytest.fail('Background operation did not finish')

def plan(app,w):
    evidence=app.workspace.inventory('selected')[0]['id']
    tasks=[{'id':f'T{i}','title':f'Review {i}','objective':'Review the selected record','executor':executor,'dependencyIds':[f'T{j}' for j in range(1,i)],'evidenceIds':[evidence],'rationale':'Bounded record review','expectedOutput':'Cited findings'} for i,executor in enumerate(['Deterministic','Local AI','Human','Local AI'],1)]
    with patch('governor.compact_plan.generate',return_value={'tasks':tasks,'assumptions':[],'questions':[]}):
        app.plan(w['id']);w=settle(app,w)
    assert not w.get('error'),w.get('error')
    return w

def test_real_shared_store_and_explicit_approval(app):
    w=create(app)
    assert w['status']=='Draft' and not w['operation']
    w=plan(app,w)
    assert w['planState']=='PROPOSED'
    with pytest.raises(ValueError):app.execute(w['id'],'T1')
    app.approve(w['id']);app.execute(w['id'],'T1');w=settle(app,w)
    assert w['tasks'][0]['status']=='Completed'
    saved=app.store.loader.load(w['id'],strict=True)
    assert saved.results['T1'].status.value=='COMPLETED'
    assert len(saved.plans)==2
    assert Store(app.store.root,app.workspace.repo,app.workspace.grants).read(w['id'])['tasks'][0]['result']

def test_failed_model_never_completes(app):
    w=create(app)
    with patch('governor.model.call',side_effect=TimeoutError('Model request timed out')):
        app.plan(w['id']);w=settle(app,w)
    assert w['error'] and w['status']=='Blocked' and not w['tasks']

def test_corruption_does_not_hide_other_workflows(app):
    bad=create(app);good=create(app)
    app.store.artifacts.path(bad['id'],'final/state.json').write_text('{')
    rows={w['id']:w for w in app.store.list()}
    assert rows[bad['id']]['readOnly']
    assert rows[good['id']]['status']=='Draft'

def test_new_human_route_is_honestly_unavailable(app):
    w=create(app)
    with pytest.raises(ValueError,match='not connected'):app.human(w['id'],'T3',{'operator':'invented'})

def test_unknown_model_task_fields_rejected():
    from jsonschema import Draft202012Validator,ValidationError
    with pytest.raises(ValidationError):Draft202012Validator(model.PLAN_SCHEMA).validate({'tasks':[],'assumptions':[],'questions':[],'secret':'not allowed'})

def test_failed_task_can_be_retried_without_false_corruption(app):
    w=plan(app,create(app));app.approve(w['id']);app.execute(w['id'],'T1');settle(app,w)
    with patch('governor.model.call',side_effect=RuntimeError('Model unavailable')):
        app.execute(w['id'],'T2');w=settle(app,w)
    assert w['tasks'][1]['status']=='Blocked' and not w.get('readOnly')
    app.resume(w['id'],'T2','Model connection restored; retry requested')
    assert app.store.read(w['id'])['tasks'][1]['status']=='Ready'

def test_pre_human_task_record_reads_without_granting_authority():
    from workflow_governor.core.models import TaskSpec,ExecutorType,DecisionAuthorityScope
    task=TaskSpec('T1','Review','Read selected evidence',ExecutorType.LOCAL_MODEL)
    old=task.to_dict();old.pop('requested_decision_authority_scope')
    original=json.dumps(old,sort_keys=True)
    restored=TaskSpec.from_dict(old)
    assert restored.requested_decision_authority_scope==DecisionAuthorityScope.NO_DECISION
    assert json.dumps(old,sort_keys=True)==original
    old.pop('objective')
    with pytest.raises(Exception):TaskSpec.from_dict(old)
