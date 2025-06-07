import yfinance as yf
import pandas as pd
import requests
from typing import Dict, Optional, List
from dataclasses import dataclass
import time
from datetime import datetime, timedelta


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
        # 数字のみの場合（日本株）は .T を追加
        if symbol.isdigit():
            return f"{symbol}.T"
        # アルファベットのみで.Tが付いていない場合（米国株など）
        elif symbol.isalpha() and len(symbol) <= 5:
            # 米国株式として処理（.Tを付けない）
            return symbol
        # 既に.Tが付いている場合
        elif not symbol.endswith('.T') and symbol.isdigit():
            return f"{symbol}.T"
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
            # 404エラーは銘柄が見つからない場合なので、より分かりやすいメッセージに
            if "404" in str(e):
                print(f"銘柄が見つかりません ({symbol}): Yahoo Financeにデータがない可能性があります")
            else:
                print(f"株価取得エラー ({symbol}): {e}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockInfo]:
        """複数の株式情報を一括取得"""
        results = {}
        
        for symbol in symbols:
            stock_info = self.get_stock_info(symbol)
            if stock_info:
                results[symbol] = stock_info
            
            # レート制限対策（少し待機）
            time.sleep(0.1)
        
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
            one_year_ago = datetime.now() - timedelta(days=365)
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