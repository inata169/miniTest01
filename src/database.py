import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from csv_parser import Holding
from data_sources import StockInfo


class DatabaseManager:
    """SQLiteデータベース管理クラス"""
    
    def __init__(self, db_path: str = "data/portfolio.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベースとテーブルを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 保有銘柄テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    average_cost REAL NOT NULL,
                    current_price REAL DEFAULT 0,
                    acquisition_amount REAL NOT NULL,
                    market_value REAL DEFAULT 0,
                    profit_loss REAL DEFAULT 0,
                    broker TEXT NOT NULL,
                    account_type TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, broker, account_type)
                )
            ''')
            
            # アラート履歴テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    triggered_price REAL,
                    strategy_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 株価履歴テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATE NOT NULL,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            ''')
            
            # 監視銘柄テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    target_buy_price REAL,
                    target_sell_price REAL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def insert_holdings(self, holdings: List[Holding]) -> int:
        """保有銘柄を一括挿入"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            inserted_count = 0
            for holding in holdings:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO holdings 
                        (symbol, name, quantity, average_cost, current_price, 
                         acquisition_amount, market_value, profit_loss, broker, account_type, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        holding.symbol,
                        holding.name,
                        holding.quantity,
                        holding.average_cost,
                        holding.current_price,
                        holding.acquisition_amount,
                        holding.market_value,
                        holding.profit_loss,
                        holding.broker,
                        holding.account_type,
                        datetime.now()
                    ))
                    inserted_count += 1
                except sqlite3.Error as e:
                    print(f"保有銘柄挿入エラー ({holding.symbol}): {e}")
            
            conn.commit()
            return inserted_count
    
    def get_all_holdings(self) -> List[Dict]:
        """全保有銘柄を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM holdings 
                ORDER BY market_value DESC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_current_prices(self, price_updates: Dict[str, float]):
        """現在価格を一括更新"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for symbol, price in price_updates.items():
                cursor.execute('''
                    UPDATE holdings 
                    SET current_price = ?,
                        market_value = quantity * ?,
                        profit_loss = (quantity * ?) - acquisition_amount,
                        updated_at = ?
                    WHERE symbol = ?
                ''', (price, price, price, datetime.now(), symbol))
            
            conn.commit()
    
    def add_to_watchlist(self, symbol: str, name: str, strategy_name: str, 
                        target_buy_price: Optional[float] = None,
                        target_sell_price: Optional[float] = None):
        """監視銘柄に追加"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO watchlist 
                    (symbol, name, strategy_name, target_buy_price, target_sell_price, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (symbol, name, strategy_name, target_buy_price, target_sell_price, datetime.now()))
                
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"監視銘柄追加エラー: {e}")
                return False
    
    def get_watchlist(self) -> List[Dict]:
        """監視銘柄一覧を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM watchlist 
                WHERE is_active = 1
                ORDER BY created_at DESC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def log_alert(self, symbol: str, alert_type: str, message: str, 
                  triggered_price: Optional[float] = None, 
                  strategy_name: Optional[str] = None):
        """アラートをログに記録"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO alerts 
                    (symbol, alert_type, message, triggered_price, strategy_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (symbol, alert_type, message, triggered_price, strategy_name))
                
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"アラートログエラー: {e}")
                return False
    
    def get_alerts(self, limit: int = 100) -> List[Dict]:
        """アラート履歴を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM alerts 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def save_price_history(self, symbol: str, stock_info: StockInfo):
        """株価履歴を保存"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO price_history 
                    (symbol, date, close_price, volume)
                    VALUES (?, ?, ?, ?)
                ''', (
                    symbol,
                    datetime.now().date(),
                    stock_info.current_price,
                    stock_info.volume
                ))
                
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"株価履歴保存エラー: {e}")
                return False
    
    def get_portfolio_summary(self) -> Dict:
        """ポートフォリオサマリーを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_stocks,
                    SUM(acquisition_amount) as total_acquisition,
                    SUM(market_value) as total_market_value,
                    SUM(profit_loss) as total_profit_loss,
                    AVG(profit_loss / acquisition_amount * 100) as avg_return_rate
                FROM holdings
            ''')
            
            result = cursor.fetchone()
            
            # None値を安全に0に変換
            total_stocks = result[0] if result[0] is not None else 0
            total_acquisition = result[1] if result[1] is not None else 0
            total_market_value = result[2] if result[2] is not None else 0
            total_profit_loss = result[3] if result[3] is not None else 0
            avg_return_rate = result[4] if result[4] is not None else 0
            
            # 収益率計算（ゼロ除算対策）
            return_rate = 0
            if total_acquisition is not None and total_acquisition > 0 and total_market_value is not None:
                return_rate = ((total_market_value / total_acquisition) - 1) * 100
            
            return {
                'total_stocks': total_stocks,
                'total_acquisition': total_acquisition,
                'total_market_value': total_market_value,
                'total_profit_loss': total_profit_loss,
                'avg_return_rate': avg_return_rate,
                'return_rate': return_rate
            }


if __name__ == "__main__":
    # テスト用
    db = DatabaseManager()
    
    # サマリー表示
    summary = db.get_portfolio_summary()
    print("ポートフォリオサマリー:")
    print(f"  銘柄数: {summary['total_stocks']}")
    print(f"  取得金額: ¥{summary['total_acquisition']:,.0f}")
    print(f"  評価金額: ¥{summary['total_market_value']:,.0f}")
    print(f"  損益: ¥{summary['total_profit_loss']:,.0f}")
    print(f"  収益率: {summary['return_rate']:+.2f}%")