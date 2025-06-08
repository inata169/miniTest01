#!/usr/bin/env python3
"""
簡単EXE作成スクリプト（最小構成）
"""

import os
import sys
import subprocess


def build_simple_exe():
    """簡単なEXE作成"""
    print("🔨 簡単EXE作成中...")
    
    # PyInstallerコマンド（ワンライナー）
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # 単一EXEファイル
        '--windowed',                   # コンソール非表示
        '--name=JapaneseStockWatchdog', # EXE名
        '--add-data=config;config',     # 設定フォルダを含める
        '--add-data=data;data',         # データフォルダを含める
        '--add-data=src;src',           # srcフォルダを含める
        '--hidden-import=tkinter',      # tkinter明示的に含める
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=csv_parser',   # カスタムモジュール
        '--hidden-import=data_sources',
        '--hidden-import=database',
        '--hidden-import=alert_manager',
        '--hidden-import=stock_monitor',
        '--hidden-import=logger',
        '--hidden-import=exceptions',
        '--hidden-import=config_validator',
        'src/gui/main_window.py'        # メインスクリプト
    ]
    
    try:
        print("実行コマンド:")
        print(" ".join(cmd))
        print()
        
        result = subprocess.run(cmd, check=True)
        print("✅ ビルド完了!")
        
        # ファイルサイズ確認
        exe_path = "dist/JapaneseStockWatchdog.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📦 EXEファイル: {exe_path} ({size_mb:.1f}MB)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ビルドエラー: {e}")
        return False


if __name__ == "__main__":
    print("🚀 簡単EXE作成ツール")
    print("=" * 30)
    
    if build_simple_exe():
        print("\n🎉 完了!")
        print("EXEファイル: dist/JapaneseStockWatchdog.exe")
    else:
        print("❌ エラーが発生しました")
    
    input("Enterキーで終了...")