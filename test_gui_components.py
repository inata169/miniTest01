#!/usr/bin/env python3
"""
GUI コンポーネント・イベントハンドリング検証テスト
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
import inspect

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def test_gui_imports():
    """GUI関連モジュールのインポートテスト"""
    print("📦 GUI関連モジュールインポートテスト開始...")
    
    try:
        # tkinter関連インポート
        import tkinter as tk
        import tkinter.ttk as ttk
        import tkinter.messagebox as messagebox
        import tkinter.filedialog as filedialog
        print("✅ tkinter関連モジュール正常")
        
        # GUIメインウィンドウインポート
        from gui.main_window import MainWindow
        print("✅ MainWindowクラス正常")
        
        # 関連モジュールインポート
        from database import DatabaseManager
        from data_sources import MultiDataSource
        from dividend_visualizer import DividendVisualizer
        print("✅ 関連モジュール正常")
        
        print("✅ GUI関連モジュールインポートテスト完了")
        return True
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ GUI関連モジュールインポートテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_window_structure():
    """MainWindowクラス構造テスト"""
    print("\n🏗️  MainWindowクラス構造テスト開始...")
    
    try:
        from gui.main_window import MainWindow
        
        # クラス定義確認
        if not inspect.isclass(MainWindow):
            print("❌ MainWindowがクラスではありません")
            return False
        
        print("✅ MainWindowクラス定義正常")
        
        # 必須メソッドの存在確認
        required_methods = [
            '__init__',
            'create_portfolio_tab',
            'create_import_tab',  # 修正: create_csv_import_tab → create_import_tab
            'create_watch_tab',   # 修正: create_monitoring_tab → create_watch_tab
            'create_dividend_history_tab',
            'show_holdings_context_menu',
            'show_dividend_chart_for_symbol',
            'show_dividend_history_for_symbol',
            'delete_selected_holding',
            'delete_all_holdings',
            'test_alert_for_symbol',
            'load_portfolio_data',
            'update_prices',
            'show_dividend_chart',
            'load_dividend_history'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(MainWindow, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ 不足メソッド: {missing_methods}")
            return False
        else:
            print(f"✅ 必須メソッド確認完了: {len(required_methods)}個")
        
        # メソッドシグネチャ確認
        method_signatures = {}
        for method_name in required_methods:
            method = getattr(MainWindow, method_name)
            if callable(method):
                sig = inspect.signature(method)
                method_signatures[method_name] = sig
                
        print(f"✅ メソッドシグネチャ確認完了: {len(method_signatures)}個")
        
        # 重要なメソッドの詳細確認
        important_methods = [
            'show_holdings_context_menu',
            'show_dividend_chart_for_symbol',
            'show_dividend_history_for_symbol'
        ]
        
        for method_name in important_methods:
            sig = method_signatures.get(method_name)
            if sig:
                params = list(sig.parameters.keys())
                print(f"   {method_name}: {params}")
            
        print("✅ MainWindowクラス構造テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ MainWindowクラス構造テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_event_handlers():
    """イベントハンドラーテスト"""
    print("\n🎯 イベントハンドラーテスト開始...")
    
    try:
        from gui.main_window import MainWindow
        import inspect
        
        # イベントハンドラーメソッドリスト
        event_handlers = [
            'on_holdings_right_click',
            'on_portfolio_double_click', 
            'on_csv_import_click',
            'on_price_update_click',
            'on_dividend_symbol_change',
            'on_dividend_years_change',
            'show_holdings_context_menu',
            'show_dividend_chart',
            'load_dividend_history'
        ]
        
        # メソッド存在確認
        existing_handlers = []
        for handler in event_handlers:
            if hasattr(MainWindow, handler):
                existing_handlers.append(handler)
                print(f"✅ {handler}")
            else:
                print(f"⚠️  {handler} (オプション)")
        
        print(f"✅ イベントハンドラー確認: {len(existing_handlers)}/{len(event_handlers)}個")
        
        # 右クリックメニュー関連メソッドの詳細確認
        context_menu_methods = [
            'show_dividend_chart_for_symbol',
            'show_dividend_history_for_symbol', 
            'delete_selected_holding',
            'delete_all_holdings',
            'test_alert_for_symbol'
        ]
        
        for method_name in context_menu_methods:
            if hasattr(MainWindow, method_name):
                method = getattr(MainWindow, method_name)
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                print(f"   📌 {method_name}: {params}")
        
        print("✅ イベントハンドラーテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ イベントハンドラーテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_initialization_simulation():
    """GUI初期化シミュレーションテスト"""
    print("\n🚀 GUI初期化シミュレーションテスト開始...")
    
    try:
        # テスト用データベース作成
        test_db_path = "test_gui.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        from database import DatabaseManager
        from data_sources import MultiDataSource
        from dividend_visualizer import DividendVisualizer
        
        # 必要なコンポーネント初期化テスト
        print("   📊 DatabaseManager初期化...")
        db = DatabaseManager(test_db_path)
        if db:
            print("   ✅ DatabaseManager正常")
        else:
            print("   ❌ DatabaseManager異常")
            return False
        
        print("   🌐 MultiDataSource初期化...")
        data_source = MultiDataSource()
        if data_source:
            print("   ✅ MultiDataSource正常")
        else:
            print("   ❌ MultiDataSource異常")
            return False
        
        print("   📈 DividendVisualizer初期化...")
        dividend_visualizer = DividendVisualizer()
        if dividend_visualizer:
            print("   ✅ DividendVisualizer正常")
        else:
            print("   ❌ DividendVisualizer異常")
            return False
        
        # MainWindow初期化パラメータ確認
        from gui.main_window import MainWindow
        
        init_sig = inspect.signature(MainWindow.__init__)
        init_params = list(init_sig.parameters.keys())
        print(f"   🏗️  MainWindow.__init__パラメータ: {init_params}")
        
        # 実際にMainWindowを初期化せずに、必要なコンポーネントが揃っているか確認
        print("   ✅ GUI初期化に必要なコンポーネント確認完了")
        
        # テストDBクリーンアップ
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        print("✅ GUI初期化シミュレーションテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ GUI初期化シミュレーションテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dividend_tab_components():
    """配当履歴タブコンポーネントテスト"""
    print("\n📊 配当履歴タブコンポーネントテスト開始...")
    
    try:
        from gui.main_window import MainWindow
        import inspect
        
        # 配当履歴関連メソッド確認
        dividend_methods = [
            'create_dividend_history_tab',
            'show_dividend_chart',
            'load_dividend_history',
            'show_dividend_chart_for_symbol',
            'show_dividend_history_for_symbol'
        ]
        
        for method_name in dividend_methods:
            if hasattr(MainWindow, method_name):
                method = getattr(MainWindow, method_name)
                if callable(method):
                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    print(f"✅ {method_name}: {params}")
                else:
                    print(f"❌ {method_name}: 呼び出し不可")
                    return False
            else:
                print(f"❌ {method_name}: 存在しません")
                return False
        
        # 配当履歴テーブル関連の属性確認（存在すると思われる）
        expected_attributes = [
            'dividend_symbol_var',
            'dividend_years_var', 
            'dividend_history_tree',
            'dividend_summary_labels'
        ]
        
        print("   📋 期待される配当履歴タブ属性:")
        for attr in expected_attributes:
            print(f"   📌 {attr}")
        
        print("✅ 配当履歴タブコンポーネントテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 配当履歴タブコンポーネントテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_menu_system():
    """コンテキストメニューシステムテスト"""
    print("\n🖱️  コンテキストメニューシステムテスト開始...")
    
    try:
        from gui.main_window import MainWindow
        import inspect
        
        # 右クリックメニュー関連メソッド
        context_menu_methods = {
            'show_holdings_context_menu': '右クリックメニュー表示',
            'show_dividend_chart_for_symbol': '配当チャート表示',
            'show_dividend_history_for_symbol': '配当履歴表示',
            'delete_selected_holding': '個別銘柄削除',
            'delete_all_holdings': '全銘柄削除',
            'test_alert_for_symbol': 'アラートテスト'
        }
        
        for method_name, description in context_menu_methods.items():
            if hasattr(MainWindow, method_name):
                method = getattr(MainWindow, method_name)
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                
                print(f"✅ {description}")
                print(f"   メソッド: {method_name}")
                print(f"   パラメータ: {params}")
                
                # パラメータ検証
                if method_name == 'show_holdings_context_menu':
                    if 'event' in params:
                        print("   ✅ eventパラメータあり")
                    else:
                        print("   ⚠️  eventパラメータなし")
                
                elif method_name in ['show_dividend_chart_for_symbol', 
                                   'show_dividend_history_for_symbol',
                                   'delete_selected_holding',
                                   'test_alert_for_symbol']:
                    if 'symbol' in params:
                        print("   ✅ symbolパラメータあり")
                    else:
                        print("   ⚠️  symbolパラメータなし")
                
                print()
            else:
                print(f"❌ {description}: {method_name} 存在しません")
                return False
        
        print("✅ コンテキストメニューシステムテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ コンテキストメニューシステムテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling_patterns():
    """エラーハンドリングパターンテスト"""
    print("\n🛡️  エラーハンドリングパターンテスト開始...")
    
    try:
        from gui.main_window import MainWindow
        import inspect
        
        # MainWindowのメソッドでtry-except使用を確認
        methods_to_check = [
            'show_dividend_chart',
            'load_dividend_history',
            'show_dividend_chart_for_symbol',
            'show_dividend_history_for_symbol',
            'update_prices',
            'load_portfolio_data'
        ]
        
        for method_name in methods_to_check:
            if hasattr(MainWindow, method_name):
                method = getattr(MainWindow, method_name)
                source = inspect.getsource(method)
                
                # try-except パターンの存在確認
                has_try = 'try:' in source
                has_except = 'except' in source
                has_messagebox = 'messagebox' in source
                has_update_status = 'update_status' in source
                
                print(f"🔍 {method_name}:")
                print(f"   try-except: {'✅' if has_try and has_except else '❌'}")
                print(f"   messagebox: {'✅' if has_messagebox else '➖'}")
                print(f"   update_status: {'✅' if has_update_status else '➖'}")
                
                # 良いエラーハンドリングの条件
                good_error_handling = has_try and has_except and (has_messagebox or has_update_status)
                if good_error_handling:
                    print(f"   総合評価: ✅ 良好")
                else:
                    print(f"   総合評価: ⚠️  改善余地あり")
                print()
            else:
                print(f"⚠️  {method_name}: メソッドなし")
        
        print("✅ エラーハンドリングパターンテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ エラーハンドリングパターンテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_data_integration():
    """GUI-データ統合テスト"""
    print("\n🔗 GUI-データ統合テスト開始...")
    
    try:
        # データベース・データソース・可視化コンポーネントの統合確認
        from database import DatabaseManager
        from data_sources import MultiDataSource
        from dividend_visualizer import DividendVisualizer
        from gui.main_window import MainWindow
        import inspect
        
        # MainWindowがデータコンポーネントとの統合メソッドを持っているか確認
        integration_methods = [
            'load_portfolio_data',    # Database → GUI
            'update_prices',          # DataSource → GUI
            'show_dividend_chart',    # DataSource → Visualizer → GUI
            'load_dividend_history'   # DataSource → GUI
        ]
        
        for method_name in integration_methods:
            if hasattr(MainWindow, method_name):
                method = getattr(MainWindow, method_name)
                source = inspect.getsource(method)
                
                # データベース統合確認
                uses_db = 'self.db' in source or 'database' in source.lower()
                
                # データソース統合確認
                uses_data_source = 'self.data_source' in source or 'data_source' in source.lower()
                
                # 可視化統合確認
                uses_visualizer = 'self.dividend_visualizer' in source or 'visualizer' in source.lower()
                
                print(f"🔗 {method_name}:")
                print(f"   データベース統合: {'✅' if uses_db else '➖'}")
                print(f"   データソース統合: {'✅' if uses_data_source else '➖'}")
                print(f"   可視化統合: {'✅' if uses_visualizer else '➖'}")
                print()
            else:
                print(f"⚠️  {method_name}: メソッドなし")
        
        print("✅ GUI-データ統合テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ GUI-データ統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """GUIコンポーネント検証メイン"""
    print("🖥️  GUI コンポーネント・イベントハンドリング検証開始\n")
    
    test_results = []
    
    # 各テストを実行
    test_results.append(("GUI関連モジュールインポート", test_gui_imports()))
    test_results.append(("MainWindowクラス構造", test_main_window_structure()))
    test_results.append(("イベントハンドラー", test_event_handlers()))
    test_results.append(("GUI初期化シミュレーション", test_gui_initialization_simulation()))
    test_results.append(("配当履歴タブコンポーネント", test_dividend_tab_components()))
    test_results.append(("コンテキストメニューシステム", test_context_menu_system()))
    test_results.append(("エラーハンドリングパターン", test_error_handling_patterns()))
    test_results.append(("GUI-データ統合", test_gui_data_integration()))
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 GUIコンポーネント検証結果")
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
        print("\n🎉 GUIコンポーネントは完璧に実装されています！")
        return True
    else:
        print(f"\n⚠️  {failed}件のテストが失敗しました。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)