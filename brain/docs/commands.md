# コマンド一覧

すべてリポジトリ直下で実行します。Windowsではpythonをpy -3に置き換えられます。

| コマンド（pythonに続ける部分） | 効果・主な終了コード |
| --- | --- |
| brain/tools/init_project.py SLUG "TITLE" | 案件作成。0=作成済み/既存維持、2=入力不備や衝突 |
| brain/tools/generate_now.py | ProjectからNOWを更新。0=成功、2=metadata不備等 |
| brain/tools/generate_now.py --check | 書かずに同期確認。1=古い、2=入力不備 |
| brain/tools/check_workspace_layout.py --include-untracked | Git追跡・未追跡の配置確認。0=適合、1=逸脱 |
| brain/tools/check_deliverable_records.py | 既存完成記録の形式と参照先。0=形式適合、2=不備/記録なし |
| brain/tools/check_deliverable_records.py --strict | 上記にreviewed/sufficientを要求。3=途中/根拠不足 |
| brain/tools/check_deliverable_records.py --lookup PATH | 成果物パスの完全一致で逆引き。4=該当なし |
| brain/tools/check_deliverable_records.py --inventory | Git管理下のoutput/archiveのファイル名だけを一覧。全成果物の網羅性は保証しない |
| brain/tools/check_git_session.py --phase start | fetchとGit状態の確認。0=開始条件適合 |
| brain/tools/check_git_session.py --phase end | fetchとGit状態の確認。0=接続先との一致確認 |
| brain/tools/generate_project_guides.py | 各案件のフォルダ案内HTMLを更新。--checkなら更新せず点検 |
| brain/tools/check_public_package.py | Markdownリンク、Project metadata、公開版の構成確認 |
| -m unittest discover -s brain/tools -p "test_*.py" -q | 隔離した回帰テスト。0=成功 |

Gitチェッカーは10=commitの確認必要、11=push必要、12=remote未確認、13=branch/upstream/分岐の確認必要。
commit、push、pull、stash、reset、merge、rebaseは実行しません。fetchはリモートへ接続して追跡情報を更新します。
接続先未設定やZIPからの新規Git環境では、バックアップ完了の0を期待しないでください。
完了表示の文言はGITHUB BACKUP COMPLETEですが、実際に照合する対象は設定済みupstreamです。

生成されるものはNOWと案内HTML、initializerで指定した新規案件のみ。その他の検査は作業本文を書き換えません。
