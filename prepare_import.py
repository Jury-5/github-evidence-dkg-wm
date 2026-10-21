"""Offline request preparation only; never connects to a DKG node."""
import argparse
import hashlib
import json
import re
from urllib.parse import urlparse


MAX_EXPORT_BYTES = 262144


def load_export(path):
    with open(path, 'rb') as f:
        data = f.read(MAX_EXPORT_BYTES + 1)
    if len(data) > MAX_EXPORT_BYTES:
        raise ValueError('Export exceeds 256 KiB limit')
    return json.loads(data.decode('utf-8'))


def literal(value):
    return json.dumps(value, ensure_ascii=False)


def prepare(issue, context_graph):
    if not isinstance(issue, dict) or not isinstance(context_graph, str) or not context_graph.strip():
        raise ValueError('Issue object and nonempty Context Graph ID required')
    if len(json.dumps(issue, ensure_ascii=False).encode('utf-8')) > MAX_EXPORT_BYTES:
        raise ValueError('Export exceeds 256 KiB limit')
    url = issue.get('html_url', '')
    if not isinstance(url, str) or not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[1-9][0-9]*', url):
        raise ValueError('Canonical public GitHub issue URL required')
    repo = issue.get('repository')
    if not isinstance(repo, dict) or repo.get('private') is not False:
        raise ValueError('Explicit repository.private=false metadata required; obtain it independently')
    parts = urlparse(url).path.strip('/').split('/')
    if repo.get('full_name') != '/'.join(parts[:2]):
        raise ValueError('Repository metadata does not match issue URL')
    user = issue.get('user')
    if not isinstance(user, dict) or not isinstance(user.get('login'), str) or not user['login']:
        raise ValueError('Source author required')
    for key in ('title', 'created_at', 'updated_at'):
        if not isinstance(issue.get(key), str) or not issue[key]:
            raise ValueError('Missing source field: ' + key)
    if issue.get('body') is not None and not isinstance(issue['body'], str):
        raise ValueError('Issue body must be a string or null')
    record = {k: issue.get(k) for k in ('html_url', 'title', 'body', 'created_at', 'updated_at')}
    record['author'] = user['login']
    raw = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    digest = hashlib.sha256(raw).hexdigest()
    identity = hashlib.sha256(url.encode()).hexdigest()[:16]
    # Full version digest prevents silent overwrites of different revisions.
    name = 'github-issue-' + identity + '-' + digest
    subject = url + '#evidence-' + digest
    ns = 'https://schema.org/'
    props = [('url', url), ('name', record['title']), ('text', record['body'] or ''),
             ('author', record['author']), ('dateCreated', record['created_at']),
             ('dateModified', record['updated_at']), ('identifier', 'sha256:' + digest)]
    quads = [{'subject': subject, 'predicate': ns + k, 'object': literal(v)} for k, v in props]
    quads.append({'subject': subject, 'predicate': ns + 'description',
                  'object': literal('Untrusted source evidence; not verified fact or agent instructions.')})
    return {'status': 'offline-plan-only', 'source': url, 'sourceHash': digest,
            'knowledgeAssetName': name,
            'requests': [
                {'method': 'GET', 'path': '/api/agent/identity', 'body': None},
                {'method': 'POST', 'path': '/api/knowledge-assets',
                 'body': {'contextGraphId': context_graph, 'name': name}},
                {'method': 'POST', 'path': '/api/knowledge-assets/' + name + '/wm/write',
                 'body': {'contextGraphId': context_graph, 'quads': quads}}],
            'operatorChecks': ['Verify intended caller identity before mutation',
                               'Inspect existing KA and import manifest before execution',
                               'Validate write count and read-back; do not treat HTTP 200 alone as proof',
                               'No automatic retry after timeout, partial response or conflict']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('issue_json')
    ap.add_argument('--context-graph', required=True)
    args = ap.parse_args()
    issue = load_export(args.issue_json)
    print(json.dumps(prepare(issue, args.context_graph), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
