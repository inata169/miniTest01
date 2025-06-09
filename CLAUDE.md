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
- **AlertManager**: Multi-channel notifications (email, LINE, desktop)
- **TechnicalAnalysis**: RSI, moving averages, and other indicators
- **DataSources**: Yahoo Finance API integration for free stock data

### Data Flow
1. CSV import from brokers → PortfolioManager → SQLite database
2. StockMonitor fetches Yahoo Finance data → applies strategies → triggers alerts
3. AlertManager sends notifications via configured channels

### Database Schema (SQLite)
- `holdings`: symbol, name, quantity, average_cost, current_price
- `alerts`: symbol, alert_type, message, created_at
- `price_history`: symbol, date, OHLCV data

## Important Implementation Notes

### CSV Encoding Handling
- Both SBI and Rakuten Securities export in Shift-JIS (cp932) encoding
- Always use proper encoding detection in `csv_parser.py`
- Handle Japanese characters correctly in stock names

### Free Data Sources
- **Stock prices**: Yahoo Finance (yfinance library) - no API limits
- **Financial data**: EDINET API (FSA Japan) - free government service
- **Economic indicators**: FRED API - free Federal Reserve data
- **Notifications**: Gmail SMTP, LINE Notify (1000/month free)

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