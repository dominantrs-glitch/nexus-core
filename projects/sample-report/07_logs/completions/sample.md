# 架空サンプルの作成・中断記録

```trace
{
  "schema": 1,
  "project_record": "brain/projects/sample-report.md",
  "recorded_at": "2026-09-15",
  "event_date": "unknown",
  "review_state": "partial",
  "evidence_state": "gaps",
  "origin": "contemporaneous",
  "source_snapshot": "f6605451acc05f1d9ad66f1faa421897b179b8cd",
  "artifacts": [{"path": "projects/sample-report/05_output/report.md", "role": "provisional"}],
  "sources": [
    {"path": "projects/sample-report/03_context/docs/goal.md", "basis": "source"},
    {"path": "projects/sample-report/07_logs/decisions/record.md", "basis": "source"},
    {"path": "projects/sample-report/03_context/docs/check.md", "basis": "test-result"}
  ]
}
```

## 成果物と完成範囲

公開版の説明用に作成した[架空の草案](../../05_output/report.md)。実案件の完成記録ではない。
source_snapshotはこの公開用リポジトリの草案を含むコミットであり、元の個人環境や過去の受入を示さない。
記録日はこのサンプルを作った日。架空の業務の実施日はunknownとしている。

## 判断と理由

[判断ログ](../decisions/record.md)のとおり、単純な文字情報の例なのでMarkdownを選んだ。
実利用者の判断を再現したものではなく、サンプル作成者の判断である。

## 確認結果

[検証メモ](../../03_context/docs/check.md)と[公開版の検証記録](../../../../brain/docs/validation.md)を参照。
3つの見出しの存在を自動確認する。実利用者の受入・全表示環境での読みやすさ確認とは別である。

## 未確認・残件

実利用者の受入と業務への効果は未確認。部分記録を許容する例としてpartial/gapsを維持する。
標準検査の終了0とstrictの終了3の違いを試せる。

## 調査範囲と出典

この公開版の架空ファイルだけを対象とする。個人の会話、業務資料、元環境の履歴は使用していない。
[草案の入口](../../05_output/README.md)からこの記録に辿れる。
