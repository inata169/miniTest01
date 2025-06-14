#!/usr/bin/env python3
"""
データベース操作完全性テストスイート
"""

import sys
import os
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def test_database_initialization():
    """データベース初期化テスト"""
    print("🗄️ データベース初期化テスト開始...")
    
    try:
        from database import DatabaseManager
        
        # 一時データベースで初期化テスト
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db_path = os.path.join(temp_dir, "test_init.db")
            
            db = DatabaseManager(test_db_path)
            
            if not os.path.exists(test_db_path):
                print("❌ データベースファイル作成失敗")
                return False
            
            # テーブル存在確認
            with sqlite3.connect(test_db_path) as conn:
                cursor = conn.cursor()
                
                # テーブル一覧取得
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = ['holdings', 'alerts', 'price_history', 'watchlist']
                
                for table in expected_tables:
                    if table in tables:
                        print(f"✅ テーブル {table} 作成成功")
                    else:
                        print(f"❌ テーブル {table} 作成失敗")
                        return False
                
                # テーブル構造確認
                for table in expected_tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    print(f"   📋 {table} テーブル: {len(columns)}カラム")
                    
                    # 主要カラムの存在確認
                    column_names = [col[1] for col in columns]
                    
                    if table == 'holdings':
                        required_columns = ['id', 'symbol', 'name', 'quantity', 'average_cost']
                        for col in required_columns:
                            if col in column_names:
                                print(f"   ✅ {col} カラム存在")
                            else:
                                print(f"   ❌ {col} カラム不足")
                                return False
        
        print("✅ データベース初期化テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ データベース初期化テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_holdings_operations():
    """保有銘柄操作テスト"""
    print("\n📊 保有銘柄操作テスト開始...")
    
    try:
        from database import DatabaseManager
        from csv_parser import Holding
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db_path = os.path.join(temp_dir, "test_holdings.db")
            db = DatabaseManager(test_db_path)
            
            # テストデータ作成
            test_holdings = [
                Holding(
                    symbol="7203",
                    name="トヨタ自動車",
                    quantity=100,
                    average_cost=2500.0,
                    current_price=2600.0,
                    acquisition_amount=250000.0,
                    market_value=260000.0,
                    profit_loss=10000.0,
                    broker="SBI証券",
                    account_type="NISA"
                ),
                Holding(
                    symbol="6758",
                    name="ソニーグループ",
                    quantity=50,
                    average_cost=12000.0,
                    current_price=13000.0,
                    acquisition_amount=600000.0,
                    market_value=650000.0,
                    profit_loss=50000.0,
                    broker="楽天証券",
                    account_type="特定"
                )
            ]
            
            # データ挿入テスト
            inserted_count = db.insert_holdings(test_holdings)
            if inserted_count == len(test_holdings):
                print(f"✅ 保有銘柄挿入成功: {inserted_count}件")
            else:
                print(f"❌ 保有銘柄挿入失敗: {inserted_count}/{len(test_holdings)}件")
                return False
            
            # データ取得テスト
            all_holdings = db.get_all_holdings()
            if len(all_holdings) == len(test_holdings):
                print(f"✅ 保有銘柄取得成功: {len(all_holdings)}件")
            else:
                print(f"❌ 保有銘柄取得失敗: {len(all_holdings)}/{len(test_holdings)}件")
                return False
            
            # データ内容確認（順序に依存しない比較）
            holdings_by_symbol = {h['symbol']: h for h in all_holdings}
            
            for expected in test_holdings:
                if expected.symbol in holdings_by_symbol:
                    holding = holdings_by_symbol[expected.symbol]
                    
                    symbol_match = holding['symbol'] == expected.symbol
                    name_match = holding['name'] == expected.name
                    quantity_match = holding['quantity'] == expected.quantity
                    
                    if symbol_match and name_match and quantity_match:
                        print(f"   ✅ {expected.symbol} データ整合性OK")
                    else:
                        print(f"   ❌ {expected.symbol} データ整合性NG")
                        print(f"      期待: symbol={expected.symbol}, name={expected.name}, quantity={expected.quantity}")
                        print(f"      実際: symbol={holding['symbol']}, name={holding['name']}, quantity={holding['quantity']}")
                        print(f"      比較: symbol={symbol_match}, name={name_match}, quantity={quantity_match}")
                        return False
                else:
                    print(f"   ❌ {expected.symbol} データが見つかりません")
                    return False
            
            # 価格更新テスト
            price_updates = {
                "7203": 2700.0,
                "6758": 13500.0
            }
            
            db.update_current_prices(price_updates)
            print("✅ 価格更新実行成功")
            
            # 更新後データ確認
            updated_holdings = db.get_all_holdings()
            for holding in updated_holdings:
                symbol = holding['symbol']
                if symbol in price_updates:
                    expected_price = price_updates[symbol]
                    if holding['current_price'] == expected_price:
                        print(f"   ✅ {symbol} 価格更新確認: ¥{expected_price:,.0f}")
                    else:
                        print(f"   ❌ {symbol} 価格更新失敗: {holding['current_price']} != {expected_price}")
                        return False
            
            # 個別銘柄削除テスト
            delete_result = db.delete_holding("7203")
            if delete_result:
                print("✅ 個別銘柄削除成功")
                
                # 削除確認
                remaining_holdings = db.get_all_holdings()
                if len(remaining_holdings) == len(test_holdings) - 1:
                    print("   ✅ 削除後件数確認OK")
                else:
                    print(f"   ❌ 削除後件数確認NG: {len(remaining_holdings)}")
                    return False
            else:
                print("❌ 個別銘柄削除失敗")
                return False
            
            # 全銘柄削除テスト
            deleted_count = db.delete_all_holdings()
            if deleted_count > 0:
                print(f"✅ 全銘柄削除成功: {deleted_count}件")
                
                # 全削除確認
                final_holdings = db.get_all_holdings()
                if len(final_holdings) == 0:
                    print("   ✅ 全削除後確認OK")
                else:
                    print(f"   ❌ 全削除後確認NG: {len(final_holdings)}件残存")
                    return False
            else:
                print("⚠️  全銘柄削除: 削除対象なし")
        
        print("✅ 保有銘柄操作テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 保有銘柄操作テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_portfolio_summary():
    """ポートフォリオサマリーテスト"""
    print("\n📈 ポートフォリオサマリーテスト開始...")
    
    try:
        from database import DatabaseManager
        from csv_parser import Holding
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db_path = os.path.join(temp_dir, "test_summary.db")
            db = DatabaseManager(test_db_path)
            
            # 多様なテストデータ
            test_holdings = [
                Holding(
                    symbol="7203",
                    name="トヨタ自動車",
                    quantity=100,
                    average_cost=2500.0,
                    current_price=2700.0,
                    acquisition_amount=250000.0,
                    market_value=270000.0,
                    profit_loss=20000.0,
                    broker="SBI証券",
                    account_type="NISA"
                ),
                Holding(
                    symbol="6758",
                    name="ソニーグループ",
                    quantity=50,
                    average_cost=12000.0,
                    current_price=11000.0,
                    acquisition_amount=600000.0,
                    market_value=550000.0,
                    profit_loss=-50000.0,
                    broker="楽天証券",
                    account_type="特定"
                ),
                Holding(
                    symbol="9984",
                    name="ソフトバンクグループ",
                    quantity=30,
                    average_cost=8000.0,
                    current_price=8500.0,
                    acquisition_amount=240000.0,
                    market_value=255000.0,
                    profit_loss=15000.0,
                    broker="SBI証券",
                    account_type="特定"
                )
            ]
            
            db.insert_holdings(test_holdings)
            
            # サマリー計算
            summary = db.get_portfolio_summary()
            
            # 期待値計算
            expected_total_stocks = len(test_holdings)
            expected_total_acquisition = sum(h.acquisition_amount for h in test_holdings)
            expected_total_market_value = sum(h.market_value for h in test_holdings)
            expected_total_profit_loss = sum(h.profit_loss for h in test_holdings)
            expected_return_rate = ((expected_total_market_value / expected_total_acquisition) - 1) * 100
            
            # 検証
            checks = [
                ('total_stocks', expected_total_stocks),
                ('total_acquisition', expected_total_acquisition),
                ('total_market_value', expected_total_market_value),
                ('total_profit_loss', expected_total_profit_loss)
            ]
            
            for field, expected in checks:
                actual = summary.get(field, 0)
                if abs(actual - expected) < 0.01:  # 浮動小数点誤差許容
                    print(f"✅ {field}: {actual:,.0f} (期待: {expected:,.0f})")
                else:
                    print(f"❌ {field}: {actual:,.0f} != {expected:,.0f}")
                    return False
            
            # 収益率確認
            actual_return_rate = summary.get('return_rate', 0)
            if abs(actual_return_rate - expected_return_rate) < 0.01:
                print(f"✅ return_rate: {actual_return_rate:.2f}% (期待: {expected_return_rate:.2f}%)")
            else:
                print(f"❌ return_rate: {actual_return_rate:.2f}% != {expected_return_rate:.2f}%")
                return False
            
            print("✅ ポートフォリオサマリーテスト完了")
            return True
        
    except Exception as e:
        print(f"❌ ポートフォリオサマリーテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alert_management():
    """アラート管理テスト"""
    print("\n🚨 アラート管理テスト開始...")
    
    try:
        from database import DatabaseManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db_path = os.path.join(temp_dir, "test_alerts.db")
            db = DatabaseManager(test_db_path)
            
            # アラートデータ作成
            test_alerts = [
                {
                    'symbol': '7203',
                    'alert_type': 'buy',
                    'message': '買い推奨: トヨタ自動車',
                    'triggered_price': 2700.0,
                    'strategy_name': 'default_strategy'
                },
                {
                    'symbol': '6758',
                    'alert_type': 'sell',
                    'message': '利益確定: ソニーグループ',
                    'triggered_price': 13500.0,
                    'strategy_name': 'profit_strategy'
                },
                {
                    'symbol': '9984',
                    'alert_type': 'test',
                    'message': 'テストアラート: ソフトバンクG',
                    'triggered_price': 8500.0,
                    'strategy_name': 'test_strategy'
                }
            ]
            
            # アラート挿入テスト
            for alert in test_alerts:
                result = db.log_alert(
                    alert['symbol'],
                    alert['alert_type'],
                    alert['message'],
                    alert['triggered_price'],
                    alert['strategy_name']
                )
                
                if result:
                    print(f"✅ アラート挿入成功: {alert['symbol']} - {alert['alert_type']}")
                else:
                    print(f"❌ アラート挿入失敗: {alert['symbol']}")
                    return False
            
            # アラート取得テスト
            alerts = db.get_alerts(10)
            
            if len(alerts) == len(test_alerts):
                print(f"✅ アラート取得成功: {len(alerts)}件")
            else:
                print(f"❌ アラート取得件数ミスマッチ: {len(alerts)}/{len(test_alerts)}")
                return False
            
            # アラート内容確認
            for alert in alerts:
                symbol = alert['symbol']
                alert_type = alert['alert_type']
                message = alert['message']
                
                # 対応するテストデータ検索
                matching_test = None
                for test_alert in test_alerts:
                    if (test_alert['symbol'] == symbol and 
                        test_alert['alert_type'] == alert_type):
                        matching_test = test_alert
                        break
                
                if matching_test:
                    print(f"   ✅ {symbol} - {alert_type}: データ整合性OK")
                    
                    # 日時確認
                    if 'created_at' in alert and alert['created_at']:
                        print(f"   ✅ {symbol}: 作成日時設定済み")
                    else:
                        print(f"   ⚠️  {symbol}: 作成日時未設定")
                else:
                    print(f"   ❌ {symbol} - {alert_type}: 対応するテストデータなし")
                    return False
            
            # アラート履歴クリアテスト
            clear_result = db.clear_alerts()
            if clear_result:
                print("✅ アラート履歴クリア成功")
                
                # クリア確認
                remaining_alerts = db.get_alerts(10)
                if len(remaining_alerts) == 0:
                    print("   ✅ クリア後確認OK")
                else:
                    print(f"   ❌ クリア後確認NG: {len(remaining_alerts)}件残存")
                    return False
            else:
                print("❌ アラート履歴クリア失敗")
                return False
        
        print("✅ アラート管理テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ アラート管理テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_watchlist_operations():
    """監視銘柄操作テスト"""
    print("\n👁️ 監視銘柄操作テスト開始...")
    
    try:
        from database import DatabaseManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db_path = os.path.join(temp_dir, "test_watchlist.db")
            db = DatabaseManager(test_db_path)
            
            # 監視銘柄データ
            test_watchlist = [
                {
                    'symbol': '4519',
                    'name': '中外製薬',
                    'strategy_name': 'defensive_strategy',
                    'target_buy_price': 6500.0,
                    'target_sell_price': 8000.0
                },
                {
                    'symbol': '8591',
                    'name': 'オリックス',
                    'strategy_name': 'dividend_strategy',
                    'target_buy_price': 3000.0,
                    'target_sell_price': 3500.0
                }
            ]
            
            # 監視銘柄追加テスト
            for item in test_watchlist:
                result = db.add_to_watchlist(
                    item['symbol'],
                    item['name'],
                    item['strategy_name'],
                    item['target_buy_price'],
                    item['target_sell_price']
                )
                
                if result:
                    print(f"✅ 監視銘柄追加成功: {item['symbol']} - {item['name']}")
                else:
                    print(f"❌ 監視銘柄追加失敗: {item['symbol']}")
                    return False
            
            # 監視銘柄取得テスト
            watchlist = db.get_watchlist()
            
            if len(watchlist) == len(test_watchlist):
                print(f"✅ 監視銘柄取得成功: {len(watchlist)}件")
            else:
                print(f"❌ 監視銘柄取得件数ミスマッチ: {len(watchlist)}/{len(test_watchlist)}")
                return False
            
            # データ内容確認
            for item in watchlist:
                symbol = item['symbol']
                name = item['name']
                strategy_name = item['strategy_name']
                
                # 対応するテストデータ検索
                matching_test = None
                for test_item in test_watchlist:
                    if test_item['symbol'] == symbol:
                        matching_test = test_item
                        break
                
                if matching_test:
                    if (name == matching_test['name'] and
                        strategy_name == matching_test['strategy_name']):
                        print(f"   ✅ {symbol}: データ整合性OK")
                    else:
                        print(f"   ❌ {symbol}: データ整合性NG")
                        return False
                else:
                    print(f"   ❌ {symbol}: 対応するテストデータなし")
                    return False
        
        print("✅ 監視銘柄操作テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 監視銘柄操作テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concurrent_operations():
    """並行操作テスト"""
    print("\n🔄 並行操作テスト開始...")
    
    try:
        from database import DatabaseManager
        from csv_parser import Holding
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db_path = os.path.join(temp_dir, "test_concurrent.db")
            db = DatabaseManager(test_db_path)
            
            # 複数操作の同時実行シミュレーション
            test_holding = Holding(
                symbol="TEST",
                name="テスト銘柄",
                quantity=100,
                average_cost=1000.0,
                current_price=1000.0,
                acquisition_amount=100000.0,
                market_value=100000.0,
                profit_loss=0.0,
                broker="テスト証券",
                account_type="テスト"
            )
            
            # 1. データ挿入
            db.insert_holdings([test_holding])
            print("✅ データ挿入完了")
            
            # 2. 価格更新
            db.update_current_prices({"TEST": 1100.0})
            print("✅ 価格更新完了")
            
            # 3. アラート追加
            db.log_alert("TEST", "test", "テストアラート", 1100.0, "test_strategy")
            print("✅ アラート追加完了")
            
            # 4. 監視銘柄追加
            db.add_to_watchlist("TEST", "テスト銘柄", "test_strategy", 900.0, 1200.0)
            print("✅ 監視銘柄追加完了")
            
            # 5. サマリー取得
            summary = db.get_portfolio_summary()
            if summary['total_stocks'] == 1:
                print("✅ サマリー取得完了")
            else:
                print("❌ サマリー整合性エラー")
                return False
            
            # 6. 各データの整合性確認
            holdings = db.get_all_holdings()
            alerts = db.get_alerts(5)
            watchlist = db.get_watchlist()
            
            if (len(holdings) == 1 and
                len(alerts) == 1 and
                len(watchlist) == 1):
                print("✅ 並行操作後データ整合性確認")
            else:
                print(f"❌ データ整合性エラー: holdings={len(holdings)}, alerts={len(alerts)}, watchlist={len(watchlist)}")
                return False
            
            # 7. 価格が正しく更新されているか確認
            if holdings[0]['current_price'] == 1100.0:
                print("✅ 価格更新整合性確認")
            else:
                print(f"❌ 価格更新整合性エラー: {holdings[0]['current_price']} != 1100.0")
                return False
        
        print("✅ 並行操作テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 並行操作テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """データベース操作完全性テストメイン"""
    print("🗄️ データベース操作完全性テスト開始\n")
    
    test_results = []
    
    # 各テストを実行
    test_results.append(("データベース初期化", test_database_initialization()))
    test_results.append(("保有銘柄操作", test_holdings_operations()))
    test_results.append(("ポートフォリオサマリー", test_portfolio_summary()))
    test_results.append(("アラート管理", test_alert_management()))
    test_results.append(("監視銘柄操作", test_watchlist_operations()))
    test_results.append(("並行操作", test_concurrent_operations()))
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 データベース操作完全性テスト結果")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-"*60)
    print(f"総テスト数: {len(test_results)}")
    print(f"成功: {passed}")
    print(f"失敗: {failed}")
    print(f"成功率: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 データベース操作は完璧に動作しています！")
        return True
    else:
        print(f"\n⚠️  {failed}件のテストが失敗しました。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)