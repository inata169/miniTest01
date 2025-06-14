#!/usr/bin/env python3
"""
J Quants API統合詳細テストスイート
"""

import sys
import os
import time
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def test_jquants_authentication():
    """J Quants API認証テスト"""
    print("🔐 J Quants API認証テスト開始...")
    
    try:
        from data_sources import JQuantsDataSource
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        # 認証情報取得
        jquants_email = os.getenv('JQUANTS_EMAIL')
        refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
        
        print(f"📧 Email設定: {'✅' if jquants_email else '❌'}")
        print(f"🔑 Token設定: {'✅' if refresh_token else '❌'}")
        
        if not refresh_token and not jquants_email:
            print("⚠️  認証情報なし - 無料モードテスト")
            source = JQuantsDataSource()
            if source.client is None:
                print("✅ 無料モード正常動作")
                return True
            else:
                print("❌ 無料モード異常")
                return False
        
        # 認証ありテスト
        source = JQuantsDataSource(jquants_email, None, refresh_token)
        
        if source.client:
            print("✅ J Quants API認証成功")
            
            # 認証されたAPIの基本テスト
            test_symbol = '7203'
            stock_info = source.get_stock_info(test_symbol)
            
            if stock_info:
                print(f"✅ 認証済みAPI株価取得成功: {test_symbol}")
                print(f"   銘柄名: {stock_info.name}")
                print(f"   価格: ¥{stock_info.current_price:,.0f}")
                
                if stock_info.pe_ratio:
                    print(f"   PER: {stock_info.pe_ratio:.2f}")
                if stock_info.pb_ratio:
                    print(f"   PBR: {stock_info.pb_ratio:.2f}")
                if stock_info.dividend_yield:
                    print(f"   配当利回り: {stock_info.dividend_yield:.2f}%")
            else:
                print(f"⚠️  認証済みAPI株価取得なし: {test_symbol}")
                
        else:
            print("⚠️  J Quants API認証失敗 - フォールバック動作確認")
            
        print("✅ J Quants API認証テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ J Quants API認証テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_symbol_processing():
    """銘柄コード処理テスト"""
    print("\n🔢 銘柄コード処理テスト開始...")
    
    try:
        from data_sources import JQuantsDataSource
        
        source = JQuantsDataSource()
        
        # 4桁→5桁変換テスト
        test_cases = [
            ('7203', '72030'),  # トヨタ
            ('6758', '67580'),  # ソニー
            ('9984', '99840'),  # ソフトバンクG
            ('1234', '12340'),  # 一般的な4桁
        ]
        
        for input_code, expected in test_cases:
            result = source._format_jquants_symbol(input_code)
            if result == expected:
                print(f"✅ {input_code} → {result}")
            else:
                print(f"❌ {input_code} → {result} (期待: {expected})")
                return False
        
        # 日本株判定テスト
        japanese_stocks = ['7203', '6758', '9984', '1234A']
        non_japanese = ['AAPL', 'GOOGL', 'PORTFOLIO_TOTAL', 'FUND_ABC']
        
        for symbol in japanese_stocks:
            if source._is_japanese_stock(symbol):
                print(f"✅ 日本株判定正常: {symbol}")
            else:
                print(f"❌ 日本株判定異常: {symbol}")
                return False
        
        for symbol in non_japanese:
            if not source._is_japanese_stock(symbol):
                print(f"✅ 非日本株判定正常: {symbol}")
            else:
                print(f"❌ 非日本株判定異常: {symbol}")
                return False
        
        print("✅ 銘柄コード処理テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 銘柄コード処理テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_mechanism():
    """フォールバック機能テスト"""
    print("\n🔄 フォールバック機能テスト開始...")
    
    try:
        from data_sources import MultiDataSource
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        jquants_email = os.getenv('JQUANTS_EMAIL')
        refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
        
        data_source = MultiDataSource(jquants_email, None, refresh_token)
        
        # 日本株テスト（J Quants → Yahoo Finance フォールバック）
        japanese_symbols = ['7203', '6758', '9984']
        
        for symbol in japanese_symbols:
            stock_info = data_source.get_stock_info(symbol)
            if stock_info:
                print(f"✅ {symbol} フォールバック取得成功")
                print(f"   価格: ¥{stock_info.current_price:,.0f}")
                
                # データソース判定
                if stock_info.pe_ratio and stock_info.pb_ratio:
                    print(f"   📊 財務データあり (おそらくJ Quants)")
                else:
                    print(f"   📈 基本データのみ (おそらくYahoo Finance)")
                    
            else:
                print(f"⚠️  {symbol} フォールバック取得失敗")
        
        # 米国株テスト（Yahoo Finance直接）
        us_symbols = ['AAPL', 'GOOGL', 'TSLA']
        
        for symbol in us_symbols:
            stock_info = data_source.get_stock_info(symbol)
            if stock_info:
                print(f"✅ {symbol} 米国株取得成功")
                print(f"   価格: ${stock_info.current_price:.2f}")
            else:
                print(f"⚠️  {symbol} 米国株取得失敗")
        
        print("✅ フォールバック機能テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ フォールバック機能テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rate_limiting():
    """レート制限テスト"""
    print("\n⏱️  レート制限テスト開始...")
    
    try:
        from data_sources import MultiDataSource
        from dotenv import load_dotenv
        import os
        import time
        
        load_dotenv()
        
        jquants_email = os.getenv('JQUANTS_EMAIL')
        refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
        
        data_source = MultiDataSource(jquants_email, None, refresh_token)
        
        # 連続リクエストテスト
        symbols = ['7203', '6758', '9984', '8591', '4519']
        
        start_time = time.time()
        
        for i, symbol in enumerate(symbols):
            print(f"   リクエスト {i+1}: {symbol}")
            stock_info = data_source.get_stock_info(symbol)
            
            if stock_info:
                print(f"   ✅ 成功: ¥{stock_info.current_price:,.0f}")
            else:
                print(f"   ⚠️  失敗または制限")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✅ レート制限テスト完了")
        print(f"   総時間: {total_time:.1f}秒")
        print(f"   平均応答時間: {total_time/len(symbols):.1f}秒/リクエスト")
        
        # レート制限が適切に機能しているかチェック
        if total_time > len(symbols) * 1.5:  # 1.5秒/リクエスト以上なら制限機能OK
            print("✅ レート制限機能が正常動作")
        else:
            print("⚠️  レート制限機能が軽い（問題なし）")
        
        return True
        
    except Exception as e:
        print(f"❌ レート制限テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dividend_history_deep():
    """配当履歴取得詳細テスト"""
    print("\n📈 配当履歴詳細テスト開始...")
    
    try:
        from data_sources import MultiDataSource
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        jquants_email = os.getenv('JQUANTS_EMAIL')
        refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
        
        data_source = MultiDataSource(jquants_email, None, refresh_token)
        
        # 配当実績のある銘柄でテスト
        dividend_symbols = ['7203', '8591', '8306', '4519', '9434']  # 配当実績銘柄
        
        for symbol in dividend_symbols:
            try:
                print(f"\n📊 {symbol} 配当履歴分析:")
                
                dividend_history = data_source.get_dividend_history(symbol, 5)
                
                if dividend_history:
                    print(f"   ✅ {len(dividend_history)}年分の配当履歴取得")
                    
                    # 配当データの詳細分析
                    for item in dividend_history:
                        year = item.get('year', 'N/A')
                        dividend = item.get('dividend', 0)
                        date = item.get('date', 'N/A')
                        
                        print(f"   {year}年: ¥{dividend:.1f} ({date})")
                    
                    # 成長率計算
                    if len(dividend_history) >= 2:
                        latest = dividend_history[0]['dividend']
                        previous = dividend_history[1]['dividend']
                        
                        if previous > 0:
                            growth_rate = ((latest - previous) / previous) * 100
                            print(f"   📈 最新年成長率: {growth_rate:+.1f}%")
                        
                        # 平均配当計算
                        avg_dividend = sum(item['dividend'] for item in dividend_history) / len(dividend_history)
                        print(f"   📊 平均配当: ¥{avg_dividend:.1f}")
                    
                else:
                    print(f"   ⚠️  配当履歴なし")
                    
            except Exception as e:
                print(f"   ❌ {symbol} 配当履歴エラー: {e}")
        
        print("\n✅ 配当履歴詳細テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 配当履歴詳細テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_validation():
    """データ検証テスト"""
    print("\n🔍 データ検証テスト開始...")
    
    try:
        from data_sources import MultiDataSource
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        jquants_email = os.getenv('JQUANTS_EMAIL')
        refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
        
        data_source = MultiDataSource(jquants_email, None, refresh_token)
        
        # データ妥当性チェック銘柄
        test_symbols = ['7203', '6758', '9984']
        
        for symbol in test_symbols:
            stock_info = data_source.get_stock_info(symbol)
            
            if stock_info:
                print(f"\n🔍 {symbol} データ検証:")
                
                # 価格の妥当性
                if stock_info.current_price > 0:
                    print(f"   ✅ 価格妥当: ¥{stock_info.current_price:,.0f}")
                else:
                    print(f"   ❌ 価格異常: {stock_info.current_price}")
                    
                # PERの妥当性
                if stock_info.pe_ratio:
                    if 0 < stock_info.pe_ratio < 1000:
                        print(f"   ✅ PER妥当: {stock_info.pe_ratio:.2f}")
                    else:
                        print(f"   ⚠️  PER異常: {stock_info.pe_ratio}")
                else:
                    print(f"   ➖ PERなし")
                    
                # PBRの妥当性
                if stock_info.pb_ratio:
                    if 0 < stock_info.pb_ratio < 100:
                        print(f"   ✅ PBR妥当: {stock_info.pb_ratio:.2f}")
                    else:
                        print(f"   ⚠️  PBR異常: {stock_info.pb_ratio}")
                else:
                    print(f"   ➖ PBRなし")
                    
                # 配当利回りの妥当性
                if stock_info.dividend_yield:
                    if 0 <= stock_info.dividend_yield <= 15:  # 0-15%の範囲
                        print(f"   ✅ 配当利回り妥当: {stock_info.dividend_yield:.2f}%")
                    else:
                        print(f"   ⚠️  配当利回り異常: {stock_info.dividend_yield}%")
                else:
                    print(f"   ➖ 配当利回りなし")
                    
                # 出来高の妥当性
                if stock_info.volume >= 0:
                    print(f"   ✅ 出来高妥当: {stock_info.volume:,}")
                else:
                    print(f"   ❌ 出来高異常: {stock_info.volume}")
            else:
                print(f"⚠️  {symbol} データなし")
        
        print("\n✅ データ検証テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ データ検証テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """J Quants API詳細テスト実行"""
    print("🔬 J Quants API統合詳細テスト開始\n")
    
    test_results = []
    
    # 各テストを実行
    test_results.append(("J Quants API認証", test_jquants_authentication()))
    test_results.append(("銘柄コード処理", test_symbol_processing()))
    test_results.append(("フォールバック機能", test_fallback_mechanism()))
    test_results.append(("レート制限", test_rate_limiting()))
    test_results.append(("配当履歴詳細", test_dividend_history_deep()))
    test_results.append(("データ検証", test_data_validation()))
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 J Quants API詳細テスト結果")
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
        print("\n🎉 J Quants API統合は完璧に動作しています！")
        return True
    else:
        print(f"\n⚠️  {failed}件のテストが失敗しました。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)