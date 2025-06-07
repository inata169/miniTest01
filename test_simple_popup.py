#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなポップアップテスト
"""

import tkinter as tk
from tkinter import messagebox
import sys

def test_simple_popup():
    """最もシンプルなポップアップテスト"""
    try:
        print("ポップアップテストを開始...")
        
        # ルートウィンドウを作成
        root = tk.Tk()
        root.withdraw()  # メインウィンドウを隠す
        
        # 最前面に表示
        root.attributes('-topmost', True)
        
        # メッセージボックスを表示
        result = messagebox.showinfo(
            "テスト通知",
            "これはテスト通知です。\n\nOKボタンを押してください。",
            parent=root
        )
        
        print(f"ユーザーの応答: {result}")
        
        # クリーンアップ
        root.destroy()
        
        print("✅ ポップアップテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def test_console_alert():
    """コンソールアラートテスト"""
    print("\n" + "🔔 "*20)
    print("🚨 重要なアラート 🚨")
    print("🔔 "*20)
    print("銘柄: TEST")
    print("アクション: 買い推奨")
    print("価格: ¥1,000")
    print("🔔 "*20 + "\n")

if __name__ == "__main__":
    print("📱 通知テスト")
    print("="*40)
    
    # 1. コンソールアラート（常に動作）
    print("\n1. コンソールアラートテスト:")
    test_console_alert()
    
    # 2. ポップアップテスト
    print("2. ポップアップテスト:")
    if test_simple_popup():
        print("デスクトップ通知が正常に動作しました！")
    else:
        print("デスクトップ通知に問題があります。")
        print("応答不可モードを確認してください。")
    
    input("\nEnterキーを押して終了...")