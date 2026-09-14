#!/usr/bin/env python3
"""Check tracked workspace placement without reading document bodies or moving files."""
from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path, PurePosixPath
import subprocess


def violations(paths: list[str], config: dict) -> list[str]:
    problems = []
    for value in sorted(set(paths)):
        parts = PurePosixPath(value).parts
        if not parts:
            continue
        if len(parts) == 1:
            if value not in config['root_files']:
                problems.append(f'{value}: repository root file has no assigned role')
            continue
        if parts[0] not in config['root_directories']:
            problems.append(f'{value}: repository root directory has no assigned role')
            continue
        if parts[0] == 'brain':
            if len(parts) == 2 and parts[1] not in config['brain_files']:
                problems.append(f'{value}: place supporting documents in brain/docs or brain/indexes')
            elif len(parts) > 2 and parts[1] not in config['brain_directories']:
                problems.append(f'{value}: brain directory has no assigned role')
        if parts[0] != 'projects':
            continue
        if len(parts) == 2:
            if parts[1] not in config['project_index_files']:
                problems.append(f'{value}: projects/ must contain project directories, not loose files')
            continue
        project, entry = parts[1:3]
        if len(parts) == 3:
            allowed = config['project_root_file_patterns'] + config['entrypoints'].get(project, [])
            if not any(fnmatch.fnmatchcase(entry, pattern) for pattern in allowed):
                problems.append(f'{value}: move document/data to an appropriate numbered layer')
        elif entry not in config['project_directories'] and entry not in config['legacy_directories'].get(project, {}):
            problems.append(f'{value}: project directory has no assigned role')
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--include-untracked', action='store_true', help='also check non-ignored local files')
    args = parser.parse_args()
    root = args.repo_root.resolve()
    config = json.loads((root / 'brain/config/workspace-layout.json').read_text(encoding='utf-8'))
    command = ['git', '-C', str(root), 'ls-files', '-z', '--cached']
    if args.include_untracked:
        command += ['--others', '--exclude-standard']
    paths = [p for p in subprocess.check_output(command).decode('utf-8').split('\0') if p]
    problems = violations(paths, config)
    for problem in problems:
        print(problem)
    print(f'Workspace layout: {len(set(paths))} files checked; {len(problems)} unassigned paths.')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
