# 日本株ウォッチドッグ (Japanese Stock Watchdog)

![バージョン](https://img.shields.io/badge/version-1.3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![ライセンス](https://img.shields.io/badge/license-MIT-orange.svg)
![プラットフォーム](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

日本株式市場をリアルタイムで監視し、設定した条件に基づいて売買タイミングをアラートする**完全無料**の自動化投資支援システムです。SBI証券・楽天証券のCSVファイルから保有銘柄を自動インポートし、**J Quants API（無料）**および**Yahoo Finance API**を使用してリアルタイム株価監視を行います。

## 🌟 主要機能

### 📊 ポートフォリオ管理
- **🆕 欲しい銘柄タブ**: 将来購入したい銘柄を体系的に管理、希望価格設定
- **🔥 条件マッチング視覚化**: 🔥買い頃！⚡あと少し👀要注目😴様子見の4段階表示
- **SBI証券・楽天証券CSVインポート**: Shift-JISエンコーディング完全対応
- **リアルタイム損益計算**: 取得価格、現在価格、収益率の自動計算
- **複数口座対応**: NISA、一般口座、つみたてNISAなど口座タイプ別管理
- **日本株・米国株対応**: 4桁コード（日本株）とティッカー（米国株）の両方をサポート

### 📈 株価監視・アラート
- **🆕 J Quants API**: 日本株特化の無料データソース（レート制限回避）
- **Yahoo Finance API**: フォールバック用データソース
- **マルチデータソース**: J Quants → Yahoo Finance 自動切り替え
- **投資戦略別アラート**: 配当利回り・PER・PBRベースの買い条件
- **利益確定・損切りアラート**: 設定した利益率・損失率に達した際の自動通知
- **多様な通知方法**: Gmail、Discord、LINE Notify、デスクトップ通知

### 🔍 高度な分析機能
- **テクニカル分析**: RSI、移動平均線、ボリンジャーバンド（将来実装）
- **ファンダメンタル分析**: PER、PBR、ROE、配当利回りの自動取得
- **リスク管理**: 銘柄別・セクター別のリスク分散度分析

## 🚀 クイックスタート

### 1. システム要件

- **Python**: 3.8以上
- **OS**: Windows 10/11、macOS 10.14+、Ubuntu 18.04+
- **メモリ**: 512MB以上
- **ディスク容量**: 100MB以上
- **インターネット接続**: 株価データ取得用

### 2. インストール

#### 仮想環境セットアップ（推奨）
```bash
# uvをインストール（初回のみ）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 仮想環境作成とパッケージインストール
uv venv
source .venv/bin/activate  # Linux/macOS
# または .venv\Scripts\activate  # Windows

# 依存関係をインストール
uv pip install -r requirements.txt

# 簡単アクティベーション（作成済み）
./activate_env.sh

### 🔑 認証設定（.env方式）

#### 3. 環境変数設定（推奨・セキュア）
```bash
# 設定テンプレートをコピー
cp .env.example .env

# .envファイルを編集（秘密情報を設定）
nano .env
```

**基本設定例**:
```env
# J Quants API（日本株データ取得・推奨）
JQUANTS_REFRESH_TOKEN=your_jquants_refresh_token

# Gmail通知（オプション）
GMAIL_USERNAME=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_digit_app_password

# Discord通知（オプション）
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123/abc

# LINE Notify（オプション・2025年3月終了予定）
LINE_NOTIFY_TOKEN=your_line_token
```
```

#### 自動セットアップ（従来方式）
```bash
# Windows
setup.bat

# 通知設定（対話式）
setup_notifications.bat

# Linux/macOS
python setup.py
```

#### 手動インストール
```bash
# 1. リポジトリをクローン
git clone https://github.com/inata169/miniTest01.git
cd miniTest01

# 2. 仮想環境セットアップ（推奨）
uv venv && source .venv/bin/activate

# 3. 依存関係をインストール
uv pip install -r requirements.txt

# 4. 必要なディレクトリを作成
mkdir -p data/csv_imports data/backups logs

# 5. アプリケーションを起動
python src/main.py --gui
```

### 3. 初回設定

#### GUIモード（推奨）

**WSL/Linux環境:**
```bash
# 仮想環境を有効化してから起動
source .venv/bin/activate  # または ./activate_env.sh
python3 src/main.py --gui

# 簡単起動スクリプト（v1.1.0+）
./run_app.sh
```

**Windows環境（GUI設定時推奨）:**
```powershell
# PowerShellで実行
cd "C:\Users\放射治療研究用PC\Documents\ClaudeCode\miniTest01"
.\venv_windows\Scripts\Activate.ps1

# IMPORTANT: SSL証明書エラー回避のため環境変数設定
set CURL_CA_BUNDLE=
set SSL_CERT_FILE=

python src/main.py --gui
```

#### コマンドラインモード
```bash
# 仮想環境を有効化
source .venv/bin/activate

# インタラクティブモード
python3 src/main.py

# バックグラウンド監視モード
python3 src/main.py --daemon

# ヘルプ表示
python3 src/main.py --help
```

## 📥 CSVインポート手順

### SBI証券の場合

1. **SBI証券にログイン** → 「口座管理」→「口座（円建）」
2. **保有証券をクリック** → 「CSVダウンロード」をクリック
3. **SaveFile.csv**というファイルがダウンロードされます
4. **アプリでインポート**: 「CSVインポート」タブ → ファイル選択 → 「インポート実行」

### 楽天証券の場合

1. **楽天証券にログイン** → 「マイメニュー」→「資産残高・保有商品」
2. **CSV で保存**をクリック
3. **assetbalance(all)_***.csv**というファイルがダウンロードされます
4. **アプリでインポート**: 自動フォーマット判定でインポート

### ヘルプ機能

**GUIアプリケーション内**でCSV取得方法を確認：
- **ヘルプメニュー** → **「CSVファイル取得方法」**をクリック
- **詳細な手順画像付き**で楽天証券・SBI証券の両方の取得方法を表示
- **注意事項**や**エンコーディング情報**も含む完全ガイド

### 対応CSVフォーマット

#### SBI証券フォーマット（SaveFile.csv）
```csv
銘柄コード,銘柄名,保有株数,,取得単価,現在値,取得金額,評価金額,評価損益
"7203","トヨタ自動車",100,,2500,2600,250000,260000,+10000
```

#### 楽天証券フォーマット（assetbalance(all)_*.csv）
**2025年最新版対応済み**
```csv
"種別","銘柄コード・ティッカー","銘柄","口座","保有数量","［単位］","平均取得価額","［単位］","現在値","［単位］",...
"国内株式","7203","トヨタ自動車","NISA成長投資枠","100","株","2500","円","2600","円",...
"投資信託","","楽天・全米株式インデックス・ファンド","つみたてNISA","10000","口","20000","円","21000","円",...
"米国株式","AAPL","アップル","NISA成長投資枠","10","株","150.00","USD","160.00","USD",...
```

### 📊 解析機能

- **自動フォーマット判定**: ファイル内容から証券会社を自動識別
- **多様な資産タイプ**: 国内株式、米国株式、投資信託、ETF、外貨預り金
- **NISA口座対応**: つみたてNISA、NISA成長投資枠、特定口座を区別
- **投資信託対応**: 銘柄コードがない投資信託も疑似シンボルで管理
- **エンコーディング自動検出**: Shift-JIS、UTF-8等を自動判定

## 📊 使用方法

### ポートフォリオ表示

**メイン画面**では以下の情報を表示：
- **サマリー情報**: 総銘柄数、取得金額、評価金額、損益、収益率
- **サマリー表示制御**: チェックボックスでサマリー情報の表示/非表示を切り替え可能
- **銘柄一覧**: 銘柄別の詳細情報（取得価格、現在価格、損益、収益率）
- **色分け表示**: 利益は緑、損失は赤で視覚的に判別
- **🆕 ソート機能**: ヘッダークリックで全カラムをソート可能（v1.1.0+）

### 株価更新機能

```bash
# 手動更新
「株価更新」ボタンをクリック

# 自動更新設定
config/settings.json で更新間隔を設定
```

### 🆕 アラート機能（v1.1.0）

**ポートフォリオタブ**のアラート機能：
- **アラートテストボタン**: 通知機能の動作確認
- **アラート履歴タブ**: 過去のアラート履歴を色分け表示
  - 💰 買い推奨（青色）
  - ✅ 利益確定（緑色）
  - ⚠️ 損切り（赤色）
  - 🧪 テスト（黒色）

**デスクトップ通知**：
- 絵文字付きタイトル
- 適切なアイコン表示
- メインスレッドで確実に動作

### 監視・アラート設定

**監視タブ**で以下を設定：
- **監視銘柄の追加**: 銘柄コード入力で自動追加
- **投資戦略の選択**: ディフェンシブ、成長株、デフォルト戦略
- **アラート条件**: 買い条件・売り条件のカスタマイズ

## ⚙️ 詳細設定

### 投資戦略設定 (`config/strategies.json`)

```json
{
  "default_strategy": {
    "buy_conditions": {
      "dividend_yield_min": 3.0,    // 最低配当利回り（%）
      "per_max": 15.0,              // 最大PER
      "pbr_max": 1.5                // 最大PBR
    },
    "sell_conditions": {
      "profit_target": 20.0,        // 利益確定ライン（%）
      "stop_loss": -10.0            // 損切りライン（%）
    }
  },
  "defensive_strategy": {
    "buy_conditions": {
      "dividend_yield_min": 2.5,
      "per_max": 20.0,
      "pbr_max": 2.0
    },
    "sell_conditions": {
      "profit_target": 15.0,
      "stop_loss": -8.0
    }
  },
  "growth_strategy": {
    "buy_conditions": {
      "dividend_yield_min": 1.0,
      "per_max": 25.0,
      "pbr_max": 3.0
    },
    "sell_conditions": {
      "profit_target": 30.0,
      "stop_loss": -15.0
    }
  }
}
```

### 通知設定 (`config/settings.json`)

```json
{
  "database": {
    "path": "data/portfolio.db"
  },
  "notifications": {
    "email": {
      "enabled": false,             // メール通知有効/無効
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your_email@gmail.com",
      "password": "app_password",   // Gmailアプリパスワード
      "recipients": ["alerts@yourdomain.com"]
    },
    "desktop": {
      "enabled": true               // デスクトップ通知有効/無効
    },
    "console": {
      "enabled": true               // コンソール通知有効/無効
    }
  },
  "monitoring": {
    "check_interval_minutes": 30,  // 監視間隔（分）
    "market_hours_only": true,     // 市場時間のみ監視
    "market_start_hour": 9,        // 市場開始時間
    "market_end_hour": 15          // 市場終了時間
  }
}
```

### 通知設定手順

#### 簡単設定（推奨）
```bash
# 対話式セットアップを実行
setup_notifications.bat

# 選択肢：
# 1. デスクトップ通知のみ（パスワード不要）
# 2. Gmail + デスクトップ通知（アプリパスワード必要）
```

#### Gmail通知設定（手動）

**セキュリティ重視**: 環境変数でパスワード管理

1. **Googleアカウント**の2段階認証を有効化
2. **アプリパスワード**を生成：
   - [Google アプリパスワード](https://myaccount.google.com/apppasswords)
   - 「メール」を選択してパスワードを生成
3. **環境変数に設定**：
   ```cmd
   # Windows
   setx GMAIL_USERNAME "your_email@gmail.com"
   setx GMAIL_APP_PASSWORD "your_16_char_app_password"
   ```
4. **設定ファイル**で通知先を設定：
   ```json
   {
     "notifications": {
       "email": {
         "enabled": true,
         "recipients": ["alerts@yourdomain.com"]
       }
     }
   }
   ```

## 📁 詳細ファイル構成

```
japanese-stock-watchdog/
├── src/                         # ソースコード
│   ├── main.py                  # メインアプリケーション
│   ├── csv_parser.py            # CSVパーサー（SBI/楽天対応）
│   ├── data_sources.py          # Yahoo Finance株価取得
│   ├── stock_monitor.py         # 株価監視・アラートエンジン
│   ├── alert_manager.py         # 通知管理（メール・デスクトップ）
│   ├── database.py              # SQLiteデータベース管理
│   └── gui/
│       └── main_window.py       # tkinter GUIメインウィンドウ
├── config/                      # 設定ファイル
│   ├── settings.json            # アプリケーション設定
│   └── strategies.json          # 投資戦略設定
├── data/                        # データディレクトリ
│   ├── portfolio.db             # SQLiteデータベース
│   └── csv_imports/             # CSVインポート用フォルダ
├── logs/                        # ログファイル
│   └── app.log                  # アプリケーションログ
├── tests/                       # テストファイル
│   └── test_csv_parser.py       # CSVパーサーテスト
├── requirements.txt             # Python依存関係
├── setup.py                     # 自動セットアップスクリプト
├── setup.bat                    # Windows用セットアップ
├── setup_notifications.bat      # 通知設定（対話式）
├── run_gui.bat                  # Windows用GUI起動
├── clear_db.py                  # データクリアスクリプト
├── debug_db.py                  # デバッグ用スクリプト
├── CHANGELOG.md                 # 変更履歴
├── CLAUDE.md                    # 開発者向けガイド
└── README.md                    # このファイル
```

## 🔧 技術仕様

### 使用技術
- **言語**: Python 3.8+
- **GUI**: tkinter（Python標準ライブラリ）
- **データベース**: SQLite3（Python標準ライブラリ）
- **株価API**: Yahoo Finance（yfinance）
- **データ処理**: pandas, numpy
- **文字エンコーディング**: chardet（自動検出）

### データソース
- **株価データ**: Yahoo Finance API（無料・無制限）
- **企業財務データ**: Yahoo Finance経由で取得
- **配当情報**: Yahoo Finance配当履歴
- **為替レート**: Yahoo Finance（米国株用）

### サポート市場
- **日本株**: 東京証券取引所（TSE）
- **米国株**: ナスダック、NYSE
- **ETF**: 日本・米国上場ETF
- **投資信託**: 楽天証券経由の投資信託

## 💰 コスト構造

### 完全無料で利用可能
- ✅ **Yahoo Finance API**: 無制限・無料
- ✅ **SQLiteデータベース**: ローカル・無料
- ✅ **Gmail通知**: 個人アカウント・無料
- ✅ **Python & tkinter**: オープンソース・無料
- ✅ **デスクトップアプリ**: インストール不要

### 必要な環境
- 💻 **PC**: Windows/Mac/Linux対応
- 🌐 **インターネット接続**: 株価データ取得用
- 📧 **Gmailアカウント**: 通知用（オプション）

## 🔒 セキュリティ・プライバシー

### データ保護
- **ローカル保存**: 全データはローカルに保存（クラウド非依存）
- **暗号化なし**: パスワード等の機密情報は保存しない
- **API制限**: Yahoo Finance利用規約に準拠した適切な使用

### 注意事項
- **環境変数でパスワード管理**: 設定ファイルに直接記載しない
- **デスクトップ通知のみ**: パスワード不要で最も安全
- CSVファイルには個人の投資情報が含まれます
- 定期的なバックアップを推奨します

## 🛠️ トラブルシューティング

### よくある問題

#### 1. 株価が取得できない
```bash
# 症状: "404 Error" や "株価取得エラー"
# 解決方法:
- Yahoo Financeで銘柄コードを確認
- インターネット接続を確認
- しばらく時間をおいて再試行
```

#### 2. CSVインポートエラー
```bash
# 症状: "不明なCSVフォーマット"
# 解決方法:
- ファイルがShift-JIS（cp932）で保存されているか確認
- SBI/楽天証券の正式なCSVエクスポート機能を使用
- ファイル名に日本語文字が含まれていないか確認
```

#### 3. 文字化け
```bash
# 症状: 銘柄名が文字化け
# 解決方法:
- CSVファイルのエンコーディングを確認
- chardetライブラリがインストールされているか確認
pip install chardet
```

#### 4. Gmail通知エラー
```bash
# 症状: "メール設定が不完全です"
# 解決方法:
# 1. 環境変数を確認
echo $GMAIL_USERNAME
echo $GMAIL_APP_PASSWORD

# 2. デスクトップ通知のみに変更
setup_notifications.bat  # 選択肢1を選択
```

#### 5. GUI起動エラー
```bash
# 症状: tkinterエラー
# 解決方法（Ubuntu/Linux）:
sudo apt-get install python3-tk

# 解決方法（macOS）:
brew install python-tk
```

#### 🆕 6. 日本語文字化け（v1.1.0で解決済み）
```bash
# 症状: GUI画面で日本語が□□□に表示される
# 解決方法（WSL/Linux）:
sudo apt install fonts-noto-cjk fonts-noto-cjk-extra

# 自動フォント検出機能により自動解決
```

#### 🆕 7. アラート通知が消えない（v1.1.0で解決済み）
```bash
# 症状: デスクトップ通知のOKボタンが押せない
# 解決方法: v1.1.0でメインスレッド実行に修正済み
# 緊急対処: ESCキーまたはAlt+F4で強制終了
```

### ログファイルの確認
```bash
# アプリケーションログを確認
cat logs/app.log

# データベース内容を確認
python debug_db.py

# データファイル一覧表示
python clear_db.py --list

# データベースのみリセット（バックアップ付き）
python clear_db.py

# 全データクリア（バックアップ付き）
python clear_db.py --all

# CSVファイルのみクリア
python clear_db.py --csv

# ログファイルのみクリア
python clear_db.py --logs
```

## 🔄 アップデート・メンテナンス

### 定期メンテナンス
```bash
# 1. データベースの手動バックアップ
cp data/portfolio.db data/backups/portfolio_backup_$(date +%Y%m%d).db

# 2. 古いログファイルのクリア
python clear_db.py --logs

# 3. 依存関係の更新
pip install --upgrade -r requirements.txt

# 4. テスト実行
python -m pytest tests/ -v

# 5. 設定ファイルの検証
python src/config_validator.py
```

## 🔧 トラブルシューティング

### Windows環境でのよくある問題

#### **SSL証明書エラー**
```
株価取得エラー: curl: (77) error setting certificate verify locations
```
**解決方法**: 環境変数を設定してからアプリケーションを起動
```cmd
set CURL_CA_BUNDLE=
set SSL_CERT_FILE=
python src/main.py --gui
```

#### **Yahoo Finance API制限エラー**
```
429 Client Error: Too Many Requests
```
**原因**: 短時間での大量APIアクセスによるレート制限
**解決方法**: 
- 24時間待機（自動IP制限解除）
- 異なるネットワーク接続（モバイルテザリング等）
- 異なる場所からのアクセス

#### **仮想環境エラー**
```
.\venv_windows\Scripts\activate : 用語として認識されません
```
**解決方法**: PowerShell実行ポリシーの変更
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv_windows\Scripts\Activate.ps1
```

### WSL環境での問題

#### **X11 GUIエラー**
```
[xcb] Unknown sequence number while appending request
```
**解決方法**: Windows側Python環境でGUIを実行、WSL側ではデーモンモードを使用
```bash
# WSL側はデーモンモード推奨
python src/main.py --daemon
```

#### **フォント問題**
```
日本語が正しく表示されない
```
**解決方法**: 
```bash
sudo apt install fonts-noto-cjk fonts-noto-cjk-extra
```

## 💻 Windows実行ファイル（EXE）

### 📦 EXE版の特徴

- **単体実行可能**: Pythonインストール不要
- **設定ファイル同梱**: 初期設定済み
- **Windows最適化**: Windows 10/11で動作確認済み
- **簡単配布**: フォルダごとコピーで配布可能

### 🚀 EXE作成方法

#### 推奨方法（修正版）
```bash
# 依存関係をインストール
pip install -r requirements.txt

# 修正版ビルドスクリプト実行
python build_fixed.py
```

#### その他の作成方法
```bash
# デバッグ用（コンソール表示）
python build_debug.py

# 簡単ビルド
python build_simple.py

# フルビルド
python build_exe.py
```

### 📁 EXE配布パッケージ

```
dist/
├── JapaneseStockWatchdog.exe    # メインアプリケーション
├── test.bat                     # テスト用起動スクリプト
├── config/                      # 設定ファイル
│   ├── settings.json
│   └── strategies.json
├── data/                        # データディレクトリ
│   ├── csv_imports/
│   └── backups/
└── logs/                        # ログディレクトリ
```

### 🔧 EXE使用方法

1. **起動**: `JapaneseStockWatchdog.exe` をダブルクリック
2. **テスト**: `test.bat` で動作確認
3. **設定**: `config/settings.json` で詳細設定
4. **CSVインポート**: アプリ内のヘルプメニューで手順確認

### 📋 動作要件

- **OS**: Windows 10/11 (64bit)
- **メモリ**: 2GB以上推奨
- **ストレージ**: 200MB以上の空き容量
- **ネット接続**: 株価データ取得用

## 🆕 v1.3.0 新機能（2025年12月リリース）

### 🔥 データソース革命 - Yahoo Finance制限問題を完全解決

#### **J Quants API統合（無料・日本株特化）**
- **完全無料**: J Quants Personal Plan（制限なし）
- **日本市場特化**: 東証データ直接提供で高品質
- **レート制限なし**: Yahoo Finance 429エラーを完全回避
- **リアルタイムデータ**: 20分遅延だが安定した高品質データ
- **財務データ充実**: PER、PBR、配当利回り等の包括的データ

#### **🔄 マルチデータソース・フォールバック**
```
優先順位: J Quants API → Yahoo Finance → その他
- 第一選択: J Quants（日本株専用・高品質）
- フォールバック: Yahoo Finance（レート制限時）
- 自動切り替え: エラー時の無停止データ取得
```

#### **🔐 .env完全対応 - 業界標準セキュリティ**
すべての秘密情報を.envファイルで一元管理：
- **J Quants API認証**: リフレッシュトークン方式
- **Gmail通知**: アプリパスワード
- **Discord Webhook**: Webhook URL
- **LINE Notify**: アクセストークン
- **Git除外**: .envファイルは自動的にGit管理対象外

```env
# .env ファイル例
JQUANTS_REFRESH_TOKEN=your_token_here
GMAIL_USERNAME=your@gmail.com
GMAIL_APP_PASSWORD=abcd_efgh_ijkl_mnop
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123/abc
LINE_NOTIFY_TOKEN=your_line_token
```

### 🛡️ セキュリティ強化
- **環境変数優先**: .env → 設定ファイル の順で読み込み
- **後方互換性**: 既存の設定ファイルも継続利用可能
- **詳細ガイド**: .env.example に完全な設定手順を記載
- **自動読み込み**: python-dotenv による自動.env読み込み

## 🆕 v1.2.1 新機能（2025年12月リリース）

### 🎯 投資判断支援の大幅強化

#### **🆕 欲しい銘柄管理システム**
- **将来投資計画**: 購入予定銘柄の体系的管理
- **希望購入価格設定**: 目標価格と現在価格の差額表示
- **条件マッチング**: 買い条件の充足度をリアルタイム表示
- **投資メモ**: 銘柄選定理由の記録機能
- **ワンクリック移動**: 監視リストへの簡単移行

#### **🔥 条件マッチング視覚化システム**
保有銘柄と欲しい銘柄の両方で、投資条件の充足度を視覚的に表示：

| 表示 | 条件一致数 | 意味 | 色分け |
|------|-----------|------|--------|
| 🔥買い頃！ | 3条件一致 | 即座に購入検討 | 濃い緑背景 |
| ⚡検討中 | 2条件一致 | 購入タイミング接近 | オレンジ背景 |
| 👀監視中 | 1条件一致 | 監視継続 | 薄い赤背景 |
| 😴様子見 | 0条件一致 | 条件改善待ち | グレー背景 |

#### **💰 売りシグナル表示**
売り条件（利益確定・損切り）に達した銘柄には専用アイコンで表示：
- **💰売り頃！**: 利益確定条件達成
- **⚠️損切り**: 損切り条件達成

#### **💡 投資判断の即座把握**
```
保有銘柄画面での表示例:
🔥買い頃！ | 7203 | TOYOTA MOTOR | ¥2,616 | PER7.3 PBR1.0 配当0%
⚡検討中   | 6758 | SONY GROUP  | ¥12,850 | PER12.5 PBR2.8 配当1.2%
👀監視中   | 9984 | SoftBank G  | ¥7,420 | PER45.2 PBR0.8 配当5.1%
😴様子見   | 8306 | MUFG       | ¥1,285 | PER8.9 PBR0.4 配当4.8%
💰売り頃！ | 4519 | 中外製薬    | ¥4,200 | 利益+18.5%
```

### 🔧 システム安定性向上
- **価格更新エラー修正**: 整数型銘柄コードの処理を改善、"'int' object has no attribute 'startswith'"エラーを解決
- **堅牢な型変換**: より安全な文字列変換とエラーハンドリング
- **欲しい銘柄タブ**: 完全な機能実装とエラー回避

### 🎨 ユーザビリティ向上
- **直感的なインターフェース**: 絵文字とカラーコーディングで一目瞭然
- **投資タイミングの可視化**: 「もうちょっとで買い」「あと少しで売り」が瞬時に判断
- **ウィンドウサイズ最適化**: 1300x910ピクセルで情報を見やすく表示
- **ポートフォリオ構成最適化**: 3つのタブで効率的な銘柄管理
  - **保有銘柄**: 現在の投資状況
  - **監視リスト**: リアルタイム監視対象  
  - **欲しい銘柄**: 将来の投資計画

## 🆕 v1.1.0 新機能（2025年6月リリース）

### ✅ 実装済み機能
- **🧪 アラートテスト機能**: 通知システムの動作確認
- **📊 テーブルソート**: 全カラムのクリックソート対応
- **🎨 日本語フォント自動検出**: OSに最適なフォントを自動選択
- **🎯 色分けアラート履歴**: アラート種別を視覚的に区別
- **🔧 デスクトップ通知改善**: メインスレッド実行で安定動作
- **📦 uvパッケージ管理**: 高速な仮想環境とパッケージ管理
- **🚀 簡単起動スクリプト**: `./run_app.sh`で一発起動
- **📱 Discord通知**: LINE Notify終了対応、リッチEmbed形式通知

### 緊急対応：LINE Notify終了への対策（2025年3月終了予定）
- **⚠️ LINE Notify廃止**: 2025年3月31日でサービス終了
- **✅ Discord通知実装**: 完全無料・無制限の代替通知システム
- **🎨 リッチ通知**: 色分け・構造化された見やすいEmbed形式
- **📱 マルチデバイス対応**: PC・スマホ両方でプッシュ通知受信
- **🔄 段階的移行**: LINE + Discord併用期間を設けてスムーズに移行

## 🎯 v1.2.0 開発ロードマップ

### 🔥 高優先度機能（短期実装予定）

#### 📊 テクニカル指標強化
- **RSI（相対力指数）**: 買われ過ぎ・売られ過ぎの判定
- **MACD（移動平均収束拡散）**: トレンド転換点の検出
- **ボリンジャーバンド**: 価格レンジとボラティリティ分析
- **移動平均線**: 5日線・25日線・75日線のゴールデンクロス/デッドクロス
- **出来高分析**: 価格変動と出来高の相関関係

#### 📈 チャート表示機能
- **ローソク足チャート**: 日足・週足・月足対応
- **テクニカル指標重畳**: RSI、MACD等をチャート上に表示
- **パターン認識**: ダブルトップ・ヘッドアンドショルダー等の自動検出
- **インタラクティブ操作**: ズーム・パン・期間選択
- **マルチタイムフレーム**: 複数期間の同時表示

#### ⚡ リアルタイム監視強化
- **監視間隔短縮**: 現在30分間隔 → 1分間隔（市場開場中）
- **ティック更新**: 秒単位での価格変動監視（主要銘柄）
- **板情報監視**: 買い板・売り板の厚み変化検出
- **出来高急増検出**: 異常な出来高増加の即座アラート

### 🧠 中優先度機能（中期実装予定）

#### 🤖 機械学習予測システム
- **価格予測モデル**: LSTM・Transformerによる株価予測
- **売買タイミング最適化**: 強化学習による最適エントリー/エグジット
- **リスク評価**: ポートフォリオリスクの機械学習評価
- **相関分析**: 銘柄間・セクター間の相関関係分析
- **感情分析**: ニュース・SNSの感情スコアと株価の関連分析

#### 📈 バックテスト機能
- **戦略検証**: 過去データでの投資戦略パフォーマンス測定
- **リスク指標**: シャープレシオ・最大ドローダウン・VaR算出
- **最適化**: パラメータ最適化による戦略改善
- **比較分析**: 複数戦略の同時比較・ランキング

#### 🎯 高度な条件設定
- **複合条件**: AND/OR論理演算による複雑な条件設定
- **時系列条件**: 「3日連続上昇」「出来高2倍以上が続く」等
- **相対条件**: 「市場平均より○%上昇」「セクター内順位」等
- **カスタムスクリプト**: Python式での独自条件定義

### 🌐 低優先度機能（長期実装予定）

#### 🌐 Web UI
- **ブラウザベース**: どこからでもアクセス可能
- **レスポンシブデザイン**: スマホ・タブレット最適化
- **リアルタイムダッシュボード**: WebSocket による即時更新
- **クラウド同期**: 設定・データの自動バックアップ

#### 🔗 外部連携強化
- **証券会社API**: SBI・楽天の公式API連携（発表時）
- **経済指標連携**: 日銀・内閣府の経済統計自動取得
- **ニュース連携**: 日経・ロイター等のニュース解析
- **SNS連携**: Twitter・Reddit の投資関連情報収集

## 📋 実装予定タイムライン

### Phase 1: 基盤強化（v1.2.0 - 2025年7-8月）
```
Week 1-2: テクニカル指標実装（RSI、MACD、ボリンジャーバンド）
Week 3-4: チャート表示機能（ローソク足、インタラクティブ操作）
Week 5-6: リアルタイム監視強化（1分間隔監視）
Week 7-8: テスト・デバッグ・ドキュメント整備
```

### Phase 2: 高度分析（v1.3.0 - 2025年9-10月）
```
Week 1-2: バックテスト機能実装
Week 3-4: 機械学習基盤構築（価格予測モデル）
Week 5-6: 高度な条件設定システム
Week 7-8: パフォーマンス最適化・安定性向上
```

### Phase 3: 拡張機能（v1.4.0 - 2025年11-12月）
```
Week 1-2: Web UI基盤構築
Week 3-4: 外部API連携機能
Week 5-6: モバイルアプリ対応検討
Week 7-8: 統合テスト・リリース準備
```

## 🔧 技術仕様

### 新規技術スタック
- **チャート描画**: matplotlib / plotly.js
- **機械学習**: scikit-learn / tensorflow / pytorch
- **リアルタイム処理**: asyncio / websockets
- **Web UI**: Flask/FastAPI + React/Vue.js
- **データベース**: SQLite → PostgreSQL移行検討

## 🛠️ 開発者向け情報

### テスト・デバッグツール

#### 簡単テストスイート
```bash
# 依存関係なしでのコア機能テスト
python3 test_comprehensive.py

# 個別機能テスト
python3 test_database_simple.py       # データベース機能
python3 test_csv_simple.py           # CSV解析機能  
python3 test_notifications_simple.py # 通知システム

# デバッグ・修正ツール
python3 debug_and_fix.py            # 問題の自動検出と修正
```

#### 本格テストスイート（依存関係インストール後）
```bash
# 元のテスト実行
python -m pytest tests/ -v

# カバレッジレポート
python -m pytest --cov=src tests/

# データベース構造確認
python debug_db.py

# ログレベル変更（デバッグ用）
echo '{"logging": {"level": "DEBUG"}}' > config/settings_local.json
```

### テスト状況・品質保証

#### ✅ テスト済み機能
- **データベース操作**: SQLiteテーブル作成、データ挿入・更新・取得、ポートフォリオサマリー計算
- **CSV解析**: SBI・楽天証券フォーマット自動判定、日本語エンコーディング対応、数値変換、2025年最新版対応
- **通知システム**: コンソール・デスクトップ・メール通知、設定管理、アラート書式設定
- **設定管理**: JSON設定ファイル読み込み、投資戦略設定、エラーハンドリング
- **Windows EXE**: PyInstallerによる単体実行ファイル作成、モジュール読み込み問題解決

#### 🔧 修正済み問題
1. **外部ライブラリ依存**: pandas, yfinance, tkinter不足 → 依存関係なしで動作するバージョン作成
2. **SQLite datetime警告**: Python 3.12+での非推奨警告 → 適切なdatetimeアダプター登録で修正
3. **全角文字変換**: 日本語数値処理 → 全角カンマ・数字の半角変換機能追加
4. **CSV解析エラー**: 複雑なフォーマット → ロバストなパーサー実装
5. **楽天証券CSV新フォーマット**: 2025年版フォーマット変更 → 最新仕様に完全対応
6. **EXEモジュール読み込み**: PyInstallerでのカスタムモジュール問題 → 専用エントリーポイントで解決

#### 🚀 動作確認済み環境
- **Python**: 3.12.3 (最新版)
- **OS**: Linux (WSL2), Windows 10/11対応確認済み
- **データベース**: SQLite 3.x
- **文字エンコーディング**: UTF-8, Shift-JIS (cp932), EUC-JP
- **証券会社**: SBI証券（SaveFile.csv）、楽天証券（assetbalance形式、2025年最新版）
- **配布形式**: Python スクリプト版、Windows EXE 単体実行版

### 依存関係管理

#### 必須依存関係
```bash
# 最小構成（コア機能のみ）
python3 >= 3.8
sqlite3 (Python標準ライブラリ)
json (Python標準ライブラリ)
csv (Python標準ライブラリ)
```

#### 推奨依存関係
```bash
# フル機能利用
pip install yfinance>=0.2.28    # 株価データ取得
pip install pandas>=1.5.0       # データ処理
pip install chardet>=5.0.0      # 文字エンコーディング検出
pip install requests>=2.28.0    # HTTP通信
```

#### オプション依存関係
```bash
# GUI・通知機能
pip install tkinter              # デスクトップGUI (通常は標準インストール)
pip install openpyxl>=3.0.0     # Excelファイル読み込み
pip install email-validator>=1.3.0  # メール設定検証
```

### 設定ファイル検証
```bash
# 設定ファイルの妥当性チェック
python src/config_validator.py

# 投資戦略設定の検証
python src/config_validator.py --strategies
```

### エラーハンドリング
- **CSVImportError**: CSV形式不正・エンコーディングエラー
- **StockDataError**: 株価取得失敗・API制限
- **DatabaseError**: SQLite操作エラー・データ不整合
- **ConfigError**: 設定ファイル不正・必須項目不足

## 👥 コミュニティ・サポート

### バグ報告・機能要望
- **GitHub Issues**: バグ報告・新機能提案
- **GitHub Discussions**: 質問・議論
- **Documentation**: CLAUDE.md（開発者向け詳細ガイド）

### 貢献方法
1. **Fork** このリポジトリ
2. **Feature branch** を作成: `git checkout -b feature/new-feature`
3. **Tests** を追加: `tests/test_new_feature.py`
4. **Commit**: `git commit -am 'Add new feature'`
5. **Push**: `git push origin feature/new-feature`
6. **Pull Request** を作成

### コーディング規約
- **PEP 8**: Python標準コーディング規約に準拠
- **Type Hints**: 型注釈の使用推奨
- **Docstrings**: Google形式のドキュメント文字列
- **Error Handling**: カスタム例外クラスの使用
- **Logging**: ログレベルに応じた適切なログ出力

## 📄 ライセンス

MIT License

Copyright (c) 2024 Japanese Stock Watchdog

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## ⚠️ 免責事項

**重要**: このソフトウェアは投資の参考情報を提供するものであり、投資助言を行うものではありません。

- 📊 **データの正確性**: 株価データの正確性は保証されません
- ⏰ **遅延データ**: Yahoo Financeからのデータは15-20分程度の遅延があります
- 💰 **投資判断**: 最終的な投資判断は必ずご自身の責任で行ってください
- 📜 **利用規約**: Yahoo Finance の利用規約に従った適切な使用をお心がけください
- 🔒 **セキュリティ**: アプリパスワード等の認証情報は適切に管理してください

**投資は元本保証されません。株式投資に伴うリスクを十分理解の上でご利用ください。**