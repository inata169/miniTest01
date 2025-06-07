import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from data_sources import YahooFinanceDataSource, StockInfo
from database import DatabaseManager


@dataclass
class Strategy:
    """投資戦略データクラス"""
    name: str
    buy_conditions: Dict
    sell_conditions: Dict


@dataclass
class Alert:
    """アラートデータクラス"""
    symbol: str
    alert_type: str
    message: str
    triggered_price: float
    strategy_name: str
    timestamp: datetime


class StockMonitor:
    """株価監視クラス"""
    
    def __init__(self, config_path: str = "config/strategies.json"):
        self.data_source = YahooFinanceDataSource()
        self.db = DatabaseManager()
        self.strategies = self.load_strategies(config_path)
        
        self.monitoring = False
        self.monitor_thread = None
        self.check_interval = 1800  # 30分間隔
        
        # コールバック関数
        self.alert_callbacks: List[Callable] = []
        
        # 最後のアラート時刻を記録（重複防止）
        self.last_alerts = {}
    
    def load_strategies(self, config_path: str) -> Dict[str, Strategy]:
        """戦略設定をロード"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            strategies = {}
            for name, data in config.items():
                strategies[name] = Strategy(
                    name=name,
                    buy_conditions=data.get('buy_conditions', {}),
                    sell_conditions=data.get('sell_conditions', {})
                )
            
            return strategies
            
        except Exception as e:
            print(f"戦略設定読み込みエラー: {e}")
            return {}
    
    def add_alert_callback(self, callback: Callable):
        """アラートコールバック関数を追加"""
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self):
        """監視開始"""
        if self.monitoring:
            print("既に監視中です")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("株価監視を開始しました")
    
    def stop_monitoring(self):
        """監視停止"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("株価監視を停止しました")
    
    def _monitor_loop(self):
        """監視メインループ"""
        while self.monitoring:
            try:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 株価チェック開始")
                
                # 市場開場時間チェック
                if not self.data_source.is_market_open():
                    print("市場クローズ中 - 次回チェックまで待機")
                    time.sleep(self.check_interval)
                    continue
                
                # 保有銘柄をチェック
                self._check_holdings()
                
                # 監視銘柄をチェック
                self._check_watchlist()
                
                print("株価チェック完了 - 次回チェックまで待機")
                
            except Exception as e:
                print(f"監視エラー: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_holdings(self):
        """保有銘柄の売り条件チェック"""
        holdings = self.db.get_all_holdings()
        
        for holding in holdings:
            symbol = holding['symbol']
            
            # 株価情報取得
            stock_info = self.data_source.get_stock_info(symbol)
            if not stock_info:
                continue
            
            # 株価履歴保存
            self.db.save_price_history(symbol, stock_info)
            
            # 戦略に基づく売り判定
            for strategy_name, strategy in self.strategies.items():
                sell_alert = self._check_sell_conditions(holding, stock_info, strategy)
                if sell_alert:
                    self._trigger_alert(sell_alert)
    
    def _check_watchlist(self):
        """監視銘柄の買い条件チェック"""
        watchlist = self.db.get_watchlist()
        
        for item in watchlist:
            symbol = item['symbol']
            strategy_name = item['strategy_name']
            
            if strategy_name not in self.strategies:
                continue
            
            strategy = self.strategies[strategy_name]
            
            # 株価情報取得
            stock_info = self.data_source.get_stock_info(symbol)
            if not stock_info:
                continue
            
            # 配当情報取得
            dividend_info = self.data_source.get_dividend_info(symbol)
            
            # 買い条件チェック
            buy_alert = self._check_buy_conditions(stock_info, dividend_info, strategy)
            if buy_alert:
                self._trigger_alert(buy_alert)
    
    def _check_buy_conditions(self, stock_info: StockInfo, dividend_info: Dict, strategy: Strategy) -> Optional[Alert]:
        """買い条件をチェック"""
        conditions = strategy.buy_conditions
        reasons = []
        
        # 配当利回りチェック
        min_dividend_yield = conditions.get('dividend_yield_min', 0)
        current_dividend_yield = dividend_info.get('dividend_yield', 0)
        if current_dividend_yield >= min_dividend_yield:
            reasons.append(f"配当利回り {current_dividend_yield:.2f}% >= {min_dividend_yield}%")
        elif min_dividend_yield > 0:
            return None  # 配当利回り条件を満たさない
        
        # PER チェック
        max_per = conditions.get('per_max', float('inf'))
        current_per = stock_info.pe_ratio or 0
        if current_per > 0 and current_per <= max_per:
            reasons.append(f"PER {current_per:.1f} <= {max_per}")
        elif max_per < float('inf') and current_per > max_per:
            return None  # PER条件を満たさない
        
        # PBR チェック
        max_pbr = conditions.get('pbr_max', float('inf'))
        current_pbr = stock_info.pb_ratio or 0
        if current_pbr > 0 and current_pbr <= max_pbr:
            reasons.append(f"PBR {current_pbr:.1f} <= {max_pbr}")
        elif max_pbr < float('inf') and current_pbr > max_pbr:
            return None  # PBR条件を満たさない
        
        # アラートが既に最近発生していないかチェック
        alert_key = f"{stock_info.symbol}_buy_{strategy.name}"
        if self._is_recent_alert(alert_key):
            return None
        
        if reasons:
            message = f"【買い推奨】{stock_info.name} ({stock_info.symbol})\\n" + \
                     f"現在価格: ¥{stock_info.current_price:,.0f}\\n" + \
                     f"理由: {', '.join(reasons)}"
            
            return Alert(
                symbol=stock_info.symbol,
                alert_type='buy',
                message=message,
                triggered_price=stock_info.current_price,
                strategy_name=strategy.name,
                timestamp=datetime.now()
            )
        
        return None
    
    def _check_sell_conditions(self, holding: Dict, stock_info: StockInfo, strategy: Strategy) -> Optional[Alert]:
        """売り条件をチェック"""
        conditions = strategy.sell_conditions
        
        avg_cost = holding['average_cost']
        current_price = stock_info.current_price
        return_rate = ((current_price / avg_cost) - 1) * 100 if avg_cost > 0 else 0
        
        # 利益確定チェック
        profit_target = conditions.get('profit_target', float('inf'))
        if return_rate >= profit_target:
            # アラートが既に最近発生していないかチェック
            alert_key = f"{stock_info.symbol}_sell_profit_{strategy.name}"
            if not self._is_recent_alert(alert_key):
                message = f"【利益確定推奨】{stock_info.name} ({stock_info.symbol})\\n" + \
                         f"現在価格: ¥{current_price:,.0f}\\n" + \
                         f"収益率: {return_rate:+.2f}% (目標: {profit_target}%)"
                
                return Alert(
                    symbol=stock_info.symbol,
                    alert_type='sell_profit',
                    message=message,
                    triggered_price=current_price,
                    strategy_name=strategy.name,
                    timestamp=datetime.now()
                )
        
        # 損切りチェック
        stop_loss = conditions.get('stop_loss', float('-inf'))
        if return_rate <= stop_loss:
            # アラートが既に最近発生していないかチェック
            alert_key = f"{stock_info.symbol}_sell_loss_{strategy.name}"
            if not self._is_recent_alert(alert_key):
                message = f"【損切り推奨】{stock_info.name} ({stock_info.symbol})\\n" + \
                         f"現在価格: ¥{current_price:,.0f}\\n" + \
                         f"収益率: {return_rate:+.2f}% (損切りライン: {stop_loss}%)"
                
                return Alert(
                    symbol=stock_info.symbol,
                    alert_type='sell_loss',
                    message=message,
                    triggered_price=current_price,
                    strategy_name=strategy.name,
                    timestamp=datetime.now()
                )
        
        return None
    
    def _is_recent_alert(self, alert_key: str, hours: int = 24) -> bool:
        """最近同じアラートが発生していないかチェック"""
        if alert_key in self.last_alerts:
            last_time = self.last_alerts[alert_key]
            if datetime.now() - last_time < timedelta(hours=hours):
                return True
        return False
    
    def _trigger_alert(self, alert: Alert):
        """アラートを発火"""
        # データベースに記録
        self.db.log_alert(
            alert.symbol, 
            alert.alert_type, 
            alert.message, 
            alert.triggered_price, 
            alert.strategy_name
        )
        
        # 重複防止のため記録
        alert_key = f"{alert.symbol}_{alert.alert_type}_{alert.strategy_name}"
        self.last_alerts[alert_key] = alert.timestamp
        
        # コールバック関数を呼び出し
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"アラートコールバックエラー: {e}")
        
        print(f"[ALERT] {alert.message}")
    
    def add_stock_to_watchlist(self, symbol: str, name: str, strategy_name: str = "default_strategy"):
        """監視銘柄に追加"""
        if strategy_name not in self.strategies:
            raise ValueError(f"不明な戦略: {strategy_name}")
        
        success = self.db.add_to_watchlist(symbol, name, strategy_name)
        if success:
            print(f"監視銘柄に追加: {symbol} ({name}) - 戦略: {strategy_name}")
        else:
            print(f"監視銘柄追加エラー: {symbol}")
        
        return success
    
    def get_monitoring_status(self) -> Dict:
        """監視状況を取得"""
        return {
            'is_monitoring': self.monitoring,
            'check_interval_minutes': self.check_interval // 60,
            'market_open': self.data_source.is_market_open(),
            'strategies_count': len(self.strategies),
            'watchlist_count': len(self.db.get_watchlist()),
            'holdings_count': len(self.db.get_all_holdings())
        }


if __name__ == "__main__":
    # テスト用
    monitor = StockMonitor()
    
    # アラートコールバック設定
    def print_alert(alert: Alert):
        print(f"★ {alert.alert_type.upper()}: {alert.message}")
    
    monitor.add_alert_callback(print_alert)
    
    # 監視状況表示
    status = monitor.get_monitoring_status()
    print("=== 監視設定 ===")
    for key, value in status.items():
        print(f"{key}: {value}")
    
    # テスト用監視銘柄追加
    # monitor.add_stock_to_watchlist("7203", "トヨタ自動車", "default_strategy")
    
    print("\\n監視を開始します（Ctrl+Cで停止）")
    try:
        monitor.start_monitoring()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n監視を停止します...")
        monitor.stop_monitoring()