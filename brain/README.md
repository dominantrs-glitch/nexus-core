# AI外部脳

案件の現在地と、将来使う判断・事実をMarkdownで管理します。
初回は[全体README](../README.md)、[運用規則](AGENTS.md)、[チュートリアル](docs/quickstart.md)を読みます。

- [projects](projects/README.md)：現在地・現在の判断・次の行動・未解決事項。
- [memory](memory/README.md)：本人が保存を希望した、再利用する記録。
- [inbox](inbox.md)：保存が必要だが分類が決まらない項目。
- [NOW](NOW.md)：Projectの先頭metadataから生成した一覧。手で編集しません。
- [テンプレート](templates/README.md)：記録形式の見本。

再開時は関連Project、必要なMemory、今回の資料の順に読みます。
現在の状態をProject本文と先頭metadataの両方に反映し、NOWはgenerate_now.pyで再生成します。
公開版のsample-reportは架空の説明用案件です。実際の利用者の判断や検証結果ではありません。
