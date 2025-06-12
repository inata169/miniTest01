#!/usr/bin/env python3
"""
Simple database test without external dependencies
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_database_without_dependencies():
    """Test database functionality without importing external dependencies"""
    
    print("=== Simple Database Test ===")
    
    # Test database creation directly
    db_path = "data/test_portfolio.db"
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    try:
        # Initialize database
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create holdings table
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
            
            # Create alerts table
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
            
            # Create watchlist table
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
            print("✓ Database tables created successfully")
            
            # Test data insertion
            cursor.execute('''
                INSERT OR REPLACE INTO holdings 
                (symbol, name, quantity, average_cost, current_price, 
                 acquisition_amount, market_value, profit_loss, broker, account_type, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "7203",
                "トヨタ自動車",
                100,
                2500.0,
                2600.0,
                250000.0,
                260000.0,
                10000.0,
                "SBI",
                "一般",
                datetime.now()
            ))
            
            cursor.execute('''
                INSERT OR REPLACE INTO holdings 
                (symbol, name, quantity, average_cost, current_price, 
                 acquisition_amount, market_value, profit_loss, broker, account_type, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "9984",
                "ソフトバンクグループ",
                50,
                5000.0,
                4800.0,
                250000.0,
                240000.0,
                -10000.0,
                "SBI",
                "一般",
                datetime.now()
            ))
            
            conn.commit()
            print("✓ Test data inserted successfully")
            
            # Test data retrieval
            cursor.execute('''
                SELECT * FROM holdings 
                ORDER BY market_value DESC
            ''')
            
            holdings = cursor.fetchall()
            print(f"✓ Retrieved {len(holdings)} holdings:")
            
            for holding in holdings:
                symbol = holding[1]
                name = holding[2]
                quantity = holding[3]
                current_price = holding[5]
                market_value = holding[7]
                profit_loss = holding[8]
                print(f"  {symbol}: {name} - {quantity}株 ¥{current_price:,.0f} (¥{profit_loss:+,.0f})")
            
            # Test portfolio summary
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_stocks,
                    SUM(acquisition_amount) as total_acquisition,
                    SUM(market_value) as total_market_value,
                    SUM(profit_loss) as total_profit_loss
                FROM holdings
            ''')
            
            result = cursor.fetchone()
            total_stocks = result[0] if result[0] is not None else 0
            total_acquisition = result[1] if result[1] is not None else 0
            total_market_value = result[2] if result[2] is not None else 0
            total_profit_loss = result[3] if result[3] is not None else 0
            
            return_rate = 0
            if total_acquisition > 0:
                return_rate = ((total_market_value / total_acquisition) - 1) * 100
            
            print("✓ Portfolio summary:")
            print(f"  銘柄数: {total_stocks}")
            print(f"  取得金額: ¥{total_acquisition:,.0f}")
            print(f"  評価金額: ¥{total_market_value:,.0f}")
            print(f"  損益: ¥{total_profit_loss:+,.0f}")
            print(f"  収益率: {return_rate:+.2f}%")
            
            # Test watchlist
            cursor.execute('''
                INSERT OR REPLACE INTO watchlist 
                (symbol, name, strategy_name, target_buy_price, target_sell_price, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("6758", "ソニーグループ", "growth_strategy", 8000.0, 12000.0, datetime.now()))
            
            conn.commit()
            
            cursor.execute('SELECT * FROM watchlist WHERE is_active = 1')
            watchlist = cursor.fetchall()
            print(f"✓ Watchlist entries: {len(watchlist)}")
            
            for item in watchlist:
                symbol = item[1]
                name = item[2]
                strategy = item[3]
                print(f"  {symbol}: {name} ({strategy})")
            
            # Test alert logging
            cursor.execute('''
                INSERT INTO alerts 
                (symbol, alert_type, message, triggered_price, strategy_name)
                VALUES (?, ?, ?, ?, ?)
            ''', ("7203", "buy", "Test buy alert", 2600.0, "test_strategy"))
            
            conn.commit()
            
            cursor.execute('SELECT COUNT(*) FROM alerts')
            alert_count = cursor.fetchone()[0]
            print(f"✓ Alert entries: {alert_count}")
            
            print("✓ All database tests passed!")
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False
    
    finally:
        # Clean up test database
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✓ Test database cleaned up")
    
    return True

if __name__ == "__main__":
    success = test_database_without_dependencies()
    sys.exit(0 if success else 1)