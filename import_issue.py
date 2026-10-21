"""Import a reviewed public export into local DKG WM; no SHARE/PUBLISH."""
import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from prepare_import import prepare, load_export


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Redirect refused; bearer token must stay on local node')


def execute(issue, graph, url, token, expected_author, journal_path):
    target = urllib.parse.urlsplit(url)
    if target.scheme != 'http' or target.hostname not in ('127.0.0.1', '::1') or target.username or target.password or target.query or target.fragment or target.path not in ('', '/'):
        raise ValueError('Explicit loopback HTTP origin required')
    if not token or not expected_author:
        raise ValueError('Token and expected caller identity required')
    plan = prepare(issue, graph)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    def call(method, path, body=None):
        payload = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(url.rstrip('/') + path, data=payload,
            headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}, method=method)
        with opener.open(req, timeout=20) as response:
            raw = response.read(1048577)
            if len(raw) > 1048576:
                raise RuntimeError('Node response exceeds 1 MiB limit')
            result = json.loads(raw)
            if response.status == 207 or not isinstance(result, dict) or result.get('errors') or result.get('error'):
                raise RuntimeError('Partial or invalid response; inspect local operation journal')
            return result
    identity = call('GET', '/api/agent/identity')
    if identity.get('agentAddress') != expected_author:
        raise RuntimeError('Caller identity mismatch; no mutation performed')
    journal = Path(journal_path)
    journal.parent.mkdir(parents=True, exist_ok=True)
    state = {'sourceHash': plan['sourceHash'], 'contextGraphId': graph,
             'nodeOrigin': url.rstrip('/'), 'expectedAuthor': expected_author,
             'knowledgeAssetName': plan['knowledgeAssetName'], 'status': 'prepared'}
    # Refuse all journal reuse, including failures: an operator must inspect ambiguous effects.
    with journal.open('x', encoding='utf-8') as f:
        json.dump(state, f)
    def persist(status):
        state['status'] = status
        tmp = journal.with_suffix(journal.suffix + '.tmp')
        with tmp.open('w', encoding='utf-8') as f:
            json.dump(state, f, indent=2); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, journal)
    name = plan['knowledgeAssetName']
    try:
        persist('create-outcome-unknown')
        created = call('POST', '/api/knowledge-assets', plan['requests'][1]['body'])
        if created.get('alreadyExists') is not False:
            raise RuntimeError('Existing or ambiguous KA; refusing append')
        persist('created')
        persist('write-outcome-unknown')
        result = call('POST', plan['requests'][2]['path'], plan['requests'][2]['body'])
        expected = plan['requests'][2]['body']['quads']
        if result.get('written') != len(expected):
            raise RuntimeError('Written count mismatch')
        persist('written-readback-pending')
        result = call('GET', '/api/knowledge-assets/' + name + '/wm/quads?contextGraphId=' + urllib.parse.quote(graph, safe=''))
        canonical = lambda quads: sorted((q['subject'], q['predicate'], q['object']) for q in quads)
        if result.get('count') != len(expected) or canonical(result.get('quads', [])) != canonical(expected):
            raise RuntimeError('Readback differs from planned evidence')
        persist('verified')
        return state
    except Exception:
        # Keep the last durable phase. Never automatically retry a mutation.
        raise RuntimeError('Import stopped; inspect journal phase before recovery') from None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('issue_json'); p.add_argument('--context-graph', required=True)
    p.add_argument('--node-url', default='http://127.0.0.1:19240')
    p.add_argument('--expected-author', required=True)
    p.add_argument('--journal', required=True)
    a = p.parse_args()
    issue = load_export(a.issue_json)
    result = execute(issue, a.context_graph, a.node_url, os.environ.get('DKG_AUTH_TOKEN', ''), a.expected_author, a.journal)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
