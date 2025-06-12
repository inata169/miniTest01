#!/usr/bin/env python3
"""
Discord通知機能テスト
"""

import os
import sys
from datetime import datetime

# 親ディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from alert_manager import AlertManager
from stock_monitor import Alert


def main():
    """Discord通知テストのメイン関数"""
    print("="*50)
    print("Discord通知機能テスト")
    print("="*50)
    
    # AlertManager初期化
    alert_manager = AlertManager()
    
    # 設定確認
    discord_config = alert_manager.config.get('notifications', {}).get('discord', {})
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL') or discord_config.get('webhook_url', '')
    
    print(f"Discord通知設定: {'有効' if discord_config.get('enabled', False) else '無効'}")
    print(f"WebhookURL設定: {'あり' if webhook_url else 'なし'}")
    print()
    
    if not webhook_url:
        print("❌ Discord WebhookURLが設定されていません")
        print()
        print("設定方法:")
        print("1. Discordサーバーを作成（または既存サーバーを使用）")
        print("   - Discordアプリで「+」ボタン → 「サーバーを作成」")
        print("   - または既存のサーバーを使用")
        print()
        print("2. ウェブフックを作成")
        print("   - サーバー名をクリック → 「サーバー設定」")
        print("   - 「連携サービス」 → 「ウェブフック」")
        print("   - 「新しいウェブフック」をクリック")
        print()
        print("3. ウェブフック設定")
        print("   - 名前: 日本株ウォッチドッグ")
        print("   - チャンネル: 通知を受け取りたいチャンネルを選択")
        print("   - 「ウェブフックURLをコピー」をクリック")
        print()
        print("4. アプリに設定")
        print("   方法1) 環境変数で設定（推奨）:")
        print("   export DISCORD_WEBHOOK_URL='コピーしたWebhookURL'")
        print()
        print("   方法2) 設定ファイルで設定:")
        print("   config/settings.json の discord.webhook_url に設定")
        print("   config/settings.json の discord.enabled を true に設定")
        print()
        return False
    
    if not discord_config.get('enabled', False):
        print("❌ Discord通知が無効になっています")
        print("config/settings.json で以下を設定してください:")
        print('"discord": {"enabled": true, "webhook_url": "..."}')
        print()
        return False
    
    # Discord通知専用テスト実行
    print("Discord通知テストを実行中...")
    success = alert_manager.test_discord_notification()
    
    if success:
        print("✅ Discord通知テスト完了")
        print("Discordサーバーで通知を確認してください")
        print()
        print("通知の特徴:")
        print("- 📊 リッチなEmbed形式で表示")
        print("- 🎨 アラートタイプ別の色分け")
        print("- 📱 PC・スマホ両方で受信可能")
        print("- 🔔 プッシュ通知対応")
    else:
        print("❌ Discord通知テストが失敗しました")
    
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