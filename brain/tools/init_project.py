#!/usr/bin/env python3
"""Create a minimal, model-independent project workspace without overwriting data."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


SLUG_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
OPTIONAL_LAYERS = ("01_raw", "02_web", "08_archive", "09_skills", "06_app", "src", "tests", "docs", "scripts", "config", "runtime", "portable")
CORE_DIRECTORIES = ("03_context", "04_work", "05_output", "07_logs")
OPTIONAL_READMES = {
    "01_raw": "# 01_raw\n\n本人・顧客から受領した加工前の原本を置く場所です。内容を上書きせず、Git管理可否を確認してから追加します。\n",
    "02_web": "# 02_web\n\n外部から取得した資料を置く場所です。URL、取得日、情報源、保存目的を近くに残します。\n",
}


class InitializationError(ValueError):
    """Raised when initialization would be ambiguous or overwrite files."""


def template_root() -> Path:
    return Path(__file__).resolve().parents[1] / "templates" / "project-workspace"


def read_template(name: str) -> str:
    return (template_root() / name).read_text(encoding="utf-8")


def validate_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise InitializationError("workspace root must be a non-empty path relative to the repository root")
    return path


def render(template: str, replacements: dict[str, str]) -> str:
    for key, value in replacements.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def initialize(repo_root: Path, slug: str, title: str, workspace_root: str, optional_layers: list[str]) -> list[Path]:
    if not SLUG_PATTERN.fullmatch(slug):
        raise InitializationError("project slug must use lowercase letters, digits, and hyphens only")
    if not title.strip() or "\n" in title or "\r" in title:
        raise InitializationError("title must be one non-empty line")
    if len(set(optional_layers)) != len(optional_layers):
        raise InitializationError("each optional layer may be requested once")

    workspace_prefix = validate_relative_path(workspace_root)
    workspace_path = workspace_prefix / slug
    project_path = repo_root / "brain" / "projects" / f"{slug}.md"
    workspace = repo_root / workspace_path
    readme_path = workspace / "README.md"
    goal_path = workspace / "goal.md"
    context_path = workspace / "03_context" / "context.md"
    decisions_path = workspace / "07_logs" / "decisions.md"

    expected = [project_path, readme_path, goal_path, context_path, decisions_path]
    if project_path.exists() and readme_path.exists():
        return []
    existing = [path for path in expected if path.exists()]
    if existing or workspace.exists():
        rendered = ", ".join(str(path.relative_to(repo_root)) for path in existing or [workspace])
        raise InitializationError(f"refusing to overwrite or merge an existing workspace: {rendered}")

    replacements = {
        "SLUG": slug,
        "TITLE": title.strip(),
        "DATE": date.today().isoformat(),
        "WORKSPACE_PATH": workspace_path.as_posix(),
    }
    project_path.parent.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True)
    project_path.write_text(render(read_template("project.md.template"), replacements), encoding="utf-8", newline="\n")
    readme_path.write_text(render(read_template("README.md.template"), replacements), encoding="utf-8", newline="\n")
    goal_path.write_text(render(read_template("goal.md.template"), replacements), encoding="utf-8", newline="\n")

    created = [project_path, readme_path, goal_path]
    for layer in CORE_DIRECTORIES:
        layer_path = workspace / layer
        layer_path.mkdir()
        if layer == "03_context":
            guide = layer_path / "README.md"
            guide.write_text(render(read_template("context.md.template"), replacements), encoding="utf-8", newline="\n")
            context_path.write_text(render(read_template("context-entry.md.template"), replacements), encoding="utf-8", newline="\n")
            created.extend([guide, context_path])
        elif layer == "07_logs":
            decisions_path.write_text(render(read_template("decisions.md.template"), replacements), encoding="utf-8", newline="\n")
            created.append(decisions_path)
        else:
            keep = layer_path / ".gitkeep"
            keep.write_text("", encoding="utf-8")
            created.append(keep)
    for layer in optional_layers:
        layer_path = workspace / ("03_context/docs" if layer == "docs" else "06_app/" + layer if layer in {"src", "tests", "scripts", "config", "runtime", "portable"} else layer)
        layer_path.mkdir(parents=True, exist_ok=True)
        if layer == "runtime":
            ignore = layer_path / ".gitignore"
            ignore.write_text("*\n!.gitignore\n", encoding="utf-8", newline="\n")
            created.append(ignore)
        elif layer in OPTIONAL_READMES:
            guide = layer_path / "README.md"
            guide.write_text(OPTIONAL_READMES[layer], encoding="utf-8", newline="\n")
            created.append(guide)
        else:
            keep = layer_path / ".gitkeep"
            keep.write_text("", encoding="utf-8")
            created.append(keep)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a minimal Project Workspace Harness workspace.")
    parser.add_argument("slug", help="lowercase project identifier, for example monthly-report")
    parser.add_argument("title", help="human-readable project title")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--workspace-root", default="projects")
    parser.add_argument("--with", dest="optional_layers", nargs="+", choices=OPTIONAL_LAYERS, default=[])
    args = parser.parse_args()

    try:
        created = initialize(args.repo_root.resolve(), args.slug, args.title, args.workspace_root, args.optional_layers)
    except (InitializationError, OSError) as error:
        print(f"Project initialization failed: {error}", file=sys.stderr)
        return 2

    if not created:
        print("Project workspace already exists; no files were changed.")
        return 0
    print("Created project workspace:")
    for path in created:
        print(f"- {path.relative_to(args.repo_root.resolve())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
