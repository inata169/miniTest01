#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知設定セットアップスクリプト（Python版）
"""

import json
import os
import sys
import shutil

def main():
    print("通知設定セットアップ")
    print()
    
    print("通知方法を選択してください:")
    print("1. デスクトップ通知のみ（パスワード不要）")
    print("2. Gmail + デスクトップ通知（アプリパスワード必要）")
    print()
    
    while True:
        choice = input("選択 (1 または 2): ").strip()
        
        if choice == "1":
            setup_desktop_only()
            break
        elif choice == "2":
            setup_gmail_and_desktop()
            break
        else:
            print("無効な選択です。1 または 2 を入力してください。")
            continue
    
    print()
    test_choice = input("通知設定テストを実行しますか？ (y/n): ").strip().lower()
    
    if test_choice in ['y', 'yes']:
        print()
        print("通知テストを実行中...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, "src/alert_manager.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("テスト完了")
            else:
                print(f"テスト実行でエラーが発生しました: {result.stderr}")
        except Exception as e:
            print(f"テスト実行エラー: {e}")
    
    print()
    print("セットアップ完了！")
    input("Enterキーを押して終了...")

def setup_desktop_only():
    """デスクトップ通知のみの設定"""
    print()
    print("デスクトップ通知のみを設定します...")
    
    desktop_config = "config/settings_desktop_only.json"
    target_config = "config/settings.json"
    
    if os.path.exists(desktop_config):
        shutil.copy2(desktop_config, target_config)
        print("設定完了: デスクトップポップアップとコンソール表示のみ")
        print("パスワード設定は不要です。")
    else:
        print(f"エラー: {desktop_config} が見つかりません")

def setup_gmail_and_desktop():
    """Gmail + デスクトップ通知の設定"""
    print()
    print("Gmail + デスクトップ通知を設定します...")
    print()
    print("1. Gmailでアプリパスワードを作成してください:")
    print("   - https://myaccount.google.com/apppasswords")
    print("   - 2段階認証が有効である必要があります")
    print()
    
    gmail_user = input("Gmailアドレスを入力: ").strip()
    gmail_pass = input("アプリパスワード(16文字)を入力: ").strip()
    recipient = input("通知先メールアドレスを入力: ").strip()
    
    print()
    print("環境変数を設定中...")
    
    # Windows環境変数設定
    if os.name == 'nt':
        os.system(f'setx GMAIL_USERNAME "{gmail_user}" >nul 2>&1')
        os.system(f'setx GMAIL_APP_PASSWORD "{gmail_pass}" >nul 2>&1')
    else:
        # Unix/Linux環境
        bashrc_path = os.path.expanduser("~/.bashrc")
        with open(bashrc_path, "a") as f:
            f.write(f'\nexport GMAIL_USERNAME="{gmail_user}"\n')
            f.write(f'export GMAIL_APP_PASSWORD="{gmail_pass}"\n')
    
    print("設定ファイルを更新中...")
    try:
        config_path = "config/settings.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['notifications']['email']['enabled'] = True
        data['notifications']['email']['recipients'] = [recipient]
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("設定ファイル更新完了")
        print()
        print("環境変数とメール設定が完了しました。")
        print("PCを再起動するか、新しいコマンドプロンプトを開いてください。")
        
    except Exception as e:
        print(f"設定ファイル更新エラー: {e}")

if __name__ == "__main__":
    main()