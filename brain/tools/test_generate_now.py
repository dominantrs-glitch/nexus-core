#!/usr/bin/env python3
"""Focused regression tests for the NOW generator."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("generate_now.py")
SPEC = importlib.util.spec_from_file_location("generate_now", MODULE_PATH)
assert SPEC and SPEC.loader
NOW = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = NOW
SPEC.loader.exec_module(NOW)


def write_project(root: Path, name: str, metadata: str) -> None:
    path = root / "brain" / "projects" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{metadata}\n---\n\n# {name}\n", encoding="utf-8")


class NowGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "NOW test"], cwd=self.root, check=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def commit_all(self, date: str) -> None:
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "-c", f"user.name=NOW test", "-c", f"user.email=test@example.invalid", "commit", "-qm", "fixture"],
            cwd=self.root,
            check=True,
            env={"GIT_AUTHOR_DATE": f"{date}T12:00:00+00:00", "GIT_COMMITTER_DATE": f"{date}T12:00:00+00:00"},
        )

    def test_snapshot_is_disposable_and_excludes_finished_projects(self) -> None:
        write_project(
            self.root,
            "active",
            """project: active\ntitle: 実装案件\nstatus: ACTIVE\nlast_confirmed: 2026-08-24\ncurrent: 実装済み\nnext: UAT\nwaiting_for: none\nshow_in_now: true\nwatch_paths:\n  - app/""",
        )
        write_project(
            self.root,
            "done",
            """project: done\ntitle: 完了案件\nstatus: DONE\nlast_confirmed: 2026-08-24\ncurrent: 完了\nnext:\nwaiting_for: none\nshow_in_now: false""",
        )
        (self.root / "app").mkdir()
        self.commit_all("2026-08-24")
        output = NOW.render([NOW.load_project(path) for path in sorted((self.root / "brain/projects").glob("*.md"))], self.root)
        self.assertIn("### 実装案件", output)
        self.assertIn("- **実装案件** — UAT", output)
        self.assertNotIn("完了案件", output)
        self.assertNotIn("生成日時", output)

    def test_later_watched_change_becomes_needs_check_without_claiming_progress(self) -> None:
        write_project(
            self.root,
            "waiting",
            """project: waiting\ntitle: 待機案件\nstatus: WAITING\nlast_confirmed: 2026-08-24\ncurrent: 記録済み状態\nnext: 本人確認\nwaiting_for: 本人UAT\nshow_in_now: true\nwatch_paths:\n  - app/""",
        )
        app_file = self.root / "app" / "file.txt"
        app_file.parent.mkdir()
        app_file.write_text("old", encoding="utf-8")
        self.commit_all("2026-08-24")
        app_file.write_text("new", encoding="utf-8")
        self.commit_all("2026-08-25")
        project = NOW.load_project(self.root / "brain/projects/waiting.md")
        output = NOW.render([project], self.root)
        self.assertIn("## NEEDS CHECK", output)
        self.assertIn("### 待機案件", output)
        self.assertIn("進捗は自動判定せず", output)
        active_waiting_section = output.split("## NEEDS CHECK", 1)[0]
        self.assertNotIn("### 待機案件", active_waiting_section)

    def test_supporting_note_without_project_metadata_is_ignored(self) -> None:
        project_dir = self.root / "brain" / "projects"
        project_dir.mkdir(parents=True)
        (project_dir / "design-note.md").write_text("# Design note\n\nnot a Project record\n", encoding="utf-8")
        write_project(
            self.root,
            "active",
            """project: active\ntitle: 実装案件\nstatus: ACTIVE\nlast_confirmed: 2026-08-24\ncurrent: 実装済み\nnext: UAT\nwaiting_for: none\nshow_in_now: true""",
        )
        records = NOW.project_record_paths(project_dir)
        self.assertEqual([project_dir / "active.md"], records)


if __name__ == "__main__":
    unittest.main()
