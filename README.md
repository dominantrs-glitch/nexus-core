# nexus-core（公開版）

**ネクサスコアの公開版**です。個人用基盤から、個人記録を除いた共通の仕組みを切り出しています。

AIとの仕事を、別の日・別の会話から続けるためのMarkdown作業基盤です。
現在地、判断理由、成果物、確認結果を分けて残し、人とAIが同じファイルを読みます。

個人用の環境から共通の構造とプログラムを切り出した公開用コピーです。
実際の個人記録・業務資料・会話・元環境のGit履歴は含みません。同梱案件は架空の例です。
これはファイルと運用ルールの基盤であり、AIモデルやチャットアプリそのものではありません。

## 何ができるか

- 案件を標準構造で作り、現在の状態と次の行動を1か所で管理する。
- 本人の判断、確認できた事実、仮説、過去の判断を区別して残す。
- 成果物から「なぜこの形か」「どこまで確認したか」を辿る。
- Projectの記録から現在地一覧を生成し、配置・記録・Git状態を点検する。

記録を読む・書く判断は人または接続したAIが行います。
自動で全会話を記憶する機能、無条件の自動保存・自動公開、記録漏れの完全検出はありません。

## 最初に試す

必要なものはGit、Python 3.12以上、UTF-8のファイルを扱えるエディタです。
追加のPythonパッケージ、APIキー、AI契約はスクリプトの動作確認には不要です。
手元で試す場合はこのリポジトリをcloneするかZIPを展開し、リポジトリ直下で実行します。
ZIPで取得した場合は最初に `git init` を実行してください。

```sh
python --version
git --version
python -m unittest discover -s brain/tools -p "test_*.py" -q
python brain/tools/check_workspace_layout.py --include-untracked
python brain/tools/check_deliverable_records.py
python brain/tools/generate_now.py --check
python brain/tools/check_public_package.py
```

Windowsで `python` が使えない場合は、各コマンドの `python` を `py -3` に置き換えます。
各検査の意味と終了コードは[コマンド一覧](brain/docs/commands.md)にあります。
Git状態確認は接続先がある場合に実行します。ZIP直後のremote未設定をバックアップ完了とはしません。

次に[チュートリアル](brain/docs/quickstart.md)で、自分の案件を1件作ってください。
先に完成形を読みたい場合は[架空の週次レポート案件](projects/sample-report/README.md)を開きます。

## 構造

| 場所 | 役割 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | AIが作業を始める入口と権限の境界 |
| [brain/](brain/README.md) | 現在地・判断・Memoryの管理 |
| [brain/projects/](brain/projects/README.md) | 各案件のCurrent / Decisions / Next / Open |
| [brain/memory/](brain/memory/README.md) | 本人が保存を希望した、案件をまたいで使う記録 |
| [brain/NOW.md](brain/NOW.md) | Projectから生成する表示専用一覧 |
| [projects/](projects/README.md) | 資料、作業物、成果物、コード、判断・完成記録 |
| [brain/templates/](brain/templates/README.md) | 新規案件、Memory、完成記録のひな型 |
| [brain/tools/](brain/docs/commands.md) | 作成・生成・検査のプログラム |

フォルダの役割は[WORKSPACE_CONTRACT.md](WORKSPACE_CONTRACT.md)、保存と履歴の規則は[brain/AGENTS.md](brain/AGENTS.md)が正本です。

## AIに読ませる

ファイルを読む機能があるAIに、リポジトリへのアクセスを与えて次のように依頼します。

> このリポジトリのREADME.md、AGENTS.md、brain/README.md、brain/AGENTS.mdを読み、何をする仕組みか説明してください。
> 次にbrain/docs/quickstart.mdと架空のsample-report案件を読み、現在地、判断の理由、確認済みと未確認を区別して説明してください。
> この段階ではファイル変更・外部送信はせず、取得できない資料は未取得と示してください。

URLを渡しただけで全ファイルが自動取得されるとは限りません。読み取り機能がない場合は必要なファイルを添付します。
利用者のAIがAGENTS.mdを自動認識するかも環境に依存します。詳細は[AIからの利用](brain/docs/ai-usage.md)を参照してください。

## 導入・評価・限界

- [自分の環境へのコピーと設定](brain/docs/adoption.md)
- [設計判断と切り出した範囲](brain/docs/design.md)
- [記録工程](brain/docs/deliverable-recording.md)
- [評価するための質問と手順](brain/retrieval_eval/README.md)
- [確認結果と既知の限界](brain/docs/validation.md)

この公開用コピーの第三者による導入・理解はまだ未検証です。
同梱の自動検査が通っても、任意のAIが説明を正しく理解することや、判断記録が毎回残ることは保証しません。
現段階では再配布・改変のライセンスを指定していません。まず構造の閲覧・評価を目的とする公開版です。
