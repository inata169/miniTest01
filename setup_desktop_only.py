#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
デスクトップ通知のみセットアップ（自動実行版）
"""

import json
import os
import shutil
import sys

def setup_desktop_only():
    """デスクトップ通知のみの設定"""
    print("デスクトップ通知のみを設定します...")
    
    desktop_config = "config/settings_desktop_only.json"
    target_config = "config/settings.json"
    
    if os.path.exists(desktop_config):
        shutil.copy2(desktop_config, target_config)
        print("✅ 設定完了: デスクトップポップアップとコンソール表示のみ")
        print("✅ パスワード設定は不要です。")
        
        # 設定内容を確認表示
        with open(target_config, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n📋 設定内容:")
        notifications = data.get('notifications', {})
        print(f"  📧 メール通知: {'有効' if notifications.get('email', {}).get('enabled') else '無効'}")
        print(f"  🖥️  デスクトップ通知: {'有効' if notifications.get('desktop', {}).get('enabled') else '無効'}")
        print(f"  📺 コンソール通知: {'有効' if notifications.get('console', {}).get('enabled') else '無効'}")
        
        return True
    else:
        print(f"❌ エラー: {desktop_config} が見つかりません")
        return False

def main():
    print("🔔 通知設定セットアップ（デスクトップのみ）")
    print("=" * 50)
    
    if setup_desktop_only():
        print("\n🎉 セットアップ完了！")
        print("\n📌 使用方法:")
        print("  python src/alert_manager.py  # 通知テスト")
        print("  python src/main.py           # メインアプリ起動")
    else:
        print("\n❌ セットアップに失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main()