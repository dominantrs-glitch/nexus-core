"""Check this package's local Markdown links and metadata. No writes or network."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from generate_now import load_project, project_record_paths

ROOT = Path(__file__).resolve().parents[2]

def check(root=ROOT):
    errors = []
    documents = sorted(root.rglob('*.md'))
    for path in documents:
        if '.git' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        # Templates and fenced examples are not actual navigation links.
        body = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
        for raw in re.findall(r'\[[^\]\n]+\]\(([^)]+)\)', body):
            link = raw.strip().strip('<>')
            if '{{' in link:
                continue
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not target.is_relative_to(root.resolve()) or not target.exists():
                errors.append(f'{path.relative_to(root)}: missing/outside link {raw}')
    for path in project_record_paths(root / 'brain/projects'):
        try:
            load_project(path)
        except ValueError as exc:
            errors.append(str(exc))
    print(f'Package: {len(documents)} Markdown documents; {len(errors)} errors. Paths/metadata only; no comprehension test.')
    for error in errors:
        print(error, file=sys.stderr)
    return errors

if __name__ == '__main__':
    raise SystemExit(bool(check()))
