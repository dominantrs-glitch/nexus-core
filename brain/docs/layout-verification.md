# フォルダ配置更新の検証

対象は2026-09-15の配置更新。比較基準はe52f836136c9d4d73cc8decac4c255337f9bd0cc、変更後はこの文書と同じGitコミットです。

## 実施条件

Windows、Python 3.12.10、Git。実施者は本変更を担当したCodexです。

## 確認方法

- `python -m unittest discover -s brain/tools -p "test_*.py" -q`
- `python brain/tools/check_workspace_layout.py --include-untracked`
- `python brain/tools/check_public_package.py`
- `python brain/tools/generate_now.py --check`
- `python brain/tools/generate_project_guides.py --check`
- `python brain/tools/check_deliverable_records.py`

今回追加した回帰検査は、入口への文書散在の拒否、新規案件名の表記統一、新規作成した案内リンクの到達先です。既存の初期化・Git・NOW・記録検査も併せて実施します。

## 結果

49件中48成功、1件SKIP、失敗0件（12.284秒）。SKIPはWindowsのシンボリックリンク作成権限によるものです。
配置点検は69ファイルで逸脱0件、Markdown参照・metadata検査は38文書で不備0件。NOW・案内は同期済みです。
完成記録2件の構造不備は0件。架空例1件のpartial/gapsは維持し、今回の基盤変更とは区別しています。
元の個人用リポジトリのファイルを公開版へ追加していません。公開版の移動は12ファイルです。

## 限界

シンボリックリンク作成が許可されないWindowsでは、その検査はSKIPです。
第三者の理解・導入・本人受入、全原本と全アプリ内部の分類は今回の検証対象ではありません。
