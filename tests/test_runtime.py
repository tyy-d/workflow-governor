import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from governor.workspace import Workspace
from governor.store import Store
from governor.service import Service,validate_plan
from governor.model import validate_citations

class Boundaries(unittest.TestCase):
 def test_access_and_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'allowed').mkdir();(root/'allowed/a.txt').write_text('source');(root/'allowed/leak.txt').symlink_to('/etc/passwd')
   ws=Workspace(root,{'x':{'root':'allowed','policies':[]}})
   self.assertEqual(len(ws.inventory('x')),1)
   for p in ['../secret','/etc/passwd','cases/a/ground_truth/answer.json','company/provenance/data.txt','personas/P001/actor.md','allowed/leak.txt']:
    with self.assertRaises(ValueError):ws.safe(p)
 def test_exact_citations(self):
  sources=[{'id':'E-1','lines':[{'line':2,'text':'Recorded status: Conditional'}]}]
  result={'findings':[{'statement':'observed','citations':[{'sourceId':'E-1','line':2,'quote':'Conditional'}]}]}
  validate_citations(result,sources)
  result['findings'][0]['citations'][0]['quote']='Active'
  with self.assertRaises(ValueError):validate_citations(result,sources)
 def test_markdown_only_citation_restore(self):
  sources=[{'id':'P-1','lines':[{'line':7,'text':'Status must be **Active** and gate `PASS`.'}]}]
  result={'findings':[{'statement':'Policy','citations':[{'sourceId':'P-1','line':7,'quote':'Status must be Active and gate PASS.'}]}]}
  validate_citations(result,sources)
  self.assertEqual(result['findings'][0]['citations'][0]['quote'],sources[0]['lines'][0]['text'])
  self.assertEqual(len(result['citationCorrections']),1)
  with self.assertRaises(ValueError):validate_citations({'findings':[{'citations':[{'sourceId':'P-1','line':8,'quote':'Active'}]}]},sources)
 def test_server_resolves_cited_source_line(self):
  sources=[{'id':'E-1','lines':[{'line':3,'text':'Recorded status: Conditional'},{'line':4,'text':''}]}]
  result={'findings':[{'statement':'Recorded state','citations':[{'sourceId':'E-1','line':3}]}]}
  validate_citations(result,sources);self.assertEqual(result['findings'][0]['citations'][0]['quote'],'Recorded status: Conditional')
  with self.assertRaises(ValueError):validate_citations({'findings':[{'citations':[{'sourceId':'E-1','line':4}]}]},sources)
 def test_dag(self):
  tasks=[{'id':'T1','executor':'Deterministic','dependencyIds':[],'evidenceIds':['E']},{'id':'T2','executor':'Human','dependencyIds':['T1'],'evidenceIds':['E']},{'id':'T3','executor':'Local AI','dependencyIds':['T1','T2'],'evidenceIds':['E']}]
  validate_plan({'tasks':tasks},[{'id':'E'}])
  tasks[0]['dependencyIds']=['T3']
  with self.assertRaises(ValueError):validate_plan({'tasks':tasks},[{'id':'E'}])
 def test_human_state_recovery_persistence(self):
  with tempfile.TemporaryDirectory() as d:
   store=Store(d);service=Service(store,None)
   w={'id':'WF-123456789abc','name':'test','objective':'Review source evidence','createdAt':'2026','updatedAt':'2026','planState':'PROPOSED','planNumber':1,'operation':None,'activity':[],'sources':[],'evidence':[],'status':'Planning','tasks':[{'id':'T1','title':'Human review','objective':'Review evidence','expectedOutput':'Reasoned response','executor':'Human','status':'Pending','dependencyIds':[],'evidenceIds':[]}],'finalState':{}}
   store.save(w)
   with self.assertRaises(ValueError):service.human(w['id'],'T1',{'action':'Complete','judgment':'yes','reason':'why','operator':'tester'})
   service.approve(w['id'])
   with self.assertRaises(ValueError):service.human(w['id'],'T1',{'action':'Complete'})
   service.human(w['id'],'T1',{'action':'Ask Clarification','judgment':'Need scope','reason':'Cannot authorize external work','operator':'test reviewer'})
   self.assertEqual(store.read(w['id'])['tasks'][0]['status'],'Blocked')
   service.resume(w['id'],'T1','Scope is review only')
   service.human(w['id'],'T1',{'action':'Complete','judgment':'Keep blocked externally','reason':'No external authorization','operator':'test reviewer'})
   reopened=Store(d).read(w['id'])
   self.assertEqual(reopened['tasks'][0]['status'],'Completed');self.assertIn('No external authorization',json.dumps(reopened['finalState']))
   self.assertEqual(len(list((store.directory(w['id'])/'artifacts/human').glob('*.json'))),2)
 def test_interrupt_recovery(self):
  with tempfile.TemporaryDirectory() as d:
   store=Store(d);w={'id':'WF-123456789abc','name':'Interrupted test','objective':'Review','createdAt':'2026','planState':'APPROVED','operation':'Execute T1','status':'In Progress','activity':[],'tasks':[{'id':'T1','title':'Review','executor':'Local AI','dependencyIds':[],'status':'Running'}]};store.save(w)
   Service(store,None);r=store.read(w['id']);self.assertIsNone(r['operation']);self.assertEqual(r['tasks'][0]['status'],'Blocked');self.assertTrue(r['finalState']['blockers']);self.assertEqual(json.loads((store.directory(w['id'])/'tasks/T1/task.json').read_text())['status'],'Blocked')

if __name__=='__main__':unittest.main()
