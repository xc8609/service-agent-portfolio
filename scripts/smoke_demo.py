"""HTTP smoke against a running local synthetic demo; no model keys."""
import json
import urllib.request
from uuid import uuid4


def request(path,payload=None,token=None):
    headers={'Content-Type':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    req=urllib.request.Request('http://127.0.0.1:8000'+path,
        data=json.dumps(payload).encode() if payload is not None else None,headers=headers)
    with urllib.request.urlopen(req,timeout=10) as response:return json.load(response)

ready=request('/health/ready');assert ready['agent_enabled'] is False
session=request('/v1/demo/session',{'persona':'verified'})
token=session['access_token'];contact=session['contact_id']
context=request('/v1/agent-tools/get_contact_context',{'contact_id':contact},token)
assert context['data']['masked_card_refs']==['DEMO-4242']
result=request('/v1/agent-tools/search_transactions',{'contact_id':contact,'card_ref':'DEMO-4242',
    'date_from':'2026-10-01','date_to':'2026-10-31','amount_minor':8500,'merchant_query':None,'cursor':None,'limit':50},token)
assert len(result['data']['records'])==2
ids=[r['id'] for r in result['data']['records']]
evidence=request('/v1/agent-tools/get_transaction_evidence',{'contact_id':contact,'transaction_ids':ids},token)
assert evidence['data']['relationships']==[]
assert evidence['data']['missing_evidence']
print('PASS: ready → scoped contact → filtered search → selected evidence; no LLM credentials.')

history=request('/v1/workspace/get_investigation',{'contact_id':contact},token)
report={'contact_id':contact,'expected_revision':history['current_revision'],
    'operation_key':str(uuid4()),'statement':'Synthetic smoke: one purchase; entry mapping unresolved.',
    'recognition':'one_purchase_unresolved','recognized_transaction_id':None,
    'transaction_versions':[{'id':r['id'],'version':r['version']} for r in evidence['data']['records']]}
saved=request('/v1/workspace/save_investigation',report,token)
assert saved['saved_revision']==history['current_revision']+1
assert saved['history'][-1]['recognized_transaction_id'] is None
assert request('/v1/workspace/save_investigation',report,token)==saved
print('PASS: scoped customer-report persistence and idempotent replay; no financial action.')

cases=request('/v1/workspace/get_related_cases',{'contact_id':contact,'transaction_ids':ids},token)
assert cases['review_state']=='review_existing_work'
case=cases['cases'][0]
assert case['reference']=='DEMO-CASE-001' and case['coverage']=='full_selection'
assert case['snapshot']['investigation_status']=='awaiting_documents'
assert any(w['assignee_name']=='Demo specialist Alex' for w in case['work_items'])
snapshot=request('/v1/agent-tools/get_case_snapshot',{'contact_id':contact,'case_id':case['snapshot']['case_id'],'expected_work_version':None},token)
assert snapshot['data']==case['snapshot']
assert 'UNAPPROVED PRIVATE UPDATE' not in json.dumps(cases)
print('PASS: scoped related-case progress, accountable ownership and duplicate-enquiry review; no case created.')
