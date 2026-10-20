"""Render current contract reference docs from JSON; does not implement or validate runtime behavior."""
from pathlib import Path
import json
C=Path(__file__).resolve().parents[1]/'specs/contracts'
def load(name):return json.loads((C/name).read_text())
def main():
    a=load('agent-tools.json');m=load('data-model.json');p=load('permissions.json')
    head='BANK-S02-v0.4 · Current candidate; application implementation and runtime acceptance pending.\n'
    text='# Agent tool and trusted command registry\n\n'+head+'\nOnly the model-tool allowlist is available to the agent. UI/human commands are not model tools. [JSON Schemas](agent-tools.json) and [OpenAPI](openapi.json) are canonical; domain effects require server permissions and transitions.\n\n| Interface | Exposure | Purpose / authority |\n|---|---|---|\n'
    for t in a['tools']+a['human_or_system_only']:
        text+='| '+t['name']+' | '+t['exposure']+' | '+t.get('purpose',t.get('authorization',''))+' |\n'
    text+='\n## Semantic guards\n\n'+''.join('- '+s+'\n' for s in a['semantic_guards'])
    (C/'agent-tools.md').write_text(text)
    text='# Permission matrix v0.4\n\n'+head+'\nD-17–D-22 are accepted to their stated extent. Below are engineering mappings for review. Default deny; trusted staff scope and customer disclosure verification are separate.\n\n| Action | '+' | '.join(p['roles'])+' |\n|---|'+ '|'.join('---' for _ in p['roles'])+'|\n'
    for x in p['actions']:text+='| '+x['action']+' | '+' | '.join(x['grants'][r] for r in p['roles'])+' |\n'
    text+='\n## Predicates\n\n'+''.join('- **'+k+'**: '+v+'\n' for k,v in p['conditions'].items())
    text+='\n## Action boundaries\n\n'+''.join('- **'+x['action']+'**: '+x.get('notes','')+'\n' for x in p['actions'])
    text+='\nBefore claim: masked summaries only. After claim: case-relevant details; no internal notes in feedback/model DTOs. Reassignment revokes old scope. Caller verification must belong to current callback before disclosure. Scheduler metadata privilege never transfers to the model. Runtime API/database enforcement remains unexecuted.\n'
    (C/'permissions.md').write_text(text)
    text='# Data model v0.4\n\n'+head+'\nSynthetic operational records only. [Structured model](data-model.json) defines fields/keys/checks; [reference DDL](schema-reference.sql) is not applied to PostgreSQL. Cross-record authority and transitions also require service validation.\n'
    for e in m['entities']:
        text+='\n## '+e['name']+'\n\n'+e['purpose']+'\n\n| Field | Type | Nullable | Reference |\n|---|---|---|---|\n'
        for f in e['fields']:text+='| '+f['name']+' | '+f['type']+' | '+str(f['nullable'])+' | '+f.get('references','primary key' if f.get('primary') else '')+' |\n'
        text+='\nUnique: '+str(e['unique'])+'.\n'+''.join('- '+v+'\n' for v in e.get('invariants',[]))+''.join('- SQL check: `'+v+'`.\n' for v in e.get('checks',[]))
    text+='\n## Link and history constraints\n\nService transactions must check same-case/customer linkage for every related record; an FK alone does not enforce this. Cross-plan contact limits use case/service date. Approved plan/commitment supersession is atomic and preserves history. Separate original investigation/first-callback obligations from later plan windows. Identity, audit and model-safe projections remain distinct.\n'
    (C/'data-model.md').write_text(text)
if __name__=='__main__':main()
