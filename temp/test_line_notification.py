#!/usr/bin/env python3
"""
LINE通知機能テスト
"""

import os
import sys
from datetime import datetime

# 親ディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from alert_manager import AlertManager
from stock_monitor import Alert


def main():
    """LINE通知テストのメイン関数"""
    print("="*50)
    print("LINE通知機能テスト")
    print("="*50)
    
    # AlertManager初期化
    alert_manager = AlertManager()
    
    # 設定確認
    line_config = alert_manager.config.get('notifications', {}).get('line', {})
    line_token = os.getenv('LINE_NOTIFY_TOKEN') or line_config.get('token', '')
    
    print(f"LINE通知設定: {'有効' if line_config.get('enabled', False) else '無効'}")
    print(f"トークン設定: {'あり' if line_token else 'なし'}")
    print()
    
    if not line_token:
        print("❌ LINE Notifyトークンが設定されていません")
        print()
        print("設定方法:")
        print("1. https://notify-bot.line.me/ja/ にアクセス")
        print("2. LINEアカウントでログイン")
        print("3. 「マイページ」→ 「トークンを発行する」")
        print("4. トークン名を入力（例：日本株ウォッチドッグ）")
        print("5. 送信先を選択（1:1でLINE Notifyから送る、グループを選択、など）")
        print("6. 発行されたトークンを以下の方法で設定:")
        print()
        print("   方法1) 環境変数で設定（推奨）:")
        print("   export LINE_NOTIFY_TOKEN='発行されたトークン'")
        print()
        print("   方法2) 設定ファイルで設定:")
        print("   config/settings.json の line.token に設定")
        print("   config/settings.json の line.enabled を true に設定")
        print()
        return False
    
    if not line_config.get('enabled', False):
        print("❌ LINE通知が無効になっています")
        print("config/settings.json で以下を設定してください:")
        print('"line": {"enabled": true, "token": "..."}')
        print()
        return False
    
    # LINE通知専用テスト実行
    print("LINE通知テストを実行中...")
    success = alert_manager.test_line_notification()
    
    if success:
        print("✅ LINE通知テスト完了")
        print("LINEアプリで通知を確認してください")
    else:
        print("❌ LINE通知テストが失敗しました")
    
    print()
    print("="*50)
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)