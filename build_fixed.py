#!/usr/bin/env python3
"""
修正版EXE作成スクリプト
モジュール読み込み問題を解決
"""

import os
import sys
import subprocess
import shutil


def build_fixed_exe():
    """修正版EXE作成"""
    print("🔨 修正版EXE作成中...")
    
    # 前回のビルドファイルを削除
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🗑️  buildディレクトリを削除")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🗑️  distディレクトリを削除")
    
    # PyInstallerコマンド（修正版）
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                        # 単一EXEファイル
        '--windowed',                       # コンソール非表示
        '--name=JapaneseStockWatchdog',     # EXE名
        '--add-data=config;config',         # 設定フォルダ
        '--add-data=data;data',             # データフォルダ
        '--add-data=src;src',               # srcフォルダ全体
        '--paths=src',                      # Pythonパス
        '--collect-all=tkinter',            # tkinter全体
        '--hidden-import=csv_parser',       # カスタムモジュール
        '--hidden-import=data_sources',
        '--hidden-import=database',
        '--hidden-import=alert_manager',
        '--hidden-import=stock_monitor',
        '--hidden-import=logger',
        '--hidden-import=exceptions',
        '--hidden-import=config_validator',
        '--hidden-import=yfinance',         # 外部ライブラリ
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=chardet',
        '--hidden-import=requests',
        '--clean',                          # クリーンビルド
        '--noconfirm',                      # 確認スキップ
        'main_exe.py'                       # 修正されたエントリーポイント
    ]
    
    try:
        print("実行コマンド:")
        print(" ".join(cmd))
        print()
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ ビルド完了!")
        
        # 警告があれば表示
        if result.stderr:
            print("\n⚠️  警告:")
            print(result.stderr[:500])  # 最初の500文字のみ
        
        # ファイルサイズ確認
        exe_path = "dist/JapaneseStockWatchdog.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n📦 EXEファイル: {exe_path} ({size_mb:.1f}MB)")
            
            # 設定ファイルをコピー
            copy_config_files()
            
            return True
        else:
            print("❌ EXEファイルが作成されませんでした")
            return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ビルドエラー: {e}")
        if e.stderr:
            print(f"エラー詳細: {e.stderr}")
        return False


def copy_config_files():
    """設定ファイルをdistにコピー"""
    print("\n📂 設定ファイルをコピー中...")
    
    # configディレクトリが既に含まれているかチェック
    dist_config = "dist/config"
    if not os.path.exists(dist_config):
        os.makedirs(dist_config, exist_ok=True)
        
        # 設定ファイルをコピー
        config_files = ["config/settings.json", "config/strategies.json"]
        for config_file in config_files:
            if os.path.exists(config_file):
                shutil.copy2(config_file, dist_config)
                print(f"✅ {config_file} をコピー")
    
    # dataディレクトリ作成
    os.makedirs("dist/data/csv_imports", exist_ok=True)
    os.makedirs("dist/data/backups", exist_ok=True)
    os.makedirs("dist/logs", exist_ok=True)
    
    print("✅ 必要なディレクトリを作成")


def create_test_script():
    """テスト用スクリプト作成"""
    test_content = '''@echo off
echo Testing JapaneseStockWatchdog.exe...
echo.

if exist "JapaneseStockWatchdog.exe" (
    echo Starting application...
    JapaneseStockWatchdog.exe
) else (
    echo JapaneseStockWatchdog.exe not found!
)

pause
'''
    
    with open('dist/test.bat', 'w', encoding='cp932') as f:
        f.write(test_content)
    
    print("✅ テスト用バッチファイルを作成: dist/test.bat")


if __name__ == "__main__":
    print("🔧 修正版EXE作成ツール")
    print("=" * 40)
    print("モジュール読み込み問題を修正します")
    print()
    
    if build_fixed_exe():
        create_test_script()
        print("\n🎉 完了!")
        print("📁 ファイル場所: dist/JapaneseStockWatchdog.exe")
        print("🧪 テスト実行: dist/test.bat")
        print("\n💡 問題が続く場合:")
        print("   python build_debug.py でコンソール版を作成")
    else:
        print("❌ エラーが発生しました")
    
    input("Enterキーで終了...")