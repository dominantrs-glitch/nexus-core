#!/usr/bin/env python3
"""Report Git session safety without changing the working tree or pushing."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


EXIT_COMPLETE = 0
EXIT_COMMIT_REVIEW = 10
EXIT_PUSH_REQUIRED = 11
EXIT_REMOTE_NOT_VERIFIED = 12
EXIT_SYNC_REVIEW = 13


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def run_git(repo_root: Path, *args: str) -> CommandResult:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        return CommandResult(1, "", str(error))
    # Porcelain status uses a leading space to distinguish index and worktree
    # changes.  Preserve it while removing only trailing line terminators.
    return CommandResult(completed.returncode, completed.stdout.rstrip(), completed.stderr.strip())


def status_entries(repo_root: Path) -> tuple[int, int, int, CommandResult]:
    result = run_git(repo_root, "status", "--porcelain=v1", "--untracked-files=all")
    staged = unstaged = untracked = 0
    if result.returncode:
        return staged, unstaged, untracked, result
    for line in result.stdout.splitlines():
        if line.startswith("??"):
            untracked += 1
            continue
        if len(line) >= 2:
            staged += line[0] != " "
            unstaged += line[1] != " "
    return staged, unstaged, untracked, result


def print_check(label: str, state: str, detail: str) -> None:
    print(f"[{state}] {label}: {detail}")


def complete_result(phase: str) -> str:
    return "START READY" if phase == "start" else "GITHUB BACKUP COMPLETE"


def check_session(repo_root: Path, phase: str) -> int:
    print("Git session check")
    repository = run_git(repo_root, "rev-parse", "--is-inside-work-tree")
    if repository.returncode or repository.stdout != "true":
        print_check("repository detected", "FAIL", "not a Git working tree")
        print("RESULT: GIT REPOSITORY REQUIRED")
        return EXIT_SYNC_REVIEW
    print_check("repository detected", "PASS", str(repo_root))

    branch = run_git(repo_root, "symbolic-ref", "--quiet", "--short", "HEAD")
    detached = branch.returncode != 0
    if detached:
        print_check("branch", "FAIL", "detached HEAD")
    else:
        print_check("branch", "PASS", branch.stdout)

    staged, unstaged, untracked, status = status_entries(repo_root)
    if status.returncode:
        print_check("working tree status", "FAIL", status.stderr or "could not read status")
        print("RESULT: COMMIT REVIEW REQUIRED")
        return EXIT_COMMIT_REVIEW
    if staged or unstaged:
        print_check("tracked changes", "FAIL", f"staged: {staged}; unstaged: {unstaged}")
    else:
        print_check("working tree clean", "PASS", "no tracked changes")
    print_check("staged changes", "FAIL" if staged else "PASS", str(staged))
    print_check("unstaged tracked changes", "FAIL" if unstaged else "PASS", str(unstaged))
    print_check(
        "untracked non-ignored files",
        "WARN" if untracked else "PASS",
        str(untracked) + ("; require review" if untracked else ""),
    )

    local_head = run_git(repo_root, "rev-parse", "HEAD")
    if local_head.returncode:
        print_check("local HEAD", "FAIL", "repository has no commit yet")
    else:
        print_check("local HEAD", "PASS", local_head.stdout)

    remotes = run_git(repo_root, "remote")
    fetch_ok = False
    if remotes.returncode or not remotes.stdout:
        print_check("remote state refreshed", "WARN", "no remote configured")
    else:
        fetched = run_git(repo_root, "fetch", "--prune")
        fetch_ok = fetched.returncode == 0
        if fetch_ok:
            print_check("remote state refreshed", "PASS", "git fetch --prune succeeded")
        else:
            print_check("remote state refreshed", "FAIL", fetched.stderr or "git fetch --prune failed")

    upstream = run_git(repo_root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    upstream_ok = upstream.returncode == 0
    if upstream_ok:
        print_check("upstream configured", "PASS", upstream.stdout)
    else:
        print_check("upstream configured", "FAIL", "no upstream configured for current branch")

    behind = ahead = None
    upstream_head = CommandResult(1, "", "")
    if upstream_ok and fetch_ok:
        counts = run_git(repo_root, "rev-list", "--left-right", "--count", "@{upstream}...HEAD")
        try:
            behind, ahead = (int(value) for value in counts.stdout.split())
        except ValueError:
            print_check("upstream comparison", "FAIL", counts.stderr or "could not count commits")
        else:
            print_check("behind", "PASS" if behind == 0 else "FAIL", str(behind))
            print_check("ahead", "PASS" if ahead == 0 else "FAIL", str(ahead))
        upstream_head = run_git(repo_root, "rev-parse", "@{upstream}")
        if upstream_head.returncode:
            print_check("upstream HEAD", "FAIL", upstream_head.stderr or "could not resolve upstream")
        else:
            print_check("upstream HEAD", "PASS", upstream_head.stdout)
    elif upstream_ok:
        print_check("upstream comparison", "FAIL", "remote state was not refreshed")

    if detached:
        print("RESULT: BRANCH REVIEW REQUIRED")
        return EXIT_SYNC_REVIEW
    if local_head.returncode:
        print("RESULT: COMMIT REVIEW REQUIRED" if staged or unstaged or untracked else "RESULT: INITIAL COMMIT REQUIRED")
        return EXIT_COMMIT_REVIEW
    if not upstream_ok:
        print("RESULT: UPSTREAM REQUIRED")
        return EXIT_SYNC_REVIEW
    if not fetch_ok:
        print("RESULT: REMOTE NOT VERIFIED")
        print("Do not report GitHub backup as complete.")
        return EXIT_REMOTE_NOT_VERIFIED
    if staged or unstaged or untracked:
        print("RESULT: COMMIT REVIEW REQUIRED")
        return EXIT_COMMIT_REVIEW
    if behind is None or ahead is None:
        print("RESULT: REMOTE NOT VERIFIED")
        return EXIT_REMOTE_NOT_VERIFIED
    if behind and ahead:
        print("RESULT: DIVERGENCE REVIEW REQUIRED")
        return EXIT_SYNC_REVIEW
    if behind:
        print("RESULT: SYNCHRONIZATION REQUIRED")
        return EXIT_SYNC_REVIEW
    if ahead:
        print("RESULT: PUSH REQUIRED")
        print("GitHub backup is not complete.")
        return EXIT_PUSH_REQUIRED
    if local_head.stdout == upstream_head.stdout:
        print_check("local HEAD matches upstream", "PASS", "yes")
        print(f"RESULT: {complete_result(phase)}")
        return EXIT_COMPLETE
    print_check("local HEAD matches upstream", "FAIL", "no")
    print("RESULT: SYNCHRONIZATION REQUIRED")
    return EXIT_SYNC_REVIEW


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--phase", choices=("start", "end"), default="end")
    args = parser.parse_args()
    return check_session(args.repo_root.resolve(), args.phase)


if __name__ == "__main__":
    sys.exit(main())
