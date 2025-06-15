# 個人設定ファイルのセットアップガイド

## 概要
個人情報保護のため、設定ファイルはテンプレート形式で提供されています。
初回セットアップ時に、個人の認証情報を設定する必要があります。

## セットアップ手順

### 1. 設定ファイルの作成

```bash
# テンプレートから個人設定ファイルを作成
cp config/settings.json.example config/settings.json
cp .env.example .env
```

### 2. 個人情報の設定

#### A. .env ファイルの編集（メイン設定）
```bash
# Gmail設定
GMAIL_USERNAME=あなたのgmail@gmail.com
GMAIL_APP_PASSWORD=あなたの16桁アプリパスワード
GMAIL_RECIPIENTS=your_email@example.com,another_email@example.com

# Discord設定  
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# J Quants API設定
JQUANTS_REFRESH_TOKEN=あなたのリフレッシュトークン
```

#### B. config/settings.json の確認（オプション）
基本的に認証情報は全て .env ファイルで管理されるため、settings.json では通知の有効/無効の切り替えのみ行います：
```json
{
  "notifications": {
    "email": {
      "enabled": true
    },
    "discord": {
      "enabled": true
    }
  }
}
```

### 3. セキュリティ確認

✅ `.gitignore` が以下のファイルを除外していることを確認：
- `config/settings.json`
- `.env`

✅ 個人情報を含むファイルがGitにコミットされないことを確認：
```bash
git status
# config/settings.json と .env が表示されないことを確認
```

## 重要な注意事項

🔒 **個人情報保護**:
- `config/settings.json` と `.env` は絶対にGitにコミットしないでください
- これらのファイルには認証情報が含まれています

🔄 **バックアップ**:
- 設定ファイルは定期的にローカルバックアップを取ってください
- クラウドストレージに保存する場合は暗号化してください

🗂️ **ファイル構造**:
```
config/
├── settings.json.example  # テンプレート（Git管理対象）
├── settings.json          # 個人設定（Git管理対象外）
├── strategies.json        # 戦略設定（Git管理対象）
└── gui_settings.json      # GUI設定（Git管理対象）

.env.example                # テンプレート（Git管理対象）
.env                        # 個人環境変数（Git管理対象外）
```

## トラブルシューティング

### Q: 設定ファイルが見つからないエラーが出る
A: テンプレートから設定ファイルを作成してください：
```bash
cp config/settings.json.example config/settings.json
```

### Q: 認証エラーが発生する
A: `.env` ファイルの認証情報を確認してください：
- Gmail: アプリパスワードが正しいか
- Discord: Webhook URLが有効か  
- J Quants: リフレッシュトークンが期限切れでないか

### Q: Gitに個人情報がコミットされてしまった
A: 以下の手順でファイルを除外してください：
```bash
git rm --cached config/settings.json
git rm --cached .env
git commit -m "Remove personal info files"
git push
```