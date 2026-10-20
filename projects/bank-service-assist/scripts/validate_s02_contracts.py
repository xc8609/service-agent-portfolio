"""Verify authored S02 schema/plan artifacts, not application behavior or PostgreSQL DDL."""
from pathlib import Path
import copy
import importlib.metadata
import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/bank-service-assist';C=P/'specs/contracts';D=P/'docs/sprint-02'
FORMATS=FormatChecker()

@FORMATS.checks('date-time', raises=(ValueError, TypeError))
def strict_datetime(value):
    """Check the portfolio timestamp subset without optional format dependencies."""
    if not isinstance(value,str):return True
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})',value):
        return False
    return datetime.fromisoformat(value.replace('Z','+00:00')).tzinfo is not None

def sample(schema, key=''):
    if 'const' in schema:return schema['const']
    if 'enum' in schema:return schema['enum'][0]
    if 'anyOf' in schema:return sample(schema['anyOf'][0],key)
    if 'oneOf' in schema:return sample(schema['oneOf'][0],key)
    kind=schema.get('type')
    if isinstance(kind,list):
        if 'null' in kind:return None
        kind=kind[0]
    if kind=='object':return {k:sample(v,k) for k,v in schema['properties'].items() if k in schema.get('required',[])}
    if kind=='array':return [sample(schema['items']) for _ in range(schema.get('minItems',0))]
    if kind=='integer':return schema.get('minimum',1)
    if kind=='boolean':return True
    if kind=='null':return None
    if kind=='string':
        if schema.get('format')=='date-time':return '2026-10-19T15:00:00Z'
        if schema.get('format')=='date':return '2026-10-19'
        if schema.get('pattern')=='^[A-Z]{3}$':return 'CAD'
        return 'demo_01'
    raise AssertionError(schema)

def main():
    contract=json.loads((C/'agent-tools.json').read_text())
    api=json.loads((C/'openapi.json').read_text())
    auth=json.loads((C/'permissions.json').read_text())
    model=json.loads((C/'data-model.json').read_text())
    plan=json.loads((ROOT/'docs/backlog/sprint-forecast.json').read_text())
    backlog=json.loads((ROOT/'docs/backlog/trello-cards.json').read_text())
    updates=json.loads((D/'trello-updates.json').read_text())
    examples=[];schema_count=0
    tools=contract['tools'];commands=contract['human_or_system_only']
    names={x['name'] for x in tools};human={x['name'] for x in commands}
    assert not names & human
    for tool in tools+commands:
        for k in ['input_schema','success_schema']:
            schema=tool[k];Draft202012Validator.check_schema(schema);schema_count+=1
            val=Draft202012Validator(schema,format_checker=FORMATS)
            payload=sample(schema);val.validate(payload)
            examples.append(dict(id=tool['name']+'-'+k+'-positive',valid=True,payload=payload))
            if k=='input_schema':
                bad=copy.deepcopy(payload);bad['role']='administrator'
                assert list(val.iter_errors(bad)),tool['name']
                examples.append(dict(id=tool['name']+'-untrusted-role-negative',valid=False,payload=bad))
                bad=copy.deepcopy(payload);del bad[schema['required'][0]]
                assert list(val.iter_errors(bad)),tool['name']
                examples.append(dict(id=tool['name']+'-missing-required-negative',valid=False,payload=bad))
        op=api['paths'][tool['http']['path']]['post']
        assert op['operationId']==tool['name']
        assert op['x-model-callable']==(tool['name'] in names)
        assert op['requestBody']['content']['application/json']['schema']==tool['input_schema']
        assert op['responses']['200']['content']['application/json']['schema']==tool['success_schema']
    Draft202012Validator.check_schema(contract['error_schema']);schema_count+=1
    # Specific boundary examples, not only mechanically missing fields.
    t=next(x for x in tools if x['name']=='create_proposal');v=Draft202012Validator(t['input_schema']);bad=sample(t['input_schema']);bad['proposal']['kind']='refund'
    assert list(v.iter_errors(bad));examples.append(dict(id='no-refund-proposal',valid=False,payload=bad))
    t=next(x for x in tools if x['name']=='search_transactions');v=Draft202012Validator(t['input_schema']);bad=sample(t['input_schema']);bad['limit']=51
    assert list(v.iter_errors(bad));examples.append(dict(id='bounded-search',valid=False,payload=bad))
    t=next(x for x in commands if x['name']=='record_callback_attempt');v=Draft202012Validator(t['input_schema']);bad=sample(t['input_schema']);bad['verification_result']=True
    assert list(v.iter_errors(bad));examples.append(dict(id='no-client-asserted-proof',valid=False,payload=bad))
    assert len(auth['roles'])==len(set(auth['roles']))
    for a in auth['actions']:assert set(a['grants'])==set(auth['roles'])
    assert all(x=='deny' for x in next(a for a in auth['actions'] if a['action']=='financial.execute')['grants'].values())
    entity={x['name']:x for x in model['entities']};assert len(entity)==len(model['entities'])
    fks=0
    for e in model['entities']:
        fields={x['name']:x for x in e['fields']};assert len(fields)==len(e['fields'])
        assert any(x.get('primary') for x in e['fields'])
        for u in e['unique']:assert set(u)<=set(fields)
        for f in fields.values():
            if 'references' in f:
                table,col=f['references'].split('.');assert table in entity
                assert col in {x['name'] for x in entity[table]['fields']};fks+=1
    sql=(C/'schema-reference.sql').read_text()
    assert set(re.findall(r'CREATE TABLE (\w+)',sql))==set(entity)
    # Verify DDL columns/FKs match the structured model (not a PostgreSQL execution).
    for e in entity.values():
        table_sql=re.search(r'CREATE TABLE '+e['name']+r' \((.*?)\n\);',sql,re.S).group(1)
        for f in e['fields']:
            assert re.search(r'\b'+f['name']+r'\s+'+re.escape(f['type'])+r'(?=\s|,|$)',table_sql), (e['name'],f['name'])
            if 'references' in f:
                table,col=f['references'].split('.')
                assert f"ALTER TABLE {e['name']} ADD FOREIGN KEY ({f['name']}) REFERENCES {table}({col});" in sql
    # Hand-authored boundary fixtures exercise alternative payload branches.
    boundary=json.loads((C/'continuation-schema-cases.json').read_text())['cases']
    registry={x['name']:x for x in tools+commands}
    for case in boundary:
        v=Draft202012Validator(registry[case['interface']][case.get('schema','input_schema')],format_checker=FORMATS)
        assert v.is_valid(case['payload']) == case['valid'],case['id']
    decisions=json.loads((D/'business-review.json').read_text())['items']
    assert len(decisions)==6 and all(x['status']=='Accepted by owner' for x in decisions)
    permission_actions={a['action']:a for a in auth['actions']}
    for cmd in commands:assert cmd['permission_action'] in permission_actions
    for name in ['commitment.confirm','contact_continuation.decide']:
        grants=permission_actions[name]['grants']
        assert all(v=='deny' for role,v in grants.items() if role!='queue_lead')
    cal=json.loads((C/'calendar-fixtures.json').read_text())
    for case in cal['cases']:
        first=datetime.fromisoformat(case['first_placed_at']).astimezone(ZoneInfo(cal['timezone']))
        date=first.date();count=0
        while True:
            if date.weekday() in cal['open_weekdays'] and date.isoformat() not in case['holidays']:count+=1
            if count==3:break
            date+=timedelta(days=1)
        expected=datetime.combine(date,datetime.strptime(cal['close'],'%H:%M').time(),tzinfo=ZoneInfo(cal['timezone']))
        assert expected==datetime.fromisoformat(case['expected_end']),case['id']
    delivery=json.loads((D/'delivery-specs.json').read_text())['stories']
    delivery_ac=0
    for story in delivery:
        base=P/'specs'/story['id']
        for name in ['spec.md','design.md','tasks.md','acceptance.md']:assert (base/name).is_file()
        for case in story['acceptance']:
            assert case['id'] in (base/'spec.md').read_text()
            assert case['testId'] in (base/'acceptance.md').read_text()
            assert case['execution']=='Not executed'
            delivery_ac+=1
    assert len({s['id'] for s in plan['sprints']})==len(plan['sprints'])
    bystory={x['id']:x for x in backlog['stories']};bysp={x['id']:x for x in plan['sprints']}
    totals={k:0 for k in ['dev','ba','qa','total']};covered=[]
    for sp in plan['sprints']:
        for k in ['dev','ba','qa']:
            actual=sum(bystory[x]['estimate'][k] for x in sp['stories']);assert actual==sp['load'][k];assert actual<=sp['capacity'][k]
        assert sum(sp['developer_lanes'].values())==sp['load']['dev']
        assert max(sp['developer_lanes'].values())<=7
        covered+=sp['stories']
    assert len(covered)==len(set(covered))==len(bystory)
    for x in bystory.values():
        for k in totals:totals[k]+=x['estimate'][k]
        for dep in x['deps']:assert bysp[bystory[dep]['sprint']]['order']<=bysp[x['sprint']]['order']
    assert totals==plan['total']
    assert len(updates)==len({x['id'] for x in updates})
    assert all(any(m in x['description'] for m in ['BANK-S02-v0.3','BANK-S02-v0.4']) and len(x['description'])<=16384 for x in updates)
    links=0
    files=[D/'README.md',D/'forecast-impact.md',C/'permissions.md',C/'data-model.md',C/'interface-notes.md',ROOT/'docs/backlog/sprints.md']
    for id in ['BA-06','BA-07','BA-08','BA-09']:
        files += [P/'specs'/id/name for name in ['spec.md','design.md','tasks.md','acceptance.md']]
    for file in files:
        for href in re.findall(r'\[[^\]]+\]\(([^)]+)\)',file.read_text()):
            if href.startswith(('https:','http:','#')):continue
            assert (file.parent/href.split('#')[0]).exists(),(file,href)
            links+=1
    (C/'schema-examples.json').write_text(json.dumps(dict(version=contract['version'],kind='Authored schema-only examples, not realistic bank records or held-out model evaluation',examples=examples),indent=2)+'\n')
    result=dict(status='PASS',date='2026-10-19',jsonschema_version=importlib.metadata.version('jsonschema'),schemas_meta_validated=schema_count,payload_examples=len(examples),model_tools=len(tools),trusted_commands=len(commands),permission_actions=len(auth['actions']),entities=len(entity),foreign_keys=fks,sprints=len(plan['sprints']),delivery_sprints=12,reserve_sprints=2,role_effort=totals,local_links=links,trello_payloads=len(updates),limits='Schema/meta/example validation, structural references and aggregate/lane capacity only. Does not execute PostgreSQL DDL, API authorization, semantic state guards, live models, application UAT, resource-level critical-path scheduling or deployment. Trello verification separate.')
    result.update(contract_version=contract['version'],authored_boundary_examples=len(boundary),calendar_spec_examples=len(cal['cases']),new_detailed_stories=len(delivery),new_planned_acceptance_cases=delivery_ac)
    (D/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
