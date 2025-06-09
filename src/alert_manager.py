import smtplib
import json
import os
import tkinter as tk
from tkinter import messagebox
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, List
import threading

from stock_monitor import Alert


class AlertManager:
    """アラート通知管理クラス"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config = self.load_config(config_path)
        self.notification_methods = {
            'desktop': self._send_desktop_notification,
            'email': self._send_email_notification,
            'console': self._send_console_notification
        }
    
    def load_config(self, config_path: str) -> Dict:
        """設定ファイルをロード"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return {
                'notifications': {
                    'email': {'enabled': False},
                    'desktop': {'enabled': True},
                    'console': {'enabled': True}
                }
            }
    
    def send_alert(self, alert: Alert):
        """アラートを各通知方法で送信"""
        notifications_config = self.config.get('notifications', {})
        
        # デスクトップ通知（メインスレッドで実行）
        if notifications_config.get('desktop', {}).get('enabled', True):
            self.notification_methods['desktop'](alert)
        
        # メール通知
        email_config = notifications_config.get('email', {})
        if email_config.get('enabled', False):
            threading.Thread(
                target=self.notification_methods['email'], 
                args=(alert,), 
                daemon=True
            ).start()
        
        # コンソール通知
        if notifications_config.get('console', {}).get('enabled', True):
            self.notification_methods['console'](alert)
    
    def _send_desktop_notification(self, alert: Alert):
        """デスクトップ通知を送信（シンプル版）"""
        try:
            # アラートタイプに応じたアイコンとタイトル
            alert_icons = {
                'buy': ('💰 買い推奨アラート', 'info'),
                'sell_profit': ('✅ 利益確定アラート', 'info'), 
                'sell_loss': ('⚠️ 損切りアラート', 'warning'),
                'test': ('🧪 テストアラート', 'info')
            }
            
            title, icon = alert_icons.get(alert.alert_type, ('📊 株価アラート', 'info'))
            
            # メッセージ整形
            message = alert.message.replace('\\n', '\n')
            
            # 直接メッセージボックスを表示（シンプル）
            if icon == "warning":
                messagebox.showwarning(title, message)
            else:
                messagebox.showinfo(title, message)
            
        except Exception as e:
            print(f"デスクトップ通知エラー: {e}")
    
    def _send_email_notification(self, alert: Alert):
        """メール通知を送信"""
        try:
            email_config = self.config['notifications']['email']
            
            # SMTP設定（環境変数を優先）
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            username = os.getenv('GMAIL_USERNAME') or email_config.get('username', '')
            password = os.getenv('GMAIL_APP_PASSWORD') or email_config.get('password', '')
            recipients = email_config.get('recipients', [])
            
            if not all([username, password, recipients]):
                print("メール設定が不完全です。環境変数GMAIL_USERNAMEとGMAIL_APP_PASSWORDを設定してください。")
                return
            
            # メール作成
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = ', '.join(recipients)
            
            # 件名
            if alert.alert_type == 'buy':
                subject = f"【買い推奨】{alert.symbol}"
            elif alert.alert_type == 'sell_profit':
                subject = f"【利益確定】{alert.symbol}"
            elif alert.alert_type == 'sell_loss':
                subject = f"【損切り】{alert.symbol}"
            else:
                subject = f"【株価アラート】{alert.symbol}"
            
            msg['Subject'] = subject
            
            # 本文
            body = f"""
株価アラート通知

銘柄: {alert.symbol}
アラート種別: {alert.alert_type}
発火価格: ¥{alert.triggered_price:,.0f}
戦略: {alert.strategy_name}
発生時刻: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

詳細:
{alert.message.replace('\\n', '\n')}

---
日本株ウォッチドッグより自動送信
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # メール送信
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            print(f"メール送信完了: {subject}")
            
        except Exception as e:
            print(f"メール送信エラー: {e}")
    
    def _send_console_notification(self, alert: Alert):
        """コンソール通知を送信"""
        try:
            timestamp = alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            # アラートタイプに応じたプレフィックス
            if alert.alert_type == 'buy':
                prefix = "🔵 BUY"
            elif alert.alert_type == 'sell_profit':
                prefix = "🟢 SELL (利益確定)"
            elif alert.alert_type == 'sell_loss':
                prefix = "🔴 SELL (損切り)"
            else:
                prefix = "⚪ ALERT"
            
            print(f"\n{'='*50}")
            print(f"{prefix} ALERT - {timestamp}")
            print(f"{'='*50}")
            print(f"銘柄: {alert.symbol}")
            print(f"価格: ¥{alert.triggered_price:,.0f}")
            print(f"戦略: {alert.strategy_name}")
            print("-" * 50)
            print(alert.message.replace('\\n', '\n'))
            print(f"{'='*50}\n")
            
        except Exception as e:
            print(f"コンソール通知エラー: {e}")
    
    def send_daily_report(self, portfolio_summary: Dict, recent_alerts: List[Dict]):
        """日次レポートを送信"""
        try:
            # レポート作成
            report = self._create_daily_report(portfolio_summary, recent_alerts)
            
            # 疑似アラートオブジェクトを作成
            report_alert = Alert(
                symbol="DAILY_REPORT",
                alert_type="report",
                message=report,
                triggered_price=0,
                strategy_name="daily_report",
                timestamp=datetime.now()
            )
            
            # コンソールとメールで送信
            self._send_console_notification(report_alert)
            
            email_config = self.config.get('notifications', {}).get('email', {})
            if email_config.get('enabled', False):
                self._send_email_daily_report(report, portfolio_summary)
            
        except Exception as e:
            print(f"日次レポート送信エラー: {e}")
    
    def _create_daily_report(self, portfolio_summary: Dict, recent_alerts: List[Dict]) -> str:
        """日次レポートを作成"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""
【日次レポート】{today}

=== ポートフォリオサマリー ===
銘柄数: {portfolio_summary.get('total_stocks', 0)}
取得金額: ¥{portfolio_summary.get('total_acquisition', 0):,.0f}
評価金額: ¥{portfolio_summary.get('total_market_value', 0):,.0f}
損益: ¥{portfolio_summary.get('total_profit_loss', 0):+,.0f}
収益率: {portfolio_summary.get('return_rate', 0):+.2f}%

=== 本日のアラート ===
"""
        
        if recent_alerts:
            for alert in recent_alerts[-10:]:  # 最新10件
                alert_time = alert.get('created_at', '')
                report += f"• {alert.get('symbol', '')} ({alert.get('alert_type', '')}): {alert.get('message', '')[:50]}...\n"
        else:
            report += "本日のアラートはありません\n"
        
        return report
    
    def _send_email_daily_report(self, report: str, portfolio_summary: Dict):
        """日次レポートをメールで送信"""
        try:
            email_config = self.config['notifications']['email']
            
            # SMTP設定（環境変数を優先）
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            username = os.getenv('GMAIL_USERNAME') or email_config.get('username', '')
            password = os.getenv('GMAIL_APP_PASSWORD') or email_config.get('password', '')
            recipients = email_config.get('recipients', [])
            
            if not all([username, password, recipients]):
                return
            
            # メール作成
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = ', '.join(recipients)
            
            today = datetime.now().strftime('%Y-%m-%d')
            profit_loss = portfolio_summary.get('total_profit_loss', 0)
            profit_emoji = "📈" if profit_loss >= 0 else "📉"
            
            msg['Subject'] = f"{profit_emoji} 日次レポート {today} (損益: ¥{profit_loss:+,.0f})"
            
            # HTML形式の本文
            html_body = f"""
<html>
<body>
<h2>📊 日本株ウォッチドッグ 日次レポート</h2>
<p><strong>日付:</strong> {today}</p>

<h3>💼 ポートフォリオサマリー</h3>
<table border="1" style="border-collapse: collapse;">
<tr><td><strong>銘柄数</strong></td><td>{portfolio_summary.get('total_stocks', 0)}</td></tr>
<tr><td><strong>取得金額</strong></td><td>¥{portfolio_summary.get('total_acquisition', 0):,.0f}</td></tr>
<tr><td><strong>評価金額</strong></td><td>¥{portfolio_summary.get('total_market_value', 0):,.0f}</td></tr>
<tr><td><strong>損益</strong></td><td style="color: {'green' if profit_loss >= 0 else 'red'}">¥{profit_loss:+,.0f}</td></tr>
<tr><td><strong>収益率</strong></td><td style="color: {'green' if profit_loss >= 0 else 'red'}">{portfolio_summary.get('return_rate', 0):+.2f}%</td></tr>
</table>

<h3>🔔 アラート情報</h3>
<pre>{report.split('=== 本日のアラート ===')[1] if '=== 本日のアラート ===' in report else '本日のアラートはありません'}</pre>

<hr>
<p><small>このメールは日本株ウォッチドッグより自動送信されました</small></p>
</body>
</html>
"""
            
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # メール送信
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            print(f"日次レポートメール送信完了: {today}")
            
        except Exception as e:
            print(f"日次レポートメール送信エラー: {e}")
    
    def test_notifications(self):
        """通知機能のテスト"""
        test_alert = Alert(
            symbol="TEST",
            alert_type="buy",
            message="これはテスト通知です\\n通知機能が正常に動作しています",
            triggered_price=1000,
            strategy_name="test_strategy",
            timestamp=datetime.now()
        )
        
        print("通知機能をテストしています...")
        self.send_alert(test_alert)
        print("テスト完了")


if __name__ == "__main__":
    # テスト用
    alert_manager = AlertManager()
    
    # 通知テスト
    alert_manager.test_notifications()