"""Structural specification checks only; does not execute application acceptance tests."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'projects/bank-service-assist'
D = P / 'docs/sprint-01'

def main():
    w = json.loads((D / 'workflow-stories.json').read_text())
    r = json.loads((D / 'requirements.json').read_text())
    c = json.loads((P / 'specs/contracts/agent-tools.json').read_text())
    b = json.loads((ROOT / 'docs/backlog/trello-cards.json').read_text())
    updates = json.loads((D / 'workflow-trello-updates.json').read_text())
    requirements = {q['id'] for q in r['requirements']}
    backlog = {q['id'] for q in b['stories']}
    names = {q['name'] for q in c['tools']}
    assert len(requirements) == len(r['requirements'])
    assert len(backlog) == len(b['stories'])
    assert len(names) == len(c['tools'])
    assert not (names & {q['name'] for q in c['human_or_system_only']})
    ac, tests, docs = set(), set(), []
    decisions = (D / 'decision-log.md').read_text()
    for s in w['stories']:
        assert set(s['requirements']) <= requirements, s['id']
        assert set(s['deps']) <= backlog, s['id']
        assert set(s['tools']) <= names, s['id']
        assert all('| '+v+' |' in decisions for v in s['decisions']), s['id']
        for file in ['spec.md', 'design.md', 'tasks.md', 'acceptance.md']:
            p = P / 'specs' / s['id'] / file
            assert p.is_file(), p
            docs.append(p)
        for a in s['acceptance']:
            assert a['id'] not in ac and a['testId'] not in tests
            assert a['given'] and a['when'] and a['then']
            assert a['execution'] == 'Not executed'
            ac.add(a['id']); tests.add(a['testId'])
    for t in c['tools']:
        for schema_key in ['input_schema', 'success_schema']:
            schema = t[schema_key]
            assert schema['type'] == 'object'
            assert schema['additionalProperties'] is False
            assert set(schema['required']) <= set(schema['properties'])
        assert not ({'role', 'actor_id', 'base_url', 'sql'} & set(t['input_schema']['properties']))
        assert t['side_effect'] in ['read', 'draft_only']
        assert {'data', 'meta'} == set(t['success_schema']['required'])
    assert len({x['id'] for x in updates}) == len(updates)
    assert all('BANK-SDD-v0.2' in x['description'] and len(x['description']) <= 16384 for x in updates)
    assert {x['id'] for x in updates if x['action'] == 'create'} == {'DEV-11', 'DEV-12', 'DEV-13'}
    for x in updates:
        assert not re.search(r'(?i)(sk-[A-Za-z0-9]{20,}|-----BEGIN .*PRIVATE KEY)', x['description'])
    docs += [D / 'workflow-increment.md', D / 'workflow-traceability.md', P / 'specs/contracts/agent-tools.md']
    local_links = 0
    for p in docs:
        for href in re.findall(r'\[[^\]]+\]\(([^)]+)\)', p.read_text()):
            if href.startswith(('https:', 'http:', '#')):
                continue
            assert (p.parent / href.split('#')[0]).exists(), (p, href)
            local_links += 1
    new = [q for q in b['stories'] if q['id'] in ['DEV-11', 'DEV-12', 'DEV-13']]
    assert [sum(q['estimate'][key] for q in new) for key in ['dev', 'ba', 'qa', 'total']] == [11, 2, 3, 16]
    out = dict(status='PASS', checks='ID uniqueness, dependency/requirement/tool/decision references, four-file SDD presence, acceptance state, schema shape, tool authority separation, description size, obvious-secret pattern, local links, estimate arithmetic', stories=len(w['stories']), acceptance_examples=len(ac), tools=len(names), human_system_commands=len(c['human_or_system_only']), requirements=len(requirements), scenarios=len(r['scenarios']), local_links=local_links, trello_payloads=len(updates), limitations='Not a full JSON Schema meta-validation, runtime/security test, rendered-diagram review, model evaluation or UAT. Trello save verification is separate.')
    (D / 'workflow-validation.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
