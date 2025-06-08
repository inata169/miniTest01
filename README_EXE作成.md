# Windows EXE ファイル作成ガイド

## 🎯 作成できるもの

- **JapaneseStockWatchdog.exe**: 日本株ウォッチドッグのWindows実行ファイル
- **単体実行可能**: Pythonをインストールしていないマシンでも動作
- **設定ファイル込み**: 必要なファイルをすべて含んだ配布パッケージ

## 🔧 事前準備

### 1. 必要なソフトウェア
```bash
# Python 3.8以上
python --version

# pipが利用可能であること
pip --version
```

### 2. 依存関係のインストール
```bash
# 自動インストール（推奨）
pip install -r requirements.txt

# 手動インストール
pip install pyinstaller>=6.0.0
pip install yfinance pandas chardet requests
```

## 🚀 EXE作成方法

### 方法1: 修正版ビルド（🆕推奨）
```bash
# モジュール読み込み問題を解決した最新版
python build_fixed.py
```

### 方法2: デバッグビルド
```bash
# エラー確認用（コンソール表示）
python build_debug.py
```

### 方法3: 簡単ビルド
```bash
# 最小構成でのビルド
python build_simple.py
```

### 方法4: フルビルド
```bash
# 設定ファイル込みの完全ビルド
python build_exe.py
```

### 方法5: バッチファイル
```bash
# Windows バッチファイルを実行
build_exe.bat
```

### 方法6: 手動ビルド
```bash
# PyInstallerコマンド直接実行
python -m PyInstaller --onefile --windowed --name=JapaneseStockWatchdog src/gui/main_window.py
```

## 📁 ビルド結果

ビルド成功後、以下のフォルダ構成で出力されます：

```
dist/
├── JapaneseStockWatchdog.exe    # メインアプリケーション
├── 起動.bat                     # 起動用バッチファイル
├── README_Windows.txt           # 配布用説明書
├── config/                      # 設定ファイル
│   ├── settings.json
│   └── strategies.json
├── data/                        # データフォルダ
│   ├── csv_imports/
│   └── backups/
└── logs/                        # ログフォルダ
```

## ⚙️ ビルドオプション

### 修正版ビルド（build_fixed.py）🆕
- ✅ モジュール読み込み問題を解決
- ✅ 専用エントリーポイント（main_exe.py）使用
- ✅ パス設定の最適化
- ✅ 全カスタムモジュール明示的に包含
- ✅ 設定ファイル自動コピー
- ✅ テスト用バッチファイル作成

### デバッグビルド（build_debug.py）
- ✅ コンソール表示でエラー確認可能
- ✅ 問題解決用の詳細ログ
- ✅ 開発・トラブルシューティング向け

### フルビルド（build_exe.py）
- ✅ 詳細な依存関係チェック
- ✅ 設定ファイル自動コピー
- ✅ 起動バッチファイル作成
- ✅ 配布用README作成
- ✅ ディレクトリ構造自動作成

### 簡単ビルド（build_simple.py）
- ✅ 最小構成での高速ビルド
- ✅ 単一EXEファイル出力
- ⚠️ モジュール読み込み問題あり（修正版推奨）

## 🔍 トラブルシューティング

### よくある問題

#### 1. PyInstallerが見つからない
```bash
# 解決方法
pip install pyinstaller
```

#### 2. tkinterエラー
```bash
# Windows
# 通常は標準インストールされています

# Linux（参考）
sudo apt-get install python3-tk
```

#### 3. メモリ不足
```bash
# 解決方法: 簡単ビルドを使用
python build_simple.py
```

#### 4. モジュールが見つからない（'csv_parser' など）
```bash
# 原因: カスタムモジュールの読み込み失敗
# 解決方法: 修正版ビルドを使用
python build_fixed.py

# それでもダメなら: デバッグ版で詳細確認
python build_debug.py
```

#### 5. ファイルが見つからない
```bash
# 原因: 相対パス問題
# 解決方法: 設定ファイルを手動でdistフォルダにコピー
```

### デバッグ用コマンド

```bash
# 詳細ログ付きビルド
python -m PyInstaller --onefile --debug=all src/gui/main_window.py

# 依存関係確認
python -m PyInstaller --collect-all yfinance src/gui/main_window.py

# コンソール表示版（デバッグ用）
python -m PyInstaller --onefile --console src/gui/main_window.py
```

## 📦 配布方法

### 1. 単体配布
- `dist/JapaneseStockWatchdog.exe` のみ配布
- ユーザーが設定ファイルを作成

### 2. パッケージ配布（推奨）
- `dist/` フォルダ全体をZIP圧縮
- 設定ファイル・説明書込み
- 解凍後すぐに使用可能

### 3. インストーラー作成
```bash
# 将来の拡張案
# Inno Setupや NSIS を使用してインストーラー作成
```

## 🔐 セキュリティ注意事項

### Windows Defender
- 初回実行時に警告が表示される場合があります
- 「詳細情報」→「実行」で継続可能
- 配布時にはデジタル署名を推奨

### ファイアウォール
- Yahoo Finance API接続のためインターネットアクセスが必要
- 初回実行時にファイアウォール許可が必要

## 📊 ファイルサイズ目安

| ビルド方法 | ファイルサイズ | 起動速度 |
|-----------|---------------|----------|
| 簡単ビルド | 15-25MB | 高速 |
| フルビルド | 30-50MB | 普通 |
| 依存関係込み | 80-120MB | やや遅い |

## 🚀 パフォーマンス最適化

### 起動速度向上
```bash
# UPX圧縮（ファイルサイズ削減、起動高速化）
pip install upx
python -m PyInstaller --onefile --upx-dir=/path/to/upx src/gui/main_window.py
```

### ファイルサイズ削減
```bash
# 不要モジュール除外
python -m PyInstaller --onefile --exclude-module matplotlib --exclude-module PIL src/gui/main_window.py
```

## ✅ 品質チェック

ビルド後の確認項目：

- [x] EXEファイルが正常に起動する
- [x] GUIが正しく表示される
- [x] CSVインポート機能が動作する
- [x] データベース作成ができる
- [x] 設定ファイルが読み込まれる
- [x] ヘルプメニューが表示される
- [x] サマリー表示切り替えが動作する
- [x] モジュール読み込みエラーが解決済み

### 🆕 修正済み問題

#### v1.1で解決
- ✅ **ModuleNotFoundError: 'csv_parser'**: 専用エントリーポイントで解決
- ✅ **パス設定問題**: `main_exe.py`でPythonパス最適化
- ✅ **カスタムモジュール読み込み**: 全モジュール明示的に包含
- ✅ **設定ファイル配布**: 自動コピー機能追加

## 📞 サポート

問題が発生した場合：

1. **ログファイル確認**: `logs/app.log`
2. **GitHub Issues**: バグ報告・質問
3. **デバッグビルド**: `--console` オプションでエラー詳細確認

---

## 📝 開発者向けメモ

### カスタマイズ

`build_exe.py` の設定項目：

```python
# アイコン設定
icon='app_icon.ico'

# バージョン情報
version_info='version_info.txt'

# 追加ファイル
datas=[('config', 'config'), ('icons', 'icons')]

# 隠れた依存関係
hiddenimports=['custom_module']
```

### 自動化

CI/CD パイプラインでの自動ビルド：

```yaml
# GitHub Actions 例
- name: Build EXE
  run: |
    pip install -r requirements.txt
    python build_exe.py
    
- name: Upload artifact
  uses: actions/upload-artifact@v3
  with:
    name: JapaneseStockWatchdog-exe
    path: dist/
```