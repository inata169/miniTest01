#!/usr/bin/env python3
"""
日本株ウォッチドッグ メインアプリケーション
Japanese Stock Watchdog Main Application
"""

import argparse
import sys
import os
import signal
import time
from datetime import datetime

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock_monitor import StockMonitor
from alert_manager import AlertManager
from database import DatabaseManager
from data_sources import YahooFinanceDataSource
import json
import os
from dotenv import load_dotenv


class WatchdogApp:
    """メインアプリケーションクラス"""
    
    def __init__(self):
        # .envファイルを読み込み
        load_dotenv()
        
        # J Quants API認証情報を環境変数から取得
        jquants_email, jquants_password, refresh_token = self._load_jquants_config()
        
        self.monitor = StockMonitor(jquants_email=jquants_email, jquants_password=jquants_password, refresh_token=refresh_token)
        self.alert_manager = AlertManager()
        self.db = DatabaseManager()
        self.data_source = YahooFinanceDataSource()
    
    def _load_jquants_config(self):
        """J Quants API設定を.envファイルまたはJSON設定ファイルから読み込み"""
        # Method 1: 環境変数から取得（推奨）
        refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
        email = os.getenv('JQUANTS_EMAIL')
        password = os.getenv('JQUANTS_PASSWORD')
        
        if refresh_token or (email and password):
            print("J Quants API認証情報を環境変数から読み込みました")
            return email, password, refresh_token
        
        # Method 2: JSON設定ファイルから取得（後方互換性）
        config_path = "config/jquants_config.json"
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print("J Quants API認証情報をJSONファイルから読み込みました")
                    return config.get('email'), config.get('password'), config.get('refresh_token')
        except Exception as e:
            print(f"J Quants設定読み込みエラー: {e}")
        
        print("J Quants API認証情報が見つかりません。Yahoo Financeをフォールバックとして使用します。")
        return None, None, None
        
        # アラートコールバック設定
        self.monitor.add_alert_callback(self.alert_manager.send_alert)
        
        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """シグナルハンドラー（Ctrl+C対応）"""
        print(f"\n終了シグナル受信 ({signum})")
        self.stop()
        sys.exit(0)
    
    def start_daemon(self):
        """デーモンモードで監視開始"""
        print("="*50)
        print("日本株ウォッチドッグ - デーモンモード")
        print("="*50)
        
        # 初期状態表示
        self.show_status()
        
        # 監視開始
        self.monitor.start_monitoring()
        
        try:
            print("\n監視を開始しました。Ctrl+C で停止します。")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def start_interactive(self):
        """インタラクティブモード"""
        print("="*50)
        print("日本株ウォッチドッグ - インタラクティブモード")
        print("="*50)
        
        while True:
            self.show_menu()
            choice = input("\n選択してください (1-9): ").strip()
            
            if choice == '1':
                self.show_status()
            elif choice == '2':
                self.show_portfolio()
            elif choice == '3':
                self.update_prices()
            elif choice == '4':
                self.add_watchlist_stock()
            elif choice == '5':
                self.show_alerts()
            elif choice == '6':
                self.start_monitoring_interactive()
            elif choice == '7':
                self.stop_monitoring()
            elif choice == '8':
                self.test_notifications()
            elif choice == '9':
                print("アプリケーションを終了します")
                self.stop()
                break
            else:
                print("無効な選択です")
            
            input("\nEnterキーで続行...")
    
    def show_menu(self):
        """メニュー表示"""
        print("\n" + "="*30)
        print("メニュー")
        print("="*30)
        print("1. ステータス表示")
        print("2. ポートフォリオ表示")
        print("3. 株価更新")
        print("4. 監視銘柄追加")
        print("5. アラート履歴")
        print("6. 監視開始")
        print("7. 監視停止")
        print("8. 通知テスト")
        print("9. 終了")
    
    def show_status(self):
        """ステータス表示"""
        print("\n" + "="*30)
        print("システム状況")
        print("="*30)
        
        # 監視状況
        status = self.monitor.get_monitoring_status()
        print(f"監視状態: {'実行中' if status['is_monitoring'] else '停止中'}")
        print(f"チェック間隔: {status['check_interval_minutes']} 分")
        print(f"市場状況: {'開場中' if status['market_open'] else 'クローズ'}")
        print(f"戦略数: {status['strategies_count']}")
        print(f"監視銘柄数: {status['watchlist_count']}")
        print(f"保有銘柄数: {status['holdings_count']}")
        
        # ポートフォリオサマリー
        summary = self.db.get_portfolio_summary()
        if summary['total_stocks'] > 0:
            print(f"\nポートフォリオ:")
            print(f"  評価金額: ¥{summary['total_market_value']:,.0f}")
            print(f"  損益: ¥{summary['total_profit_loss']:+,.0f}")
            print(f"  収益率: {summary['return_rate']:+.2f}%")
    
    def show_portfolio(self):
        """ポートフォリオ表示"""
        print("\n" + "="*50)
        print("ポートフォリオ")
        print("="*50)
        
        holdings = self.db.get_all_holdings()
        
        if not holdings:
            print("保有銘柄がありません")
            return
        
        # ヘッダー
        print(f"{'銘柄コード':<8} {'銘柄名':<15} {'保有数':<8} {'平均取得':<10} {'現在価格':<10} {'損益':<12} {'収益率':<8}")
        print("-" * 80)
        
        # 銘柄一覧
        for holding in holdings:
            return_rate = ((holding['market_value'] / holding['acquisition_amount']) - 1) * 100 if holding['acquisition_amount'] > 0 else 0
            profit_loss = holding['profit_loss']
            
            # 収益率の色分け用記号
            symbol_prefix = "📈" if profit_loss > 0 else "📉" if profit_loss < 0 else "➖"
            
            print(f"{holding['symbol']:<8} {holding['name'][:15]:<15} {holding['quantity']:<8,} "
                  f"¥{holding['average_cost']:<9,.0f} ¥{holding['current_price']:<9,.0f} "
                  f"{symbol_prefix}¥{profit_loss:<10,.0f} {return_rate:+6.2f}%")
    
    def update_prices(self):
        """株価更新"""
        print("\n株価情報を更新中...")
        
        holdings = self.db.get_all_holdings()
        symbols = [h['symbol'] for h in holdings]
        
        if not symbols:
            print("更新する銘柄がありません")
            return
        
        price_updates = {}
        updated_count = 0
        
        for symbol in symbols:
            print(f"  {symbol} を取得中...", end=" ")
            stock_info = self.data_source.get_stock_info(symbol)
            if stock_info:
                price_updates[symbol] = stock_info.current_price
                print(f"¥{stock_info.current_price:,.0f}")
                updated_count += 1
            else:
                print("取得失敗")
        
        if price_updates:
            self.db.update_current_prices(price_updates)
            print(f"\n{updated_count} 銘柄の株価を更新しました")
        else:
            print("\n株価情報を取得できませんでした")
    
    def add_watchlist_stock(self):
        """監視銘柄追加"""
        print("\n" + "="*30)
        print("監視銘柄追加")
        print("="*30)
        
        symbol = input("銘柄コード (例: 7203): ").strip()
        if not symbol:
            print("銘柄コードが入力されていません")
            return
        
        # 銘柄情報取得
        print(f"{symbol} の情報を取得中...")
        stock_info = self.data_source.get_stock_info(symbol)
        if not stock_info:
            print("銘柄情報を取得できませんでした")
            return
        
        print(f"銘柄名: {stock_info.name}")
        print(f"現在価格: ¥{stock_info.current_price:,.0f}")
        
        # 戦略選択
        strategies = list(self.monitor.strategies.keys())
        print(f"\n戦略を選択してください:")
        for i, strategy in enumerate(strategies, 1):
            print(f"{i}. {strategy}")
        
        try:
            choice = int(input("選択 (番号): ").strip())
            if 1 <= choice <= len(strategies):
                strategy_name = strategies[choice - 1]
            else:
                print("無効な選択です")
                return
        except ValueError:
            print("無効な入力です")
            return
        
        # 監視銘柄に追加
        success = self.monitor.add_stock_to_watchlist(symbol, stock_info.name, strategy_name)
        if success:
            print(f"\n{symbol} ({stock_info.name}) を監視銘柄に追加しました")
            print(f"戦略: {strategy_name}")
        else:
            print("監視銘柄の追加に失敗しました")
    
    def show_alerts(self):
        """アラート履歴表示"""
        print("\n" + "="*50)
        print("アラート履歴 (最新10件)")
        print("="*50)
        
        alerts = self.db.get_alerts(10)
        
        if not alerts:
            print("アラート履歴がありません")
            return
        
        for alert in alerts:
            timestamp = alert['created_at']
            alert_type_map = {
                'buy': '買い推奨',
                'sell_profit': '利益確定',
                'sell_loss': '損切り'
            }
            alert_type_str = alert_type_map.get(alert['alert_type'], alert['alert_type'])
            
            print(f"[{timestamp}] {alert['symbol']} - {alert_type_str}")
            print(f"  {alert['message'][:100]}...")
            print()
    
    def start_monitoring_interactive(self):
        """インタラクティブモードで監視開始"""
        if self.monitor.monitoring:
            print("既に監視中です")
            return
        
        print("監視を開始します...")
        self.monitor.start_monitoring()
        print("監視が開始されました")
    
    def stop_monitoring(self):
        """監視停止"""
        if not self.monitor.monitoring:
            print("監視は実行されていません")
            return
        
        print("監視を停止します...")
        self.monitor.stop_monitoring()
        print("監視が停止されました")
    
    def test_notifications(self):
        """通知テスト"""
        print("通知機能をテストします...")
        self.alert_manager.test_notifications()
    
    def stop(self):
        """アプリケーション停止"""
        self.monitor.stop_monitoring()
        print("アプリケーションを終了しました")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="日本株ウォッチドッグ")
    parser.add_argument('--daemon', action='store_true', help='デーモンモードで実行')
    parser.add_argument('--gui', action='store_true', help='GUIモードで実行')
    
    args = parser.parse_args()
    
    if args.gui:
        # GUIモード
        try:
            from gui.main_window import MainWindow
            app = MainWindow()
            app.run()
        except ImportError as e:
            print(f"GUIモジュールの読み込みエラー: {e}")
            print("src/gui/main_window.py が存在することを確認してください")
    elif args.daemon:
        # デーモンモード
        app = WatchdogApp()
        app.start_daemon()
    else:
        # インタラクティブモード
        app = WatchdogApp()
        app.start_interactive()


if __name__ == "__main__":
    main()