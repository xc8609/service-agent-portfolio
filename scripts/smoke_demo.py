"""HTTP smoke against a running local synthetic demo; no model keys."""
import json
import urllib.request


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
