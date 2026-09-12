"""Short local-model wire format; preserve the existing four-task plan contract."""
from jsonschema import Draft202012Validator
from . import model

ROLES = ('Deterministic', 'Local AI', 'Human', 'Local AI')
DEPENDENCIES = ([], ['T1'], ['T2'], ['T1', 'T2', 'T3'])
OUTPUTS = ('Extracted facts with source references.', 'Evidence synthesis and unresolved gaps.',
           'Attributed human judgment, uncertainty and authority limits.',
           'Final cited findings, unresolved blockers and next actions.')

def generate(goal, revision, sources, directory):
    # The existing planner already mandates this sequence. Generate business-specific
    # instructions with Qwen; construct repeated IDs/executor/dependency fields in code.
    text = {'type': 'string', 'minLength': 1, 'maxLength': 160}
    item = model.object_schema({'title': {'type':'string','minLength':1,'maxLength':55},
                                'objective': text,
                                'sources': model.arr({'type':'integer','minimum':0,'maximum':len(sources)-1},minItems=1,maxItems=len(sources))})
    schema = model.object_schema({'tasks': model.arr(item,minItems=4,maxItems=4),
                                  'assumptions': model.arr(text,maxItems=2),
                                  'questions': model.arr(text,maxItems=2)})
    if not sources:
        raise ValueError('Planning requires authorized evidence')
    draft = model.call(
        'Propose exactly four tasks in order: deterministic record/date extraction (inspect_records only); '
        'local AI evidence/policy synthesis; human bounded review, without external approval; '
        'local AI final reconciliation of actual results, uncertainty and authority. '
        'Tailor each to the goal and evidence. Titles at most 4 words; objectives at most 12 words. '
        'Use source indexes, not filenames or IDs. Keep assumptions/questions short and only if needed. '
        'Do not repeat facts, predict completed work or invent company policy.',
        {'goal':goal,'revision':revision,'sources':[
            {'index':i,'path':s['path'],'policy':s['policy'],'content':s['content']}
            for i,s in enumerate(sources)]},schema,directory,'plan',700)
    Draft202012Validator(schema).validate(draft)
    tasks=[]
    for i, task in enumerate(draft['tasks']):
        tasks.append({'id':f'T{i+1}','title':task['title'],'objective':task['objective'],
                      'executor':ROLES[i],'dependencyIds':list(DEPENDENCIES[i]),
                      'evidenceIds':list(dict.fromkeys(sources[n]['id'] for n in task['sources'])),
                      'rationale':task['objective'],'expectedOutput':OUTPUTS[i],
                      'authorityRequirement':None,
                      'requestedDecisionAuthorityScope':'ANALYSIS_OR_RECOMMENDATION' if ROLES[i]=='Human' else 'NO_DECISION'})
    result={'tasks':tasks,'assumptions':draft['assumptions'],'questions':draft['questions']}
    Draft202012Validator(model.PLAN_SCHEMA).validate(result)
    return result
