import yfinance as yf
import pandas as pd
import requests
from typing import Dict, Optional, List
from dataclasses import dataclass
import time
from datetime import datetime, timedelta
from logger import app_logger
import numpy as np
try:
    from jquantsapi import Client as JQuantsClient
    JQUANTS_AVAILABLE = True
except ImportError:
    JQUANTS_AVAILABLE = False
    app_logger.warning("J Quants API client not available. Install with: pip install jquants-api-client")


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
    roe: Optional[float] = None
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
                dividend_yield=info.get('dividendYield') if info.get('dividendYield') else None,
                roe=info.get('returnOnEquity') * 100 if info.get('returnOnEquity') else None,
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
                            dividend_yield=info.get('dividendYield') if info.get('dividendYield') else None,
                            roe=info.get('returnOnEquity') * 100 if info.get('returnOnEquity') else None,
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
            
            # 配当データが異常に多い場合の対策（通常は年4回程度）
            if len(dividends) > 50:
                # 最近の1年分のみ使用
                one_year_ago = pd.Timestamp.now() - timedelta(days=365)
                recent_dividends = dividends[dividends.index >= one_year_ago]
            else:
                # 最新の配当4回分を使用（四半期配当想定）
                recent_dividends = dividends.tail(4)
            
            annual_dividend = recent_dividends.sum()
            
            # 現在価格での配当利回り計算（ticker再利用で効率化）
            try:
                current_data = ticker.history(period="1d", interval="1d")
                if not current_data.empty:
                    current_price = float(current_data['Close'].iloc[-1])
                    
                    # 配当利回りの妥当性チェック
                    if annual_dividend > 0 and current_price > 0:
                        raw_yield = (annual_dividend / current_price * 100)
                        # 異常値の場合は0にリセット（15%超は異常値として扱う）
                        dividend_yield = raw_yield if raw_yield <= 15.0 else 0
                    else:
                        dividend_yield = 0
                else:
                    dividend_yield = 0
            except:
                dividend_yield = 0
            
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


class JQuantsDataSource:
    """J Quants API対応データソース（日本株専用・無料）"""
    
    def __init__(self, email: str = None, password: str = None, refresh_token: str = None):
        if not JQUANTS_AVAILABLE:
            raise ImportError("J Quants API client not installed")
        
        self.client = None
        self.email = email
        self.password = password
        self.refresh_token = refresh_token
        self.cache = {}
        self.cache_duration = 300  # 5分間キャッシュ
        
        # 認証情報がある場合は初期化
        if refresh_token or (email and password):
            self._initialize_client()
    
    def _initialize_client(self):
        """J Quants APIクライアントを初期化"""
        try:
            if self.refresh_token:
                # トークン認証（推奨）
                app_logger.info(f"J Quants API認証試行中（トークン長: {len(self.refresh_token)}文字）")
                self.client = JQuantsClient(refresh_token=self.refresh_token)
                app_logger.info("J Quants APIクライアント初期化完了（トークン）")
            elif self.email and self.password:
                # メール/パスワード認証
                app_logger.info(f"J Quants API認証試行中（メール: {self.email}）")
                self.client = JQuantsClient(mail_address=self.email, password=self.password)
                app_logger.info("J Quants API認証成功（メール/パスワード）")
            else:
                app_logger.warning("J Quants API認証情報不足")
                self.client = None
        except Exception as e:
            app_logger.error(f"J Quants API認証失敗: {e}")
            self.client = None
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """キャッシュが有効かチェック"""
        if symbol not in self.cache:
            return False
        cached_time = self.cache[symbol].get('timestamp', 0)
        return time.time() - cached_time < self.cache_duration
    
    def _format_jquants_symbol(self, symbol: str) -> str:
        """J Quants API用銘柄コード変換（4桁→5桁）"""
        # 4桁の場合は末尾に0を追加
        if len(symbol) == 4 and symbol.isdigit():
            return symbol + "0"
        return symbol
    
    def _is_japanese_stock(self, symbol: str) -> bool:
        """日本株かどうかを判定"""
        # 疑似シンボルは日本株ではない
        if (symbol.startswith('PORTFOLIO_') or 
            symbol.startswith('FUND_') or
            symbol == 'STOCK_PORTFOLIO' or
            symbol == 'TOTAL_PORTFOLIO' or
            len(symbol) > 10):
            return False
        
        # 数字のみの場合は日本株
        if symbol.isdigit() and len(symbol) == 4:
            return True
        
        # 数字+アルファベット1文字の場合は日本株の優先株
        if len(symbol) == 5 and symbol[:4].isdigit() and symbol[4].isalpha():
            return True
        
        # アルファベットのみの場合は米国株
        if symbol.isalpha():
            return False
        
        # その他の場合は日本株として扱う
        return True
    
    def _safe_float_conversion(self, value, field_name: str) -> Optional[float]:
        """安全な数値変換"""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                if value.strip() == '' or value.strip() == '-':
                    return None
                # カンマを除去して数値変換
                value = value.replace(',', '')
            return float(value)
        except (ValueError, TypeError):
            app_logger.warning(f"数値変換エラー ({field_name}): {value}")
            return None

    def _get_financial_metrics(self, jquants_code: str, current_price: float) -> tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """J Quants APIから財務指標を取得（PER、PBR、ROE、配当利回り）"""
        try:
            # 財務データ取得
            fins_response = self.client.get_fins_statements(code=jquants_code)
            
            pe_ratio = None
            pb_ratio = None
            roe = None
            dividend_yield = None
            
            # DataFrameレスポンスの処理
            if hasattr(fins_response, 'empty'):
                if not fins_response.empty:
                    latest_fin = fins_response.iloc[-1]
                else:
                    app_logger.warning(f"財務データが空: {jquants_code}")
                    return None, None, None, None
                
                # 直接取得可能な指標
                pe_ratio = self._safe_float_conversion(latest_fin.get('PriceEarningsRatio'), 'PER')
                pb_ratio = self._safe_float_conversion(latest_fin.get('PriceBookValueRatio'), 'PBR') 
                roe = self._safe_float_conversion(latest_fin.get('RateOfReturnOnEquity'), 'ROE')
                
                # 配当利回り（直接取得または計算）
                dividend_yield_direct = self._safe_float_conversion(latest_fin.get('DividendYieldAnnual'), '配当利回り直接')
                if dividend_yield_direct:
                    dividend_yield = dividend_yield_direct
                else:
                    # 配当から計算
                    annual_dividend = self._safe_float_conversion(latest_fin.get('ResultDividendPerShareAnnual'), '年間配当実績')
                    if not annual_dividend:
                        annual_dividend = self._safe_float_conversion(latest_fin.get('ForecastDividendPerShareAnnual'), '年間配当予想')
                    
                    if annual_dividend and annual_dividend > 0 and current_price > 0:
                        dividend_yield = (annual_dividend / current_price) * 100
                
                # 直接取得できない場合の計算フォールバック
                if not pe_ratio:
                    eps = self._safe_float_conversion(latest_fin.get('EarningsPerShare'), 'EPS')
                    if eps and eps > 0 and current_price > 0:
                        pe_ratio = current_price / eps
                
                if not pb_ratio:
                    bps = self._safe_float_conversion(latest_fin.get('BookValuePerShare'), 'BPS')
                    if bps and bps > 0 and current_price > 0:
                        pb_ratio = current_price / bps
                
                if not roe:
                    # ROE = 純利益 / 自己資本 * 100
                    net_income = self._safe_float_conversion(latest_fin.get('NetIncome'), '純利益')
                    equity = self._safe_float_conversion(latest_fin.get('Equity'), '自己資本')
                    if net_income and equity and equity > 0:
                        roe = (net_income / equity) * 100
                        
            elif isinstance(fins_response, dict) and 'statements' in fins_response:
                statements = fins_response['statements']
                if statements:
                    latest_fin = statements[-1]
                    
                    # 同様の処理をdict形式でも実行
                    pe_ratio = self._safe_float_conversion(latest_fin.get('PriceEarningsRatio'), 'PER')
                    pb_ratio = self._safe_float_conversion(latest_fin.get('PriceBookValueRatio'), 'PBR')
                    roe = self._safe_float_conversion(latest_fin.get('RateOfReturnOnEquity'), 'ROE')
                    
                    # 配当利回り
                    dividend_yield_direct = self._safe_float_conversion(latest_fin.get('DividendYieldAnnual'), '配当利回り直接')
                    if dividend_yield_direct:
                        dividend_yield = dividend_yield_direct
                    else:
                        annual_dividend = self._safe_float_conversion(latest_fin.get('ResultDividendPerShareAnnual'), '年間配当実績')
                        if not annual_dividend:
                            annual_dividend = self._safe_float_conversion(latest_fin.get('ForecastDividendPerShareAnnual'), '年間配当予想')
                        
                        if annual_dividend and annual_dividend > 0 and current_price > 0:
                            dividend_yield = (annual_dividend / current_price) * 100
            
            app_logger.info(f"財務データ取得: {jquants_code} PER={pe_ratio}, PBR={pb_ratio}, ROE={roe}%, 配当利回り={dividend_yield}%")
            return pe_ratio, pb_ratio, roe, dividend_yield
            
        except Exception as e:
            app_logger.warning(f"財務データ取得エラー ({jquants_code}): {e}")
            return None, None, None, None

    def get_dividend_history(self, symbol: str, years: int = 5) -> List[Dict]:
        """過去の配当履歴を取得"""
        if not self._is_japanese_stock(symbol):
            return []
            
        if not self.client:
            app_logger.warning("J Quants API未認証のため配当履歴取得不可")
            return []
        
        try:
            jquants_code = self._format_jquants_symbol(symbol)
            
            # 財務データ取得（複数年分）
            fins_response = self.client.get_fins_statements(code=jquants_code)
            
            dividend_history = []
            
            # DataFrameレスポンスの処理
            if hasattr(fins_response, 'empty'):
                if fins_response.empty:
                    app_logger.warning(f"配当履歴データが空: {jquants_code}")
                    return []
                    
                # 最新から指定年数分のデータを取得
                try:
                    # カラム名を確認して適切な日付カラムを使用
                    date_column = None
                    for col in ['Date', 'DisclosedDate', 'AnnouncementDate', 'ReportDate']:
                        if col in fins_response.columns:
                            date_column = col
                            break
                    
                    if date_column:
                        df = fins_response.sort_values(date_column, ascending=False)
                        recent_data = df.head(years * 4)  # 四半期データ想定で年数×4
                    else:
                        available_cols = list(fins_response.columns)
                        app_logger.warning(f"日付カラムが見つかりません ({jquants_code})")
                        app_logger.info(f"利用可能カラム: {available_cols[:10]}...")  # 最初の10個のみ表示
                        # 日付ソートなしで最新データを使用
                        recent_data = fins_response.tail(years * 4)
                        
                except Exception as e:
                    app_logger.error(f"DataFrame処理エラー ({jquants_code}): {e}")
                    return []
                
                # 年度別に配当データを集計
                yearly_dividends = {}
                for _, row in recent_data.iterrows():
                    try:
                        # 複数の日付カラムを試行
                        date_value = None
                        for col in [date_column, 'Date', 'DisclosedDate', 'AnnouncementDate', 'ReportDate']:
                            if col and col in row and pd.notna(row[col]):
                                date_value = row[col]
                                break
                        
                        if date_value is None:
                            continue
                            
                        # 日付から年度を抽出
                        if isinstance(date_value, pd.Timestamp):
                            year = date_value.year
                            date_str = date_value.strftime('%Y-%m-%d')
                        else:
                            date_str = str(date_value)
                            if len(date_str) >= 4:
                                year = int(date_str[:4])
                            else:
                                continue
                        
                        annual_dividend = self._safe_float_conversion(row.get('ResultDividendPerShareAnnual'), '年間配当')
                        
                        if annual_dividend and annual_dividend > 0:
                            if year not in yearly_dividends or yearly_dividends[year]['dividend'] < annual_dividend:
                                yearly_dividends[year] = {
                                    'year': year,
                                    'dividend': annual_dividend,
                                    'date': date_str
                                }
                    except (ValueError, TypeError) as e:
                        app_logger.debug(f"行処理エラー ({jquants_code}): {e}")
                        continue
                
                # リストに変換してソート
                dividend_history = sorted(yearly_dividends.values(), key=lambda x: x['year'], reverse=True)
                
            elif isinstance(fins_response, dict) and 'statements' in fins_response:
                statements = fins_response['statements']
                yearly_dividends = {}
                
                for statement in statements[-years*4:]:  # 最近のデータのみ
                    try:
                        # 複数の日付フィールドを試行
                        date_value = None
                        for date_field in ['Date', 'DisclosedDate', 'AnnouncementDate', 'ReportDate']:
                            if date_field in statement and statement[date_field]:
                                date_value = statement[date_field]
                                break
                        
                        if date_value is None:
                            continue
                        
                        # 日付から年度を抽出
                        if isinstance(date_value, (pd.Timestamp, pd.Timedelta)):
                            year = date_value.year
                            date_str = date_value.strftime('%Y-%m-%d')
                        else:
                            date_str = str(date_value)
                            if len(date_str) >= 4:
                                year = int(date_str[:4])
                            else:
                                continue
                        
                        annual_dividend = self._safe_float_conversion(statement.get('ResultDividendPerShareAnnual'), '年間配当')
                        
                        if annual_dividend and annual_dividend > 0:
                            if year not in yearly_dividends or yearly_dividends[year]['dividend'] < annual_dividend:
                                yearly_dividends[year] = {
                                    'year': year,
                                    'dividend': annual_dividend,
                                    'date': date_str
                                }
                    except (ValueError, TypeError) as e:
                        app_logger.debug(f"statement処理エラー: {e}")
                        continue
                
                dividend_history = sorted(yearly_dividends.values(), key=lambda x: x['year'], reverse=True)
            
            app_logger.info(f"配当履歴取得: {symbol} - {len(dividend_history)}年分")
            return dividend_history
            
        except Exception as e:
            app_logger.error(f"配当履歴取得エラー ({symbol}): {e}")
            return []

    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """J Quants APIから株価情報を取得"""
        # 日本株以外はスキップ
        if not self._is_japanese_stock(symbol):
            app_logger.info(f"J Quants API: 日本株以外をスキップ ({symbol})")
            return None
            
        if not self.client:
            app_logger.warning("J Quants API未認証のため無料モードで実行")
            return self._get_stock_info_free(symbol)
        
        # キャッシュチェック
        if self._is_cache_valid(symbol):
            return self.cache[symbol]['data']
        
        try:
            # J Quants API用銘柄コード変換
            jquants_code = self._format_jquants_symbol(symbol)
            app_logger.info(f"J Quants API: {symbol} → {jquants_code}")
            
            # J Quants APIで株価取得
            prices_response = self.client.get_prices_daily_quotes(code=jquants_code)
            
            # DataFrameレスポンスの処理
            if hasattr(prices_response, 'empty'):
                if prices_response.empty:
                    app_logger.warning(f"J Quants API: DataFrameが空 ({symbol})")
                    return None
                quotes = [prices_response.iloc[-1].to_dict()]  # 最新行をdictに変換
            elif isinstance(prices_response, dict) and 'daily_quotes' in prices_response:
                quotes = prices_response['daily_quotes']
                if not quotes:
                    app_logger.warning(f"J Quants API: データなし ({symbol})")
                    return None
            else:
                app_logger.warning(f"J Quants API: 未知のレスポンス形式 ({symbol})")
                return None
            
            # 最新データを取得
            latest_quote = quotes[-1]
            previous_quote = quotes[-2] if len(quotes) > 1 else latest_quote
            
            # 株式情報取得（同じコード変換を適用）
            info_response = self.client.get_listed_info(code=jquants_code)
            company_name = symbol  # デフォルト
            
            # DataFrameレスポンスの処理
            if hasattr(info_response, 'empty'):
                if not info_response.empty:
                    company_name = info_response.iloc[0].get('CompanyName', symbol)
            elif isinstance(info_response, dict) and 'listed_info' in info_response:
                listed_info = info_response['listed_info']
                if listed_info and len(listed_info) > 0:
                    company_name = listed_info[0].get('CompanyName', symbol)
            
            # 財務データを取得
            pe_ratio, pb_ratio, roe, dividend_yield = self._get_financial_metrics(jquants_code, float(latest_quote.get('Close', 0)))
            
            # StockInfo作成
            current_price = latest_quote.get('Close', 0)
            previous_close = previous_quote.get('Close', current_price)
            change_percent = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
            
            stock_info = StockInfo(
                symbol=symbol,
                name=company_name,
                current_price=float(current_price),
                previous_close=float(previous_close),
                change_percent=change_percent,
                volume=int(latest_quote.get('Volume', 0)),
                market_cap=None,  # J Quants APIから取得可能だが実装省略
                pe_ratio=pe_ratio,
                pb_ratio=pb_ratio,
                dividend_yield=dividend_yield,
                roe=roe,
                last_updated=datetime.now()
            )
            
            # キャッシュに保存
            self.cache[symbol] = {
                'data': stock_info,
                'timestamp': time.time()
            }
            
            app_logger.info(f"J Quants API取得成功: {symbol}")
            return stock_info
            
        except Exception as e:
            app_logger.error(f"J Quants API取得エラー ({symbol}): {e}")
            return None
    
    def _get_stock_info_free(self, symbol: str) -> Optional[StockInfo]:
        """無料プランでのデータ取得（制限あり）"""
        try:
            # J Quants APIの無料プランは認証が必要なため、
            # 認証情報がない場合はすぐにフォールバックする
            app_logger.info(f"J Quants API無料モード: 認証情報不足のためスキップ ({symbol})")
            return None
            
        except Exception as e:
            app_logger.error(f"J Quants API無料モードエラー ({symbol}): {e}")
            return None
    
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockInfo]:
        """複数銘柄の一括取得"""
        results = {}
        for symbol in symbols:
            stock_info = self.get_stock_info(symbol)
            if stock_info:
                results[symbol] = stock_info
            time.sleep(0.1)  # レート制限対策
        return results


class RakutenRSSDataSource:
    """楽天証券MarketSpeed RSS対応データソース"""
    
    def __init__(self, rss_url: str = None):
        self.rss_url = rss_url or "https://marketspeed.jp/rss/"
        self.session = requests.Session()
        
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """楽天証券RSSから株価情報を取得"""
        try:
            # 楽天証券RSS形式のURL構築
            url = f"{self.rss_url}?symbol={symbol}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # RSS/XMLパース処理（実装は楽天証券の仕様に依存）
                # 現在はプレースホルダー
                app_logger.info(f"楽天証券RSS取得成功: {symbol}")
                return None  # 実装待ち
            else:
                app_logger.warning(f"楽天証券RSS取得失敗: {symbol} (Status: {response.status_code})")
                return None
                
        except Exception as e:
            app_logger.error(f"楽天証券RSS取得エラー ({symbol}): {e}")
            return None


class MultiDataSource:
    """複数データソースのフォールバック機能"""
    
    def __init__(self, jquants_email: str = None, jquants_password: str = None, refresh_token: str = None):
        self.sources = []
        
        # J Quants APIを第一選択（利用可能な場合）
        if JQUANTS_AVAILABLE:
            try:
                jquants_source = JQuantsDataSource(jquants_email, jquants_password, refresh_token)
                self.sources.append(jquants_source)
                app_logger.info("J Quants APIをプライマリデータソースに設定")
            except Exception as e:
                app_logger.warning(f"J Quants API初期化失敗: {e}")
        
        # Yahoo Financeをフォールバック
        self.sources.append(YahooFinanceDataSource())
        
        # 楽天証券RSSをセカンダリフォールバック
        self.sources.append(RakutenRSSDataSource())
        
        self.primary_source = 0  # 最初に成功したソースを主力に
        
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """複数ソースから株価情報を取得（ハイブリッド取得対応）"""
        primary_info = None
        fallback_info = None
        
        # 日本株の場合はJ Quants APIを優先、米国株はYahoo Financeを優先
        is_japanese = self._is_japanese_stock(symbol)
        
        for i, source in enumerate(self.sources):
            try:
                stock_info = source.get_stock_info(symbol)
                if stock_info:
                    if isinstance(source, JQuantsDataSource) and is_japanese:
                        primary_info = stock_info
                        app_logger.info(f"J Quants API取得成功: {symbol}")
                        break
                    elif isinstance(source, YahooFinanceDataSource):
                        fallback_info = stock_info
                        if not is_japanese:
                            app_logger.info(f"Yahoo Finance取得成功（米国株）: {symbol}")
                            return stock_info
                            
            except Exception as e:
                app_logger.warning(f"データソース {source.__class__.__name__} 失敗 ({symbol}): {e}")
                continue
        
        # 日本株でJ Quants APIから基本データを取得した場合、不足している財務データをYahoo Financeで補完
        if primary_info and is_japanese:
            if (primary_info.pe_ratio is None or 
                primary_info.pb_ratio is None or 
                primary_info.dividend_yield is None):
                
                app_logger.info(f"財務データ補完開始: {symbol}")
                primary_info = self._supplement_financial_data(primary_info, fallback_info)
            
            return primary_info
        
        # フォールバックデータがある場合はそれを返す
        if fallback_info:
            app_logger.info(f"フォールバック使用: {symbol}")
            return fallback_info
        
        app_logger.error(f"全データソース失敗: {symbol}")
        return None
    
    def _is_japanese_stock(self, symbol: str) -> bool:
        """日本株かどうかを判定"""
        # 疑似シンボルは日本株ではない
        if (symbol.startswith('PORTFOLIO_') or 
            symbol.startswith('FUND_') or
            symbol == 'STOCK_PORTFOLIO' or
            symbol == 'TOTAL_PORTFOLIO'):
            return False
        
        # 数字のみの場合は日本株
        if symbol.isdigit() and len(symbol) == 4:
            return True
        
        # 数字+アルファベット1文字の場合は日本株の優先株
        if len(symbol) == 5 and symbol[:4].isdigit() and symbol[4].isalpha():
            return True
        
        # アルファベットのみの場合は米国株
        if symbol.isalpha():
            return False
        
        return True
    
    def _supplement_financial_data(self, primary_info: StockInfo, fallback_info: Optional[StockInfo]) -> StockInfo:
        """不足している財務データをフォールバックデータで補完"""
        if not fallback_info:
            return primary_info
        
        # 不足データを補完
        if primary_info.pe_ratio is None and fallback_info.pe_ratio is not None:
            primary_info.pe_ratio = fallback_info.pe_ratio
            app_logger.info(f"PER補完: {primary_info.symbol} = {primary_info.pe_ratio}")
        
        if primary_info.pb_ratio is None and fallback_info.pb_ratio is not None:
            primary_info.pb_ratio = fallback_info.pb_ratio
            app_logger.info(f"PBR補完: {primary_info.symbol} = {primary_info.pb_ratio}")
        
        if primary_info.dividend_yield is None and fallback_info.dividend_yield is not None:
            primary_info.dividend_yield = fallback_info.dividend_yield
            app_logger.info(f"配当利回り補完: {primary_info.symbol} = {primary_info.dividend_yield}%")
        
        return primary_info
    
    def get_dividend_history(self, symbol: str, years: int = 5) -> List[Dict]:
        """配当履歴を取得（J Quants API優先）"""
        is_japanese = self._is_japanese_stock(symbol)
        
        # 日本株の場合はJ Quants APIを試行
        if is_japanese and JQUANTS_AVAILABLE:
            for source in self.sources:
                if isinstance(source, JQuantsDataSource):
                    try:
                        dividend_history = source.get_dividend_history(symbol, years)
                        if dividend_history:
                            app_logger.info(f"J Quants API配当履歴取得成功: {symbol}")
                            return dividend_history
                    except Exception as e:
                        app_logger.warning(f"J Quants API配当履歴取得失敗 ({symbol}): {e}")
        
        # フォールバック：Yahoo Financeで配当履歴を取得
        try:
            yahoo_source = None
            for source in self.sources:
                if isinstance(source, YahooFinanceDataSource):
                    yahoo_source = source
                    break
            
            if yahoo_source:
                dividend_info = yahoo_source.get_dividend_info(symbol)
                if dividend_info and dividend_info.get('annual_dividend', 0) > 0:
                    # Yahoo Financeからは単年データのみ取得可能
                    return [{
                        'year': datetime.now().year,
                        'dividend': dividend_info['annual_dividend'],
                        'date': str(dividend_info.get('last_dividend_date', ''))
                    }]
        except Exception as e:
            app_logger.warning(f"Yahoo Finance配当履歴取得失敗 ({symbol}): {e}")
        
        app_logger.warning(f"配当履歴取得失敗: {symbol}")
        return []
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockInfo]:
        """複数銘柄の一括取得"""
        results = {}
        for symbol in symbols:
            stock_info = self.get_stock_info(symbol)
            if stock_info:
                results[symbol] = stock_info
        return results
    
    def is_market_open(self) -> bool:
        """市場オープン状況チェック（第一ソースに委譲）"""
        if self.sources:
            primary_source = self.sources[0]
            if hasattr(primary_source, 'is_market_open'):
                return primary_source.is_market_open()
        return False


if __name__ == "__main__":
    # テスト用 - 環境変数から認証情報を読み込み
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    jquants_email = os.getenv('JQUANTS_EMAIL')
    jquants_password = os.getenv('JQUANTS_PASSWORD')
    refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
    
    data_source = MultiDataSource(jquants_email, jquants_password, refresh_token)
    
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