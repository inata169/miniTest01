#!/usr/bin/env python3
"""
デバッグ用EXE作成スクリプト（コンソール表示）
エラーの詳細が確認できます
"""

import os
import sys
import subprocess


def build_debug_exe():
    """デバッグ用EXE作成"""
    print("🔨 デバッグ用EXE作成中...")
    
    # PyInstallerコマンド（コンソール表示版）
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # 単一EXEファイル
        '--console',                    # コンソール表示（デバッグ用）
        '--name=JapaneseStockWatchdog_Debug', # EXE名
        '--add-data=config;config',     # 設定フォルダを含める
        '--add-data=data;data',         # データフォルダを含める
        '--add-data=src;src',           # srcフォルダを含める
        '--paths=src',                  # Pythonパスにsrcを追加
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
        '--clean',                      # 前回のビルドファイル削除
        'src/gui/main_window.py'        # メインスクリプト
    ]
    
    try:
        print("実行コマンド:")
        print(" ".join(cmd))
        print()
        
        result = subprocess.run(cmd, check=True)
        print("✅ ビルド完了!")
        
        # ファイルサイズ確認
        exe_path = "dist/JapaneseStockWatchdog_Debug.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📦 EXEファイル: {exe_path} ({size_mb:.1f}MB)")
            print("\n💡 このEXEはコンソール表示版です")
            print("   エラーメッセージが確認できます")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ビルドエラー: {e}")
        return False


if __name__ == "__main__":
    print("🐛 デバッグ用EXE作成ツール")
    print("=" * 40)
    
    if build_debug_exe():
        print("\n🎉 完了!")
        print("EXEファイル: dist/JapaneseStockWatchdog_Debug.exe")
        print("\n📝 使い方:")
        print("1. EXEファイルを実行")
        print("2. エラーメッセージをコンソールで確認")
        print("3. 問題解決後、通常版をビルド")
    else:
        print("❌ エラーが発生しました")
    
    input("Enterキーで終了...")