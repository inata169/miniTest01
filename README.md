# 日本株ウォッチドッグ (Japanese Stock Watchdog)

![バージョン](https://img.shields.io/badge/version-1.4.4-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![ライセンス](https://img.shields.io/badge/license-MIT-orange.svg)
![プラットフォーム](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

日本株式市場をリアルタイムで監視し、設定した条件に基づいて売買タイミングをアラートする**完全無料**の自動化投資支援システムです。SBI証券・楽天証券のCSVファイルから保有銘柄を自動インポートし、**J Quants API（無料）**および**Yahoo Finance API**を使用してリアルタイム株価監視を行います。

## 🌟 現在の主要機能

### 📊 ポートフォリオ管理
- **SBI証券・楽天証券CSVインポート**: Shift-JISエンコーディング完全対応
- **リアルタイム損益計算**: 取得価格、現在価格、収益率の自動計算
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

## 💰 サラリーマン投資家の皆様へ：このアプリのメリット

### 🎯 忙しいサラリーマンでも効率的な投資が可能
- **⏰ 時間効率**: 仕事中でも自動監視で買い時を逃さない
- **📱 リアルタイム通知**: Discord・メールで職場でも売買タイミングを把握
- **🔄 自動データ更新**: 手動チェック不要、設定した条件で自動アラート
- **📊 一目でわかる損益**: 複数証券会社の投資成績を統合表示

### 🎉 投資をもっと楽しく、もっとスマートに
- **📈 配当金の可視化**: 配当成長を美しいグラフで確認
- **🏆 投資成果の実感**: 色分けされた条件マッチング表示で達成感アップ
- **💡 学習機会**: PER・PBR・ROEなどの財務指標を自然に学習
- **🎯 目標設定**: 希望購入価格・利益確定ラインの明確化

### 🛡️ 無料で始める安心投資
- **💸 完全無料**: ライセンス費用・月額費用一切なし
- **🔒 データ安全**: ローカル保存でプライバシー保護
- **🌍 オープンソース**: コードの透明性で安心利用

### ⚠️ **重要：投資は自己責任です**
- **📋 このアプリは投資判断の参考情報を提供するものです**
- **⚖️ 最終的な投資判断は必ずご自身で行ってください**
- **💼 投資による利益・損失は全て自己責任となります**
- **📚 投資前に十分な調査・検討を行うことを強く推奨します**

## 🔗 J Quants API について

### 📊 J Quants API（無料）の活用推奨
**J Quants API** は日本取引所グループが提供する**無料**の株価データAPIです：

- **✅ 推奨理由**: 日本株データに特化した公式データソース
- **🚀 高い信頼性**: 東証公認の正確なリアルタイムデータ
- **🆓 完全無料**: 個人利用は制限なし、レート制限なし
- **📈 豊富なデータ**: 株価・財務・配当情報を網羅

### 🔄 Yahoo Finance フォールバック対応
- **🛡️ 安心設計**: J Quants API利用不可時の自動切り替え
- **🌍 米国株対応**: Yahoo FinanceでApple・Googleなど海外銘柄もサポート
- **⚡ 動作継続**: どちらかのAPIが停止しても影響なし

### 📝 J Quants API 登録手順（推奨・無料）
1. **[J Quants API](https://jpx-jquants.com/)** にアクセス
2. **無料アカウント作成** → メールアドレス登録のみ
3. **リフレッシュトークン取得** → `.env`ファイルに設定
4. **設定完了** → より高精度な日本株データを利用開始

> **Note**: J Quants API未登録でもYahoo Finance単体で基本機能は利用可能ですが、日本株投資をメインにされる方はJ Quants API登録を強く推奨します。

## 🆕 v1.4.4の新機能

### 🪟 Windows環境完全対応
- **ワンクリックインストール**: `setup_windows.bat` で依存関係自動解決
- **ワンクリック起動**: `run_app.bat` でSSL設定込みの簡単起動
- **コンパイルエラー回避**: プリビルドバイナリの段階的インストール
- **緊急起動**: `install_minimal.bat` で最小限構成での起動対応

### 🔧 GUI安定性向上
- **スレッドエラー修正**: "main thread is not in main loop" エラーを完全解決
- **ウィジェット存在チェック**: GUI要素の安全な更新処理
- **メインループ保護**: アプリ終了時の例外処理強化

### 📋 ユーザビリティ改善
- **バッチファイル提供**: Windows初心者でも簡単セットアップ
- **エラーハンドリング強化**: より親切なエラーメッセージ
- **トラブルシューティング充実**: 実体験ベースの解決策追加

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

### ⭐ Windows超簡単セットアップ（5分で完了）
```cmd
cd C:\Users\%USERNAME%\Documents\python
git clone https://github.com/inata169/miniTest01.git
cd miniTest01
setup_windows.bat
run_app.bat
```

### 1. システム要件
- **Python**: 3.8以上（Windows Store版推奨）
- **OS**: Windows 10/11、macOS 10.14+、Ubuntu 18.04+
- **メモリ**: 512MB以上
- **ディスク容量**: 200MB以上
- **インターネット接続**: 株価データ取得用

### 2. インストール

#### 🪟 Windows 推奨セットアップ（動作実証済み）
```cmd
# 1. 作業ディレクトリに移動
cd C:\Users\%USERNAME%\Documents\python

# 2. リポジトリをクローン
git clone https://github.com/inata169/miniTest01.git
cd miniTest01

# 3. ワンクリック自動セットアップ
setup_windows.bat

# 4. アプリ起動
run_app.bat
```

#### 🐧 Linux/macOS 推奨セットアップ
```bash
# 1. リポジトリをクローン
git clone https://github.com/inata169/miniTest01.git
cd miniTest01

# 2. uvを使用した仮想環境セットアップ（推奨）
curl -LsSf https://astral.sh/uv/install.sh | sh  # uvインストール（初回のみ）
uv venv                                           # 仮想環境作成
source .venv/bin/activate                         # Linux/macOS

# 3. 依存関係をインストール
uv pip install -r requirements.txt

# 4. 追加パッケージ（配当分析機能用）
uv pip install matplotlib jquants-api-client python-dotenv

# 5. 必要なディレクトリを作成
mkdir -p data/csv_imports data/backups logs charts
```

#### 🖥️ Windows + WSL + Ubuntu 詳細手順（実体験ベース）

**前提条件の確認**:
```bash
# WSL2がインストールされていることを確認
wsl --version
# Ubuntu 20.04 LTS以上が推奨
lsb_release -a
```

**ステップバイステップ手順**:
```bash
# 1. パッケージ更新（Ubuntu）
sudo apt update && sudo apt upgrade -y

# 2. 必要な開発ツールをインストール
sudo apt install -y curl git python3 python3-pip python3-venv

# 3. Python tkinter（GUI用）をインストール
sudo apt install -y python3-tk

# 4. 日本語フォント（CJK）をインストール
sudo apt install -y fonts-noto-cjk fonts-noto-cjk-extra

# 5. X11フォワーディング設定（GUI表示用）
export DISPLAY=:0

# 6. リポジトリクローン
git clone https://github.com/inata169/miniTest01.git
cd miniTest01

# 7. uvインストール（推奨）
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # 環境変数を再読み込み

# 8. 仮想環境作成・有効化
uv venv
source .venv/bin/activate

# 9. 依存関係インストール
uv pip install -r requirements.txt
uv pip install matplotlib jquants-api-client python-dotenv

# 10. 必要ディレクトリ作成
mkdir -p data/csv_imports data/backups logs charts

# 11. 環境設定
cp .env.example .env
nano .env  # またはcode .env
```

#### 🪟 Windows 11 - 完全動作確認済みインストール（v1.4.4+）⭐推奨

**🚀 確実セットアップ（実証済み・推奨）**:
```cmd
# 1. 作業ディレクトリに移動
cd C:\Users\%USERNAME%\Documents\python

# 2. 既存フォルダがあれば削除
rmdir /s /q miniTest01-main
rmdir /s /q miniTest01

# 3. 最新リポジトリをクローン
git clone https://github.com/inata169/miniTest01.git
cd miniTest01

# 4. 自動セットアップ実行（依存関係解決・検証付き）
setup_windows.bat

# 5. アプリ起動
run_app.bat
```

**✅ 動作確認済みの特徴**:
- **段階的インストール**: numpy/matplotlib コンパイルエラー自動回避
- **フォールバック処理**: エラー時の自動代替インストール
- **パッケージ検証**: インストール後の動作確認
- **SSL対策**: Windows SSL証明書問題の自動解決

**📋 提供されるバッチファイル**:
- **setup_windows.bat**: メインセットアップ（エラーハンドリング強化済み）
- **run_app.bat**: SSL設定 + アプリ起動
- **fix_matplotlib.bat**: matplotlib専用緊急修復スクリプト
- **install_minimal.bat**: 最小限構成での緊急起動

**🔧 手動セットアップ（従来方式）**:
```cmd
# 1. 作業ディレクトリに移動
cd C:\Users\%USERNAME%\Documents

# 2. リポジトリクローン
git clone https://github.com/inata169/miniTest01.git
cd miniTest01

# 3. 仮想環境作成（Windows標準方式）
python -m venv venv_windows

# 4. 仮想環境有効化
venv_windows\Scripts\activate.bat

# 5. setuptools・wheelアップグレード（重要）
pip install --upgrade pip setuptools wheel

# 6. 依存関係をバイナリで段階的インストール
pip install --no-deps chardet python-dotenv requests beautifulsoup4 lxml
pip install --only-binary=all numpy==1.24.3 matplotlib==3.7.2 pandas==2.0.3
pip install yfinance jquants-api-client openpyxl email-validator

# 7. 必要ディレクトリ作成
mkdir data\csv_imports data\backups logs charts

# 8. 環境設定ファイル作成
copy .env.example .env
notepad .env

# 9. SSL証明書エラー対策（重要）
set CURL_CA_BUNDLE=
set SSL_CERT_FILE=

# 10. アプリケーション起動テスト
python src/main.py --gui
```

#### 🔧 トラブルシューティング（実体験ベース）

**WSL環境でよくある問題**:
```bash
# X11表示エラーの場合
sudo apt install -y x11-apps
xeyes  # テスト用アプリで表示確認

# 日本語フォントが表示されない場合
sudo apt install -y language-pack-ja
sudo update-locale LANG=ja_JP.UTF-8
```

**Windows環境でよくある問題**:
```cmd
# 1. numpy/matplotlibコンパイルエラー（Visual Studio未インストール）
# 解決策: プリビルドバイナリを使用
pip install --only-binary=all numpy matplotlib pandas

# 2. 依存関係競合エラー
# 解決策: --no-deps オプションで段階的インストール
pip install --no-deps chardet python-dotenv requests

# 3. SSL証明書エラーが発生する場合
set REQUESTS_CA_BUNDLE=
set SSL_CERT_FILE=
set CURL_CA_BUNDLE=

# 4. PowerShell実行エラーの場合
powershell -Command "Get-ExecutionPolicy"
# RestrictedならRemoteSignedに変更
powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"

# 5. RuntimeError: main thread is not in main loop
# 解決策: v1.4.4で修正済み、最新版を使用

# 6. ModuleNotFoundError: No module named 'yfinance'
# 解決策: 仮想環境が正しく有効化されているか確認
venv_windows\Scripts\activate.bat
pip install yfinance
```

#### 📝 動作確認手順

**Windows（推奨）**:
```cmd
# 1. セットアップ完了後の確認
setup_windows.bat 実行時に以下が表示されれば成功：
matplotlib: OK
numpy: OK
pandas: OK
Setup completed successfully!

# 2. アプリケーション起動
run_app.bat

# 3. 起動確認メッセージ
🚀 日本株ウォッチドッグ - GUI起動中...
📋 初期設定を行っています。しばらくお待ちください...
✅ 初期化完了！画面を表示します
```

**Linux/macOS**:
```bash
# 1. 仮想環境が有効化されていることを確認
which python

# 2. 必要パッケージがインストールされていることを確認
python -c "import tkinter; print('tkinter: OK')"
python -c "import matplotlib; print('matplotlib: OK')"
python -c "import requests; print('requests: OK')"

# 3. アプリケーション起動テスト
python src/main.py --gui
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

#### 🪟 Windows（推奨・最も簡単）
```cmd
# ワンクリック起動
run_app.bat

# または手動実行
venv_windows\Scripts\activate.bat
set CURL_CA_BUNDLE=
set SSL_CERT_FILE=
python src/main.py --gui
```

#### 🐧 Linux/macOS GUIモード
```bash
# 仮想環境を有効化
source .venv/bin/activate

# GUIアプリケーション起動
python3 src/main.py --gui
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

## 👥 開発者情報

### 🛠️ 開発チーム
- **開発者**: inata169
- **共同開発者**: Claude Code（すごい時代になった）
- **開発PC**: 2019年3月に買ったMicrosoft Surface Go
- **開発環境**: Windows + WSL + Ubuntu
- **開発期間**: 2025年6月

### 💻 開発環境詳細
- **ハードウェア**: Microsoft Surface Go (2019年購入)
- **OS**: Windows 11 + WSL2 + Ubuntu 20.04
- **Python**: 3.8+
- **仮想環境**: uv + venv
- **エディタ**: VS Code
- **バージョン管理**: Git + GitHub

### 🚀 開発の背景
このプロジェクトは、日本の個人投資家（特にサラリーマン）が効率的に株式投資を行えるよう支援するツールとして開発されました。完全無料で、プライバシーを重視し、使いやすさを追求しています。

---

## ⚠️ 免責事項

**重要**: このソフトウェアは投資の参考情報を提供するものであり、投資助言を行うものではありません。

- 📊 **データの正確性**: 株価データの正確性は保証されません
- ⏰ **遅延データ**: データソースからのデータは遅延があります
- 💰 **投資判断**: 最終的な投資判断は必ずご自身の責任で行ってください
- 📜 **利用規約**: J Quants API および Yahoo Finance の利用規約に従った適切な使用をお心がけください
- 🔒 **セキュリティ**: APIキー等の認証情報は適切に管理してください

**投資は元本保証されません。株式投資に伴うリスクを十分理解の上でご利用ください。**