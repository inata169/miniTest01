# 日本株ウォッチドッグ (Japanese Stock Watchdog)

![バージョン](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![ライセンス](https://img.shields.io/badge/license-MIT-orange.svg)
![プラットフォーム](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

日本株式市場をリアルタイムで監視し、設定した条件に基づいて売買タイミングをアラートする**完全無料**の自動化投資支援システムです。SBI証券・楽天証券のCSVファイルから保有銘柄を自動インポートし、Yahoo Finance APIを使用してリアルタイム株価監視を行います。

## 🌟 主要機能

### 📊 ポートフォリオ管理
- **SBI証券・楽天証券CSVインポート**: Shift-JISエンコーディング完全対応
- **リアルタイム損益計算**: 取得価格、現在価格、収益率の自動計算
- **複数口座対応**: NISA、一般口座、つみたてNISAなど口座タイプ別管理
- **日本株・米国株対応**: 4桁コード（日本株）とティッカー（米国株）の両方をサポート

### 📈 株価監視・アラート
- **Yahoo Finance API**: 無料・無制限の株価データ取得
- **投資戦略別アラート**: 配当利回り・PER・PBRベースの買い条件
- **利益確定・損切りアラート**: 設定した利益率・損失率に達した際の自動通知
- **多様な通知方法**: デスクトップ通知、メール（Gmail SMTP）、コンソール表示

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

#### 自動セットアップ（推奨）
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
git clone https://github.com/your-username/japanese-stock-watchdog.git
cd japanese-stock-watchdog

# 2. 依存関係をインストール
pip install -r requirements.txt

# 3. 必要なディレクトリを作成
mkdir -p data/csv_imports data/backups logs

# 4. アプリケーションを起動
python src/main.py --gui
```

### 3. 初回設定

#### GUIモード（推奨）
```bash
# 直接起動
python src/main.py --gui

# Windows用バッチファイル
run_gui.bat
```

#### コマンドラインモード
```bash
# インタラクティブモード
python src/main.py

# バックグラウンド監視モード
python src/main.py --daemon

# ヘルプ表示
python src/main.py --help
```

## 📥 CSVインポート手順

### SBI証券の場合

1. **SBI証券にログイン** → 「ポートフォリオ」→「保有商品一覧」
2. **CSVダウンロード**をクリック
3. **文字エンコーディング**: Shift-JIS で保存される
4. **アプリでインポート**: 「CSVインポート」タブ → ファイル選択 → 「インポート実行」

### 楽天証券の場合

1. **楽天証券にログイン** → 「マイメニュー」→「保有商品一覧」
2. **CSVダウンロード**をクリック（詳細版を推奨）
3. **個別銘柄データ含む**形式を選択
4. **アプリでインポート**: 自動フォーマット判定でインポート

### 対応CSVフォーマット

#### SBI証券フォーマット
```csv
銘柄コード,銘柄名,保有株数,,取得単価,現在値,取得金額,評価金額,評価損益
"7203","トヨタ自動車",100,,2500,2600,250000,260000,+10000
```

#### 楽天証券フォーマット
```csv
区分,銘柄コード・ティッカー,銘柄名,口座,保有株数,単位,取得価額,単位,現在値,単位,...
国内株式,7203,トヨタ自動車,NISA成長投資枠,100,株,2500,円,2600,円,...
```

## 📊 使用方法

### ポートフォリオ表示

**メイン画面**では以下の情報を表示：
- **サマリー情報**: 総銘柄数、取得金額、評価金額、損益、収益率
- **銘柄一覧**: 銘柄別の詳細情報（取得価格、現在価格、損益、収益率）
- **色分け表示**: 利益は緑、損失は赤で視覚的に判別

### 株価更新機能

```bash
# 手動更新
「株価更新」ボタンをクリック

# 自動更新設定
config/settings.json で更新間隔を設定
```

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

### 機能追加予定
- 📊 **チャート表示**: ローソク足、移動平均線
- 🤖 **機械学習**: 株価予測、最適売買タイミング
- 📱 **LINE通知**: LINE Notify API連携
- 🌐 **Web UI**: ブラウザベースのインターフェース
- 📈 **バックテスト**: 過去データでの戦略検証

## 🛠️ 開発者向け情報

### デバッグ・テスト
```bash
# テスト実行
python -m pytest tests/ -v

# カバレッジレポート
python -m pytest --cov=src tests/

# データベース構造確認
python debug_db.py

# ログレベル変更（デバッグ用）
echo '{"logging": {"level": "DEBUG"}}' > config/settings_local.json
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