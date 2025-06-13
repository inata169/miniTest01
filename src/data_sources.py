import yfinance as yf
import pandas as pd
import requests
from typing import Dict, Optional, List
from dataclasses import dataclass
import time
from datetime import datetime, timedelta
from logger import app_logger


@dataclass
class StockInfo:
    """株式情報データクラス"""
    symbol: str
    name: str
    current_price: float
    previous_close: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    last_updated: datetime = None


class YahooFinanceDataSource:
    """Yahoo Finance APIを使用した株価データ取得クラス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}
        self.cache_duration = 300  # 5分間キャッシュ
    
    def _format_japanese_symbol(self, symbol: str) -> str:
        """株式シンボルをYahoo Finance形式に変換"""
        # 既に.Tが付いている場合はそのまま
        if symbol.endswith('.T'):
            return symbol
        
        # 数字のみの場合（日本株）は .T を追加
        if symbol.isdigit():
            return f"{symbol}.T"
        
        # 数字+アルファベット（日本株の優先株など: 314A, 335A）
        elif symbol[:-1].isdigit() and symbol[-1].isalpha() and len(symbol) <= 6:
            return f"{symbol}.T"
        
        # アルファベットのみで.Tが付いていない場合（米国株など）
        elif symbol.isalpha() and len(symbol) <= 5:
            # 米国株式として処理（.Tを付けない）
            return symbol
        
        return symbol
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """キャッシュが有効かチェック"""
        if symbol not in self.cache:
            return False
        
        cached_time = self.cache[symbol].get('timestamp', 0)
        return time.time() - cached_time < self.cache_duration
    
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """株式の基本情報を取得"""
        # 疑似的なシンボルをスキップ
        if (symbol.startswith('PORTFOLIO_') or 
            symbol.startswith('FUND_') or
            symbol == 'STOCK_PORTFOLIO' or
            symbol == 'TOTAL_PORTFOLIO'):
            print(f"疑似シンボルをスキップ: {symbol}")
            return None
            
        formatted_symbol = self._format_japanese_symbol(symbol)
        
        # キャッシュチェック
        if self._is_cache_valid(formatted_symbol):
            cached_data = self.cache[formatted_symbol]['data']
            return cached_data
        
        try:
            ticker = yf.Ticker(formatted_symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty:
                print(f"株価データが取得できませんでした: {symbol}")
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change_percent = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
            
            stock_info = StockInfo(
                symbol=symbol,
                name=info.get('shortName', info.get('longName', symbol)),
                current_price=float(current_price),
                previous_close=float(previous_close),
                change_percent=change_percent,
                volume=int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0,
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                pb_ratio=info.get('priceToBook'),
                dividend_yield=info.get('dividendYield'),
                last_updated=datetime.now()
            )
            
            # キャッシュに保存
            self.cache[formatted_symbol] = {
                'data': stock_info,
                'timestamp': time.time()
            }
            
            return stock_info
            
        except Exception as e:
            # 429エラー（レート制限）の場合は特別な処理
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"レート制限エラー ({symbol}): 30秒待機してリトライします...")
                time.sleep(30)
                # リトライ1回のみ
                try:
                    ticker = yf.Ticker(formatted_symbol)
                    info = ticker.info
                    hist = ticker.history(period="2d")
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                        change_percent = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
                        
                        stock_info = StockInfo(
                            symbol=symbol,
                            name=info.get('shortName', info.get('longName', symbol)),
                            current_price=float(current_price),
                            previous_close=float(previous_close),
                            change_percent=change_percent,
                            volume=int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0,
                            market_cap=info.get('marketCap'),
                            pe_ratio=info.get('trailingPE'),
                            pb_ratio=info.get('priceToBook'),
                            dividend_yield=info.get('dividendYield'),
                            last_updated=datetime.now()
                        )
                        self.cache[formatted_symbol] = {'data': stock_info, 'timestamp': time.time()}
                        return stock_info
                except:
                    pass
                print(f"レート制限継続 ({symbol}): スキップしました")
                return None
            # 404エラーは銘柄が見つからない場合なので、より分かりやすいメッセージに
            elif "404" in str(e):
                print(f"銘柄が見つかりません ({symbol}): Yahoo Financeにデータがない可能性があります")
            else:
                print(f"株価取得エラー ({symbol}): {e}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockInfo]:
        """複数の株式情報を効率的に一括取得"""
        results = {}
        
        # キャッシュされたデータを先にチェック
        uncached_symbols = []
        for symbol in symbols:
            formatted_symbol = self._format_japanese_symbol(symbol)
            if self._is_cache_valid(formatted_symbol):
                cached_data = self.cache[formatted_symbol]['data']
                results[symbol] = cached_data
            else:
                uncached_symbols.append(symbol)
        
        # キャッシュされていないシンボルのみを取得
        if uncached_symbols:
            app_logger.info(f"株価データ取得: {len(uncached_symbols)}銘柄（キャッシュ済み: {len(results)}銘柄）")
            
            # 段階的にバッチサイズを調整（レート制限対策）
            batch_size = 1  # 一度に1銘柄のみ取得
            error_count = 0
            
            for i, symbol in enumerate(uncached_symbols):
                stock_info = self.get_stock_info(symbol)
                if stock_info:
                    results[symbol] = stock_info
                    error_count = 0  # 成功時はエラーカウントリセット
                else:
                    error_count += 1
                    
                # エラーが3回連続で発生した場合は大幅に待機時間を延長
                if error_count >= 3:
                    print(f"連続エラー発生: 60秒待機します... (残り{len(uncached_symbols)-i-1}銘柄)")
                    time.sleep(60)
                    error_count = 0
                
                # 各リクエスト間の待機時間（段階的に延長）
                if i < len(uncached_symbols) - 1:
                    if error_count > 0:
                        time.sleep(5.0)  # エラー発生時は長めに待機
                    else:
                        time.sleep(2.0)   # 通常時
        
        return results
    
    def get_dividend_info(self, symbol: str) -> Dict:
        """配当情報を取得"""
        formatted_symbol = self._format_japanese_symbol(symbol)
        
        try:
            ticker = yf.Ticker(formatted_symbol)
            dividends = ticker.dividends
            
            if dividends.empty:
                return {
                    'annual_dividend': 0,
                    'dividend_yield': 0,
                    'last_dividend_date': None
                }
            
            # 過去1年の配当合計
            one_year_ago = pd.Timestamp.now() - timedelta(days=365)
            recent_dividends = dividends[dividends.index >= one_year_ago]
            annual_dividend = recent_dividends.sum()
            
            # 現在価格での配当利回り計算
            current_price = self.get_current_price(symbol)
            dividend_yield = (annual_dividend / current_price * 100) if current_price > 0 else 0
            
            return {
                'annual_dividend': float(annual_dividend),
                'dividend_yield': dividend_yield,
                'last_dividend_date': dividends.index[-1] if not dividends.empty else None
            }
            
        except Exception as e:
            print(f"配当情報取得エラー ({symbol}): {e}")
            return {
                'annual_dividend': 0,
                'dividend_yield': 0,
                'last_dividend_date': None
            }
    
    def get_current_price(self, symbol: str) -> float:
        """現在価格のみを取得"""
        stock_info = self.get_stock_info(symbol)
        return stock_info.current_price if stock_info else 0.0
    
    def get_historical_data(self, symbol: str, period: str = "1mo") -> pd.DataFrame:
        """過去の株価データを取得"""
        formatted_symbol = self._format_japanese_symbol(symbol)
        
        try:
            ticker = yf.Ticker(formatted_symbol)
            hist = ticker.history(period=period)
            return hist
        except Exception as e:
            print(f"過去データ取得エラー ({symbol}): {e}")
            return pd.DataFrame()
    
    def is_market_open(self) -> bool:
        """東京証券取引所が開いているかチェック"""
        now = datetime.now()
        
        # 平日かチェック
        if now.weekday() >= 5:  # 土曜日=5, 日曜日=6
            return False
        
        # 取引時間チェック（9:00-11:30, 12:30-15:00）
        current_time = now.time()
        morning_start = datetime.strptime("09:00", "%H:%M").time()
        morning_end = datetime.strptime("11:30", "%H:%M").time()
        afternoon_start = datetime.strptime("12:30", "%H:%M").time()
        afternoon_end = datetime.strptime("15:00", "%H:%M").time()
        
        is_morning_session = morning_start <= current_time <= morning_end
        is_afternoon_session = afternoon_start <= current_time <= afternoon_end
        
        return is_morning_session or is_afternoon_session


if __name__ == "__main__":
    # テスト用
    data_source = YahooFinanceDataSource()
    
    # テスト銘柄
    test_symbols = ["7203", "9984", "6758"]  # トヨタ、ソフトバンクG、ソニーG
    
    print("=== 株価情報テスト ===")
    for symbol in test_symbols:
        info = data_source.get_stock_info(symbol)
        if info:
            print(f"{info.symbol}: {info.name}")
            print(f"  現在価格: ¥{info.current_price:,.0f}")
            print(f"  前日比: {info.change_percent:+.2f}%")
            print(f"  出来高: {info.volume:,}")
            if info.dividend_yield:
                print(f"  配当利回り: {info.dividend_yield*100:.2f}%")
            print()
    
    print("=== 市場開始状況 ===")
    print(f"市場オープン: {data_source.is_market_open()}")