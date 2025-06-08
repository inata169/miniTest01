#日本株ウォッチドッグ （Japanese Stock Watchdog）

## プロジェクト概要
日本株式市場をリアルタイムで監視し、設定した条件に基づいて売買タイミングをメール・通知でアラートする自動化システム。SBI証券・楽天証券のCSVフォーマットに対応し、保有銘柄の管理と投資判断を支援します。

## 主要機能

### 1. 株価監視・アラート機能
- リアルタイム株価取得（Yahoo Finance API等を使用）
- 買い時・売り時の自動判定とメール通知
- 設定可能なアラート条件（価格、配当利回り、テクニカル指標等）
- SMS/LINE通知オプション

### 2. 投資戦略設定
- **買い条件設定**：
  - 現在の配当利回り以上での購入判定
  - PER/PBR基準値設定
  - テクニカル分析指標（RSI、移動平均等）
- **売り条件設定**：
  - 購入価格からの利益率目標（○%UP時売却）
  - 損切りライン設定
  - 配当落ち日前自動売却オプション

### 3. 銘柄分析・推奨機能
- **銘柄カテゴリ分析**：
  - ディフェンシブ株（公益、食品、医薬品等）
  - 景気敏感株（自動車、鉄鋼、化学等）
  - 成長株スクリーニング
- **財務指標分析**：
  - PER（株価収益率）
  - PBR（株価純資産倍率）
  - ROE、ROA、自己資本比率
  - 配当利回り・配当性向

### 4. ポートフォリオ管理
- 保有銘柄の一元管理
- 取得価格・評価損益の自動計算
- セクター別資産配分表示
- リスク分散度分析

## 技術仕様

### データソース（全て無料）
- **株価データ**: Yahoo Finance（yfinance Python library）※無料・制限なし
- **企業財務データ**: EDINET API（金融庁提供・無料）
- **配当情報**: Yahoo Finance + 企業IRページスクレイピング
- **経済指標**: FRED API（Federal Reserve Economic Data・無料）
- **為替レート**: Yahoo Finance

### 対応CSVフォーマット
1. **SBI証券フォーマット**
   - エンコーディング: Shift-JIS（cp932）
   - フィールド: 銘柄コード、銘柄名、保有株数、平均取得価格、現在値、取得金額、評価金額、評価損益
   - 特徴: ヘッダー行に「保有商品一覧」、データ行は「"コード","名称",数量,,取得単価,現在値,...」形式
   
2. **楽天証券フォーマット**
   - エンコーディング: Shift-JIS（cp932）
   - フィールド: 商品、銘柄コード/名称、保有数量、取得価額、評価金額、評価損益等
   - 特徴: サマリー情報含む、詳細な資産配分データ

### アラート通知方法（無料オプション）
- **Gmail SMTP**: Googleアカウントのアプリパスワード使用（無料）
- **LINE Notify API**: 個人利用無料（月1000通まで）
- **デスクトップ通知**: OS標準機能（無料）
- **ローカルログファイル**: 完全無料

## ファイル構成

```
japanese-stock-watchdog/
├── src/
│   ├── main.py              # メインアプリケーション
│   ├── stock_monitor.py     # 株価監視クラス
│   ├── alert_manager.py     # アラート管理
│   ├── portfolio_manager.py # ポートフォリオ管理
│   ├── csv_parser.py        # CSV読み込み処理（文字エンコーディング対応）
│   ├── technical_analysis.py # テクニカル分析
│   ├── data_sources.py      # 株価データ取得（Yahoo Finance等）
│   └── gui/
│       ├── main_window.py   # メインGUI
│       ├── settings_dialog.py # 設定画面
│       └── portfolio_view.py  # ポートフォリオ表示
├── config/
│   ├── settings.json        # アプリ設定
│   ├── watchlist.json       # 監視銘柄リスト
│   ├── strategies.json      # 投資戦略設定
│   └── encoding_settings.json # CSVエンコーディング設定
├── data/
│   ├── portfolio.db         # SQLite データベース
│   └── csv_imports/         # CSVインポート用フォルダ
├── logs/
│   └── app.log             # アプリケーションログ
├── requirements.txt
├── README.md
└── CLAUDE.md
```

## 実装予定の主要クラス

### 1. StockMonitor
```python
class StockMonitor:
    def __init__(self, config_path):
        # 監視設定の読み込み
    
    def add_stock(self, symbol, strategy):
        # 監視銘柄追加
    
    def check_buy_conditions(self, symbol):
        # 買い条件チェック
    
    def check_sell_conditions(self, symbol):
        # 売り条件チェック
    
    def start_monitoring(self):
        # 監視開始（バックグラウンド実行）
```

### 2. PortfolioManager
```python
class PortfolioManager:
    def __init__(self, db_path):
        # データベース接続
    
    def import_csv(self, file_path, format_type):
        # CSV読み込み（SBI/楽天フォーマット対応）
        # Shift-JISエンコーディング自動検出
    
    def parse_sbi_format(self, file_path):
        # SBI証券フォーマット専用パーサー
        # "銘柄コード","銘柄名",保有株数,,取得単価,現在値,取得金額,評価金額,評価損益
    
    def parse_rakuten_format(self, file_path):
        # 楽天証券フォーマット専用パーサー
        # 複数セクション含むCSVの解析
    
    def update_current_prices(self):
        # 現在価格更新
    
    def calculate_performance(self):
        # 運用成績計算
```

### 3. AlertManager
```python
class AlertManager:
    def __init__(self, notification_config):
        # 通知設定読み込み
    
    def send_buy_alert(self, symbol, reason):
        # 買いアラート送信
    
    def send_sell_alert(self, symbol, reason):
        # 売りアラート送信
    
    def send_daily_report(self):
        # 日次レポート送信
```

## 設定例

### 投資戦略設定（strategies.json）
```json
{
  "default_strategy": {
    "buy_conditions": {
      "dividend_yield_min": 3.0,
      "per_max": 15.0,
      "pbr_max": 1.5,
      "rsi_max": 30
    },
    "sell_conditions": {
      "profit_target": 20.0,
      "stop_loss": -10.0,
      "dividend_ex_date_sell": true
    }
  },
  "defensive_strategy": {
    "sectors": ["electric_power", "gas", "pharmaceutical"],
    "buy_conditions": {
      "dividend_yield_min": 2.5,
      "per_max": 20.0
    }
  }
}
```

### 監視銘柄設定（watchlist.json）
```json
{
  "watchlist": [
    {
      "symbol": "7203",
      "name": "トヨタ自動車",
      "strategy": "cyclical_strategy",
      "category": "景気敏感"
    },
    {
      "symbol": "9432",
      "name": "NTT",
      "strategy": "defensive_strategy",
      "category": "ディフェンシブ"
    }
  ]
}
```

## 起動・使用方法

### 1. 初期設定
```bash
# 依存関係インストール
pip install -r requirements.txt

# 設定ファイル作成
python src/setup.py

# GUIで設定
python src/gui/main_window.py
```

### 2. CSV インポート
- SBI証券・楽天証券からエクスポートしたCSVファイルを `data/csv_imports/` に配置
- GUI または CLI でインポート実行

### 3. 監視開始
```bash
# バックグラウンドで監視開始
python src/main.py --daemon

# GUI モードで起動
python src/gui/main_window.py
```

## 通知設定

### メール設定例
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your_email@gmail.com",
    "password": "app_password",
    "recipients": ["alerts@yourdomain.com"]
  }
}
```

## データベーススキーマ

### holdings テーブル
- symbol (銘柄コード)
- name (銘柄名)
- quantity (保有株数)
- average_cost (平均取得価格)
- current_price (現在価格)
- last_updated (最終更新日時)

### alerts テーブル
- symbol, alert_type, message, created_at

### price_history テーブル
- symbol, date, open, high, low, close, volume

## 将来の拡張予定（無料範囲内）

1. **機械学習による予測機能**
   - scikit-learn使用（無料）
   - 株価トレンド予測
   - 最適売買タイミング提案

2. **リスク管理機能**
   - VaR（Value at Risk）計算
   - ポ
   - 損益通算シミュレーション
   - 確定申告用データ出力

4. **データ取得拡張（無料範囲）**
   - より多くの経済指標取得
   - 企業決算情報の自動収集
   - ニュースセンチメント分析（無料API範囲内）

## コスト構造

### 完全無料で利用可能
- **株価データ取得**: Yahoo Finance（yfinance）- 制限なし
- **財務データ**: EDINET API（金融庁）- 無料
- **通知**: Gmail（個人アカウント）、LINE Notify（月1000通まで）
- **データベース**: SQLite（ローカル）
- **GUI**: tkinter（Python標準ライブラリ）

### 必要な環境
- Python 3.8以上（無料）
- インターネット接続（データ取得用）
- Gmailアカウント（通知用・無料）

### 注意事項
- Yahoo Financeは利用規約に従った使用（過度なリクエスト禁止）
- データの正確性は保証されません（投資は自己責任）
- リアルタイムデータには若干の遅延あり（15-20分程度）