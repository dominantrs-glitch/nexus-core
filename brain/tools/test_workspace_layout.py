"""Guard against reintroducing scattered app files in project roots."""
import json
import re
from pathlib import Path
import tempfile
import unittest
from check_workspace_layout import violations
from init_project import initialize
from urllib.parse import unquote

CONFIG=json.loads((Path(__file__).resolve().parents[1]/'config/workspace-layout.json').read_text(encoding='utf-8'))

class LayoutTests(unittest.TestCase):
    def test_new_project_names_are_consistent(self):
        self.assertEqual(1, len(violations(['projects/New_Project/README.md'], CONFIG)))
        self.assertEqual([], violations(['projects/new-project/README.md'], CONFIG))
        for name in CONFIG.get('existing_project_names', {}):
            self.assertEqual([], violations([f'projects/{name}/README.md'], CONFIG))

    def test_initialized_navigation_links_reach_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in ['context/docs/workspace-contract.md', 'brain/docs/deliverable-recording.md']:
                file = root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text('Test reference', encoding='utf-8')
            created = initialize(root, 'demo', 'Demo', 'projects', ['docs'])
            for file in created:
                if file.suffix != '.md':
                    continue
                for link in re.findall(r'\[[^\]\n]*\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
                    if '://' not in link:
                        self.assertTrue((file.parent / unquote(link.split('#')[0])).exists(), f'{file}: {link}')

    def test_navigation_layers_reject_loose_documents(self):
        scattered = ['goal.md', 'WORKSPACE_CONTRACT.md', 'brain/NOW.md',
                     'brain/inbox.md', 'projects/demo/goal.md', 'projects/demo/MANIFEST.md',
                     'projects/demo/03_context/context.md', 'projects/demo/07_logs/decisions.md']
        self.assertEqual(len(scattered), len(violations(scattered, CONFIG)))
        self.assertEqual([], violations(['context/docs/workspace-contract.md',
            'brain/indexes/NOW.md', 'brain/inbox/items.md', 'projects/demo/03_context/README.md',
            'projects/demo/03_context/docs/goal.md', 'projects/demo/07_logs/decisions/record.md'], CONFIG))

    def test_rejects_loose_code_but_accepts_numbered_layers(self):
        self.assertEqual(2,len(violations(['projects/demo/main.py','projects/demo/src/main.py'],CONFIG)))
        self.assertEqual([],violations(['projects/demo/README.md','projects/demo/06_app/main.py',
            'projects/demo/06_app/src/main.py','projects/demo/03_context/docs/setup.md'],CONFIG))

    def test_initializer_places_app_and_docs_without_loose_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            initialize(root,'demo','Demo','projects',['06_app','src','tests','docs','runtime','08_archive'])
            p=root/'projects/demo'
            self.assertTrue((p/'06_app/src/.gitkeep').exists())
            self.assertTrue((p/'03_context/docs/.gitkeep').exists())
            self.assertEqual('*\n!.gitignore\n',(p/'06_app/runtime/.gitignore').read_text())
            self.assertFalse((p/'src').exists())
            self.assertFalse((p/'docs').exists())
            self.assertEqual([], violations([f.relative_to(root).as_posix() for f in root.rglob('*') if f.is_file()], CONFIG))

if __name__=='__main__':unittest.main()
