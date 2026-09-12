from unittest.mock import patch
import pytest
from jsonschema import ValidationError
from governor.compact_plan import generate

SOURCES=[{'id':'E-a','path':'workspace/a.md','policy':False,'content':'Actual evidence'}]
def draft(index=0):
    return {'tasks':[{'title':'Review evidence','objective':'Inspect supplied facts','sources':[index]} for _ in range(4)],'assumptions':[],'questions':[]}

def test_expansion_preserves_contract_and_evidence(tmp_path):
    with patch('governor.model.call',return_value=draft()) as call:
        p=generate('Review','',SOURCES,tmp_path)
    assert [t['executor'] for t in p['tasks']]==['Deterministic','Local AI','Human','Local AI']
    assert p['tasks'][3]['dependencyIds']==['T1','T2','T3']
    assert all(t['evidenceIds']==['E-a'] for t in p['tasks'])
    assert call.call_args.args[-1]==700

@pytest.mark.parametrize('index',[-1,1,100])
def test_invalid_source_index_fails(tmp_path,index):
    with patch('governor.model.call',return_value=draft(index)):
        with pytest.raises(ValidationError):generate('Review','',SOURCES,tmp_path)
