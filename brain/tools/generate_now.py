#!/usr/bin/env python3
"""Generate the disposable brain/indexes/NOW.md snapshot from Project metadata.

Project files are the source of truth.  This script deliberately does not
interpret their prose or update their metadata; it only renders the current
snapshot and optionally flags records whose watched files changed later.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


VALID_STATUSES = {"ACTIVE", "WAITING", "MAINTENANCE", "STABLE", "DONE", "ARCHIVED"}
REQUIRED_FIELDS = {
    "project",
    "title",
    "status",
    "last_confirmed",
    "current",
    "next",
    "waiting_for",
    "show_in_now",
}
EMPTY_SCALAR_FIELDS = {"next", "waiting_for"}


class MetadataError(ValueError):
    """Project metadata is missing or cannot be safely interpreted."""


@dataclass(frozen=True)
class Project:
    path: Path
    project: str
    title: str
    status: str
    last_confirmed: date
    current: str
    next_action: str
    waiting_for: str
    show_in_now: bool
    watch_paths: tuple[str, ...]


def parse_front_matter(path: Path) -> dict[str, str | list[str]]:
    """Read the intentionally small YAML subset used by Project metadata."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise MetadataError(f"{path}: metadata must begin with ---")

    try:
        closing_index = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as error:
        raise MetadataError(f"{path}: metadata is missing its closing ---") from error

    metadata: dict[str, str | list[str]] = {}
    active_list: str | None = None
    for line in lines[1:closing_index]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.strip()
        if stripped.startswith("-"):
            if active_list is None:
                raise MetadataError(f"{path}: list item without a key")
            value = stripped[1:].strip()
            if not value:
                raise MetadataError(f"{path}: empty list item for {active_list}")
            assert isinstance(metadata[active_list], list)
            metadata[active_list].append(value)
            continue
        if ":" not in line or line.startswith((" ", "\t")):
            raise MetadataError(f"{path}: unsupported metadata line: {line}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if not key or key in metadata:
            raise MetadataError(f"{path}: invalid or duplicate metadata key: {key}")
        if value:
            metadata[key] = value
            active_list = None
        else:
            metadata[key] = []
            active_list = key
    return metadata


def load_project(path: Path) -> Project:
    metadata = parse_front_matter(path)
    missing = REQUIRED_FIELDS - metadata.keys()
    if missing:
        raise MetadataError(f"{path}: missing required metadata: {', '.join(sorted(missing))}")
    for key in EMPTY_SCALAR_FIELDS:
        if metadata.get(key) == []:
            metadata[key] = ""
    if any(isinstance(metadata[key], list) for key in REQUIRED_FIELDS):
        raise MetadataError(f"{path}: required metadata values must be one line")

    status = str(metadata["status"])
    if status not in VALID_STATUSES:
        raise MetadataError(f"{path}: unsupported status: {status}")
    show_value = str(metadata["show_in_now"]).lower()
    if show_value not in {"true", "false"}:
        raise MetadataError(f"{path}: show_in_now must be true or false")
    raw_watch_paths = metadata.get("watch_paths", [])
    if isinstance(raw_watch_paths, str):
        raise MetadataError(f"{path}: watch_paths must be a list")
    try:
        confirmed = date.fromisoformat(str(metadata["last_confirmed"]))
    except ValueError as error:
        raise MetadataError(f"{path}: last_confirmed must be YYYY-MM-DD") from error

    return Project(
        path=path,
        project=str(metadata["project"]),
        title=str(metadata["title"]),
        status=status,
        last_confirmed=confirmed,
        current=str(metadata["current"]),
        next_action=str(metadata["next"]),
        waiting_for=str(metadata["waiting_for"]),
        show_in_now=show_value == "true",
        watch_paths=tuple(raw_watch_paths),
    )


def project_record_paths(project_dir: Path) -> list[Path]:
    """Return only Project records; supporting design notes need no NOW metadata."""
    paths: list[Path] = []
    for path in sorted(project_dir.glob("*.md")):
        first_line = path.read_text(encoding="utf-8").splitlines()[:1]
        if first_line and first_line[0].strip() == "---":
            paths.append(path)
    return paths


def git_last_changed(root: Path, relative_path: str) -> date | None:
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise MetadataError(f"watch path escapes the repository: {relative_path}") from error
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", relative_path],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        # A fresh ZIP + git init has no HEAD yet; no historical change exists.
        # Invalid repositories and repositories with other history still fail.
        history = subprocess.run(
            ["git", "rev-list", "--all", "--max-count=1"], cwd=root,
            check=True, capture_output=True, text=True,
        )
        if not history.stdout.strip():
            return None
        result.check_returncode()
    value = result.stdout.strip()
    return date.fromisoformat(value) if value else None


def needs_check(project: Project, root: Path) -> tuple[str, ...]:
    changed_paths: list[str] = []
    for watched_path in project.watch_paths:
        changed = git_last_changed(root, watched_path)
        if changed and changed > project.last_confirmed:
            changed_paths.append(watched_path)
    return tuple(changed_paths)


def render(projects: list[Project], root: Path) -> str:
    seen = set()
    for project in projects:
        if project.project in seen:
            raise MetadataError(f"duplicate project metadata id: {project.project}")
        seen.add(project.project)

    visible = [
        project
        for project in projects
        if project.show_in_now and project.status not in {"DONE", "ARCHIVED"}
    ]
    stale = {project.project: needs_check(project, root) for project in visible}
    current = [project for project in visible if not stale[project.project]]
    active = [
        project
        for project in current
        if project.status == "ACTIVE"
        or (project.status in {"MAINTENANCE", "STABLE"} and project.next_action)
    ]
    waiting = [project for project in current if project.status == "WAITING"]
    actionable = [project for project in active + waiting if project.next_action and project.next_action.lower() != "none"]
    actionable.sort(key=lambda item: (item.status != "ACTIVE", item.title))

    lines = ["# NOW", "", "## NEXT", ""]
    if actionable:
        for project in actionable[:5]:
            lines.append(f"- **{project.title}** — {project.next_action}")
    else:
        lines.append("現在、記録された次のAI作業はありません。")

    lines.extend(["", "## ACTIVE", ""])
    if active:
        for project in active:
            lines.extend(
                [
                    f"### {project.title}",
                    *([f"- 状態: {project.status}"] if project.status != "ACTIVE" else []),
                    f"- 現在地: {project.current}",
                    f"- 次の行動: {project.next_action or 'なし'}",
                    "",
                ]
            )
    else:
        lines.append("現在進行中のProjectはありません。")

    lines.extend(["", "## WAITING", ""])
    if waiting:
        for project in waiting:
            lines.extend(
                [
                    f"### {project.title}",
                    f"- 現在地: {project.current}",
                    f"- 待ち: {project.waiting_for or '未記録'}",
                    f"- 次の行動: {project.next_action or 'なし'}",
                    "",
                ]
            )
    else:
        lines.append("待機中のProjectはありません。")

    lines.extend(["", "## NEEDS CHECK", ""])
    stale_projects = [project for project in visible if stale[project.project]]
    if stale_projects:
        for project in stale_projects:
            watched = ", ".join(stale[project.project])
            lines.extend(
                [
                    f"### {project.title}",
                    f"- 最終確認: {project.last_confirmed.isoformat()}",
                    f"- 要確認: `{watched}` に最終確認後の変更を検知。進捗は自動判定せず、Project記録を確認する。",
                    f"- 記録上の次の行動: {project.next_action or 'なし'}",
                    "",
                ]
            )
    else:
        lines.append("記録の最新性を確認する必要があるProjectはありません。")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate brain/indexes/NOW.md from Project metadata.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--check", action="store_true", help="fail instead of writing when NOW.md is stale")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    project_dir = root / "brain" / "projects"
    output = root / "brain" / "indexes" / "NOW.md"
    try:
        projects = [load_project(path) for path in project_record_paths(project_dir)]
        content = render(projects, root)
    except (MetadataError, OSError, subprocess.CalledProcessError) as error:
        print(f"NOW generation failed: {error}", file=sys.stderr)
        return 2

    existing = output.read_text(encoding="utf-8") if output.exists() else None
    if existing == content:
        print("brain/indexes/NOW.md is already current.")
        return 0
    if args.check:
        print("brain/indexes/NOW.md is not current.", file=sys.stderr)
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")
    print("Regenerated brain/indexes/NOW.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
