#!/usr/bin/env python3
"""
株価更新のデバッグ用スクリプト
"""
import sys
import os

# パス追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import DatabaseManager
from data_sources import YahooFinanceDataSource

def debug_stock_update():
    """株価更新をデバッグ"""
    print("=== 株価更新デバッグ ===")
    
    # データベースから銘柄取得
    db = DatabaseManager()
    holdings = db.get_all_holdings()
    
    print(f"データベース内銘柄数: {len(holdings)}")
    print("\n--- 銘柄一覧 ---")
    
    symbols = []
    skipped_symbols = []
    
    for i, holding in enumerate(holdings, 1):
        symbol = holding['symbol']
        name = holding['name']
        
        # 疑似シンボルチェック
        is_pseudo = (symbol.startswith('PORTFOLIO_') or 
                    symbol.startswith('FUND_') or
                    symbol == 'STOCK_PORTFOLIO' or
                    symbol == 'TOTAL_PORTFOLIO')
        
        if is_pseudo:
            skipped_symbols.append(symbol)
            print(f"{i:2d}: {symbol:<15} | {name:<20} | [スキップ: 疑似シンボル]")
        else:
            symbols.append(symbol)
            print(f"{i:2d}: {symbol:<15} | {name:<20} | [更新対象]")
    
    print(f"\n更新対象銘柄: {len(symbols)} 件")
    print(f"スキップ銘柄: {len(skipped_symbols)} 件")
    
    if len(skipped_symbols) > 0:
        print(f"スキップされた銘柄: {', '.join(skipped_symbols)}")
    
    # 実際に株価取得をテスト
    if symbols:
        print(f"\n=== 株価取得テスト ===")
        data_source = YahooFinanceDataSource()
        
        success_count = 0
        error_count = 0
        
        for symbol in symbols[:5]:  # 最初の5銘柄だけテスト
            print(f"取得中: {symbol}...", end=" ")
            try:
                stock_info = data_source.get_stock_info(symbol)
                if stock_info:
                    print(f"成功 (¥{stock_info.current_price:,.0f})")
                    success_count += 1
                else:
                    print("失敗 (データなし)")
                    error_count += 1
            except Exception as e:
                print(f"エラー: {e}")
                error_count += 1
        
        print(f"\nテスト結果: 成功 {success_count}, 失敗 {error_count}")
        
        # 予想される更新結果
        expected_updated = len(symbols) - error_count * (len(symbols) // 5)  # 推定
        expected_skipped = len(skipped_symbols)
        
        print(f"\n=== 予想される更新結果 ===")
        print(f"更新予定: 約{expected_updated}銘柄")
        print(f"スキップ: {expected_skipped}銘柄")
        print(f"表示メッセージ例: '株価更新完了: {expected_updated}銘柄を更新, {expected_skipped}銘柄をスキップ'")

if __name__ == "__main__":
    debug_stock_update()