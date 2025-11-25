# Octoparse Export

Octoparse のタスクデータを取得し、Google Drive に CSV 形式でエクスポートするアプリ。

## 機能

- Google Spreadsheet からタスク ID を読み込み
- Octoparse API からデータを取得
- CSV ファイルとして Google Drive にアップロード
- 処理結果を Spreadsheet に記録

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

| task_id | task_name |
|---------|-----------|
| xxx-xxx | Task 1 |
| yyy-yyy | Task 2 |

### 実行

```bash
python main.py "<spreadsheet_url>" "<folder_id>"
```

- `spreadsheet_url`: タスク一覧の Google Spreadsheet URL
- `folder_id`: 出力先の Google Drive フォルダ ID（オプション）

### 出力

```
Google Drive/
└── [Task Name]/
    └── [timestamp]/
        └── data.csv
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
├── .env                 # 認証情報（gitignore）
├── client_secret.json   # OAuth クライアント（gitignore）
└── token.json           # OAuth トークン（自動生成、gitignore）
```

## ライセンス

MIT
