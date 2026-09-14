---
project: nexus-core
title: nexus-core 公開基盤
status: STABLE
last_confirmed: 2026-09-15
current: 公開基盤の入口・命名・配置ルールと作成・点検処理を統一
next: none
waiting_for: none
show_in_now: false
---

# nexus-core 公開基盤

## Current

この記録は公開ソフトウェアの保守状態です。利用者の個人記録ではありません。
[配置ガイド](../docs/folder-layout.md)に従い、分類の入口と文書本体を分離しました。
[今回の確認記録](../../logs/completions/2026-09-15-folder-layout.md)を参照します。

## Decisions

入口はREADME・AGENTS等に絞り、用途別の下位フォルダに本体を置きます。
詳細な理由・技術上の例外は[配置の判断](../../logs/records/folder-layout.md)にあります。

## Next

現行配置を新規案件作成と配置点検で維持します。利用者の案件は別のProjectとして作成します。

## Open

独立した第三者・AIの理解、実運用への定着は未検証です。ライセンスは未指定です。
