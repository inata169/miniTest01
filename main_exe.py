#!/usr/bin/env python3
"""
EXE用エントリーポイント
PyInstallerでのモジュール読み込み問題を解決
"""

import os
import sys
from pathlib import Path

def setup_paths():
    """パスを設定"""
    # 実行ファイルのディレクトリを取得
    if getattr(sys, 'frozen', False):
        # PyInstallerでビルドされた場合
        base_path = Path(sys._MEIPASS)
        app_path = Path(sys.executable).parent
    else:
        # 通常のPython実行の場合
        base_path = Path(__file__).parent
        app_path = base_path
    
    # srcディレクトリをPythonパスに追加
    src_path = base_path / 'src'
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    # カレントディレクトリを実行ファイルの場所に設定
    os.chdir(app_path)
    
    return base_path, app_path


def main():
    """メイン処理"""
    try:
        # パス設定
        base_path, app_path = setup_paths()
        
        # GUIモジュールをインポート
        try:
            from gui.main_window import MainWindow
        except ImportError as e:
            print(f"GUIモジュールのインポートエラー: {e}")
            # フォールバック: 直接パスを指定
            gui_path = base_path / 'src' / 'gui'
            sys.path.insert(0, str(gui_path))
            sys.path.insert(0, str(base_path / 'src'))
            from main_window import MainWindow
        
        # アプリケーション起動
        app = MainWindow()
        app.run()
        
    except Exception as e:
        import traceback
        error_msg = f"アプリケーション起動エラー:\n{str(e)}\n\n詳細:\n{traceback.format_exc()}"
        
        # GUIでエラー表示を試行
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # メインウィンドウを隠す
            messagebox.showerror("エラー", error_msg)
            
        except:
            # GUIが使えない場合はコンソール表示
            print(error_msg)
            input("Enterキーで終了...")


if __name__ == "__main__":
    main()