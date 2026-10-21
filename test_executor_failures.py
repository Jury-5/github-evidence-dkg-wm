"""Local HTTP failure-boundary tests. These do not replace DKG-node tests."""
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from import_issue import execute


class FailureTests(unittest.TestCase):
    def run_case(self, fault):
        calls = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def reply(self, status, data):
                self.send_response(status); self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            def do_GET(self):
                calls.append(('GET', self.path))
                if self.path == '/api/agent/identity':
                    self.reply(200, {'agentAddress': 'wrong' if fault == 'identity' else 'expected'})
                else:
                    self.reply(200, {'quads': [], 'count': 0})
            def do_POST(self):
                calls.append(('POST', self.path))
                self.rfile.read(int(self.headers.get('Content-Length', 0)))
                if fault == 'redirect':
                    self.send_response(302); self.send_header('Location', '/redirect-target'); self.end_headers()
                elif self.path.endswith('/wm/write'):
                    if fault == 'disconnect':
                        self.close_connection = True
                        return
                    if fault == 'oversized':
                        self.reply(200, {'padding': 'x' * 1048577})
                        return
                    if fault == 'partial': self.reply(207, {'written': 2, 'errors': ['partial']})
                    elif fault == 'badcount': self.reply(200, {'written': 1})
                    else: self.reply(200, {'written': 8})
                else:
                    self.reply(200, {'alreadyExists': fault == 'exists'})
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        issue = {'html_url': 'https://github.com/example/repo/issues/1',
                 'repository': {'private': False, 'full_name': 'example/repo'},
                 'user': {'login': 'fixture'}, 'title': 'fixture', 'body': '',
                 'created_at': '2026-10-20T00:00:00Z', 'updated_at': '2026-10-20T00:00:00Z'}
        try:
            with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directory:
                journal = Path(directory) / 'operation.json'
                with self.assertRaises(RuntimeError):
                    execute(issue, 'demo', 'http://127.0.0.1:'+str(server.server_port), 'synthetic-test-token', 'expected', journal)
                phase = json.loads(journal.read_text())['status'] if journal.exists() else None
                return calls, phase
        finally:
            server.shutdown(); server.server_close(); thread.join()

    def test_wrong_identity_never_mutates(self):
        calls, phase = self.run_case('identity')
        self.assertEqual(len(calls), 1); self.assertIsNone(phase)

    def test_existing_asset_never_appends(self):
        calls, phase = self.run_case('exists')
        self.assertEqual(len([c for c in calls if c[0]=='POST']), 1)
        self.assertEqual(phase, 'create-outcome-unknown')

    def test_lost_write_response_preserves_unknown_outcome(self):
        calls, phase = self.run_case('disconnect')
        self.assertEqual(len([c for c in calls if c[0]=='POST']), 2)
        self.assertEqual(phase, 'write-outcome-unknown')

    def test_oversized_response_stops_without_retry(self):
        calls, phase = self.run_case('oversized')
        self.assertEqual(len([c for c in calls if c[0]=='POST']), 2)
        self.assertEqual(phase, 'write-outcome-unknown')

    def test_partial_write_never_retries(self):
        calls, phase = self.run_case('partial')
        self.assertEqual(len([c for c in calls if c[0]=='POST']), 2)
        self.assertEqual(phase, 'write-outcome-unknown')

    def test_bad_write_count_stops_before_readback(self):
        calls, phase = self.run_case('badcount')
        self.assertEqual(len([c for c in calls if c[0]=='GET']), 1)
        self.assertEqual(phase, 'write-outcome-unknown')

    def test_bad_readback_never_reports_verified(self):
        calls, phase = self.run_case('readback')
        self.assertEqual(phase, 'written-readback-pending')

    def test_redirect_is_not_followed(self):
        calls, phase = self.run_case('redirect')
        self.assertFalse(any(path=='/redirect-target' for _,path in calls))
        self.assertEqual(phase, 'create-outcome-unknown')


if __name__ == '__main__':
    unittest.main()
