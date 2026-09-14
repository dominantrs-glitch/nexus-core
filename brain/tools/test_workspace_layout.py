"""Guard against reintroducing scattered app files in project roots."""
import json
from pathlib import Path
import tempfile
import unittest
from check_workspace_layout import violations
from init_project import initialize

CONFIG=json.loads((Path(__file__).resolve().parents[1]/'config/workspace-layout.json').read_text(encoding='utf-8'))

class LayoutTests(unittest.TestCase):
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

if __name__=='__main__':unittest.main()
