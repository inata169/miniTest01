#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Toast通知テスト
"""

import subprocess
import sys
import os

def test_windows_toast():
    """Windows Toast通知のテスト"""
    try:
        # PowerShellを使ってWindows Toast通知を表示
        powershell_script = '''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.ShowBalloonTip(5000, "株価アラート", "テスト通知: これはWindows Toast通知です", [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Seconds 6
$notify.Dispose()
'''
        
        print("Windows Toast通知をテスト中...")
        result = subprocess.run(
            ["powershell", "-Command", powershell_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Windows Toast通知が送信されました")
            return True
        else:
            print(f"❌ PowerShellエラー: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Toast通知エラー: {e}")
        return False

def test_simple_dialog():
    """シンプルなダイアログテスト"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        print("ダイアログボックスをテスト中...")
        
        # メインウィンドウを作成
        root = tk.Tk()
        root.withdraw()  # メインウィンドウを隠す
        
        # 最前面に強制表示
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        
        # ダイアログを表示
        messagebox.showinfo(
            "株価アラート - テスト", 
            "🔔 テスト通知\n\n銘柄: TEST\n価格: ¥1,000\n\nこのダイアログが見えていれば成功です！"
        )
        
        root.destroy()
        print("✅ ダイアログテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ ダイアログエラー: {e}")
        return False

def test_console_beep():
    """コンソールビープ音テスト"""
    try:
        print("ビープ音テスト中... \a")  # \a はベル文字
        
        # Windowsの場合、追加のビープ音
        if os.name == 'nt':
            import winsound
            winsound.Beep(1000, 500)  # 1000Hz で 500ms
            print("✅ ビープ音テスト完了")
        
        return True
    except Exception as e:
        print(f"❌ ビープ音エラー: {e}")
        return False

def main():
    print("🔔 Windows通知システム総合テスト")
    print("=" * 50)
    
    # 1. 応答不可モード確認
    print("\n📱 1. 応答不可モード確認:")
    print("Windows設定で「応答不可」がオフになっているか確認してください")
    
    # 2. Toast通知テスト
    print("\n🎯 2. Windows Toast通知テスト:")
    toast_ok = test_windows_toast()
    
    # 3. ダイアログテスト
    print("\n💬 3. ダイアログボックステスト:")
    dialog_ok = test_simple_dialog()
    
    # 4. ビープ音テスト
    print("\n🔊 4. ビープ音テスト:")
    beep_ok = test_console_beep()
    
    # 結果サマリー
    print("\n📋 テスト結果:")
    print(f"  Toast通知: {'✅' if toast_ok else '❌'}")
    print(f"  ダイアログ: {'✅' if dialog_ok else '❌'}")
    print(f"  ビープ音: {'✅' if beep_ok else '❌'}")
    
    if not any([toast_ok, dialog_ok]):
        print("\n💡 推奨事項:")
        print("  1. Windows設定 → システム → 通知 → 応答不可をオフ")
        print("  2. ウイルス対策ソフトがポップアップをブロックしていないか確認")
        print("  3. Pythonを管理者権限で実行")
    
    input("\nEnterキーを押して終了...")

if __name__ == "__main__":
    main()