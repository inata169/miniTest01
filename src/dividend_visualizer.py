"""
配当推移可視化モジュール
J Quants APIから取得した配当履歴データをグラフで表示
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from logger import app_logger

# 日本語フォント設定（WSL対応）
import matplotlib
import warnings

# フォント警告を抑制
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

try:
    # WSL環境では利用可能なフォントを確認
    available_fonts = matplotlib.font_manager.get_font_names()
    
    # 優先順位でフォントを選択
    preferred_fonts = [
        'DejaVu Sans',      # 基本フォント（英数字）
        'Liberation Sans',   # WSLで利用可能
        'Arial',            # Windows標準
        'sans-serif'        # フォールバック
    ]
    
    selected_font = 'DejaVu Sans'  # デフォルト
    for font in preferred_fonts:
        if font in available_fonts or font == 'sans-serif':
            selected_font = font
            break
    
    plt.rcParams['font.family'] = [selected_font]
    plt.rcParams['font.sans-serif'] = [selected_font, 'DejaVu Sans', 'Liberation Sans', 'Arial']
    
    # 日本語文字対応（必要に応じて）
    plt.rcParams['axes.unicode_minus'] = False
    
    # フォント警告を無効化
    matplotlib.font_manager._log.setLevel('ERROR')
    
except Exception as e:
    # フォント設定が失敗した場合はデフォルトを使用
    plt.rcParams['font.family'] = ['DejaVu Sans']
    print(f"フォント設定警告: {e}")
    pass

class DividendVisualizer:
    """配当推移可視化クラス"""
    
    def __init__(self):
        self.figure_size = (12, 8)
        self.colors = {
            'dividend_bar': '#2E8B57',      # 配当棒グラフ
            'growth_line': '#FF6347',       # 成長率ライン
            'trend_line': '#4169E1',        # トレンドライン
            'grid': '#E0E0E0',              # グリッド
            'background': '#F8F8FF'         # 背景
        }
    
    def create_dividend_chart(self, symbol: str, dividend_history: List[Dict], 
                            current_price: float = None, save_path: str = None) -> str:
        """配当推移チャートを作成"""
        if not dividend_history:
            app_logger.warning(f"配当履歴データなし: {symbol}")
            return None
        
        try:
            # データ準備
            df = pd.DataFrame(dividend_history)
            df = df.sort_values('year')
            
            # グラフ作成
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figure_size, 
                                         facecolor=self.colors['background'])
            fig.suptitle(f'{symbol} Dividend Trend Analysis', fontsize=16, fontweight='bold')
            
            # 上段：配当金額推移
            self._plot_dividend_amount(ax1, df, symbol, current_price)
            
            # 下段：配当成長率推移
            self._plot_dividend_growth(ax2, df, symbol)
            
            # レイアウト調整
            plt.tight_layout()
            
            # 保存またはファイルパス生成
            if save_path:
                file_path = save_path
            else:
                # プロジェクトルートの絶対パスを取得
                import os
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                charts_dir = os.path.join(project_root, 'charts')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(charts_dir, f"dividend_{symbol}_{timestamp}.png")
            
            # ディレクトリ作成
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            plt.savefig(file_path, dpi=300, bbox_inches='tight', 
                       facecolor=self.colors['background'])
            plt.close()
            
            app_logger.info(f"配当チャート作成完了: {file_path}")
            return file_path
            
        except Exception as e:
            app_logger.error(f"配当チャート作成エラー ({symbol}): {e}")
            return None
    
    def _plot_dividend_amount(self, ax, df, symbol, current_price):
        """配当金額推移をプロット"""
        years = df['year'].values
        dividends = df['dividend'].values
        
        # 棒グラフ
        bars = ax.bar(years, dividends, color=self.colors['dividend_bar'], 
                     alpha=0.7, edgecolor='white', linewidth=1)
        
        # トレンドライン
        if len(years) > 1:
            z = np.polyfit(years, dividends, 1)
            trend_line = np.poly1d(z)
            ax.plot(years, trend_line(years), color=self.colors['trend_line'], 
                   linewidth=2, linestyle='--', label='Trend')
        
        # 数値ラベル
        for bar, dividend in zip(bars, dividends):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'¥{dividend:.1f}', ha='center', va='bottom', fontsize=10)
        
        # 配当利回り表示（現在価格がある場合）
        if current_price and len(dividends) > 0:
            latest_dividend = dividends[-1]
            dividend_yield = (latest_dividend / current_price) * 100
            ax.text(0.02, 0.98, f'Latest Yield: {dividend_yield:.2f}%', 
                   transform=ax.transAxes, va='top', 
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # グラフ設定
        ax.set_title('Annual Dividend Trend', fontsize=14, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Dividend (JPY)', fontsize=12)
        ax.grid(True, color=self.colors['grid'], alpha=0.7)
        ax.set_facecolor(self.colors['background'])
        
        # Y軸範囲調整
        if len(dividends) > 0:
            ax.set_ylim(0, max(dividends) * 1.1)
    
    def _plot_dividend_growth(self, ax, df, symbol):
        """配当成長率推移をプロット"""
        if len(df) < 2:
            ax.text(0.5, 0.5, 'Need 2+ years of data for growth rate calculation', 
                   transform=ax.transAxes, ha='center', va='center', fontsize=12)
            ax.set_title('Dividend Growth Rate Trend', fontsize=14, fontweight='bold')
            return
        
        years = df['year'].values[1:]  # 成長率は2年目から
        dividends = df['dividend'].values
        growth_rates = []
        
        # 成長率計算
        for i in range(1, len(dividends)):
            if dividends[i-1] > 0:
                growth_rate = ((dividends[i] - dividends[i-1]) / dividends[i-1]) * 100
                growth_rates.append(growth_rate)
            else:
                growth_rates.append(0)
        
        # 折れ線グラフ
        ax.plot(years, growth_rates, color=self.colors['growth_line'], 
               linewidth=3, marker='o', markersize=8, label='Growth Rate')
        
        # ゼロライン
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # 数値ラベル
        for year, growth in zip(years, growth_rates):
            ax.text(year, growth + (max(growth_rates) - min(growth_rates)) * 0.05,
                   f'{growth:+.1f}%', ha='center', va='bottom' if growth >= 0 else 'top', 
                   fontsize=10, fontweight='bold')
        
        # 平均成長率表示
        avg_growth = np.mean(growth_rates)
        ax.text(0.02, 0.98, f'Avg Growth: {avg_growth:+.2f}%/year', 
               transform=ax.transAxes, va='top',
               bbox=dict(boxstyle='round', 
                        facecolor='lightgreen' if avg_growth > 0 else 'lightcoral', 
                        alpha=0.8))
        
        # 成長トレンド評価
        trend_text = self._evaluate_dividend_trend(growth_rates)
        ax.text(0.02, 0.88, trend_text, transform=ax.transAxes, va='top',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # グラフ設定
        ax.set_title('Dividend Growth Rate Trend', fontsize=14, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Growth Rate (%)', fontsize=12)
        ax.grid(True, color=self.colors['grid'], alpha=0.7)
        ax.set_facecolor(self.colors['background'])
    
    def _evaluate_dividend_trend(self, growth_rates: List[float]) -> str:
        """配当成長トレンドを評価"""
        if not growth_rates:
            return "No Data"
        
        positive_count = sum(1 for rate in growth_rates if rate > 0)
        total_count = len(growth_rates)
        positive_ratio = positive_count / total_count if total_count > 0 else 0
        avg_growth = np.mean(growth_rates)
        
        if positive_ratio >= 0.8 and avg_growth > 5:
            return "Excellent Growth"
        elif positive_ratio >= 0.6 and avg_growth > 0:
            return "Stable Growth"
        elif avg_growth > 0:
            return "Modest Growth"
        elif avg_growth > -5:
            return "Stable Dividend"
        else:
            return "Declining Trend"
    
    def create_comparison_chart(self, stocks_data: Dict[str, List[Dict]], 
                              save_path: str = None) -> str:
        """複数銘柄の配当比較チャートを作成"""
        try:
            fig, ax = plt.subplots(figsize=self.figure_size, 
                                 facecolor=self.colors['background'])
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
            
            for i, (symbol, dividend_history) in enumerate(stocks_data.items()):
                if not dividend_history:
                    continue
                
                df = pd.DataFrame(dividend_history).sort_values('year')
                years = df['year'].values
                dividends = df['dividend'].values
                
                color = colors[i % len(colors)]
                ax.plot(years, dividends, marker='o', linewidth=2, 
                       label=symbol, color=color, markersize=6)
            
            ax.set_title('Dividend Comparison by Stock', fontsize=16, fontweight='bold')
            ax.set_xlabel('Year', fontsize=12)
            ax.set_ylabel('Dividend (JPY)', fontsize=12)
            ax.legend(loc='upper left')
            ax.grid(True, color=self.colors['grid'], alpha=0.7)
            ax.set_facecolor(self.colors['background'])
            
            if save_path:
                file_path = save_path
            else:
                # プロジェクトルートの絶対パスを取得
                import os
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                charts_dir = os.path.join(project_root, 'charts')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(charts_dir, f"dividend_comparison_{timestamp}.png")
            
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            plt.tight_layout()
            plt.savefig(file_path, dpi=300, bbox_inches='tight', 
                       facecolor=self.colors['background'])
            plt.close()
            
            app_logger.info(f"配当比較チャート作成完了: {file_path}")
            return file_path
            
        except Exception as e:
            app_logger.error(f"配当比較チャート作成エラー: {e}")
            return None


def test_dividend_visualizer():
    """配当可視化機能のテスト"""
    # サンプルデータ
    sample_data = [
        {'year': 2020, 'dividend': 85.0, 'date': '2020-12-31'},
        {'year': 2021, 'dividend': 90.0, 'date': '2021-12-31'},
        {'year': 2022, 'dividend': 92.0, 'date': '2022-12-31'},
        {'year': 2023, 'dividend': 95.0, 'date': '2023-12-31'},
        {'year': 2024, 'dividend': 100.0, 'date': '2024-12-31'},
    ]
    
    visualizer = DividendVisualizer()
    chart_path = visualizer.create_dividend_chart('7203', sample_data, current_price=2800)
    
    if chart_path:
        print(f"Test chart created: {chart_path}")
    else:
        print("Test chart creation failed")


if __name__ == "__main__":
    test_dividend_visualizer()