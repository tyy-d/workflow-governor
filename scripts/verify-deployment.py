#!/usr/bin/env python3
"""Verify saved real acceptance evidence, without invoking or changing a model."""
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path

root=Path(__file__).resolve().parents[1];logs=root/'runtime/deployment'
identity=(logs/'acceptance-workflow-id.txt').read_text().strip();directory=root/'runtime/workflows'/identity
w=json.loads((directory/'manifest.json').read_text())
assert w['status']=='Completed' and not w.get('operation') and not w.get('error'),w['status']
assert all(t['status']=='Completed' for t in w['tasks'])
sources={s['id']:s for s in w['sources']}
for s in sources.values():
 assert not {'ground_truth','provenance','personas','persona_memory'}.intersection(Path(s['path']).parts)
for t in w['tasks']:
 for finding in t['result'].get('findings',[]):
  for citation in finding['citations']:
   source=sources[citation['sourceId']]
   line=next(l['text'] for l in source['lines'] if l['line']==citation['line'])
   assert citation['quote'] in line
 if t['executor']!='Human':
  records=[json.loads(p.read_text()) for p in (directory/'tasks'/t['id']).rglob('core-execution.json')]
  assert any(r['runner']=='MinimalTaskRunner' and r['mock_assisted'] is False and r['result']['status']=='COMPLETED' for r in records)
 else:
  assert t['humanResponse']['judgment'] and t['humanResponse']['reason']
  assert 'demonstration' in t['humanResponse']['operator'].lower()
assert any(e['title']=='Task resumed' for e in w['activity'])
assert list((directory/'plans').glob('*core-approval.json'))
requests=[json.loads(p.read_text()) for p in directory.rglob('*-request.json')]
responses=[json.loads(p.read_text()) for p in directory.rglob('*-response.json')]
assert requests and all(r['model']=='qwen-local' for r in requests)
assert responses and all(r['usage']['completion_tokens']>0 for r in responses)
browser=json.loads((logs/'browser-acceptance.json').read_text());assert browser['status']=='passed' and browser['workflowId']==identity
with urllib.request.urlopen('http://127.0.0.1:8080/api/workflows/'+identity) as r:assert json.load(r)['status']=='Completed'
raw=subprocess.check_output(['sg','docker','-c','docker inspect qwen-local'],text=True)
container=json.loads(raw)[0]
baseline=root.parent/'model-serving/logs/thinking-container.json'
before=json.loads(baseline.read_text())[0] if baseline.exists() else None
if before:assert before['State']['StartedAt']==container['State']['StartedAt']
report={'status':'passed','workflowId':identity,'lanUrl':'http://10.50.17.202:8080/#'+identity,
 'upstreamCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
 'model':'Qwen/Qwen3.8-27B-FP8','servedId':'qwen-local','modelUrl':'http://127.0.0.1:8000/v1',
 'modelContainerStartedAt':container['State']['StartedAt'],'modelNotRestarted':bool(before),
 'realModelCalls':len(responses),'modelSeconds':round(sum(r['seconds'] for r in responses),3),
 'usage':{'prompt_tokens':sum(r['usage']['prompt_tokens'] for r in responses),'completion_tokens':sum(r['usage']['completion_tokens'] for r in responses)},
 'browser':browser,'sourceCount':len(sources),'followedPendingOriginals':[s['path'] for s in sources.values() if s.get('discoveryRef')],
 'humanInput':'Explicitly labeled automated acceptance operator; not employee approval',
 'sharedRunnerVerified':True,'allCitationLocationsVerified':True,'finalState':w['finalState'],
 'manifestSha256':hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest()}
(logs/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:report[k] for k in ['status','workflowId','realModelCalls','modelSeconds','usage','modelNotRestarted']},indent=2))
