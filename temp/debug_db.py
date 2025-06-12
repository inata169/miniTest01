#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/src')

from database import DatabaseManager

def main():
    db = DatabaseManager()
    holdings = db.get_all_holdings()
    
    print("=== 現在のデータベース内容 ===")
    print(f"保有銘柄数: {len(holdings)}")
    print()
    
    for holding in holdings:
        print(f"Symbol: {holding['symbol']}")
        print(f"Name: {holding['name']}")
        print(f"Broker: {holding['broker']}")
        print(f"Account: {holding['account_type']}")
        print(f"Quantity: {holding['quantity']}")
        print(f"Current Price: ¥{holding['current_price']:,.2f}")
        print(f"Market Value: ¥{holding['market_value']:,.2f}")
        print("-" * 40)

if __name__ == "__main__":
    main()