#!/usr/bin/env python3
"""Generate small project entrance pages from the numbered workspace layout."""
from pathlib import Path
import argparse
import html
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
NAME = '00_このフォルダについて.html'
ROLES = {'01_raw':'受領した原本', '02_web':'外部資料', '03_context':'整理済み情報・説明書',
         '04_work':'中間物・検証結果', '05_output':'完成物・配布物', '06_app':'コード・設定・起動・実行環境',
         '07_logs':'判断理由', '08_archive':'旧版', '09_skills':'反復手順'}

def render(project: Path) -> str:
    rows = ''.join(f'<tr><td><a href="{quote(name)}/">{name}/</a></td><td>{role}</td></tr>'
                   for name, role in ROLES.items() if (project/name).is_dir())
    title = html.escape(project.name)
    return f'''<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — フォルダ案内</title><style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:40px auto;padding:20px;line-height:1.8;color:#243343}}table{{border-collapse:collapse;width:100%}}td{{padding:12px;border-bottom:1px solid #ddd}}a{{color:#185b82}}</style>
<h1>{title}</h1><p><a href="README.md">最初に読むREADME・起動手順</a> ／ <a href="../README.md">全案件</a></p>
<table>{rows}</table><p>必要な分類だけを使います。アプリの起動ファイルは06_app内、説明書は03_context/docs内にあります。</p>
<p><a href="../../WORKSPACE_CONTRACT.md">配置・管理ルール</a> ／ <a href="../../brain/docs/quickstart.md">新規案件の作り方</a></p></html>
'''

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    changed=[]
    for project in sorted((ROOT/'projects').iterdir()):
        if not project.is_dir() or not (project/'README.md').is_file():continue
        p=project/NAME;content=render(project)
        if not p.exists() or p.read_text(encoding='utf-8')!=content:
            changed.append(project.name)
            if not args.check:p.write_text(content,encoding='utf-8',newline='\n')
    print(f'Project guides: {len(changed)} '+('outdated' if args.check else 'updated'))
    return int(args.check and bool(changed))

if __name__=='__main__':raise SystemExit(main())
