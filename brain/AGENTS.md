# AI外部脳の運用ルール

このルールの作用範囲は `brain/` 配下です。ほかのプロジェクトや既存の Canonical Context / Correction Log に、通常の保存処理を理由として変更を加えません。

## 最初に行うこと

1. この `brain/README.md` を読む。
2. 相談が特定プロジェクトに関するものなら、対応する `projects/<project-name>.md` を読む。
3. `memory/` を検索して、相談に必要な項目だけを読む。
4. Canonical Context または Correction Log は、相談に必要なときだけ既存の保存先から読む。

外部脳全体や全 Memory を、毎回コンテキストに入れてはいけません。

## 保存のトリガー

本人が「これを保存」「覚えておいて」「記録しておいて」「外部脳に残して」など、保存意思を明示したときに保存処理を行います。

本人に、保存先、フォルダ、type、Memory ID、Markdown 形式を指定させません。内容から AI が判断します。

### Project checkpoint の例外

Project の **現在地** は、NOW が古い記録を表示し続けないよう、本人の明示的な「保存して」がなくても、明確な状態遷移が観測できた時点で `projects/<project-name>.md` を checkpoint してよい。対象は、実装・テスト・UAT の PASS / FAIL、方針確定、Next の変更、Codex への引き渡し・完了、WAITING / 保留 / 再開、Project 完了である。

会話途中の案、雑談、仮説、未確定の思考は checkpoint しない。Memory への保存は従来どおり本人の明示的な保存意思を基本とし、Project の進捗記録と混同しない。

後日に Next が残る、複数回の ChatGPT / Codex 作業にまたがる、または中断後の再開が見込まれる AI 関連作業は Project 化する。同じ目的を ChatGPT で策定し Codex で実装し本人が UAT する流れは、別々にせず一つの Project の状態遷移として扱う。単発相談・雑談・その場で終わる簡単な調査は Project 化しない。

## 保存する内容

次の基準を満たす内容を保存候補にします。

> 別の日・別の相談で同じことを考えるとき、この情報を知らないと、再度判断・調査・実行し直す可能性が高いか。

主な対象は、重要な意思決定と理由、確認済みの事実、再利用できる学び、失敗と回避策、本人固有の考え方、プロジェクトの現在地と次の行動、過去の判断を変えた履歴です。

雑談、AI の回答全文、容易に再取得できる一般知識、一時だけ必要な情報、意味のない重複、保存価値が不明な内容は通常保存しません。分類または保存価値を安全に決められない場合だけ `inbox/items.md` に置きます。

資格情報、個人を特定し得る詳細な医療・位置・予定・第三者情報、非公開の業務情報は必要最小限に要約します。秘密そのものを保存しません。

## 保存先の選び方

- 現在地、現在の決定、次の行動、未解決事項など、進行中案件を再開するための情報は `projects/<project-name>.md` に保存する。
- 別の相談でも使う判断、事実、学び、仮説は `memory/YYYY-MM.md` に保存する。
- 上のいずれかを決められないときだけ `inbox/items.md` に保存する。

同じ内容を Project と Memory に重複保存しません。Project から重要な Memory ID を参照することはできます。

## Memory の type と記録形式

Ver.1 で使う type は次の 4 つだけです。

- `FACT`: 確認済みの事実。AI の推測を FACT にしてはいけない。
- `DECISION`: 本人が実際に採用した、または本人が明示的に確定した判断。AI の提案だけを DECISION にしてはいけない。
- `LESSON`: 実行、失敗、検証、運用から得た再利用可能な学び。
- `HYPOTHESIS`: 未確認の仮説。AI の推測や比較案を残す必要がある場合はこれを使う。

Memory は月ごとの `memory/YYYY-MM.md` に追記します。ID は `M-YYYYMMDD-NNN` とし、`memory/` を検索して重複しない次の番号を使います。各項目は最低限、次の形にします。

```markdown
## M-YYYYMMDD-NNN

type: FACT | DECISION | LESSON | HYPOTHESIS
status: active | superseded
date: YYYY-MM-DD
source: user-confirmed | verified-source | AI-hypothesis
supersedes: none | M-YYYYMMDD-NNN
project: none | <project-name>

### Summary

短く再利用できる内容。

### Reason

判断理由、確認根拠、または学びの条件。
```

不要な数値 confidence、タグ体系、Embedding 用データ、専用 ID データベースは追加しません。

## 更新と履歴

重要な FACT または DECISION が変わったときは、古い項目を削除せず `status: superseded` にします。新しい項目は `status: active` とし、`supersedes` に古い Memory ID を書きます。

単なる Project の進行は、通常 `Current` と `Next` を更新します。Project の進行だけで新しい Memory を増やしません。

## Canonical Context と Correction Log の保護

通常の Memory を Canonical Context に自動昇格させてはいけません。Canonical Context の更新は、本人が明示的に指示した場合だけ行います。

Correction Log は、AI の予測と本人の実際の判断に重要な差分があり、既存の記録基準を満たすときだけ使います。通常の好み、軽微な修正、Memory 保存のために追記してはいけません。

## 取得と回答への利用

検索はまず `projects/` と `memory/` に対して行います。特定プロジェクトの相談では、原則として次の順に必要な情報だけを取得します。

```text
関連 Project
→ 関連 Memory
→ 必要な場合だけ Canonical Context / Correction Log
```

取得した内容は、現在の回答の判断、理由、過去との比較、次の行動に実際に反映します。ファイル名や Memory ID を本人が知っていることを前提にしません。

## 案件内 Workspace Harness との関係

案件フォルダーの一次資料・外部情報・途中成果物・最終成果物を扱うときは、リポジトリルートの `context/docs/workspace-contract.md` に従う。開始時は `AGENTS.md → 関連Project → 必要なMemory → 案件構造 → 今回必要なraw / webだけ` の順に取得し、raw / web全体を毎回読まない。

`brain/projects/<project>.md` はCurrent / Decisions / Next / Openの正本であり、案件内に同じ状態を持つ `context/` 正本を通常作らない。raw / webは根拠候補、work / outputは原則非正本である。AI生成したwork / outputの内容を、それだけを理由にProjectやMemoryのFACT・DECISIONへ昇格させず、一次資料、検証済み外部情報、実装・テスト結果、または本人確認へ戻って根拠を確認する。

状態遷移が明確ならProjectをcheckpointしてよいが、単なるファイル生成や整理だけでMemoryを増やさない。旧版は削除よりarchiveへの退避を優先し、移動前後で参照・実行・テストを確認する。Canonical ContextとCorrection Logの保護、Memoryの保存トリガー、active / supersededの規則は変更しない。

## 応答時の最小確認

保存・更新したときは、保存先、type または更新内容、未確認の点だけを短く伝えます。保存しなかったときは、その理由と、Inbox に置いたかどうかを伝えます。

## 成果物の作成・改訂に伴う記録

成果物の作成・改訂を扱う場合は [記録工程](docs/deliverable-recording.md) を確認する。重要な判断・変更理由は案件内の判断ログ、完成・引渡し・中断時の版・範囲・確認結果・未確認事項は完成記録へ残し、配布入口から参照できるようにする。現在地はProjectを正本とし、詳細を重複保存せず記録へリンクする。

これは依頼された作業の記録工程であり、会話全文や無関係な個人情報を保存する承認ではない。外部反映は依頼・事前承認の範囲で行う。Memoryへの保存意思、Canonical ContextとCorrection Logの保護は変更しない。既存資料を補完するときは未調査・根拠不足を区別する。理由・検証が不明な箇所を推測で埋めず、形式検査のPASSを全件記録済み・実機成功として報告しない。

公開用の空の判断原則は [Canonical Context](../context/docs/canonical-context.md)、差分記録は [Correction Log](../logs/records/correction-log.md) を参照する。本人の指示なしに中身を作らない。
