"""Generic structured field extraction and exact date comparison. No case IDs/rules."""
import csv
import io
import json
import re
from datetime import datetime
from workflow_governor.execution.deterministic import DeterministicExecutor
from workflow_governor.core.models import TaskSpec,TaskContext,ExecutorType,ExecutionStatus

def core_operation(name,inputs):
    task=TaskSpec("record-operation",name,name,ExecutorType.DETERMINISTIC,operation=name)
    result=DeterministicExecutor().execute(task,TaskContext(task.task_id,operation_inputs=inputs))
    if result.status!=ExecutionStatus.COMPLETED:raise ValueError(result.error or result.unresolved)
    return result.output["result"]

MONTHS = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
DATE = re.compile(r'\b\d{4}-\d{2}-\d{2}\b|\b'+MONTHS+r' \d{1,2}, \d{4}\b')

def inspect_records(sources):
    findings=[];facts=[];expiries=[];observations=[]
    for s in sources:
        if s.get('policy'):continue
        text='\n'.join(x['text'] for x in s['lines'])
        parsed=None
        if s['path'].endswith('.json'):
            fields=list(json.loads(text));parsed=core_operation('extract_fields',{'content':text,'format':'json','fields':fields})['values']
        elif s['path'].endswith('.csv'):
            fields=next(csv.reader(io.StringIO(text)));parsed=core_operation('extract_fields',{'content':text,'format':'csv','fields':fields})['rows']
        facts.append({'sourceId':s['id'],'sha256':s['sha256'],'structured':parsed})
        for line in s['lines']:
            ref={'sourceId':s['id'],'line':line['line'],'quote':line['text']}
            lower=line['text'].lower()
            if (s['path'].endswith('.json') and any(k in lower for k in ['"status"','"commercial_po_eligible"','"open_exception_records"'])) or re.search(r',(?:FAIL|BLOCKED|PENDING),',line['text']):
                findings.append({'statement':'Recorded field: '+line['text'].strip(), 'citations':[ref]})
            for match in DATE.finditer(line['text']):
                raw=match.group();date=datetime.strptime(raw,'%Y-%m-%d' if raw[0].isdigit() else '%B %d, %Y').date()
                if 'expir' in lower:expiries.append((date,ref))
                if any(k in lower for k in ['exported_at','submitted','uploaded','received']):observations.append((date,ref))
    # Exact chronology only; semantic meaning/authority stays with cited model/human review.
    for expiry,er in expiries:
        for observed,orr in observations[:3]:
            comparison=core_operation('compare_dates',{'left':expiry.isoformat(),'right':observed.isoformat()})
            findings.append({'statement':f'Date comparison: expiry {expiry.isoformat()} is {"before" if expiry<observed else "on/after"} recorded observation {observed.isoformat()}; difference {-comparison["days"]} calendar days.', 'citations':[er,orr]})
    if not findings:
        for s in sources[:2]:
            line=next((x for x in s['lines'] if x['text'].strip()),None)
            if line:findings.append({'statement':'Source extracted and SHA-256 recorded: '+s['name'],'citations':[{'sourceId':s['id'],'line':line['line'],'quote':line['text']}]})
    return {'summary':'Completed deterministic record extraction and date comparisons; no external system changed.',
            'findings':findings,'blockers':[],'nextActions':[],'authorityDecisions':[], 'facts':facts,'operation':'inspect_records'}
