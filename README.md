# 日本株ウォッチドッグ (Japanese Stock Watchdog)

![バージョン](https://img.shields.io/badge/version-1.4.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![ライセンス](https://img.shields.io/badge/license-MIT-orange.svg)
![プラットフォーム](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

日本株式市場をリアルタイムで監視し、設定した条件に基づいて売買タイミングをアラートする**完全無料**の自動化投資支援システムです。SBI証券・楽天証券のCSVファイルから保有銘柄を自動インポートし、**J Quants API（無料）**および**Yahoo Finance API**を使用してリアルタイム株価監視を行います。

## 🌟 現在の主要機能

### 📊 ポートフォリオ管理
- **SBI証券・楽天証券CSVインポート**: Shift-JISエンコーディング完全対応
- **リアルタイム損益計算**: 取得価格、現在価格、収益率の自動計算
- **複数口座対応**: NISA、一般口座、つみたてNISAなど口座タイプ別管理
- **日本株・米国株対応**: 4桁コード（日本株）とティッカー（米国株）の両方をサポート
- **右クリックメニュー**: 銘柄別配当履歴表示、チャート生成、削除、アラートテスト

### 📈 株価監視・アラート
- **J Quants API**: 日本株特化の無料データソース（レート制限回避）
- **Yahoo Finance API**: フォールバック用データソース
- **マルチデータソース**: J Quants → Yahoo Finance 自動切り替え
- **投資戦略別アラート**: 配当利回り・PER・PBRベースの買い条件
- **多様な通知方法**: Gmail、Discord、デスクトップ通知

### 🔍 財務分析機能
- **財務指標表示**: PER、PBR、ROE、配当利回りの自動取得
- **配当履歴分析**: 過去5年間の配当推移とグラフ表示
- **配当成長率計算**: 前年比成長率と投資判断指標
- **マウスホバー情報**: 銘柄にマウスを合わせると詳細情報を表示

## 🆕 v1.4.0の新機能

### 🚀 パフォーマンス大幅改善
- **起動時間短縮**: 15-20秒 → 3-5秒（3-5倍高速化）
- **非同期初期化**: GUIは即座に表示、データは背景で読み込み
- **スマートキャッシュ**: 5分間キャッシュでAPI呼び出し最適化
- **バッチ処理**: 効率的な複数銘柄データ取得

### 🎯 配当分析機能
- **配当履歴表示**: J Quants APIから過去配当データを取得
- **配当推移チャート**: matplotlib による視覚的なグラフ表示
- **配当成長率分析**: 前年比成長率と投資評価の自動計算
- **右クリック操作**: 銘柄選択 → 右クリック → 配当分析をワンクリック実行

### 🖱️ 右クリックコンテキストメニュー
銘柄表で任意の銘柄を右クリックすると以下の操作が可能：
- **Show [銘柄] Dividend History**: 配当履歴データ表示
- **Show [銘柄] Dividend Chart**: 配当推移グラフ生成
- **Delete [銘柄]**: 個別銘柄の安全な削除
- **Delete All Holdings**: 全銘柄削除（二重確認付き）
- **Test Alert for [銘柄]**: 個別銘柄のアラートテスト

### 🔧 技術基盤強化
- **J Quants API統合**: 日本株専用の高品質データソース
- **マルチデータソース**: J Quants + Yahoo Finance のハイブリッド取得
- **エラーハンドリング強化**: 包括的例外処理とログ機能
- **フォント問題解決**: WSL環境での文字化け・警告を完全回避

## 🚀 クイックスタート

### 1. システム要件
- **Python**: 3.8以上
- **OS**: Windows 10/11、macOS 10.14+、Ubuntu 18.04+
- **メモリ**: 512MB以上
- **ディスク容量**: 200MB以上
- **インターネット接続**: 株価データ取得用

### 2. インストール

#### 推奨セットアップ
```bash
# 1. リポジトリをクローン
git clone https://github.com/your-username/miniTest01.git
cd miniTest01

# 2. uvを使用した仮想環境セットアップ（推奨）
curl -LsSf https://astral.sh/uv/install.sh | sh  # uvインストール（初回のみ）
uv venv                                           # 仮想環境作成
source .venv/bin/activate                         # Linux/macOS
# または .venv\\Scripts\\activate                 # Windows

# 3. 依存関係をインストール
uv pip install -r requirements.txt

# 4. 追加パッケージ（配当分析機能用）
uv pip install matplotlib jquants-api-client python-dotenv

# 5. 必要なディレクトリを作成
mkdir -p data/csv_imports data/backups logs charts
```

### 3. 環境設定（.env方式）

```bash
# 設定テンプレートをコピー
cp .env.example .env

# .envファイルを編集
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
```

### 4. アプリケーション起動

#### GUIモード（推奨）
```bash
# 仮想環境を有効化
source .venv/bin/activate

# GUIアプリケーション起動
python3 src/main.py --gui
```

#### Windows環境
```powershell
# PowerShellで実行
.venv\\Scripts\\Activate.ps1

# SSL証明書エラー回避（Windows）
set CURL_CA_BUNDLE=
set SSL_CERT_FILE=

python src/main.py --gui
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

## 📊 使用方法

### 基本操作
1. **CSVインポート**: 証券会社からCSVファイルをダウンロードしてインポート
2. **株価更新**: 「株価更新」ボタンで最新価格を取得
3. **アラート設定**: 監視タブで買い条件・売り条件を設定
4. **配当分析**: 任意の銘柄を右クリック → 配当履歴表示・チャート生成

### 配当分析機能の使い方
1. **ポートフォリオタブ** → **保有銘柄**
2. 分析したい銘柄を**右クリック**
3. **「Show [銘柄] Dividend Chart」**を選択
4. 配当推移グラフが自動生成・表示されます

### 財務指標の確認
- 銘柄行にマウスを合わせると、PER・PBR・ROE・配当利回りがツールチップ表示
- 各指標は J Quants API（日本株）または Yahoo Finance（米国株）から取得

## ⚙️ 設定ファイル

### 投資戦略設定 (`config/strategies.json`)
```json
{
  \"default_strategy\": {
    \"buy_conditions\": {
      \"dividend_yield_min\": 1.0,    // 最低配当利回り（%）
      \"per_max\": 40.0,              // 最大PER
      \"pbr_max\": 4.0                // 最大PBR
    },
    \"sell_conditions\": {
      \"profit_target\": 20.0,        // 利益確定ライン（%）
      \"stop_loss\": -10.0            // 損切りライン（%）
    }
  }
}
```

### 通知設定 (`config/settings.json`)
```json
{
  \"notifications\": {
    \"email\": {
      \"enabled\": false,
      \"recipients\": [\"alerts@yourdomain.com\"]
    },
    \"desktop\": {
      \"enabled\": true
    }
  },
  \"monitoring\": {
    \"check_interval_minutes\": 30,
    \"market_hours_only\": true
  }
}
```

## 🔧 技術仕様

### 現在の技術スタック
- **言語**: Python 3.8+
- **GUI**: tkinter（Python標準ライブラリ）
- **データベース**: SQLite3
- **株価API**: J Quants API（日本株）+ Yahoo Finance（フォールバック）
- **データ処理**: pandas, numpy
- **可視化**: matplotlib
- **文字エンコーディング**: chardet（自動検出）

### データソース
- **日本株価データ**: J Quants API（無料・高品質）
- **米国株価データ**: Yahoo Finance API
- **財務データ**: J Quants API（PER/PBR/ROE/配当利回り）
- **配当履歴**: J Quants API（過去5年分）

## 💰 コスト構造

### 完全無料で利用可能
- ✅ **J Quants API**: Personal Plan（無料・制限なし）
- ✅ **Yahoo Finance API**: 無料（フォールバック用）
- ✅ **SQLiteデータベース**: ローカル・無料
- ✅ **Gmail通知**: 個人アカウント・無料
- ✅ **Python & ライブラリ**: オープンソース・無料

## 🛠️ トラブルシューティング

### よくある問題

#### 1. J Quants API認証エラー
```bash
# 症状: \"J Quants API未認証\"
# 解決方法:
# 1. .envファイルにJQUANTS_REFRESH_TOKENを設定
# 2. J Quants APIアカウント作成: https://jpx-jquants.com/
```

#### 2. 配当グラフでフォント警告
```bash
# 症状: matplotlib フォント警告
# 解決方法: 自動的にフォント設定が調整されグラフは正常表示されます
```

#### 3. CSVインポートエラー
```bash
# 症状: \"不明なCSVフォーマット\"
# 解決方法:
# - ファイルがShift-JIS（cp932）で保存されているか確認
# - SBI/楽天証券の正式なCSVエクスポート機能を使用
```

#### 4. 右クリックメニューが表示されない
```bash
# 症状: 右クリックでメニューが出ない
# 解決方法:
# - 実際の銘柄行（データがある行）で右クリック
# - PORTFOLIO_、FUND_等の疑似シンボルは対象外
```

## 🔄 今後の開発予定

### Phase 1: 基盤強化（v1.5.0 - 2025年夏）
- テクニカル指標追加（RSI、MACD、移動平均線）
- リアルタイム監視強化（30分 → 5分間隔）
- チャート表示機能の拡張

### Phase 2: 高度分析（v1.6.0 - 2025年秋）
- バックテスト機能
- ポートフォリオリスク分析
- 業種別分析機能

### Phase 3: Web化検討（v2.0.0 - 2025年末）
- Web UI版の開発検討
- クラウド同期機能
- モバイル対応

**注意**: 上記は計画であり、実装を保証するものではありません。開発状況や需要に応じて変更される可能性があります。

## 🔒 セキュリティ・プライバシー

### データ保護
- **ローカル保存**: 全データはローカルに保存（クラウド非依存）
- **環境変数管理**: .envファイルでAPIキー等を安全に管理
- **Git除外**: .envファイルは自動的にGit管理対象外

### 注意事項
- CSVファイルには個人の投資情報が含まれます
- 定期的なバックアップを推奨します
- APIキーは適切に管理してください

## 📄 ライセンス

MIT License

Copyright (c) 2024 Japanese Stock Watchdog

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
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
- ⏰ **遅延データ**: データソースからのデータは遅延があります
- 💰 **投資判断**: 最終的な投資判断は必ずご自身の責任で行ってください
- 📜 **利用規約**: J Quants API および Yahoo Finance の利用規約に従った適切な使用をお心がけください
- 🔒 **セキュリティ**: APIキー等の認証情報は適切に管理してください

**投資は元本保証されません。株式投資に伴うリスクを十分理解の上でご利用ください。**