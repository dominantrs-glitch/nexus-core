# 最初の案件を作る

前提は[README](../../README.md)のPythonとGitです。以下はリポジトリ直下で実行します。
既存のsample-reportは読むための架空案件です。別名で自分の案件を作ります。

## 1. 初期化

```sh
python brain/tools/init_project.py my-first-project "はじめての案件" --with docs
```

brain/projects/my-first-project.mdとprojects/my-first-project/以下が作られます。
既にある同じ案件は上書きしません。不完全な既存構造がある場合はエラーで止まります。
コードを書く案件なら `--with src tests docs` を選びます。

## 2. 目的と現在地

projects/my-first-project/03_context/docs/goal.mdへ今回の目的・範囲・完成条件を記入します。
brain/projects/my-first-project.mdのCurrent / Decisions / Next / Openと先頭metadataを更新します。
currentとnextは1行、statusはACTIVE / WAITING / STABLE / MAINTENANCE / DONE / ARCHIVED。
未確認のものは未確認と書き、完成や本人受入を推測しません。

```sh
python brain/tools/generate_now.py
```

brain/indexes/NOW.mdに現在地と次の行動が表示されます。NOWを直接編集してはいけません。

## 3. 判断を残す

projects/my-first-project/07_logs/decisions/record.mdへ、日付・決定主体・決定・理由・見送った案・根拠・適用条件を記録します。
本文が短くても構いません。考えていない代替案を後から作らないでください。
案件をまたいで使うMemoryは、本人が「保存して」と明示した時に[Memory形式](../templates/records/memory.md.template)で記録します。

## 4. 成果物と確認

途中のものは04_work、渡すものは05_outputへ置きます。成果物ごとに必要な確認を行い、対象版・方法・結果・未確認を記録します。
[完成記録テンプレート](../templates/records/completion-record.md.template)を案件の07_logs/completions/へコピーします。
traceブロック内のパスはリポジトリ直下からの相対パスです。source_snapshotは `git rev-parse HEAD` で得る、照合した実在コミットです。
Gitにまだコミットがない場合は、承認したファイルだけを先にcommitして照合元を作ります。仮のSHAで埋めないでください。
完成記録の5つの節を記入し、案件READMEまたは05_outputの案内からリンクします。

```sh
python brain/tools/check_deliverable_records.py --record projects/my-first-project/07_logs/completions/RECORD.md
```

RECORD.mdは自分が作ったファイル名に置き換えます。構造検査の成功を全試験成功と読み替えないでください。
調査完了かつ根拠充足を申告できる時だけreviewed/sufficientを使い、`--strict`でも確認します。

## 5. 中断・再開

未完成ならProjectのCurrentに今回できた範囲、Nextに再開後の最初の作業、Openに不足を残します。
確認待ちならWAITING、完了条件を満たしたらDONEにします。NOWを再生成します。
新しい会話では「このリポジトリのAGENTS.mdとbrain/projects/my-first-project.mdを読み、現在地と次の作業を説明して」と依頼します。
AIが根拠にしたファイルを示せるか確認してください。

## 6. 自分用コピーとGit

個人記録を入れる前に[導入手順](adoption.md)に従って非公開の作業場所を用意します。
Gitのcommit・pushは本人の承認範囲で実施し、送信先を確認します。
このチュートリアルの実施だけでは自動でGitHubへ送信されません。
