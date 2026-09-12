#!/usr/bin/env python3
"""Inspect saved inputs/results; --new-draft creates a new workflow without executing it."""
import argparse,json,uuid,urllib.request,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[1];sys.path.insert(0,str(repo/'src'))
from governor.store import Store
p=argparse.ArgumentParser(description=__doc__);p.add_argument('workflow_id');p.add_argument('--new-draft',action='store_true');args=p.parse_args()
grants=json.loads((repo/'config/workspaces.json').read_text());w=Store(repo/'runtime/workflows',repo,grants).read(args.workflow_id)
record={'workflowId':w['id'],'goal':w['objective'],'workspace':w['workspaceKey'],'selectedSourceIds':w.get('selectedSourceIds'), 'sourceHashes':{s['id']:s.get('sha256') for s in w.get('sources',[])},'planVersion':w.get('planVersion'),'runId':w.get('runId'),'results':w.get('finalState')}
if not args.new_draft:print(json.dumps(record,ensure_ascii=False,indent=2));raise SystemExit(0)
data={'name':w['name']+' (replay)','objective':w['objective'],'workspace':w['workspaceKey'],'sourceIds':w.get('selectedSourceIds') or [s['id'] for s in w.get('sources',[]) if not s.get('policy')][:8]}
req=urllib.request.Request('http://127.0.0.1:8080/api/workflows',json.dumps(data).encode(),{'Content-Type':'application/json','Idempotency-Key':str(uuid.uuid4())})
with urllib.request.urlopen(req,timeout=15) as response:created=json.load(response)
print('New draft:',created['id'],'— no model request, approval, or task execution was started. Current authorized source files will be read when you generate its plan; output may differ.')
