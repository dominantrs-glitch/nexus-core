# 公開基盤のフォルダ配置更新

```trace
{
  "schema": 1,
  "project_record": "brain/projects/nexus-core.md",
  "recorded_at": "2026-09-15",
  "event_date": "2026-09-15",
  "review_state": "reviewed",
  "evidence_state": "sufficient",
  "origin": "contemporaneous",
  "source_snapshot": "e52f836136c9d4d73cc8decac4c255337f9bd0cc",
  "artifacts": [
    {"path": "context/docs/workspace-contract.md", "role": "final"},
    {"path": "brain/tools/init_project.py", "role": "final"},
    {"path": "brain/tools/check_workspace_layout.py", "role": "final"}
  ],
  "sources": [
    {"path": "logs/records/folder-layout.md", "basis": "source"},
    {"path": "brain/docs/layout-verification.md", "basis": "test-result"},
    {"path": "brain/config/layout-migration-2026-09-15.json", "basis": "source"}
  ]
}
```

## 成果物と完成範囲

入口の整理、配置の命名規則、initializer、NOW生成先、案内、配置検査の更新。
source_snapshotは変更前の比較基準です。変更後の版はこの記録を含むGitコミットで特定します。

## 判断と理由

[配置の判断](../records/folder-layout.md)に理由と例外を記載しました。

## 確認結果

[検証記録](../../brain/docs/layout-verification.md)を参照します。意味の理解や利用者受入を自動検査の成功と混同しません。

## 未確認・残件

第三者の理解・実運用は未検証。全原本・配布パッケージ・アプリ内部の再編は対象外です。

## 調査範囲と出典

公開リポジトリの入口、管理コード、テンプレート、架空例を照合しました。[移動対応表](../../brain/config/layout-migration-2026-09-15.json)から旧パスを追跡できます。利用者個人のデータは扱っていません。
