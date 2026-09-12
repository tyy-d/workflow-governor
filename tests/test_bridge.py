import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from governor import bridge
from governor.store import Store
from governor.service import Service

def source(identity,path,text):
 return {'id':identity,'name':path,'path':path,'sha256':'test','policy':False,'lines':[{'line':1,'text':text}],'content':'L1: '+text}
def task(identity,executor,evidence,deps=()):
 return {'id':identity,'title':'Review','objective':'Read authorized records','expectedOutput':'Cited findings','executor':executor,'dependencyIds':list(deps),'evidenceIds':evidence,'status':'Ready'}
class SharedBridge(unittest.TestCase):
 def test_unresolved_record_explicit_attachment_follow(self):
  from governor.workspace import Workspace
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'workspace').mkdir();(root/'workspace/checks.csv').write_text('state,file\nREVIEW,attachment.txt\nPASS,other.txt')
   (root/'workspace/attachment.txt').write_text('Original evidence');(root/'workspace/other.txt').write_text('Not needed')
   ws=Workspace(root,{'w':{'root':'workspace','policies':[]}})
   initial=[ws.extract(r) for r in ws.inventory('w') if r['name']=='checks.csv']
   followed=ws.referenced_pending('w',initial)
   self.assertEqual([s['name'] for s in followed],['attachment.txt'])
   self.assertEqual(followed[0]['discoveryRef']['line'],2)
 def test_real_core_runner_and_deterministic_executor(self):
  with tempfile.TemporaryDirectory() as d:
   sources=[source('E-a','workspace/status.json','{"status":"Conditional"}')]
   t=task('T1','Deterministic',['E-a']);w={'id':'WF-123456789abc','objective':'Review','planNumber':1,'tasks':[t],'sources':sources}
   result=bridge.execute_bounded(w,t,sources,[],Path(d))
   self.assertEqual(result['facts'][0]['structured']['status'],'Conditional')
   core=json.loads(Path(d,'core-execution.json').read_text());self.assertFalse(core['mock_assisted']);self.assertEqual(core['result']['status'],'COMPLETED');self.assertEqual(len(core['events']),3)
 def test_shared_model_executor_checks_real_citations(self):
  with tempfile.TemporaryDirectory() as d:
   sources=[source('E-a','workspace/a.txt','A recorded fact')];t=task('T1','Local AI',['E-a']);w={'id':'WF-123456789abc','objective':'Review','planNumber':1,'tasks':[t],'sources':sources}
   result={'summary':'Read source','findings':[{'statement':'Observed','citations':[{'sourceId':'E-a','line':1,'quote':'recorded fact'}]}],'blockers':[],'nextActions':[],'authorityDecisions':[]}
   with patch('governor.model.call',return_value=result):out=bridge.execute_bounded(w,t,sources,[],Path(d),{})
   self.assertEqual(out['summary'],'Read source')
   core=json.loads(Path(d,'core-execution.json').read_text());self.assertEqual(core['result']['executor_type'],'LOCAL_MODEL')
 def test_dependency_cited_source_is_inherited(self):
  with tempfile.TemporaryDirectory() as d:
   s1=source('E-a','workspace/a.txt','A fact');s2=source('E-b','workspace/b.txt','B fact')
   previous=task('T1','Local AI',['E-a']);previous['status']='Completed';previous['result']={'summary':'Prior','findings':[{'statement':'A fact','citations':[{'sourceId':'E-a','line':1,'quote':'A fact'}]}]}
   current=task('T2','Local AI',['E-b'],['T1']);w={'id':'WF-123456789abc','name':'Review','objective':'Review','createdAt':'2026','status':'In Progress','planState':'APPROVED','planNumber':1,'operation':None,'sources':[s1,s2],'tasks':[previous,current],'activity':[],'evidence':[],'finalState':{}}
   store=Store(d);store.save(w);service=Service(store,None);captured=[]
   def execute(w,t,sources,*args):
    captured.extend(x['id'] for x in sources);return {'summary':'Done','findings':[],'blockers':[],'nextActions':[],'authorityDecisions':[]}
   with patch('governor.bridge.execute_bounded',side_effect=execute):
    service.execute(w['id'],'T2')
    for _ in range(100):
     if not store.read(w['id']).get('operation'):break
     time.sleep(.01)
   self.assertEqual(set(captured),{'E-a','E-b'});self.assertEqual(store.read(w['id'])['tasks'][1]['status'],'Completed')
