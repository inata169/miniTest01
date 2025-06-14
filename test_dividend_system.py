#!/usr/bin/env python3
"""
配当分析システム包括テストスイート
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def test_dividend_visualizer():
    """配当可視化機能のテスト"""
    print("🧪 配当可視化機能テスト開始...")
    
    try:
        from dividend_visualizer import DividendVisualizer
        
        visualizer = DividendVisualizer()
        print("✅ DividendVisualizerクラス初期化成功")
        
        # テストデータパターン1: 正常データ
        normal_data = [
            {'year': 2020, 'dividend': 85.0, 'date': '2020-12-31'},
            {'year': 2021, 'dividend': 90.0, 'date': '2021-12-31'},
            {'year': 2022, 'dividend': 92.0, 'date': '2022-12-31'},
            {'year': 2023, 'dividend': 95.0, 'date': '2023-12-31'},
            {'year': 2024, 'dividend': 100.0, 'date': '2024-12-31'},
        ]
        
        # テストデータパターン2: 配当減少トレンド
        declining_data = [
            {'year': 2020, 'dividend': 100.0, 'date': '2020-12-31'},
            {'year': 2021, 'dividend': 95.0, 'date': '2021-12-31'},
            {'year': 2022, 'dividend': 90.0, 'date': '2022-12-31'},
            {'year': 2023, 'dividend': 85.0, 'date': '2023-12-31'},
            {'year': 2024, 'dividend': 80.0, 'date': '2024-12-31'},
        ]
        
        # テストデータパターン3: 不規則データ
        irregular_data = [
            {'year': 2020, 'dividend': 50.0, 'date': '2020-12-31'},
            {'year': 2021, 'dividend': 120.0, 'date': '2021-12-31'},
            {'year': 2022, 'dividend': 30.0, 'date': '2022-12-31'},
            {'year': 2023, 'dividend': 90.0, 'date': '2023-12-31'},
        ]
        
        # 正常データテスト
        chart_path = visualizer.create_dividend_chart('TEST_7203', normal_data, 2800)
        if chart_path and os.path.exists(chart_path):
            print(f"✅ 正常データチャート作成成功: {chart_path}")
        else:
            print("❌ 正常データチャート作成失敗")
            return False
            
        # 配当減少データテスト
        chart_path = visualizer.create_dividend_chart('TEST_DECLINE', declining_data, 1500)
        if chart_path and os.path.exists(chart_path):
            print(f"✅ 減少トレンドチャート作成成功: {chart_path}")
        else:
            print("❌ 減少トレンドチャート作成失敗")
            return False
            
        # 不規則データテスト
        chart_path = visualizer.create_dividend_chart('TEST_IRREGULAR', irregular_data, 3500)
        if chart_path and os.path.exists(chart_path):
            print(f"✅ 不規則データチャート作成成功: {chart_path}")
        else:
            print("❌ 不規則データチャート作成失敗")
            return False
        
        print("✅ 配当可視化機能テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 配当可視化機能テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """エッジケースのテスト"""
    print("\n🧪 エッジケーステスト開始...")
    
    try:
        from dividend_visualizer import DividendVisualizer
        
        visualizer = DividendVisualizer()
        
        # 空データテスト
        empty_result = visualizer.create_dividend_chart('EMPTY', [], 1000)
        if empty_result is None:
            print("✅ 空データ処理正常")
        else:
            print("❌ 空データ処理異常")
            return False
        
        # 単年データテスト
        single_data = [{'year': 2024, 'dividend': 50.0, 'date': '2024-12-31'}]
        single_result = visualizer.create_dividend_chart('SINGLE', single_data, 2000)
        if single_result and os.path.exists(single_result):
            print("✅ 単年データ処理正常")
        else:
            print("❌ 単年データ処理異常")
            return False
            
        # ゼロ配当データテスト
        zero_data = [
            {'year': 2023, 'dividend': 0.0, 'date': '2023-12-31'},
            {'year': 2024, 'dividend': 10.0, 'date': '2024-12-31'}
        ]
        zero_result = visualizer.create_dividend_chart('ZERO', zero_data, 1500)
        if zero_result and os.path.exists(zero_result):
            print("✅ ゼロ配当データ処理正常")
        else:
            print("❌ ゼロ配当データ処理異常")
            return False
        
        print("✅ エッジケーステスト完了")
        return True
        
    except Exception as e:
        print(f"❌ エッジケーステストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_path_handling():
    """パス処理のテスト"""
    print("\n🧪 パス処理テスト開始...")
    
    try:
        from dividend_visualizer import DividendVisualizer
        
        visualizer = DividendVisualizer()
        
        # 一時ディレクトリでテスト
        with tempfile.TemporaryDirectory() as temp_dir:
            test_data = [
                {'year': 2023, 'dividend': 75.0, 'date': '2023-12-31'},
                {'year': 2024, 'dividend': 80.0, 'date': '2024-12-31'}
            ]
            
            # カスタムパスでテスト
            custom_path = os.path.join(temp_dir, 'custom_dividend_chart.png')
            result = visualizer.create_dividend_chart('PATH_TEST', test_data, 2500, custom_path)
            
            if result == custom_path and os.path.exists(custom_path):
                print("✅ カスタムパス処理正常")
            else:
                print("❌ カスタムパス処理異常")
                return False
        
        # 絶対パス自動生成テスト
        result = visualizer.create_dividend_chart('AUTO_PATH', test_data, 2500)
        if result and os.path.isabs(result) and os.path.exists(result):
            print("✅ 絶対パス自動生成正常")
            print(f"   生成パス: {result}")
        else:
            print("❌ 絶対パス自動生成異常")
            return False
        
        print("✅ パス処理テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ パス処理テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_sources_integration():
    """データソース統合テスト"""
    print("\n🧪 データソース統合テスト開始...")
    
    try:
        from data_sources import MultiDataSource
        from dotenv import load_dotenv
        import os
        
        # .envファイル読み込み
        load_dotenv()
        
        # データソース初期化
        jquants_email = os.getenv('JQUANTS_EMAIL')
        refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
        
        data_source = MultiDataSource(jquants_email, None, refresh_token)
        print("✅ MultiDataSource初期化成功")
        
        # テスト銘柄で株価情報取得
        test_symbols = ['7203', '6758', '9984']  # トヨタ、ソニー、ソフトバンクG
        
        for symbol in test_symbols:
            try:
                stock_info = data_source.get_stock_info(symbol)
                if stock_info:
                    print(f"✅ {symbol} 株価取得成功: ¥{stock_info.current_price:,.0f}")
                    
                    # PER, PBR, 配当利回りの確認
                    if stock_info.pe_ratio:
                        print(f"   PER: {stock_info.pe_ratio:.2f}")
                    if stock_info.pb_ratio:
                        print(f"   PBR: {stock_info.pb_ratio:.2f}")
                    if stock_info.dividend_yield:
                        print(f"   配当利回り: {stock_info.dividend_yield:.2f}%")
                else:
                    print(f"⚠️  {symbol} 株価取得なし")
                    
            except Exception as e:
                print(f"⚠️  {symbol} 株価取得エラー: {e}")
        
        # 配当履歴取得テスト
        for symbol in ['7203', '8591']:  # トヨタ、オリックス
            try:
                dividend_history = data_source.get_dividend_history(symbol, 5)
                if dividend_history:
                    print(f"✅ {symbol} 配当履歴取得成功: {len(dividend_history)}年分")
                    for item in dividend_history[:3]:  # 最新3年分表示
                        print(f"   {item['year']}年: ¥{item['dividend']:.1f}")
                else:
                    print(f"⚠️  {symbol} 配当履歴なし")
                    
            except Exception as e:
                print(f"⚠️  {symbol} 配当履歴取得エラー: {e}")
        
        print("✅ データソース統合テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ データソース統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    """データベース操作テスト"""
    print("\n🧪 データベース操作テスト開始...")
    
    try:
        from database import DatabaseManager
        
        # テスト用データベース
        test_db_path = "test_portfolio.db"
        
        # 既存テストDBがあれば削除
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        db = DatabaseManager(test_db_path)
        print("✅ テストデータベース初期化成功")
        
        # ポートフォリオサマリーテスト
        summary = db.get_portfolio_summary()
        if isinstance(summary, dict):
            print("✅ ポートフォリオサマリー取得成功")
            print(f"   銘柄数: {summary.get('total_stocks', 0)}")
        else:
            print("❌ ポートフォリオサマリー取得失敗")
            return False
        
        # 保有銘柄取得テスト
        holdings = db.get_all_holdings()
        if isinstance(holdings, list):
            print(f"✅ 保有銘柄取得成功: {len(holdings)}件")
        else:
            print("❌ 保有銘柄取得失敗")
            return False
        
        # アラート履歴テスト
        alerts = db.get_alerts(10)
        if isinstance(alerts, list):
            print(f"✅ アラート履歴取得成功: {len(alerts)}件")
        else:
            print("❌ アラート履歴取得失敗")
            return False
        
        # テストDBクリーンアップ
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print("✅ テストデータベースクリーンアップ完了")
        
        print("✅ データベース操作テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ データベース操作テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("🚀 日本株ウォッチドッグ - 包括的テスト開始\n")
    
    test_results = []
    
    # 各テストを実行
    test_results.append(("配当可視化機能", test_dividend_visualizer()))
    test_results.append(("エッジケース", test_edge_cases()))
    test_results.append(("パス処理", test_path_handling()))
    test_results.append(("データソース統合", test_data_sources_integration()))
    test_results.append(("データベース操作", test_database_operations()))
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 テスト結果サマリー")
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
        print("\n🎉 全テスト合格！システムは正常に動作しています。")
        return True
    else:
        print(f"\n⚠️  {failed}件のテストが失敗しました。問題を修正してください。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)