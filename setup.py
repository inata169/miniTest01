#!/usr/bin/env python3
"""
日本株ウォッチドッグ セットアップスクリプト
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_python_version():
    """Python バージョンチェック"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8以上が必要です")
        print(f"現在のバージョン: {sys.version}")
        return False
    print(f"✅ Python バージョン: {sys.version_info.major}.{sys.version_info.minor}")
    return True


def install_dependencies():
    """依存関係のインストール"""
    print("📦 依存関係をインストール中...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依存関係のインストール完了")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依存関係のインストールに失敗しました")
        return False


def create_directories():
    """必要なディレクトリを作成"""
    directories = [
        "data",
        "data/csv_imports", 
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 ディレクトリ作成: {directory}")
    
    return True


def create_default_configs():
    """デフォルト設定ファイルを作成"""
    # settings.json
    settings_path = "config/settings.json"
    if not os.path.exists(settings_path):
        default_settings = {
            "database": {
                "path": "data/portfolio.db"
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipients": []
                },
                "desktop": {
                    "enabled": True
                },
                "console": {
                    "enabled": True
                }
            },
            "monitoring": {
                "check_interval_minutes": 30,
                "market_hours_only": True,
                "market_start_hour": 9,
                "market_end_hour": 15
            }
        }
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=2, ensure_ascii=False)
        print(f"⚙️  設定ファイル作成: {settings_path}")
    
    # strategies.json
    strategies_path = "config/strategies.json"
    if not os.path.exists(strategies_path):
        default_strategies = {
            "default_strategy": {
                "buy_conditions": {
                    "dividend_yield_min": 3.0,
                    "per_max": 15.0,
                    "pbr_max": 1.5
                },
                "sell_conditions": {
                    "profit_target": 20.0,
                    "stop_loss": -10.0
                }
            },
            "defensive_strategy": {
                "buy_conditions": {
                    "dividend_yield_min": 2.5,
                    "per_max": 20.0,
                    "pbr_max": 2.0
                },
                "sell_conditions": {
                    "profit_target": 15.0,
                    "stop_loss": -8.0
                }
            },
            "growth_strategy": {
                "buy_conditions": {
                    "dividend_yield_min": 1.0,
                    "per_max": 25.0,
                    "pbr_max": 3.0
                },
                "sell_conditions": {
                    "profit_target": 30.0,
                    "stop_loss": -15.0
                }
            }
        }
        
        with open(strategies_path, 'w', encoding='utf-8') as f:
            json.dump(default_strategies, f, indent=2, ensure_ascii=False)
        print(f"📊 戦略ファイル作成: {strategies_path}")
    
    return True


def validate_installation():
    """インストールの検証"""
    print("\n🔍 インストール検証中...")
    
    # 設定ファイルの検証
    try:
        sys.path.append('src')
        from config_validator import ConfigValidator
        validator = ConfigValidator()
        validator.validate_settings()
        validator.validate_strategies()
        print("✅ 設定ファイル検証完了")
    except Exception as e:
        print(f"⚠️  設定ファイル検証警告: {e}")
    
    # インポートテスト
    try:
        from src.csv_parser import CSVParser
        from src.data_sources import YahooFinanceDataSource
        from src.database import DatabaseManager
        print("✅ 主要モジュールインポート成功")
    except ImportError as e:
        print(f"❌ モジュールインポートエラー: {e}")
        return False
    
    return True


def main():
    """メイン関数"""
    print("🚀 日本株ウォッチドッグ セットアップ開始")
    print("=" * 50)
    
    # ステップごとに実行
    steps = [
        ("Python バージョンチェック", check_python_version),
        ("ディレクトリ作成", create_directories),
        ("依存関係インストール", install_dependencies),
        ("設定ファイル作成", create_default_configs),
        ("インストール検証", validate_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📌 {step_name}...")
        if not step_func():
            print(f"❌ {step_name}に失敗しました")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 セットアップ完了！")
    print("\n次のステップ:")
    print("1. CSVファイルを data/csv_imports/ フォルダに配置")
    print("2. アプリケーションを起動: python src/main.py --gui")
    print("3. 設定をカスタマイズ: config/settings.json")
    print("\n詳細は README.md をご覧ください")


if __name__ == "__main__":
    main()