"""Render authorized synthetic demo sources as separate reading pages (not a bank UI)."""
import argparse
import hashlib
import html
import json
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

STATEMENT = ('I bought once, but I see two charges for CAD 85. I cannot tell which '
             'entry is extra. I do not have the receipt.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api', default='http://127.0.0.1:5173')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if urlsplit(args.api).hostname not in ('127.0.0.1', 'localhost'):
        parser.error('Use a local disposable synthetic demo only.')
    output = args.output or Path(tempfile.mkdtemp(prefix='bank-lookup-pack-'))
    output.mkdir(parents=True, exist_ok=True)
    token = None

    def call(path, payload):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        request = urllib.request.Request(args.api + '/v1/' + path,
            data=json.dumps(payload).encode(), headers=headers)
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)

    session = call('demo/session', {'persona': 'verified'})
    token, contact = session['access_token'], session['contact_id']
    found = call('agent-tools/search_transactions', {'contact_id': contact,
        'card_ref': 'DEMO-4242', 'date_from': '2026-10-01', 'date_to': '2026-10-31',
        'amount_minor': 8500, 'merchant_query': 'DEMO STORE', 'cursor': None, 'limit': 50})['data']['records']
    if len(found) != 2:
        raise RuntimeError('Expected the two-entry synthetic fixture.')
    pair = {'contact_id': contact, 'transaction_ids': [r['id'] for r in found]}
    history = call('workspace/get_investigation', {'contact_id': contact})
    call('workspace/save_investigation', {'contact_id': contact,
        'expected_revision': history['current_revision'], 'operation_key': str(uuid4()),
        'statement': STATEMENT, 'recognition': 'one_purchase_unresolved',
        'recognized_transaction_id': None,
        'transaction_versions': [{'id': r['id'], 'version': r['version']} for r in found]})
    sources = {
        'transactions': call('agent-tools/get_transaction_evidence', pair)['data'],
        'cases': call('workspace/get_related_cases', pair),
        'rules': call('workspace/get_handling_rules', {**pair,
            'expected_versions': {r['id']: r['version'] for r in found}})['data'],
        'report': call('workspace/get_investigation', {'contact_id': contact}),
    }
    raw = json.dumps(sources, indent=2, sort_keys=True).encode()
    (output / 'sources.json').write_bytes(raw)  # No access token; do not commit generated data.
    esc = lambda value: html.escape(str(value))

    def fields(values):
        return '<dl>' + ''.join('<dt>' + esc(k) + '</dt><dd>' + esc(v) + '</dd>'
                               for k, v in values.items()) + '</dl>'

    def bullets(values):
        return '<ul>' + ''.join('<li>' + esc(v) + '</li>' for v in values) + '</ul>'

    def page(name, title, body):
        document = ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<title>' + esc(title) + '</title><style>body{font:17px/1.5 system-ui;'
            'max-width:1050px;margin:32px auto;padding:0 24px;color:#17303b}'
            'dt{font-weight:600}dd{margin:0 0 10px}article{border:1px solid #bbb;'
            'padding:18px;margin:18px 0}small{color:#51616b}</style><body>'
            '<a href="index.html">Source index</a><p><small>Synthetic prepared evidence · '
            'read-only separated-source baseline · no Agent answer</small></p><h1>'
            + esc(title) + '</h1>' + body + '</body></html>')
        (output / (name + '.html')).write_text(document)

    transaction = sources['transactions']
    page('transactions', 'Transaction source', ''.join('<article>' + fields(r) + '</article>'
        for r in transaction['records']) + fields({'Recorded relationships': transaction['relationships']})
        + bullets(transaction['missing_evidence']))
    case_body = ''
    for case in sources['cases']['cases']:
        snap = case['snapshot']
        case_body += '<article>' + fields({k: case[k] for k in
            ('reference', 'concern', 'coverage', 'owner_queue_name', 'review_hint')})
        case_body += fields({k: snap[k] for k in ('case_version', 'case_status',
            'investigation_status', 'feedback_status', 'approved_customer_explanation')})
        case_body += '<h2>Work items</h2>' + ''.join('<article>' + fields(w) + '</article>'
            for w in case['work_items']) + '<h2>Unresolved items</h2>'
        case_body += bullets(snap['unresolved_items']) + '</article>'
    page('cases', 'Case source', case_body)
    rule = sources['rules']
    rule_body = fields({'state': rule['state'], **rule['context'], 'boundary': rule['boundary']})
    for item in rule['rules']:
        rule_body += '<article><h2>' + esc(item['title']) + '</h2>'
        rule_body += fields({**item['policy_ref'], 'source': item['source_label'], 'text': item['text']})
        rule_body += '<h3>Applicability</h3>' + bullets(item['applicability'])
        rule_body += '<h3>Next steps</h3>' + bullets(item['next_steps']) + '</article>'
    page('rules', 'Procedure source', rule_body)
    page('report', 'Customer report source', ''.join('<article>' + fields(r) + '</article>'
        for r in sources['report']['history']))
    page('index', 'Separated sources', '<p>Same selected synthetic pair and saved statement as the workspace. '
        'Identity/search preparation is outside the comparison. Open a source to read its fields.</p><ul>'
        + ''.join('<li><a href="' + key + '.html">' + title + '</a></li>' for key, title in
        [('transactions', 'Transaction source'), ('cases', 'Case source'),
         ('rules', 'Procedure source'), ('report', 'Customer report source')]) + '</ul>')
    manifest = {'captured_at': datetime.now(timezone.utc).isoformat(),
                'sources_sha256': hashlib.sha256(raw).hexdigest(), 'pages': 4}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps({'output': str(output), **manifest}, indent=2))


if __name__ == '__main__':
    main()
