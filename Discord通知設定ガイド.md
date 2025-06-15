# Discord通知設定ガイド

![Discord](https://img.shields.io/badge/Discord-Webhook-5865F2.svg)
![無料](https://img.shields.io/badge/料金-完全無料-brightgreen.svg)
![制限](https://img.shields.io/badge/制限-無制限-success.svg)

日本株ウォッチドッグでDiscord通知を受け取るための**完全ガイド**です。LINE Notify終了（2025年3月）への対応として、初心者の方でも迷わず設定できるよう、画像付きで詳しく説明します。

## 🎯 Discord通知でできること

### 📱 リッチな株価アラート
- **💰 買い推奨**: 緑色のEmbed形式で視覚的に分かりやすい
- **✅ 利益確定**: 青色で利益確定タイミングを明確表示  
- **⚠️ 損切り**: 赤色で緊急の損切りタイミングを警告
- **🧪 テスト通知**: 設定確認用のテスト通知

### 📊 通知例（リッチEmbed形式）
```
💰 買い推奨アラート

銘柄      7203
価格      ¥2,580  
戦略      defensive_strategy

詳細
【買い推奨】トヨタ自動車 (7203)
現在価格: ¥2,580
理由: 配当利回り 3.2% >= 3.0%, PER 12.1 <= 15.0

日本株ウォッチドッグ
2025-06-10 14:30:15
```

## 🚀 設定手順（15分で完了）

### ステップ1: Discordアカウント作成（既にお持ちの場合はスキップ）

1. **Discord公式サイト**にアクセス
   ```
   https://discord.com/
   ```

2. **「Discordを開く」ボタン**をクリック
   - ブラウザ版またはアプリ版を選択
   - アプリ版の方が通知を受け取りやすいのでおすすめ

3. **アカウント作成**
   - メールアドレス、ユーザー名、パスワードを入力
   - 認証メールを確認してアカウントを有効化

### ステップ2: サーバー作成

1. **新しいサーバーを作成**
   - 左サイドバーの **「+」ボタン** をクリック
   - **「サーバーを作成」** を選択

2. **サーバー設定**
   ```
   サーバー名: 日本株ウォッチドッグ
   サーバー地域: Japan
   サーバーアイコン: お好みで設定（株チャートのアイコンなど）
   ```

3. **チャンネル作成**
   - デフォルトの「general」チャンネルを使用
   - または新しいチャンネルを作成:
     - チャンネル名例: 「株価アラート」「投資通知」

### ステップ3: Webhook作成

1. **サーバー設定を開く**
   - **サーバー名をクリック** → **「サーバー設定」** を選択
   - または右クリックで「サーバー設定」

2. **Webhookページに移動**
   - 左メニューの **「連携サービス」** をクリック
   - **「ウェブフック」** タブを選択

3. **新しいWebhookを作成**
   - **「新しいウェブフック」** ボタンをクリック

4. **Webhook設定**
   ```
   名前: 日本株ウォッチドッグ
   チャンネル: #general（または作成したチャンネル）
   アバター: お好みで設定（チャートアイコンなど）
   ```

5. **⚠️ 重要: WebhookURLをコピー**
   - **「ウェブフックURLをコピー」** ボタンをクリック
   - URLは以下のような形式です:
   ```
   https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz
   ```
   - **このURLは絶対に他人に教えないでください**

### ステップ4: アプリにWebhookURLを設定

#### 方法1: .envファイルで設定（推奨・安全）

**.envファイルでの設定は最も安全で推奨される方法です。**

1. **プロジェクトのルートディレクトリに移動**
   ```bash
   # アプリのフォルダに移動
   cd /path/to/stock_watchdog  # あなたのアプリフォルダ
   ```

2. **.envファイルを作成・編集**
   ```bash
   # .envファイルを作成（存在しない場合）
   notepad .env     # Windows
   nano .env        # Linux/macOS
   ```

3. **.envファイルに以下を記述**
   ```bash
   # Discord通知設定
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz
   
   # 他の設定（必要に応じて）
   # GMAIL_USERNAME=your_email@gmail.com
   # GMAIL_APP_PASSWORD=your_app_password
   # JQUANTS_EMAIL=your_jquants_email@example.com
   ```

4. **ファイルを保存**
   - 上書き保存してファイルを閉じる
   - **重要**: .envファイルは他人に見せないでください

#### 方法2: 環境変数で設定（従来方法）

**Windows の場合:**
```cmd
# コマンドプロンプトで実行
setx DISCORD_WEBHOOK_URL "コピーしたWebhookURLをここに貼り付け"

# 例
setx DISCORD_WEBHOOK_URL "https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz"
```

**Linux/macOS の場合:**
```bash
# ターミナルで実行
export DISCORD_WEBHOOK_URL="コピーしたWebhookURLをここに貼り付け"

# 永続化（再起動後も有効）
echo 'export DISCORD_WEBHOOK_URL="コピーしたWebhookURL"' >> ~/.bashrc
source ~/.bashrc
```

#### 方法2: 設定ファイルで設定

1. **`config/settings.json`** ファイルを開く

2. **Discord設定を編集**
   ```json
   {
     "notifications": {
       "email": {
         "enabled": false
       },
       "desktop": {
         "enabled": true
       },
       "console": {
         "enabled": true
       },
       "line": {
         "enabled": false
       },
       "discord": {
         "enabled": true,
         "webhook_url": "コピーしたWebhookURLをここに貼り付け"
       }
     }
   }
   ```

3. **ファイルを保存**

### ステップ5: 動作確認

#### GUIでのテスト（簡単）

1. **アプリを起動**
   ```bash
   python src/main.py --gui
   ```

2. **「ポートフォリオ」タブ**を開く

3. **「Discordテスト」ボタン**をクリック

4. **Discordサーバーで通知確認**
   - 作成したDiscordサーバーを開く
   - 設定したチャンネルに通知が表示されているか確認

#### コマンドラインでのテスト

```bash
# 仮想環境を有効化
source .venv/bin/activate

# Discord通知テスト実行
python test_discord_notification.py
```

**成功例:**
```
==================================================
Discord通知機能テスト
==================================================
Discord通知設定: 有効
WebhookURL設定: あり

Discord通知をテストしています...
Discord通知送信完了: テスト - 7203
✅ Discord通知テスト完了
Discordサーバーで通知を確認してください

通知の特徴:
- 📊 リッチなEmbed形式で表示
- 🎨 アラートタイプ別の色分け
- 📱 PC・スマホ両方で受信可能
- 🔔 プッシュ通知対応
==================================================
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### ❌ 問題1: 「WebhookURLが設定されていません」エラー

**症状:**
```
❌ Discord WebhookURLが設定されていません
```

**解決方法:**
1. WebhookURLが正しく設定されているか確認
2. URLの形式が正しいか確認（https://discord.com/api/webhooks/で始まる）
3. 環境変数の場合、コマンドプロンプト/ターミナルを再起動
4. 設定ファイルの場合、JSON形式が正しいか確認

**確認コマンド:**

**.envファイルの場合:**
```bash
# アプリを起動して動作確認
python src/main.py --gui
# 「アラートテスト」ボタンでDiscord通知をテスト
```

**環境変数の場合:**
```bash
# Windows
echo %DISCORD_WEBHOOK_URL%

# Linux/macOS  
echo $DISCORD_WEBHOOK_URL
```

#### ❌ 問題2: 「Discord通知が無効になっています」エラー

**症状:**
```
❌ Discord通知が無効になっています
```

**解決方法:**
`config/settings.json` で以下を確認:
```json
"discord": {
  "enabled": true,  ← これが true になっているか
  "webhook_url": "..."
}
```

#### ❌ 問題3: 「HTTP 404 - Not Found」エラー

**症状:**
```
Discord通知送信エラー: HTTP 404 - Not Found
```

**解決方法:**
1. WebhookURLが間違っている可能性
2. Webhookが削除された可能性
3. Discordサーバーで新しいWebhookを再作成

#### ❌ 問題4: 「HTTP 401 - Unauthorized」エラー

**症状:**
```
Discord通知送信エラー: HTTP 401 - Unauthorized
```

**解決方法:**
1. WebhookURLの認証部分が間違っている
2. URLをもう一度正確にコピー&ペースト
3. 特殊文字が正しくエスケープされているか確認

#### ❌ 問題5: 通知が届かない

**解決手順:**
1. **Discordアプリの通知設定確認**
   - ユーザー設定 → 通知 → デスクトップ通知が有効か
   - サーバー通知設定が有効か

2. **サーバー通知設定確認**
   - サーバー名右クリック → 通知設定
   - 「すべてのメッセージ」または「@メンションのみ」を選択

3. **チャンネル権限確認**
   - Webhookを設定したチャンネルに書き込み権限があるか
   - チャンネル設定 → 権限 → Webhook権限を確認

## 📊 Discordの特徴・メリット

### 💰 料金・制限
- **完全無料**: 個人利用・商用利用ともに無料
- **無制限**: API呼び出し回数制限なし
- **高頻度対応**: 1秒間に数十回の通知も可能

### 🎨 表示の豊富さ
- **リッチEmbed**: 色分け、フィールド分割、タイムスタンプ
- **アイコン対応**: 絵文字によるアラート種別表示
- **マークダウン**: テキスト装飾（太字、斜体、コードブロック）

### 📱 マルチプラットフォーム対応
- **デスクトップ**: Windows、macOS、Linux
- **モバイル**: iOS、Android
- **ブラウザ**: Chrome、Firefox、Safari、Edge

### 🔔 通知システム
- **プッシュ通知**: スマホ・PCで即座に受信
- **通知音カスタマイズ**: アラート別に音を変更可能
- **履歴保存**: 過去の通知を遡って確認可能

## 🆚 LINE Notify との比較

| 項目 | LINE Notify | Discord Webhook |
|------|------------|-----------------|
| **サービス継続** | ❌ 2025年3月終了 | ✅ 継続中 |
| **料金** | 1,000回/月 | ✅ 完全無料・無制限 |
| **表示形式** | プレーンテキスト | ✅ リッチEmbed |
| **設定難易度** | ⭐⭐ 簡単 | ⭐⭐⭐ 少し複雑 |
| **日本での普及** | ⭐⭐⭐⭐⭐ 非常に高い | ⭐⭐⭐ 中程度 |
| **プッシュ通知** | ✅ 対応 | ✅ 対応 |
| **PC・スマホ対応** | ✅ 対応 | ✅ 対応 |
| **グループ共有** | ✅ 簡単 | ✅ 対応 |

## 📱 使用例・活用方法

### 🌅 朝の投資ルーティン
```
08:30 - Discordアプリで夜間の通知確認
09:00 - 市場開場前の設定確認
09:30 - 株価監視開始、リアルタイム通知受信
```

### 📊 投資戦略別チャンネル設定

#### 複数Webhook設定例
```json
{
  "notifications": {
    "discord_defensive": {
      "enabled": true,
      "webhook_url": "守備的戦略用WebhookURL"
    },
    "discord_growth": {
      "enabled": true, 
      "webhook_url": "成長株戦略用WebhookURL"
    }
  }
}
```

#### チャンネル分け例
- **#買いアラート**: 買い推奨通知専用
- **#売りアラート**: 利益確定・損切り専用
- **#日次レポート**: 1日の成績サマリー

### 📈 効果的な活用法
1. **家族・仲間との共有**: サーバーに複数人を招待して情報共有
2. **銘柄別チャンネル**: 注目銘柄ごとにチャンネルを分ける
3. **履歴検索**: Discord検索機能で過去のアラートを検索
4. **外部連携**: Discord Bot と連携して高度な自動化

## 🔒 セキュリティ・プライバシー

### ✅ 安全な点
- **WebhookURL管理**: 適切に管理すれば安全
- **サーバー制御**: 自分のサーバーなので完全制御可能
- **ログ管理**: メッセージ履歴を自分で管理

### ⚠️ 注意点
- **WebhookURL流出**: 他人に知られると不正投稿される可能性
- **パブリックサーバー**: 公開サーバーでの使用は避ける
- **権限管理**: サーバーメンバーの権限を適切に設定

### 🛡️ 推奨セキュリティ設定
1. **プライベートサーバー**: 投資用の非公開サーバーを作成
2. **環境変数でURL管理**（設定ファイルより安全）
3. **定期的なWebhook再作成**（3-6ヶ月毎）
4. **サーバーメンバー制限**: 信頼できる人のみ招待

## 🎓 上級者向けカスタマイズ

### 🔧 Embedカスタマイズ
`src/alert_manager.py` の `_send_discord_notification()` を編集:

```python
# カスタムEmbed例
embed = {
    "title": f"🚀 {alert_type_text}シグナル検出",
    "description": f"**{alert.symbol}** の投資機会をお知らせします",
    "color": color,
    "thumbnail": {
        "url": "https://example.com/stock-icon.png"
    },
    "fields": [
        {
            "name": "📊 銘柄情報",
            "value": f"コード: {alert.symbol}\n価格: ¥{alert.triggered_price:,.0f}",
            "inline": True
        },
        {
            "name": "📈 投資判断",
            "value": f"戦略: {alert.strategy_name}\n信頼度: ⭐⭐⭐⭐",
            "inline": True
        }
    ],
    "footer": {
        "text": "⚠️ 投資判断はご自身の責任で行ってください",
        "icon_url": "https://example.com/warning-icon.png"
    }
}
```

### 📊 複数サーバー・チャンネル対応
```python
# 戦略別Webhook設定
webhooks = {
    'defensive': os.getenv('DISCORD_WEBHOOK_DEFENSIVE'),
    'growth': os.getenv('DISCORD_WEBHOOK_GROWTH'),
    'speculative': os.getenv('DISCORD_WEBHOOK_SPECULATIVE')
}

# 戦略に応じたWebhook選択
webhook_url = webhooks.get(alert.strategy_name, webhooks['defensive'])
```

### 🤖 Discord Bot連携（上級者向け）
```python
# Discord.py を使用したBot連携例
import discord
from discord.ext import commands

# アラート受信時の自動返答
@bot.event
async def on_message(message):
    if message.author.name == "日本株ウォッチドッグ":
        if "買い推奨" in message.content:
            await message.add_reaction("💰")
            await message.add_reaction("✅")
```

## 🆘 サポート・問い合わせ

### 🔍 問題解決の流れ
1. **このガイドのトラブルシューティングを確認**
2. **テストコマンドでエラー詳細を確認**
3. **Discord側の設定（サーバー・チャンネル・権限）を再確認**
4. **新しいWebhookで再試行**

### 📞 サポートリソース
- **Discord公式ヘルプ**: https://support.discord.com/
- **Webhook公式ドキュメント**: https://discord.com/developers/docs/resources/webhook
- **アプリのテストツール**: `python test_discord_notification.py`
- **GitHub Issues**: バグ報告・機能要望

### 💬 よくある質問（FAQ）

**Q: スマホでも通知を受け取れますか？**
A: はい。Discordアプリをインストールしてプッシュ通知を有効にしてください

**Q: 通知音を変更できますか？**
A: はい。Discord設定 → 通知 → 音とサウンド で変更可能

**Q: 複数の人と通知を共有したい場合は？**
A: サーバーに他の人を招待して、同じチャンネルで通知を共有可能

**Q: 古い通知を削除したい場合は？**
A: チャンネル内のメッセージを個別削除、またはチャンネル全体を削除

**Q: WebhookURLを間違えて公開してしまった場合は？**
A: 即座にWebhookを削除し、新しいWebhookを作成してください

**Q: 会社のネットワークでも使えますか？**
A: 企業ファイアウォールでDiscordがブロックされている場合があります

**Q: 通知頻度を制限したい場合は？**
A: `config/strategies.json` でアラート条件を厳しく設定

---

## ✅ 設定完了チェックリスト

- [ ] Discordアカウントを作成した
- [ ] 投資用のプライベートサーバーを作成した
- [ ] Webhookを作成してURLをコピーした
- [ ] WebhookURLをアプリに設定した（環境変数 or 設定ファイル）
- [ ] `config/settings.json` で `discord.enabled: true` に設定した
- [ ] テスト通知を送信して、Discordで受信確認した
- [ ] スマホのDiscordアプリでプッシュ通知を確認した
- [ ] 投資戦略に合わせてアラート条件を調整した

**🎉 設定完了！これで株価アラートがDiscordで受け取れます！**

---

## 📈 移行のメリット（LINE Notify → Discord）

### ✅ 即座に得られるメリット
- **サービス継続性**: 2025年3月以降も安心
- **無制限通知**: 回数制限を気にせず利用可能
- **リッチ表示**: 色分け・構造化された見やすい通知
- **履歴管理**: 過去の通知を検索・参照可能

### 📊 長期的なメリット
- **拡張性**: Bot連携、複数チャンネル対応
- **コミュニティ**: 家族・仲間との投資情報共有
- **カスタマイズ**: 表示形式の自由な変更
- **安定性**: 大手プラットフォームの安定したサービス

---

**⚠️ 投資に関する注意事項**

このツールは投資の参考情報を提供するものであり、投資助言を行うものではありません。最終的な投資判断は必ずご自身の責任で行ってください。株式投資には元本割れのリスクがあります。