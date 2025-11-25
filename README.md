# Octoparse Export

Octoparse のタスクデータを取得し、Google Drive に CSV 形式でエクスポートするアプリ。

## 機能

- Google Spreadsheet からタスク ID を読み込み
- Octoparse API からタスク名を自動取得
- CSV ファイルとして Google Drive にアップロード
- 処理結果を Spreadsheet に日本語で記録

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. Octoparse 認証設定

`.env` ファイルを作成:

```
OCTOPARSE_USERNAME=your_username
OCTOPARSE_PASSWORD=your_password
```

### 3. Google OAuth 設定

1. [Google Cloud Console](https://console.cloud.google.com) でプロジェクト作成
2. Google Sheets API と Google Drive API を有効化
3. OAuth 2.0 クライアント ID を作成（デスクトップアプリ）
4. JSON をダウンロードして `client_secret.json` として保存

### 4. 初回認証

```bash
python main.py <spreadsheet_url>
```

初回実行時にブラウザが開き、Google アカウントでログインします。
認証後、`token.json` が自動生成されます。

## 使い方

### Spreadsheet の準備

| タスクID | タスク名 |
|----------|----------|
| xxx-xxx  | (空欄でOK - 自動取得) |

### 実行

```bash
python main.py "<spreadsheet_url>" "<folder_id>"
```

- `spreadsheet_url`: タスク一覧の Google Spreadsheet URL
- `folder_id`: 出力先の Google Drive フォルダ ID（オプション）

### 出力

```
Google Drive/
└── [タスク名]/
    └── [timestamp]/
        └── data.csv
```

### Spreadsheet 結果

| タスクID | タスク名 | ステータス | ファイル場所 | レコード数 | 更新日時 |
|----------|----------|------------|--------------|------------|----------|
| xxx-xxx  | Task1    | Success    | [Drive URL]  | 1000       | 2025-... |

## Docker

### ビルド

```bash
docker build -t octoparse-export .
```

### 実行

```bash
# 認証ファイルをマウントして実行
docker run -v $(pwd)/.env:/app/.env \
           -v $(pwd)/client_secret.json:/app/client_secret.json \
           -v $(pwd)/token.json:/app/token.json \
           octoparse-export \
           python main.py "<spreadsheet_url>" "<folder_id>"
```

### Docker Compose

```bash
# 環境変数を設定
export SPREADSHEET_URL="https://docs.google.com/spreadsheets/d/xxx"
export FOLDER_ID="1GpKhRS6aG1_slnA69P-xBiS-5QwtZaEr"

# 実行
docker-compose up
```

## ファイル構成

```
octoparse_export/
├── main.py              # エントリーポイント
├── auth.py              # OAuth 認証
├── google_sheets.py     # Google Sheets API
├── google_drive.py      # Google Drive API
├── octoparse_client.py  # Octoparse API
├── requirements.txt     # 依存関係
├── Dockerfile           # Docker設定
├── docker-compose.yml   # Docker Compose設定
├── .env                 # 認証情報（gitignore）
├── client_secret.json   # OAuth クライアント（gitignore）
└── token.json           # OAuth トークン（自動生成、gitignore）
```

## ライセンス

MIT
