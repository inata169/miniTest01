"""
市場指数取得モジュール
Market Indices Data Fetcher
"""

import requests
import time
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IndexInfo:
    """市場指数情報"""
    name: str
    value: float
    change: float
    change_percent: float
    last_updated: datetime


class MarketIndicesManager:
    """市場指数管理クラス"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5分間キャッシュ
        self.last_update = None
        
        # 指数シンボルマッピング
        self.indices = {
            'nikkei': {
                'name': '日経平均',
                'symbol': '^N225',
                'yahoo_symbol': '^N225'
            },
            'topix': {
                'name': 'TOPIX',
                'symbol': '^TPX',
                'yahoo_symbol': '^TPX'
            },
            'dow': {
                'name': 'ダウ平均',
                'symbol': '^DJI',
                'yahoo_symbol': '^DJI'
            },
            'sp500': {
                'name': 'S&P500',
                'symbol': '^GSPC',
                'yahoo_symbol': '^GSPC'
            }
        }
    
    def _is_cache_valid(self) -> bool:
        """キャッシュが有効かチェック"""
        if self.last_update is None:
            return False
        
        time_diff = time.time() - self.last_update
        return time_diff < self.cache_timeout
    
    def _fetch_from_yahoo_finance(self, symbol: str) -> Optional[IndexInfo]:
        """Yahoo Finance から指数データを取得"""
        try:
            # Yahoo Finance APIを使用（非公式）
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'chart' not in data or not data['chart']['result']:
                return None
            
            result = data['chart']['result'][0]
            meta = result['meta']
            
            current_price = meta.get('regularMarketPrice')
            previous_close = meta.get('previousClose')
            
            if current_price is None or previous_close is None:
                return None
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            # 指数名を取得
            index_name = None
            for key, info in self.indices.items():
                if info['yahoo_symbol'] == symbol:
                    index_name = info['name']
                    break
            
            if index_name is None:
                index_name = symbol
            
            return IndexInfo(
                name=index_name,
                value=current_price,
                change=change,
                change_percent=change_percent,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            print(f"Yahoo Finance指数取得エラー ({symbol}): {e}")
            return None
    
    def get_all_indices(self) -> Dict[str, IndexInfo]:
        """全ての主要指数を取得"""
        if self._is_cache_valid() and self.cache:
            return self.cache
        
        indices_data = {}
        
        for key, info in self.indices.items():
            print(f"指数取得中: {info['name']}")
            index_info = self._fetch_from_yahoo_finance(info['yahoo_symbol'])
            
            if index_info:
                indices_data[key] = index_info
            else:
                # フォールバック: ダミーデータ
                indices_data[key] = IndexInfo(
                    name=info['name'],
                    value=0.0,
                    change=0.0,
                    change_percent=0.0,
                    last_updated=datetime.now()
                )
            
            # レート制限回避のための待機
            time.sleep(0.5)
        
        # キャッシュ更新
        self.cache = indices_data
        self.last_update = time.time()
        
        return indices_data
    
    def get_index(self, index_key: str) -> Optional[IndexInfo]:
        """特定の指数を取得"""
        if index_key not in self.indices:
            return None
        
        all_indices = self.get_all_indices()
        return all_indices.get(index_key)
    
    def format_index_display(self, index_info: IndexInfo) -> str:
        """指数情報を表示用に整形"""
        if index_info.value == 0:
            return f"{index_info.name}: データ取得エラー"
        
        # 変動の符号と色分け用の絵文字
        if index_info.change > 0:
            trend_emoji = "📈"
            sign = "+"
        elif index_info.change < 0:
            trend_emoji = "📉"
            sign = ""
        else:
            trend_emoji = "➖"
            sign = ""
        
        # 数値の整形
        if index_info.name in ['日経平均', 'ダウ平均']:
            # 整数表示
            value_str = f"{index_info.value:,.0f}"
            change_str = f"{index_info.change:+,.0f}"
        else:
            # 小数点以下2桁表示
            value_str = f"{index_info.value:,.2f}"
            change_str = f"{index_info.change:+,.2f}"
        
        return f"{trend_emoji} {index_info.name}: {value_str} ({sign}{change_str}, {index_info.change_percent:+.2f}%)"


def test_market_indices():
    """テスト関数"""
    manager = MarketIndicesManager()
    
    print("=== 市場指数取得テスト ===")
    indices = manager.get_all_indices()
    
    for key, index_info in indices.items():
        display_text = manager.format_index_display(index_info)
        print(display_text)
    
    print("\n=== 個別指数取得テスト ===")
    nikkei = manager.get_index('nikkei')
    if nikkei:
        print(f"日経平均: {nikkei.value:,.0f} ({nikkei.change:+,.0f}, {nikkei.change_percent:+.2f}%)")


if __name__ == "__main__":
    test_market_indices()