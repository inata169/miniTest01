# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Japanese Stock Watchdog (日本株ウォッチドッグ) - An automated system for monitoring Japanese stock market in real-time, providing buy/sell timing alerts via email/notifications based on configured conditions. Supports SBI Securities and Rakuten Securities CSV formats for portfolio management.

## Key Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initial setup
python src/setup.py

# Run GUI application
python src/gui/main_window.py

# Start monitoring daemon
python src/main.py --daemon

# Run tests (when implemented)
python -m pytest tests/
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

- Use SQLite for local data storage (no external DB required)
- Handle all text in UTF-8 internally, convert only for CSV I/O
- Implement graceful error handling for network requests
- Follow Yahoo Finance API rate limits (avoid excessive requests)
- All financial calculations should handle decimal precision carefully