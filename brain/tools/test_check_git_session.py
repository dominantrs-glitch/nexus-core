from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("check_git_session.py")


def git(directory: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(directory), *args], text=True, capture_output=True, check=True)


class GitSessionCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.remote = self.root / "remote.git"
        self.work = self.root / "work"
        git(self.root, "init", "--bare", str(self.remote))
        git(self.root, "clone", str(self.remote), str(self.work))
        git(self.work, "config", "user.email", "test@example.invalid")
        git(self.work, "config", "user.name", "Git session test")
        (self.work / ".gitignore").write_text("ignored.tmp\n", encoding="utf-8")
        (self.work / "tracked.txt").write_text("base\n", encoding="utf-8")
        git(self.work, "add", ".gitignore", "tracked.txt")
        git(self.work, "commit", "-m", "Initial fixture")
        git(self.work, "push", "-u", "origin", "HEAD")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def check(self, directory: Path | None = None, phase: str = "end") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(directory or self.work), "--phase", phase],
            text=True,
            capture_output=True,
            check=False,
        )

    def commit_local_change(self) -> None:
        (self.work / "tracked.txt").write_text("local\n", encoding="utf-8")
        git(self.work, "add", "tracked.txt")
        git(self.work, "commit", "-m", "Local change")

    def add_remote_change(self) -> None:
        peer = self.root / "peer"
        git(self.root, "clone", str(self.remote), str(peer))
        git(peer, "config", "user.email", "test@example.invalid")
        git(peer, "config", "user.name", "Git session test")
        (peer / "remote.txt").write_text("remote\n", encoding="utf-8")
        git(peer, "add", "remote.txt")
        git(peer, "commit", "-m", "Remote change")
        git(peer, "push")

    def assert_result(self, result: subprocess.CompletedProcess[str], text: str, code: int | None = None) -> None:
        self.assertIn(text, result.stdout + result.stderr)
        if code is not None:
            self.assertEqual(code, result.returncode, result.stdout + result.stderr)
        else:
            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)

    def test_clean_matching_upstream_is_complete(self) -> None:
        self.assert_result(self.check(), "RESULT: GITHUB BACKUP COMPLETE", 0)

    def test_start_phase_reports_ready(self) -> None:
        self.assert_result(self.check(phase="start"), "RESULT: START READY", 0)

    def test_unstaged_tracked_changes_require_commit_review(self) -> None:
        (self.work / "tracked.txt").write_text("changed\n", encoding="utf-8")
        result = self.check()
        self.assert_result(result, "RESULT: COMMIT REVIEW REQUIRED")
        self.assertIn("[PASS] staged changes: 0", result.stdout)
        self.assertIn("[FAIL] unstaged tracked changes: 1", result.stdout)

    def test_staged_changes_require_commit_review(self) -> None:
        (self.work / "tracked.txt").write_text("changed\n", encoding="utf-8")
        git(self.work, "add", "tracked.txt")
        result = self.check()
        self.assert_result(result, "RESULT: COMMIT REVIEW REQUIRED")
        self.assertIn("[FAIL] staged changes: 1", result.stdout)
        self.assertIn("[PASS] unstaged tracked changes: 0", result.stdout)

    def test_untracked_file_requires_commit_review(self) -> None:
        (self.work / "new.txt").write_text("new\n", encoding="utf-8")
        self.assert_result(self.check(), "RESULT: COMMIT REVIEW REQUIRED")

    def test_local_ahead_requires_push(self) -> None:
        self.commit_local_change()
        self.assert_result(self.check(), "RESULT: PUSH REQUIRED")

    def test_local_behind_requires_synchronization_review(self) -> None:
        self.add_remote_change()
        self.assert_result(self.check(), "RESULT: SYNCHRONIZATION REQUIRED")

    def test_diverged_history_requires_review(self) -> None:
        self.commit_local_change()
        self.add_remote_change()
        self.assert_result(self.check(), "RESULT: DIVERGENCE REVIEW REQUIRED")

    def test_missing_upstream_requires_review(self) -> None:
        git(self.work, "branch", "--unset-upstream")
        self.assert_result(self.check(), "RESULT: UPSTREAM REQUIRED")

    def test_detached_head_requires_review(self) -> None:
        git(self.work, "checkout", "--detach")
        self.assert_result(self.check(), "RESULT: BRANCH REVIEW REQUIRED")

    def test_fetch_failure_is_not_treated_as_synchronized(self) -> None:
        git(self.work, "remote", "set-url", "origin", str(self.root / "missing.git"))
        self.assert_result(self.check(), "RESULT: REMOTE NOT VERIFIED")

    def test_push_then_matching_upstream_is_complete(self) -> None:
        self.commit_local_change()
        git(self.work, "push")
        self.assert_result(self.check(), "RESULT: GITHUB BACKUP COMPLETE", 0)

    def test_ignored_files_do_not_block_completion(self) -> None:
        (self.work / "ignored.tmp").write_text("ignored\n", encoding="utf-8")
        self.assert_result(self.check(), "RESULT: GITHUB BACKUP COMPLETE", 0)

    def test_empty_repository_requires_initial_commit(self) -> None:
        empty = self.root / "empty"
        git(self.root, "init", str(empty))
        self.assert_result(self.check(empty), "RESULT: INITIAL COMMIT REQUIRED")


if __name__ == "__main__":
    unittest.main()
