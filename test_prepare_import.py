import copy
import json
import unittest
from prepare_import import prepare


class PrepareTests(unittest.TestCase):
    def setUp(self):
        self.issue = {'html_url': 'https://github.com/example/repo/issues/7',
                      'repository': {'private': False, 'full_name': 'example/repo'},
                      'title': 'Example', 'body': 'Quote " and newline\nЮникод',
                      'user': {'login': 'example'},
                      'created_at': '2026-10-19T00:00:00Z', 'updated_at': '2026-10-19T01:00:00Z'}

    def test_roundtrip_literals_and_no_publication(self):
        p = prepare(self.issue, 'local-demo')
        quads = p['requests'][2]['body']['quads']
        text = next(q for q in quads if q['predicate'].endswith('/text'))
        self.assertEqual(json.loads(text['object']), self.issue['body'])
        self.assertFalse(any('/share' in r['path'] or '/publish' in r['path'] for r in p['requests']))

    def test_oversized_export_rejected(self):
        self.issue['body'] = 'x' * 262145
        with self.assertRaises(ValueError):
            prepare(self.issue, 'local-demo')

    def test_revision_identity(self):
        p = prepare(self.issue, 'local-demo')
        self.assertEqual(p, prepare(copy.deepcopy(self.issue), 'local-demo'))
        self.issue['body'] += ' changed'
        self.assertNotEqual(p['knowledgeAssetName'], prepare(self.issue, 'local-demo')['knowledgeAssetName'])

    def test_private_and_unknown_visibility_rejected(self):
        for meta in ({}, {'private': True, 'full_name': 'example/repo'}):
            self.issue['repository'] = meta
            with self.assertRaises(ValueError):
                prepare(self.issue, 'local-demo')

    def test_wrong_repository_and_url_rejected(self):
        self.issue['repository']['full_name'] = 'someone/else'
        with self.assertRaises(ValueError):
            prepare(self.issue, 'local-demo')
        self.issue['html_url'] = 'https://evil.example/issue'
        with self.assertRaises(ValueError):
            prepare(self.issue, 'local-demo')


if __name__ == '__main__':
    unittest.main()
