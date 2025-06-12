#!/usr/bin/env python3
"""
日本株ウォッチドッグ EXE作成スクリプト
Windows用実行ファイルを作成します
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def create_spec_file():
    """PyInstaller用specファイルを作成"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/gui/main_window.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'yfinance',
        'pandas',
        'numpy',
        'requests',
        'chardet',
        'email_validator',
        'openpyxl',
        'sqlite3',
        'csv',
        'json',
        'datetime',
        'threading',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'PIL', 'IPython', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JapaneseStockWatchdog',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリなのでコンソールを非表示
    icon=None,  # アイコンファイルがあれば指定
    version_info=None,
)
'''
    
    with open('JapaneseStockWatchdog.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ specファイルを作成しました: JapaneseStockWatchdog.spec")


def check_dependencies():
    """必要な依存関係をチェック"""
    print("📋 依存関係をチェック中...")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstallerがインストールされていません")
        print("インストールコマンド: pip install pyinstaller>=6.0.0")
        return False
    
    try:
        import yfinance
        print(f"✅ yfinance: {yfinance.__version__}")
    except ImportError:
        print("⚠️  yfinanceがインストールされていません（オプション）")
    
    try:
        import pandas
        print(f"✅ pandas: {pandas.__version__}")
    except ImportError:
        print("⚠️  pandasがインストールされていません（オプション）")
    
    try:
        import tkinter
        print("✅ tkinter: 利用可能")
    except ImportError:
        print("❌ tkinterが利用できません")
        return False
    
    return True


def build_exe():
    """EXEファイルをビルド"""
    print("🔨 EXEファイルをビルド中...")
    
    # 既存のbuild/distディレクトリを削除
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🗑️  既存のbuildディレクトリを削除")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🗑️  既存のdistディレクトリを削除")
    
    # PyInstallerを実行
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            'JapaneseStockWatchdog.spec',
            '--clean',
            '--noconfirm'
        ], check=True, capture_output=True, text=True)
        
        print("✅ ビルド完了!")
        print(result.stdout)
        
        # ビルド結果の確認
        exe_path = Path('dist/JapaneseStockWatchdog.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 EXEファイル: {exe_path} ({size_mb:.1f}MB)")
            return True
        else:
            print("❌ EXEファイルが見つかりません")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ ビルドエラー: {e}")
        print(f"標準エラー出力: {e.stderr}")
        return False


def create_launcher():
    """起動用のバッチファイルを作成"""
    launcher_content = '''@echo off
title 日本株ウォッチドッグ
echo ========================================
echo 日本株ウォッチドッグを起動しています...
echo ========================================
echo.

cd /d "%~dp0"

if exist "JapaneseStockWatchdog.exe" (
    echo EXEファイルを起動します...
    start "" "JapaneseStockWatchdog.exe"
) else (
    echo EXEファイルが見つかりません。
    echo Pythonスクリプトを起動します...
    if exist "src\\gui\\main_window.py" (
        python src\\gui\\main_window.py
    ) else (
        echo ファイルが見つかりません。
        pause
    )
)
'''
    
    with open('dist/起動.bat', 'w', encoding='cp932') as f:
        f.write(launcher_content)
    
    print("✅ 起動用バッチファイルを作成: dist/起動.bat")


def copy_config_files():
    """設定ファイルをdistディレクトリにコピー"""
    print("📂 設定ファイルをコピー中...")
    
    dist_config = Path('dist/config')
    if not dist_config.exists():
        dist_config.mkdir(parents=True)
    
    # 設定ファイルをコピー
    config_files = [
        'config/settings.json',
        'config/strategies.json'
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            shutil.copy2(config_file, dist_config)
            print(f"✅ コピー: {config_file} → dist/config/")
    
    # データディレクトリを作成
    dist_data = Path('dist/data')
    if not dist_data.exists():
        dist_data.mkdir(parents=True)
    
    (dist_data / 'csv_imports').mkdir(exist_ok=True)
    (dist_data / 'backups').mkdir(exist_ok=True)
    
    # logsディレクトリを作成
    (Path('dist/logs')).mkdir(exist_ok=True)
    
    print("✅ 必要なディレクトリを作成しました")


def create_readme():
    """配布用READMEを作成"""
    readme_content = '''# 日本株ウォッチドッグ - Windows実行版

## 起動方法

### 方法1: EXEファイル直接起動
- `JapaneseStockWatchdog.exe` をダブルクリック

### 方法2: バッチファイル起動
- `起動.bat` をダブルクリック

## 初期設定

1. **CSVファイルの準備**
   - SBI証券: SaveFile.csv
   - 楽天証券: assetbalance(all)_***.csv

2. **通知設定（オプション）**
   - デスクトップ通知: 設定不要
   - Gmail通知: config/settings.json で設定

## フォルダ構成

```
JapaneseStockWatchdog/
├── JapaneseStockWatchdog.exe    # メインアプリケーション
├── 起動.bat                     # 起動用バッチファイル
├── config/                      # 設定ファイル
│   ├── settings.json           # アプリケーション設定
│   └── strategies.json         # 投資戦略設定
├── data/                       # データフォルダ
│   ├── csv_imports/           # CSVインポート用
│   └── backups/               # バックアップ
└── logs/                       # ログファイル
```

## トラブルシューティング

### 起動しない場合
1. Windows Defenderの除外設定を確認
2. 管理者権限で実行
3. `起動.bat` を使用

### データが保存されない場合
- フォルダの書き込み権限を確認
- データフォルダが存在することを確認

## サポート
- GitHub: https://github.com/inata169/miniTest01
- 問題報告: GitHub Issues

---
日本株ウォッチドッグ v1.0 - Windows実行版
'''
    
    with open('dist/README_Windows.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 配布用READMEを作成: dist/README_Windows.txt")


def main():
    """メイン処理"""
    print("🚀 日本株ウォッチドッグ EXE作成ツール")
    print("=" * 50)
    
    # 依存関係チェック
    if not check_dependencies():
        print("❌ 依存関係の問題があります。requirements.txtを確認してください。")
        return False
    
    # specファイル作成
    create_spec_file()
    
    # EXEビルド
    if not build_exe():
        print("❌ ビルドに失敗しました")
        return False
    
    # 配布用ファイル作成
    copy_config_files()
    create_launcher()
    create_readme()
    
    print("\n🎉 EXE作成完了!")
    print("📁 配布ファイル: dist/フォルダ")
    print("🎯 起動方法: dist/JapaneseStockWatchdog.exe または dist/起動.bat")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        input("\nエラーが発生しました。Enterキーで終了...")
        sys.exit(1)
    else:
        input("\n完了しました。Enterキーで終了...")