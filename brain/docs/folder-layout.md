# フォルダの名前とファイルの置き方

フォルダを開いた最初の階層は、README・AGENTSなどの入口と、用途を示す分類フォルダだけにします。
説明・設定・記録・成果物の本体は、その役割を表す下位フォルダへ置きます。

## 名前の揃え方

- 基盤の分類名は小文字の英語です。複数語はハイフンで区切ります。
- リポジトリ直下は `brain`（記録管理）、`context`（共通方針）、`projects`（案件）、`logs`（基盤の記録）、必要な `skills`（共通手順）です。
- 案件名は `sample-report` のような小文字英語・数字・ハイフンです。
- 案件内の大分類は既存の `01_raw`〜`09_skills` に揃えます。番号と英語名の組を変更しません。
- 説明文書は `docs`、判断記録は `decisions`、完成記録は `completions`、設定は `config` へ置きます。
- 必要な分類だけを作ります。ファイルが増えるたびに意味のない一段を追加しません。

## 基本構造

```text
README.md
AGENTS.md
context/
  README.md
  docs/
    workspace-contract.md
brain/
  README.md
  AGENTS.md
  indexes/NOW.md
  inbox/items.md
  projects/<project>.md
  memory/YYYY-MM.md
  docs/
  config/
  tools/
  templates/
    README.md
    project-workspace/
    records/
  evaluations/
projects/
  README.md
  sample-report/
    README.md
    03_context/
      README.md
      docs/
        goal.md
        context.md
    04_work/
    05_output/
    07_logs/
      decisions/record.md
      completions/<record>.md
logs/
  records/
```

`docs`・`memory`・`config`など、役割が確定した末端には複数のファイルを置いて構いません。
さらに分類する場合、その親はREADMEなどの案内だけにし、本体は適切な子フォルダへ振り分けます。

## 必要な例外

Gitの `.gitignore`・`.gitattributes`、GitHubの `.github/workflows`、AIが認識する `AGENTS.md`、アプリが配置を要求する依存設定・パッケージ構造は所定位置を使います。
案内用HTMLはREADMEと同じ入口として扱います。設定の都合がないのに例外を追加しません。

受領原本、旧版、配布済みパッケージの内部構造は保全します。実行中アプリの内部構造や既存案件名を変える際は、起動・データ保存先・自動実行まで別途移設確認が必要です。

## 点検と移動履歴

`python brain/tools/check_workspace_layout.py --include-untracked` で、リポジトリ・brain・案件の直下と、共通context・案件03_context・07_logsの入口を点検します。
この検査は、すべての原本・アーカイブ・アプリ内部まで「完全な最下層配置」を証明するものではありません。

[配置契約](../../context/docs/workspace-contract.md)が正本です。
[旧パスと新パスの対応](../config/layout-migration-2026-09-15.json)から、過去記録に残った旧パスの現在の所在を確認できます。
歴史的な記録の本文や配布済みファイルを、現在の名前に合わせて書き換えません。

この配置更新の範囲と確認結果は [変更記録](../../logs/completions/2026-09-15-folder-layout.md) にあります。
