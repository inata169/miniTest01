import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from data_sources import YahooFinanceDataSource, MultiDataSource, StockInfo
from database import DatabaseManager
from logger import app_logger


@dataclass
class Strategy:
    """投資戦略データクラス"""
    name: str
    buy_conditions: Dict
    sell_conditions: Dict
    condition_mode: str = "any_two_of_three"  # any_two_of_three, weighted_score, strict_and, any_one
    min_score: float = 0.6  # weighted_score用の閾値
    weights: Dict = None  # 重み付け


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
    
    def __init__(self, config_path: str = "config/strategies.json", jquants_email: str = None, jquants_password: str = None, refresh_token: str = None):
        # マルチデータソースを使用（J Quants API優先、Yahoo Financeフォールバック）
        self.data_source = MultiDataSource(jquants_email, jquants_password, refresh_token)
        self.db = DatabaseManager()
        self.strategies = self.load_strategies(config_path)
        
        # 遅延初期化でAlertManagerを設定
        self.alert_manager = None
        self._initialize_alert_manager()
        
        self.monitoring = False
        self.monitor_thread = None
        self.check_interval = 1800  # 30分間隔
        
        # コールバック関数
        self.alert_callbacks: List[Callable] = []
        
        # 最後のアラート時刻を記録（重複防止）
        self.last_alerts = {}
    
    def _initialize_alert_manager(self):
        """AlertManagerを遅延初期化"""
        try:
            from alert_manager import AlertManager
            self.alert_manager = AlertManager()
        except Exception as e:
            app_logger.warning(f"AlertManager初期化に失敗: {e}")
            self.alert_manager = None
    
    def _get_default_strategies(self) -> Dict[str, Strategy]:
        """デフォルト戦略を返す"""
        return {
            "default_strategy": Strategy(
                name="default_strategy",
                buy_conditions={
                    "dividend_yield_min": 1.0,
                    "per_max": 40.0,
                    "pbr_max": 4.0
                },
                sell_conditions={
                    "profit_target": 8.0,
                    "stop_loss": -3.0
                }
            )
        }
    
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
                    sell_conditions=data.get('sell_conditions', {}),
                    condition_mode=data.get('condition_mode', 'any_two_of_three'),
                    min_score=data.get('min_score', 0.6),
                    weights=data.get('weights', {
                        'dividend_weight': 0.4,
                        'per_weight': 0.3,
                        'pbr_weight': 0.3
                    })
                )
            
            return strategies
            
        except FileNotFoundError:
            app_logger.error(f"設定ファイルが見つかりません: {config_path}")
            print(f"設定ファイルが見つかりません: {config_path}")
            return self._get_default_strategies()
        except json.JSONDecodeError as e:
            app_logger.error(f"設定ファイルのJSON形式が不正です: {e}")
            print(f"設定ファイルのJSON形式が不正です: {e}")
            return self._get_default_strategies()
        except Exception as e:
            app_logger.error(f"戦略設定読み込みエラー: {e}")
            print(f"戦略設定読み込みエラー: {e}")
            return self._get_default_strategies()
    
    def add_alert_callback(self, callback: Callable):
        """アラートコールバック関数を追加"""
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self):
        """監視開始"""
        if self.monitoring:
            app_logger.warning("既に監視中です")
            print("既に監視中です")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        app_logger.info("株価監視を開始しました")
        print("株価監視を開始しました")
    
    def stop_monitoring(self):
        """監視停止"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        app_logger.info("株価監視を停止しました")
        print("株価監視を停止しました")
    
    def _monitor_loop(self):
        """監視メインループ"""
        while self.monitoring:
            try:
                app_logger.info("株価チェック開始")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 株価チェック開始")
                
                # 市場開場時間チェック
                if not self.data_source.is_market_open():
                    app_logger.info("市場クローズ中 - 次回チェックまで待機")
                    print("市場クローズ中 - 次回チェックまで待機")
                    time.sleep(self.check_interval)
                    continue
                
                # 保有銘柄をチェック
                self._check_holdings()
                
                # 監視銘柄をチェック
                self._check_watchlist()
                
                app_logger.info("株価チェック完了 - 次回チェックまで待機")
                print("株価チェック完了 - 次回チェックまで待機")
                
            except Exception as e:
                app_logger.error(f"監視エラー: {e}")
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
        """監視銘柄の買い条件チェック（最適化版）"""
        watchlist = self.db.get_watchlist()
        
        if not watchlist:
            return
        
        # 監視銘柄のシンボルリストを作成
        symbols = [item['symbol'] for item in watchlist]
        
        # 一括で株価情報を取得（効率化）
        stock_infos = self.data_source.get_multiple_stocks(symbols)
        
        # 各銘柄をチェック
        for item in watchlist:
            symbol = item['symbol']
            strategy_name = item['strategy_name']
            
            if strategy_name not in self.strategies:
                continue
            
            if symbol not in stock_infos:
                continue
            
            strategy = self.strategies[strategy_name]
            stock_info = stock_infos[symbol]
            
            # 配当情報取得
            dividend_info = self.data_source.get_dividend_info(symbol)
            
            # 買い条件チェック
            buy_alert = self._check_buy_conditions(stock_info, dividend_info, strategy)
            if buy_alert:
                self._trigger_alert(buy_alert)
    
    def _check_buy_conditions(self, stock_info: StockInfo, dividend_info: Dict, strategy: Strategy) -> Optional[Alert]:
        """買い条件をチェック（高度な判定ロジック）"""
        conditions = strategy.buy_conditions
        reasons = []
        
        # 各条件の評価
        dividend_score, dividend_reason = self._evaluate_dividend_condition(
            dividend_info.get('dividend_yield', 0), 
            conditions.get('dividend_yield_min', 0)
        )
        
        per_score, per_reason = self._evaluate_per_condition(
            stock_info.pe_ratio or 0, 
            conditions.get('per_max', float('inf'))
        )
        
        pbr_score, pbr_reason = self._evaluate_pbr_condition(
            stock_info.pb_ratio or 0, 
            conditions.get('pbr_max', float('inf'))
        )
        
        if dividend_reason:
            reasons.append(dividend_reason)
        if per_reason:
            reasons.append(per_reason)
        if pbr_reason:
            reasons.append(pbr_reason)
        
        # 戦略の条件モードに応じた判定
        is_buy_signal = self._evaluate_strategy_condition(
            strategy, dividend_score, per_score, pbr_score
        )
        
        if not is_buy_signal:
            return None
        
        # アラートが既に最近発生していないかチェック
        alert_key = f"{stock_info.symbol}_buy_{strategy.name}"
        if self._is_recent_alert(alert_key):
            return None
        
        if reasons:
            message = f"【買い推奨】{stock_info.name} ({stock_info.symbol})\n" + \
                     f"現在価格: ¥{stock_info.current_price:,.0f}\n" + \
                     f"戦略: {strategy.name} ({strategy.condition_mode})\n" + \
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
    
    def _evaluate_dividend_condition(self, current_yield: float, min_yield: float) -> tuple:
        """配当利回り条件を評価"""
        if min_yield <= 0:
            return 0, None
        
        if current_yield >= min_yield:
            return 1, f"配当利回り {current_yield:.2f}% >= {min_yield}%"
        else:
            return 0, None
    
    def _evaluate_per_condition(self, current_per: float, max_per: float) -> tuple:
        """PER条件を評価"""
        if max_per >= float('inf'):
            return 0, None
        
        if current_per > 0 and current_per <= max_per:
            return 1, f"PER {current_per:.1f} <= {max_per}"
        else:
            return 0, None
    
    def _evaluate_pbr_condition(self, current_pbr: float, max_pbr: float) -> tuple:
        """PBR条件を評価"""
        if max_pbr >= float('inf'):
            return 0, None
        
        if current_pbr > 0 and current_pbr <= max_pbr:
            return 1, f"PBR {current_pbr:.1f} <= {max_pbr}"
        else:
            return 0, None
    
    def _evaluate_strategy_condition(self, strategy: Strategy, dividend_score: int, per_score: int, pbr_score: int) -> bool:
        """戦略の条件モードに応じた判定"""
        mode = strategy.condition_mode
        
        if mode == "strict_and":
            # 全条件を満たす必要がある
            total_conditions = sum([1 for score in [dividend_score, per_score, pbr_score] if score >= 0])
            satisfied_conditions = dividend_score + per_score + pbr_score
            return satisfied_conditions == total_conditions and total_conditions > 0
        
        elif mode == "any_one":
            # 1つでも条件を満たせばOK
            return (dividend_score + per_score + pbr_score) >= 1
        
        elif mode == "any_two_of_three":
            # 3条件中2条件以上
            return (dividend_score + per_score + pbr_score) >= 2
        
        elif mode == "weighted_score":
            # 重み付きスコア
            weights = strategy.weights or {}
            weighted_score = (
                dividend_score * weights.get('dividend_weight', 0.4) +
                per_score * weights.get('per_weight', 0.3) +
                pbr_score * weights.get('pbr_weight', 0.3)
            )
            return weighted_score >= strategy.min_score
        
        else:
            # デフォルトは any_two_of_three
            return (dividend_score + per_score + pbr_score) >= 2
    
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
                message = f"【利益確定推奨】{stock_info.name} ({stock_info.symbol})\n" + \
                         f"現在価格: ¥{current_price:,.0f}\n" + \
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
                message = f"【損切り推奨】{stock_info.name} ({stock_info.symbol})\n" + \
                         f"現在価格: ¥{current_price:,.0f}\n" + \
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
        
        # 統合アラート管理システムで通知
        if self.alert_manager:
            try:
                self.alert_manager.send_alert(alert)
            except Exception as e:
                app_logger.error(f"アラート管理システムエラー: {e}")
                print(f"アラート管理システムエラー: {e}")
        
        # コールバック関数を呼び出し
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                app_logger.error(f"アラートコールバックエラー: {e}")
                print(f"アラートコールバックエラー: {e}")
        
        app_logger.info(f"[ALERT] {alert.alert_type.upper()}: {alert.symbol} - {alert.strategy_name}")
        print(f"[ALERT] {alert.message}")
    
    def add_stock_to_watchlist(self, symbol: str, name: str, strategy_name: str = "default_strategy"):
        """監視銘柄に追加"""
        if strategy_name not in self.strategies:
            raise ValueError(f"不明な戦略: {strategy_name}")
        
        success = self.db.add_to_watchlist(symbol, name, strategy_name)
        if success:
            app_logger.info(f"監視銘柄に追加: {symbol} ({name}) - 戦略: {strategy_name}")
            print(f"監視銘柄に追加: {symbol} ({name}) - 戦略: {strategy_name}")
        else:
            app_logger.error(f"監視銘柄追加エラー: {symbol}")
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
    
    print("\n監視を開始します（Ctrl+Cで停止）")
    try:
        monitor.start_monitoring()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n監視を停止します...")
        monitor.stop_monitoring()