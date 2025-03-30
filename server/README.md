# kouchou-ai-server
kouchou-aiのAPIサーバーです。
レポートの作成、取得などを行うことができます。

## 開発環境

* rye
* python 3.12
* OpenAI API Key


## セットアップ（開発環境）
プロジェクトのルートディレクトリ（kouchou-ai/）で以下のコマンドを実行して.env.serverファイルを作成し、.env.serverファイル内の環境変数を記載してください
```bash
cp .env.server.example .env.server
```
記載が必要な環境変数は現状以下の1つ。
* OPENAI_API_KEY
  * OpenAIのAPIキー。レポート作成時に利用。


## 起動
serverディレクトリで以下を実行してください。
```bash
rye sync
make run
```

起動後、 `htttp://localhost:8000/docs` 配下でSwagger UIが立ち上がるので、
そちらでAPIの動作を確認できます。
