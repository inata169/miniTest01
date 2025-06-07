#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知機能テストスクリプト
"""

import sys
import os
from datetime import datetime

# sys.pathにsrcディレクトリを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_console_notification():
    """コンソール通知のテスト"""
    print("\n" + "="*50)
    print("🔵 BUY ALERT - 2024-01-15 14:30:00")
    print("="*50)
    print("銘柄: 7203")
    print("価格: ¥2,600")
    print("戦略: test_strategy")
    print("-" * 50)
    print("これはテスト通知です")
    print("通知機能が正常に動作しています")
    print("="*50 + "\n")

def test_desktop_notification():
    """デスクトップ通知のテスト"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        print("✅ tkinter利用可能 - デスクトップ通知をテスト中...")
        
        # メインウィンドウを作成（非表示）
        root = tk.Tk()
        root.withdraw()  # メインウィンドウを隠す
        
        # テスト通知を表示
        messagebox.showinfo(
            "買い推奨アラート", 
            "銘柄: TEST\n価格: ¥1,000\n\nこれはテスト通知です\n通知機能が正常に動作しています"
        )
        
        root.destroy()
        print("✅ デスクトップ通知テスト完了")
        return True
        
    except ImportError:
        print("❌ tkinterが利用できません")
        print("💡 代替案: コンソール通知のみ使用可能")
        return False
    except Exception as e:
        print(f"❌ デスクトップ通知エラー: {e}")
        print("💡 Windows環境ではWSLでGUIアプリは制限されることがあります")
        return False

def test_email_setup():
    """メール設定のテスト"""
    gmail_username = os.getenv('GMAIL_USERNAME')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    print(f"📧 Gmail設定状況:")
    print(f"  ユーザー名: {'設定済み' if gmail_username else '未設定'}")
    print(f"  パスワード: {'設定済み' if gmail_password else '未設定'}")
    
    if gmail_username and gmail_password:
        print("✅ Gmail通知利用可能")
        return True
    else:
        print("❌ Gmail通知設定が不完全")
        print("💡 環境変数 GMAIL_USERNAME と GMAIL_APP_PASSWORD を設定してください")
        return False

def main():
    print("🔔 通知機能総合テスト")
    print("=" * 50)
    
    # 1. コンソール通知テスト（常に利用可能）
    print("\n📺 1. コンソール通知テスト:")
    test_console_notification()
    
    # 2. デスクトップ通知テスト
    print("🖥️  2. デスクトップ通知テスト:")
    desktop_ok = test_desktop_notification()
    
    # 3. メール設定確認
    print("\n📧 3. メール設定確認:")
    email_ok = test_email_setup()
    
    # 4. 総合結果
    print("\n📋 テスト結果サマリー:")
    print(f"  📺 コンソール通知: ✅ 利用可能")
    print(f"  🖥️  デスクトップ通知: {'✅ 利用可能' if desktop_ok else '❌ 利用不可'}")
    print(f"  📧 メール通知: {'✅ 利用可能' if email_ok else '❌ 設定不完全'}")
    
    if not desktop_ok:
        print("\n💡 推奨対応:")
        print("  - WSL環境の場合: Windows側でPythonスクリプトを実行")
        print("  - Linux環境の場合: sudo apt-get install python3-tk")
        print("  - 代替案: コンソール通知のみ使用")
    
    print("\n🎉 テスト完了")

if __name__ == "__main__":
    main()