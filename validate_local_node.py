"""Run with an existing authorized local node and synthetic data only."""
import argparse
import json
import os
import secrets
import urllib.parse
import urllib.request
from import_issue import NoRedirect, execute


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--node-url', default='http://127.0.0.1:19240')
    p.add_argument('--context-graph', required=True)
    p.add_argument('--expected-author', required=True)
    p.add_argument('--journal', required=True)
    args = p.parse_args()
    issue = {'html_url': 'https://github.com/example/repo/issues/9',
             'repository': {'private': False, 'full_name': 'example/repo'},
             'user': {'login': 'synthetic-fixture'}, 'title': 'Synthetic DKG walkthrough',
             'body': 'Unicode Ж and quoted "evidence". Run nonce: ' + secrets.token_hex(8),
             'created_at': '2026-10-20T00:00:00Z', 'updated_at': '2026-10-20T00:00:00Z'}
    print('Synthetic fixture prepared; no GitHub request', flush=True)
    token = os.environ.get('DKG_AUTH_TOKEN', '')
    result = execute(issue, args.context_graph, args.node_url, token, args.expected_author, args.journal)
    print('Caller verified; named WM draft written and exact read-back verified', flush=True)
    try:
        execute(issue, args.context_graph, args.node_url, token, args.expected_author, args.journal)
    except FileExistsError:
        print('Duplicate journal refused; no second mutation', flush=True)
    else:
        raise RuntimeError('Duplicate journal unexpectedly accepted')
    print(json.dumps({'status': result['status'], 'quadCount': 8, 'chainValidation': 'not performed',
                      'shareOrPublish': False, 'rewardClaimed': False}), flush=True)


if __name__ == '__main__':
    main()
