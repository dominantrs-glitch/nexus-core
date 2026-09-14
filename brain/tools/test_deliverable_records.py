"""Isolated tests: no production records, network or application execution."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import check_deliverable_records as checker


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.name = 'projects/demo/07_logs/completions/release.md'
        self.meta = {'schema': 1, 'project_record': 'brain/projects/demo.md',
                     'recorded_at': '2026-09-15', 'event_date': '2026-09-10',
                     'review_state': 'reviewed', 'evidence_state': 'sufficient',
                     'origin': 'retrospective', 'source_snapshot': 'a' * 40,
                     'artifacts': [{'path': 'projects/demo/05_output/tool.txt', 'role': 'final'}],
                     'sources': [{'path': 'projects/demo/07_logs/test.md', 'basis': 'test-result'}]}
        for p in ['brain/projects/demo.md', 'projects/demo/05_output/tool.txt', 'projects/demo/07_logs/test.md']:
            target = self.root / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('fixture only', encoding='utf-8')
        self.write()

    def write(self, meta=None, body=None):
        p = self.root / self.name
        p.parent.mkdir(parents=True, exist_ok=True)
        if body is None:
            body = '\n'.join('## ' + h + '\nFixture-supported text.\n' for h in checker.SECTIONS)
        p.write_text('# Test\n\n```trace\n' + json.dumps(meta or self.meta) + '\n```\n\n' + body, encoding='utf-8')

    def run_cli(self, *args):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            return checker.main(['--root', str(self.root), *args])

    def test_valid(self):
        self.assertEqual(checker.read_record(self.root, self.name)[1], [])
        self.assertEqual(self.run_cli('--strict'), 0)

    def test_missing_artifact(self):
        (self.root / self.meta['artifacts'][0]['path']).unlink()
        self.assertEqual(self.run_cli(), 2)

    def test_missing_source(self):
        (self.root / self.meta['sources'][0]['path']).unlink()
        self.assertEqual(self.run_cli(), 2)

    def test_empty_records_not_pass(self):
        (self.root / self.name).unlink()
        self.assertEqual(self.run_cli(), 2)

    def test_gaps_recordable_but_not_strict_pass(self):
        self.meta['evidence_state'] = 'gaps'
        self.write()
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(self.run_cli('--strict'), 3)

    def test_partial_not_strict_pass(self):
        self.meta['review_state'] = 'partial'
        self.write()
        self.assertEqual(self.run_cli('--strict'), 3)

    def test_traversal_and_absolute_paths(self):
        for path in ['../outside.md', '/etc/passwd', 'C:\\private.txt', 'a/../b', 'https://example.org/a', None, '']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                checker.within(self.root, path)

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as other:
            try:
                (self.root / 'outside').symlink_to(Path(other), target_is_directory=True)
            except OSError:
                self.skipTest('symlinks unavailable')
            with self.assertRaises(ValueError):
                checker.within(self.root, 'outside/file')

    def test_malformed_json_and_duplicate_keys(self):
        p = self.root / self.name
        for text in ['not json', '{"schema":1,"schema":1}', '[]']:
            p.write_text('```trace\n' + text + '\n```\n', encoding='utf-8')
            self.assertEqual(self.run_cli(), 2)

    def test_invalid_state_type(self):
        self.meta['review_state'] = []
        self.write()
        self.assertEqual(self.run_cli(), 2)

    def test_invalid_dates(self):
        self.meta['event_date'] = '2026-02-30'
        self.write()
        self.assertEqual(self.run_cli(), 2)
        self.meta['event_date'] = 'unknown'
        self.write()
        self.assertEqual(self.run_cli(), 0)

    def test_missing_section(self):
        self.write(body='## 成果物と完成範囲\nOnly one section.')
        self.assertEqual(self.run_cli(), 2)

    def test_fenced_example_does_not_supply_sections(self):
        self.write(body='```md\n' + '\n'.join('## ' + h + '\nExample' for h in checker.SECTIONS) + '\n```\n')
        self.assertEqual(self.run_cli(), 2)

    def test_directory_sources_rejected(self):
        self.meta['sources'][0]['path'] = 'projects/demo'
        self.write()
        self.assertEqual(self.run_cli(), 2)

    def test_directory_artifact_explicit_role(self):
        self.meta['artifacts'][0]['path'] = 'projects/demo'
        self.write()
        self.assertEqual(self.run_cli(), 2)
        self.meta['artifacts'][0]['role'] = 'source-tree'
        self.write()
        self.assertEqual(self.run_cli(), 0)

    def test_scoped_check(self):
        self.assertEqual(self.run_cli('--record', self.name, '--strict'), 0)
        self.assertEqual(self.run_cli('--record', 'not-found.md'), 2)

    def test_inventory_tracks_names_without_reading_body(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        archive = self.root / 'projects/demo/08_archive/old.txt'
        archive.parent.mkdir()
        archive.write_text('fixture', encoding='utf-8')
        private = self.root / 'projects/demo/05_output/not-tracked.txt'
        private.write_text('must not be indexed', encoding='utf-8')
        subprocess.run(['git', '-C', str(self.root), 'add', '--', 'projects/demo/05_output/tool.txt', 'projects/demo/08_archive/old.txt'], check=True)
        text = checker.inventory(self.root, {self.name: self.meta})
        self.assertIn('old.txt', text)
        self.assertIn(self.name, text)
        self.assertNotIn('not-tracked.txt', text)
        self.assertNotIn('must not be indexed', text)

    def test_lookup(self):
        self.assertEqual(self.run_cli('--lookup', self.meta['artifacts'][0]['path']), 0)
        self.assertEqual(self.run_cli('--lookup', 'projects/demo/05_output/other.txt'), 4)

    def test_lookup_rejects_traversal(self):
        self.assertEqual(self.run_cli('--lookup', '../outside'), 2)

    def test_read_only(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.run_cli('--strict')
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
