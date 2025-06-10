# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Japanese Stock Watchdog (日本株ウォッチドッグ) - An automated system for monitoring Japanese stock market in real-time, providing buy/sell timing alerts via email/notifications based on configured conditions. Supports SBI Securities and Rakuten Securities CSV formats for portfolio management.

## Key Development Commands

```bash
# Setup virtual environment with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv (first time only)
uv venv                                           # Create virtual environment
source .venv/bin/activate                         # Activate (Linux/macOS)
# or .venv\Scripts\activate                      # Activate (Windows)

# Install dependencies
uv pip install -r requirements.txt

# Quick activation (convenience script)
./activate_env.sh

# Run GUI application (main entry point) - v1.1.0+
python3 src/main.py --gui

# Alternative run script
./run_app.sh

# Start monitoring daemon
python3 src/main.py --daemon

# Interactive mode
python3 src/main.py

# Test alert notifications (new in v1.1.0)
# Click "アラートテスト" button in GUI

# Debug utilities
python3 debug_fonts.py                           # Check available fonts
python3 debug_stock_update.py                    # Debug stock price updates

# Run tests
python -m pytest tests/

# Check version info
python3 src/version.py

# Check virtual environment status
python3 --version
pip list
```

## Architecture Overview

### Core Components
- **StockMonitor**: Real-time stock price monitoring and alert generation
- **PortfolioManager**: CSV import/parsing for SBI/Rakuten formats, portfolio tracking
- **AlertManager**: Multi-channel notifications (email, Discord, desktop)
- **TechnicalAnalysis**: RSI, moving averages, and other indicators (v1.2.0+)
- **DataSources**: Yahoo Finance API integration for free stock data
- **ChartGenerator**: Interactive chart display with technical indicators (v1.2.0+)

### Data Flow
1. CSV import from brokers → PortfolioManager → SQLite database
2. StockMonitor fetches Yahoo Finance data → applies strategies → triggers alerts
3. AlertManager sends notifications via configured channels (Discord, email, desktop)
4. TechnicalAnalysis calculates indicators → generates enhanced signals (v1.2.0+)
5. ChartGenerator displays interactive visualizations (v1.2.0+)

### Database Schema (SQLite)
- `holdings`: symbol, name, quantity, average_cost, current_price
- `alerts`: symbol, alert_type, message, created_at
- `price_history`: symbol, date, OHLCV data
- `technical_indicators`: symbol, date, rsi, macd, bollinger_bands (v1.2.0+)
- `ml_predictions`: symbol, date, predicted_price, confidence_score (v1.3.0+)

## Important Implementation Notes

### CSV Encoding Handling
- Both SBI and Rakuten Securities export in Shift-JIS (cp932) encoding
- Always use proper encoding detection in `csv_parser.py`
- Handle Japanese characters correctly in stock names

### Free Data Sources
- **Stock prices**: Yahoo Finance (yfinance library) - no API limits
- **Financial data**: EDINET API (FSA Japan) - free government service
- **Economic indicators**: FRED API - free Federal Reserve data
- **Notifications**: Gmail SMTP, Discord Webhook (unlimited/free), LINE Notify (deprecated 2025/03)

### Configuration Files
- `config/settings.json`: Application settings
- `config/watchlist.json`: Monitored stocks and strategies
- `config/strategies.json`: Buy/sell conditions per strategy
- `config/encoding_settings.json`: CSV format specifications

### Investment Strategies
- **Defensive**: Utilities, pharmaceuticals (dividend yield focus)
- **Cyclical**: Automotive, steel (P/E ratio focus)
- **Growth**: Technology stocks (momentum indicators)

## File Structure Conventions

```
src/
├── main.py                    # Entry point
├── stock_monitor.py          # Core monitoring logic
├── portfolio_manager.py      # CSV parsing & portfolio tracking
├── alert_manager.py          # Notification system
├── csv_parser.py            # SBI/Rakuten format parsers
└── gui/                     # tkinter GUI components
```

## Development Guidelines

- **Virtual Environment**: Always use uv venv for isolated dependency management
- **Package Installation**: Use `uv pip install` instead of regular pip for better performance
- **Environment Activation**: Use `./activate_env.sh` for quick activation
- Use SQLite for local data storage (no external DB required)
- Handle all text in UTF-8 internally, convert only for CSV I/O
- Implement graceful error handling for network requests
- Follow Yahoo Finance API rate limits (avoid excessive requests)
- All financial calculations should handle decimal precision carefully

## Environment Setup Notes

### GUI Dependencies
- **tkinter**: Required for GUI mode (`python3 src/main.py --gui`)
- Install on Ubuntu/Linux: `sudo apt install python3-tk`
- Usually pre-installed on Windows/macOS

### Japanese Font Support (v1.1.0+)
- **WSL/Linux**: `sudo apt install fonts-noto-cjk fonts-noto-cjk-extra`
- **Windows**: Usually pre-installed (Yu Gothic, Meiryo)
- **macOS**: Usually pre-installed (Hiragino Sans)

### Known Issues & Solutions
1. **tkinter ImportError**: Install system tkinter package
2. **pandas timeout**: Use `uv pip install --timeout 300` for slow connections
3. **WSL GUI**: Export DISPLAY=:0 for X11 forwarding
4. **Japanese font issues**: Install Noto CJK fonts on Linux
5. **Alert notification stuck**: Fixed in v1.1.0 - notifications run on main thread

## New Features in v1.1.0

### Alert System
- **Alert Test Button**: Test notification functionality
- **Alert History**: View past alerts with color coding
- **Desktop Notifications**: Improved popup notifications with emoji icons
- **Alert Types**: 💰 Buy, ✅ Profit, ⚠️ Loss, 🧪 Test

### Table Enhancements  
- **Column Sorting**: Click any column header to sort
- **Sort Indicators**: Arrow indicators show sort direction
- **Numerical Sorting**: Proper handling of currency and percentage values

### UI Improvements
- **Japanese Font Auto-detection**: Automatic selection of best available Japanese font
- **Color-coded Alerts**: Visual distinction between alert types
- **Improved Status Messages**: Better user feedback

## v1.2.0+ Development Roadmap

### 🔥 High Priority Features (Short-term Implementation)

#### 📊 Technical Indicators Enhancement
```python
# Implementation planned in src/technical_analysis.py
class TechnicalAnalysis:
    def calculate_rsi(self, prices, period=14):
        """RSI (Relative Strength Index) - Overbought/Oversold detection"""
        
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """MACD (Moving Average Convergence Divergence) - Trend reversal detection"""
        
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Bollinger Bands - Price range and volatility analysis"""
        
    def detect_golden_cross(self, short_ma, long_ma):
        """Golden Cross/Dead Cross detection for moving averages"""
```

#### 📈 Chart Display Features
```python
# Implementation planned in src/chart_generator.py
class ChartGenerator:
    def create_candlestick_chart(self, symbol, timeframe='1d'):
        """Interactive candlestick chart with technical indicators overlay"""
        
    def add_technical_indicators(self, chart, indicators=['RSI', 'MACD']):
        """Add technical indicators to existing chart"""
        
    def detect_chart_patterns(self, ohlcv_data):
        """Automatic detection of chart patterns (double top, head & shoulders, etc.)"""
```

#### ⚡ Real-time Monitoring Enhancement
- **Monitoring Interval Reduction**: Current 30min → 1min (during market hours)
- **Tick-level Updates**: Second-by-second monitoring for major stocks
- **Order Book Monitoring**: Bid/ask spread and depth change detection
- **Volume Spike Detection**: Immediate alerts for abnormal volume increases

### 🧠 Medium Priority Features (Mid-term Implementation)

#### 🤖 Machine Learning Prediction System
```python
# Implementation planned in src/ml_predictor.py
class MLPredictor:
    def lstm_price_prediction(self, historical_data, forecast_days=5):
        """LSTM-based stock price prediction"""
        
    def reinforcement_learning_strategy(self, portfolio_data):
        """RL-based optimal entry/exit timing"""
        
    def sentiment_analysis(self, news_data, social_media_data):
        """News and social media sentiment analysis"""
```

#### 📈 Backtesting Framework
```python
# Implementation planned in src/backtest_engine.py
class BacktestEngine:
    def run_strategy_backtest(self, strategy, start_date, end_date):
        """Strategy performance testing on historical data"""
        
    def calculate_risk_metrics(self, returns):
        """Sharpe ratio, max drawdown, VaR calculation"""
        
    def optimize_parameters(self, strategy, parameter_ranges):
        """Parameter optimization for strategy improvement"""
```

#### 🎯 Advanced Condition System
```python
# Enhanced strategy configuration format
{
  "advanced_strategy": {
    "buy_conditions": {
      "logical_operator": "AND",
      "conditions": [
        {"type": "technical", "indicator": "RSI", "operator": "<", "value": 30},
        {"type": "technical", "indicator": "MACD", "operator": "cross_above", "value": "signal"},
        {"type": "volume", "operator": ">", "value": "average_20d * 2"},
        {"type": "time_series", "condition": "3_consecutive_days", "direction": "up"}
      ]
    },
    "custom_script": "rsi < 30 and macd_histogram > 0 and volume > sma_volume_20 * 1.5"
  }
}
```

### 🌐 Low Priority Features (Long-term Implementation)

#### 🌐 Web UI Development
- **Technology Stack**: FastAPI + React/Vue.js
- **Real-time Dashboard**: WebSocket-based live updates
- **Mobile Responsive**: Optimized for smartphones and tablets
- **Cloud Synchronization**: Automatic settings and data backup

#### 🔗 External Integration Enhancement
- **Brokerage APIs**: Official API integration when available
- **Economic Data**: Automatic import of economic indicators
- **News Integration**: Real-time news analysis and correlation
- **Social Media**: Twitter/Reddit investment sentiment tracking

## Implementation Timeline

### Phase 1: Foundation Enhancement (v1.2.0 - July-August 2025)
```
Week 1-2: Technical indicators (RSI, MACD, Bollinger Bands)
Week 3-4: Chart display (Candlestick, interactive operations)
Week 5-6: Real-time monitoring enhancement (1-minute intervals)
Week 7-8: Testing, debugging, documentation
```

### Phase 2: Advanced Analysis (v1.3.0 - September-October 2025)
```
Week 1-2: Backtesting framework implementation
Week 3-4: Machine learning foundation (price prediction models)
Week 5-6: Advanced condition setting system
Week 7-8: Performance optimization and stability improvement
```

### Phase 3: Platform Expansion (v1.4.0 - November-December 2025)
```
Week 1-2: Web UI foundation
Week 3-4: External API integration
Week 5-6: Mobile app consideration
Week 7-8: Integration testing and release preparation
```

## Technology Stack Expansion

### New Dependencies (v1.2.0+)
```bash
# Technical Analysis & Charting
pip install ta-lib
pip install mplfinance
pip install plotly

# Machine Learning (v1.3.0+)
pip install scikit-learn
pip install tensorflow
pip install pandas-ta

# Web UI (v1.4.0+)
pip install fastapi
pip install websockets
pip install jinja2
```

### File Structure Extension
```
src/
├── technical_analysis.py     # Technical indicators calculation
├── chart_generator.py        # Interactive chart generation
├── ml_predictor.py          # Machine learning predictions (v1.3.0+)
├── backtest_engine.py       # Strategy backtesting (v1.3.0+)
├── web/                     # Web UI components (v1.4.0+)
│   ├── api/                 # FastAPI endpoints
│   ├── static/              # CSS, JS, images
│   └── templates/           # HTML templates
└── strategies/              # Enhanced strategy definitions
    ├── technical_strategies.py
    ├── ml_strategies.py
    └── custom_strategies.py
```