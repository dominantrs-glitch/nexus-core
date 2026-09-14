# Workspace Contract

## 正本と取得順序

現在の本人指示を優先する。現在地はbrain/projects、再利用する記録はbrain/memoryを正本とする。
案件の03_contextは要約・案内であり、Projectと同じ現在地を二重管理しない。
資料・成果物に書かれたAIの説明は、それだけを根拠にFACTや本人のDECISIONへ昇格させない。
原資料、検証済みの情報、実施した試験、本人の確認に戻って根拠を確認する。

## 配置

| 場所 | 置くもの |
| --- | --- |
| brain/projects | Current / Decisions / Next / Open |
| brain/memory | 案件をまたいで使うFACT / DECISION / LESSON / HYPOTHESIS |
| brain/inbox/items.md | 保存が必要だが分類を決められない項目 |
| brain/docs・templates・tools・config | 説明書・ひな型・管理コード・配置設定 |
| projects/案件/01_raw | 本人や顧客から受領した原本 |
| projects/案件/02_web | 外部資料。URL・取得日・目的を併記 |
| projects/案件/03_context | 出典を伴う要約・説明書 |
| projects/案件/04_work | 下書き・生成途中・試験の出力 |
| projects/案件/05_output | 利用者へ渡す成果物 |
| projects/案件/06_app | コード・テスト・依存設定・起動ファイル・実行環境 |
| projects/案件/07_logs | 判断理由・完成記録 |
| projects/案件/08_archive | 旧版。名前だけで不採用や失敗と決めない |
| projects/案件/09_skills | 必要になった案件固有の反復手順 |

案件直下はREADME・AGENTS・案内HTMLと必要な番号付き分類に絞る。goal.md・MANIFEST.md・context.mdは03_context/docs、判断記録は07_logs/decisionsへ置く。
新規案件はinitializerを使う。不要な空分類は増やさない。
共通の判断原則の空欄は[context/docs/canonical-context.md](canonical-context.md)、本人判断との重要な差の記録先は[logs/records/correction-log.md](../../logs/records/correction-log.md)。通常の記録から自動更新しない。

## 保存と変更

原本は本文を保全し、機密性に応じてGit管理可否を判断する。非公開データは公開版へ追加しない。
移動時は参照・起動・import・生成先・自動実行を確認し、履歴を残す。
Memoryの更新はbrain/AGENTS.mdに従う。旧判断は削除せずsupersededとして新しい判断と結ぶ。
完成・中断の記録は[記録工程](../../brain/docs/deliverable-recording.md)に従う。

## 確認

`python brain/tools/check_workspace_layout.py --include-untracked` は配置を確認する。
これは内容・機密性・実行の正しさを確認する検査ではない。
Pythonツールは3.12以上とGitを前提とし、追加パッケージは使わない。
テストの結果・データは04_work、コードは06_app/testsへ置く。
__pycache__やruntimeを保存対象と混同しない。

## 入口と末端の統一ルール（2026-09-15）

本人の今回の指定により、分類の入口にはREADME・AGENTS・案内HTMLを置き、本体は用途別の下位フォルダへ分類する。基盤フォルダは小文字英語、複数語はハイフン。案件内は01_raw〜09_skillsを共通名とし、不要な空分類は作らない。

具体的な構造、技術上の例外、点検範囲、既存パスの保全は [フォルダ配置ガイド](../../brain/docs/folder-layout.md) を参照する。過去資料の所在は [移動対応表](../../brain/config/layout-migration-2026-09-15.json) で追跡する。
