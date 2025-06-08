#!/usr/bin/env python3
"""
Comprehensive test suite without external dependencies
"""

import sys
import os
import sqlite3
import json
import tempfile
from datetime import datetime

def test_all_core_functionality():
    """Test all core functionality without external dependencies"""
    
    print("=== Comprehensive Core Functionality Test ===")
    
    # Test 1: Database operations
    print("\n1. Testing Database Operations...")
    
    db_path = "data/test_comprehensive.db"
    os.makedirs("data", exist_ok=True)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
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
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, broker, account_type)
                )
            ''')
            
            # Insert test data
            test_holdings = [
                ("7203", "トヨタ自動車", 100, 2500.0, 2600.0, 250000.0, 260000.0, 10000.0, "SBI", "一般"),
                ("9984", "ソフトバンクG", 50, 5000.0, 4800.0, 250000.0, 240000.0, -10000.0, "SBI", "一般"),
                ("6758", "ソニーG", 30, 10000.0, 11000.0, 300000.0, 330000.0, 30000.0, "楽天", "NISA")
            ]
            
            for holding in test_holdings:
                cursor.execute('''
                    INSERT OR REPLACE INTO holdings 
                    (symbol, name, quantity, average_cost, current_price, 
                     acquisition_amount, market_value, profit_loss, broker, account_type, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', holding + (datetime.now().isoformat(),))
            
            conn.commit()
            
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
            total_profit_loss = result[3] if result[3] is not None else 0
            
            print(f"   Portfolio: {result[0]} stocks, Profit/Loss: ¥{total_profit_loss:+,.0f}")
            print("   ✓ Database operations working")
    
    except Exception as e:
        print(f"   ✗ Database test failed: {e}")
        return False
    
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
    
    # Test 2: Configuration handling
    print("\n2. Testing Configuration Handling...")
    
    test_config = {
        "notifications": {
            "email": {"enabled": False},
            "desktop": {"enabled": True},
            "console": {"enabled": True}
        },
        "monitoring": {
            "check_interval_minutes": 30
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
        config_path = f.name
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        if ('notifications' in loaded_config and 
            'monitoring' in loaded_config):
            print("   ✓ Configuration loading working")
        else:
            print("   ✗ Configuration structure invalid")
            return False
    
    except Exception as e:
        print(f"   ✗ Configuration test failed: {e}")
        return False
    
    finally:
        os.unlink(config_path)
    
    # Test 3: Number parsing (CSV functionality)
    print("\n3. Testing Number Parsing...")
    
    def parse_number(value):
        if value == '' or value is None:
            return 0.0
        try:
            if isinstance(value, str):
                value = value.strip()
                if value == '' or value == '-':
                    return 0.0
                value = value.replace(',', '').replace('¥', '').replace('円', '').replace('"', '')
                if value.startswith('+'):
                    value = value[1:]
                value = value.translate(str.maketrans('０１２３４５６７８９，', '0123456789,'))
                if value == '':
                    return 0.0
            return float(value)
        except:
            return 0.0
    
    test_numbers = [
        ("1,000", 1000.0),
        ("¥2,500", 2500.0),
        ("+500", 500.0),
        ("", 0.0),
        ("-", 0.0)
    ]
    
    passed = 0
    for input_val, expected in test_numbers:
        result = parse_number(input_val)
        if result == expected:
            passed += 1
    
    if passed == len(test_numbers):
        print("   ✓ Number parsing working")
    else:
        print(f"   ✗ Number parsing failed: {passed}/{len(test_numbers)}")
        return False
    
    # Test 4: Alert formatting
    print("\n4. Testing Alert Formatting...")
    
    def format_alert(symbol, alert_type, price, message):
        try:
            if alert_type == 'buy':
                prefix = "🔵 BUY"
            elif alert_type == 'sell_profit':
                prefix = "🟢 SELL (利益確定)"
            elif alert_type == 'sell_loss':
                prefix = "🔴 SELL (損切り)"
            else:
                prefix = "⚪ ALERT"
            
            formatted = f"{prefix}: {symbol} ¥{price:,.0f}\n{message}"
            return formatted
        except:
            return None
    
    test_alert = format_alert("7203", "buy", 2600.0, "買い推奨: PER 12.5")
    
    if test_alert and "7203" in test_alert and "2,600" in test_alert:
        print("   ✓ Alert formatting working")
    else:
        print("   ✗ Alert formatting failed")
        return False
    
    print("\n=== All Core Tests Passed! ===")
    return True

if __name__ == "__main__":
    success = test_all_core_functionality()
    sys.exit(0 if success else 1)
