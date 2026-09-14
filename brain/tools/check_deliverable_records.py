#!/usr/bin/env python3
"""Validate deliverable trace records; never infer decisions or test success.

A record is Markdown with one fenced `trace` JSON block. All stored paths are
repository-relative. This tool reads records and filenames only, never runs an
application, edits a record, connects to a service, or changes Project/Memory.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

SECTIONS = ("成果物と完成範囲", "判断と理由", "確認結果", "未確認・残件", "調査範囲と出典")
STATES = {"review_state": {"partial", "reviewed"}, "evidence_state": {"gaps", "sufficient"},
          "origin": {"contemporaneous", "retrospective"}}
ROLES = {"final", "provisional", "historical", "unknown", "source-tree"}
MAX_RECORD_BYTES = 512_000


def within(root: Path, value: str) -> Path:
    """Reject absolute paths, traversal and symlink escapes, including Windows paths."""
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or "\x00" in value:
        raise ValueError("repository-relative POSIX path required")
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in {"..", "."} for x in value.split("/")):
        raise ValueError("absolute/traversal path rejected")
    target = (root / value).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("path leaves repository")
    return target


def read_record(root: Path, filename: str) -> tuple[dict, list[str]]:
    errors: list[str] = []
    try:
        path = within(root, filename)
        if path.stat().st_size > MAX_RECORD_BYTES:
            raise ValueError("record too large")
        text = path.read_text(encoding="utf-8")
        blocks = re.findall(r"^```trace\s*\n(.*?)^```\s*$", text, re.M | re.S)
        if len(blocks) != 1:
            raise ValueError("exactly one trace JSON block required")
        def unique_pairs(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"duplicate metadata key: {key}")
                result[key] = value
            return result
        meta = json.loads(blocks[0], object_pairs_hook=unique_pairs)
        if not isinstance(meta, dict):
            raise ValueError("trace metadata must be an object")
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, [str(exc)]
    if meta.get("schema") != 1 or isinstance(meta.get("schema"), bool):
        errors.append("schema must be 1")
    for key, allowed in STATES.items():
        if not isinstance(meta.get(key), str) or meta[key] not in allowed:
            errors.append(f"{key} must be one of {sorted(allowed)}")
    for key in ("recorded_at", "event_date"):
        value = meta.get(key)
        try:
            if key == "event_date" and value == "unknown":
                continue
            if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
                raise ValueError()
        except ValueError:
            errors.append(f"{key}: ISO date required (event_date may be unknown)")
    project = meta.get("project_record")
    try:
        if not isinstance(project, str) or not within(root, project).is_file():
            raise ValueError("missing Project record")
    except ValueError as exc:
        errors.append(f"project_record: {exc}")
    snapshot = meta.get("source_snapshot")
    if not isinstance(snapshot, str) or not re.fullmatch(r"[0-9a-f]{40}", snapshot):
        errors.append("source_snapshot: full Git commit SHA required")
    for group in ("artifacts", "sources"):
        entries = meta.get(group)
        if not isinstance(entries, list) or not entries:
            errors.append(f"{group}: nonempty list required")
            continue
        seen: set[str] = set()
        for i, entry in enumerate(entries):
            prefix = f"{group}[{i}]"
            if not isinstance(entry, dict):
                errors.append(f"{prefix}: object required")
                continue
            try:
                value = entry.get("path")
                target = within(root, value)
                if not target.exists():
                    raise ValueError("referenced path missing")
                if value in seen:
                    raise ValueError("duplicate path")
                seen.add(value)
                if group == "sources" and not target.is_file():
                    raise ValueError("source must identify a file, not an unreviewed directory")
                if group == "artifacts":
                    if entry.get("role") not in ROLES:
                        raise ValueError("invalid artifact role")
                    if target.is_dir() and entry.get("role") != "source-tree":
                        raise ValueError("directory artifact must have source-tree role")
                elif entry.get("basis") not in {"source", "historical-record", "user-confirmation-record", "test-result", "reference-only"}:
                    raise ValueError("invalid evidence basis")
            except (TypeError, ValueError) as exc:
                errors.append(f"{prefix}: {exc}")
    # Removing fenced blocks prevents example headings from satisfying the checks.
    body = re.sub(r"^```[^\n]*\n.*?^```\s*$", "", text, flags=re.M | re.S)
    for heading in SECTIONS:
        matches = list(re.finditer(rf"^## {re.escape(heading)}\s*$", body, re.M))
        if len(matches) != 1:
            errors.append(f"exactly one section required: {heading}")
            continue
        following = body[matches[0].end():]
        content = re.split(r"^## ", following, maxsplit=1, flags=re.M)[0].strip()
        if not content or content in {"TBD", "TODO", "未記入", "-"}:
            errors.append(f"empty section: {heading}")
    return meta, errors


def record_paths(root: Path) -> list[str]:
    paths = list(root.glob("projects/*/07_logs/completions/*.md"))
    paths += list(root.glob("logs/completions/*.md"))
    return sorted(p.relative_to(root).as_posix() for p in paths if not p.is_symlink())


def inventory(root: Path, metas: dict[str, dict]) -> str:
    """List tracked output/archive candidates. This is not a completeness verdict."""
    result = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                            capture_output=True, check=True)
    files = sorted(result.stdout.decode("utf-8").split("\x00"))
    linked: dict[str, list[str]] = {}
    for name, meta in metas.items():
        for artifact in meta.get("artifacts", []):
            if isinstance(artifact, dict) and isinstance(artifact.get("path"), str):
                linked.setdefault(artifact["path"], []).append(name)
    rows = ["# 成果物候補の棚卸し", "", "Git追跡中の05_output/08_archive/旧output/archive内のファイル名だけを列挙。",
            "候補であり、完成・受入・本文調査済みを意味しない。Git管理外・外部サービス・コードのみの納品は別途確認。", "",
            "| 候補 | 区分 | 記録 |", "| --- | --- | --- |"]
    for filename in files:
        parts = PurePosixPath(filename).parts
        if len(parts) < 4 or parts[0] != "projects":
            continue
        if not set(parts[2:-1]) & {"05_output", "08_archive", "output", "archive"}:
            continue
        kind = "旧版候補" if set(parts[2:-1]) & {"08_archive", "archive"} else "成果物候補"
        records = ", ".join(linked.get(filename, [])) or "未調査・未登録"
        escape = lambda s: s.replace("|", "&#124;").replace("\n", " ")
        rows.append(f"| `{escape(filename)}` | {kind} | {escape(records)} |")
    return "\n".join(rows) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--record", action="append", help="repository-relative record path; repeatable")
    parser.add_argument("--strict", action="store_true", help="also require reviewed/sufficient")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--inventory", action="store_true", help="print read-only tracked-file inventory")
    group.add_argument("--lookup", help="find trace records for an exact repository-relative artifact path")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    names = args.record if args.record is not None else record_paths(root)
    invalid = 0
    incomplete = 0
    metas = {}
    for name in names:
        meta, errors = read_record(root, name)
        invalid += bool(errors)
        incomplete += meta.get("review_state") != "reviewed" or meta.get("evidence_state") != "sufficient"
        if not errors:
            metas[name] = meta
        for error in errors:
            print(f"INVALID {name}: {error}", file=sys.stderr)
    if not names and not args.inventory:
        print("No records: not a PASS", file=sys.stderr)
        return 2
    if args.lookup:
        try:
            within(root, args.lookup)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        matches = [name for name, meta in metas.items() if any(
            a["path"] == args.lookup for a in meta["artifacts"])]
        for name in matches:
            print(f"{name} ({metas[name]['review_state']}/{metas[name]['evidence_state']})")
        if not matches:
            print("No matching record; not evidence of completion", file=sys.stderr)
            return 4
    if args.inventory:
        try:
            print(inventory(root, metas), end="")
        except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
            print(f"Inventory unavailable: {exc}", file=sys.stderr)
            return 2
    print(f"records={len(names)} invalid={invalid} incomplete_or_gaps={incomplete}; "
          "structure/path checks only; no semantic or execution verification", file=sys.stderr)
    return 2 if invalid else (3 if args.strict and incomplete else 0)


if __name__ == "__main__":
    raise SystemExit(main())
