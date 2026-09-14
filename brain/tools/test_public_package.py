"""Standalone tutorial smoke tests with fictional content and no external service."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from check_public_package import check
from generate_now import load_project, project_record_paths, render
from init_project import initialize

ROOT = Path(__file__).resolve().parents[2]

class PublicPackageTests(unittest.TestCase):
    def test_all_document_links_and_metadata(self):
        with redirect_stdout(StringIO()):
            self.assertEqual([], check(ROOT))

    def test_sample_sections(self):
        text = (ROOT / 'projects/sample-report/05_output/report.md').read_text(encoding='utf-8')
        for section in ['成果', '残件', '次週']:
            self.assertIn('## ' + section, text)

    def test_create_record_resume_tutorial_without_private_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            initialize(root, 'my-first-project', 'Tutorial', 'projects', ['docs'])
            project = root / 'brain/projects/my-first-project.md'
            text = project.read_text(encoding='utf-8')
            text = text.replace('status: ACTIVE', 'status: WAITING').replace('current: 案件を初期化済み。一次資料、要件、現在の判断は未確認', 'current: Fictional draft ready')
            text = text.replace('next: 関連資料と要件を確認し、最初の実行可能な作業をProjectへ記録する', 'next: Ask reader to review')
            project.write_text(text, encoding='utf-8')
            records = [load_project(p) for p in project_record_paths(root / 'brain/projects')]
            output = render(records, root)
            self.assertIn('Fictional draft ready', output)
            self.assertIn('Ask reader to review', output)
            # Reload saved source; changing the view cannot change the Project.
            (root / 'brain/NOW.md').write_text('wrong view', encoding='utf-8')
            self.assertEqual('Fictional draft ready', load_project(project).current)
            regenerated = render([load_project(project)], root)
            self.assertEqual(output, regenerated)

if __name__ == '__main__':
    unittest.main()
