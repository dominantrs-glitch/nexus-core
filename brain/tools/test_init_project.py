#!/usr/bin/env python3
"""Regression tests for the deterministic Project Workspace initializer."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("init_project.py")


class InitProjectTests(unittest.TestCase):
    def run_initializer(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--repo-root", str(root)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_creates_minimal_workspace_and_project_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.run_initializer(root, "monthly-report", "Monthly Report")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((root / "projects/monthly-report/04_work/.gitkeep").is_file())
            self.assertTrue((root / "projects/monthly-report/05_output/.gitkeep").is_file())
            self.assertTrue((root / "projects/monthly-report/03_context/docs/goal.md").is_file())
            self.assertTrue((root / "projects/monthly-report/03_context/docs/context.md").is_file())
            self.assertTrue((root / "projects/monthly-report/07_logs/decisions/record.md").is_file())
            readme = (root / "projects/monthly-report/README.md").read_text(encoding="utf-8")
            self.assertIn("03_context/README.md", readme)
            project = (root / "brain/projects/monthly-report.md").read_text(encoding="utf-8")
            self.assertIn("project: monthly-report", project)
            self.assertIn("projects/monthly-report", project)
            self.assertFalse((root / "projects/monthly-report/01_raw").exists())

    def test_optional_layers_are_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.run_initializer(root, "source-review", "Source Review", "--with", "01_raw", "02_web", "08_archive", "09_skills")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((root / "projects/source-review/01_raw/README.md").is_file())
            self.assertTrue((root / "projects/source-review/02_web/README.md").is_file())
            for name in ("08_archive", "09_skills"):
                self.assertTrue((root / "projects/source-review" / name / ".gitkeep").is_file())

    def test_second_run_does_not_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = self.run_initializer(root, "audit", "Audit")
            self.assertEqual(0, first.returncode, first.stderr)
            project_path = root / "brain/projects/audit.md"
            original = project_path.read_text(encoding="utf-8")
            second = self.run_initializer(root, "audit", "Changed Title")
            self.assertEqual(0, second.returncode, second.stderr)
            self.assertIn("no files were changed", second.stdout)
            self.assertEqual(original, project_path.read_text(encoding="utf-8"))

    def test_rejects_unsafe_slug(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self.run_initializer(Path(temporary), "../unsafe", "Unsafe")
            self.assertEqual(2, result.returncode)
            self.assertIn("slug", result.stderr)


if __name__ == "__main__":
    unittest.main()
