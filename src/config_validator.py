import json
import os
from typing import Dict, Any
from exceptions import ConfigError


class ConfigValidator:
    """設定ファイルのバリデーター"""
    
    def __init__(self):
        self.required_settings = {
            'database': ['path'],
            'notifications': ['email'],
            'monitoring': ['check_interval_minutes', 'market_hours_only']
        }
        
        self.required_strategies = {
            'buy_conditions': ['dividend_yield_min', 'per_max', 'pbr_max'],
            'sell_conditions': ['profit_target', 'stop_loss']
        }
    
    def validate_settings(self, config_path: str = "config/settings.json") -> bool:
        """設定ファイルをバリデーション"""
        try:
            if not os.path.exists(config_path):
                raise ConfigError(f"設定ファイルが見つかりません: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 必須セクションのチェック
            for section, keys in self.required_settings.items():
                if section not in config:
                    raise ConfigError(f"必須セクション '{section}' がありません")
                
                section_config = config[section]
                for key in keys:
                    if key not in section_config:
                        print(f"警告: '{section}.{key}' が設定されていません（デフォルト値を使用）")
            
            # 数値範囲チェック
            if 'monitoring' in config:
                interval = config['monitoring'].get('check_interval_minutes', 30)
                if not 1 <= interval <= 1440:  # 1分〜24時間
                    raise ConfigError("check_interval_minutes は1-1440の範囲で設定してください")
            
            return True
            
        except json.JSONDecodeError as e:
            raise ConfigError(f"JSON形式エラー: {e}")
        except Exception as e:
            raise ConfigError(f"設定ファイル読み込みエラー: {e}")
    
    def validate_strategies(self, config_path: str = "config/strategies.json") -> bool:
        """戦略ファイルをバリデーション"""
        try:
            if not os.path.exists(config_path):
                raise ConfigError(f"戦略ファイルが見つかりません: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                strategies = json.load(f)
            
            if not strategies:
                raise ConfigError("戦略が定義されていません")
            
            # 各戦略のバリデーション
            for strategy_name, strategy_config in strategies.items():
                for section, keys in self.required_strategies.items():
                    if section not in strategy_config:
                        raise ConfigError(f"戦略 '{strategy_name}' に必須セクション '{section}' がありません")
                    
                    section_config = strategy_config[section]
                    for key in keys:
                        if key not in section_config:
                            raise ConfigError(f"戦略 '{strategy_name}.{section}' に必須項目 '{key}' がありません")
                        
                        value = section_config[key]
                        if not isinstance(value, (int, float)):
                            raise ConfigError(f"戦略 '{strategy_name}.{section}.{key}' は数値である必要があります")
                
                # 論理チェック
                buy_conditions = strategy_config['buy_conditions']
                sell_conditions = strategy_config['sell_conditions']
                
                if buy_conditions.get('dividend_yield_min', 0) < 0:
                    raise ConfigError(f"戦略 '{strategy_name}': dividend_yield_min は0以上である必要があります")
                
                if sell_conditions.get('profit_target', 0) <= 0:
                    raise ConfigError(f"戦略 '{strategy_name}': profit_target は0より大きい値である必要があります")
                
                if sell_conditions.get('stop_loss', 0) >= 0:
                    raise ConfigError(f"戦略 '{strategy_name}': stop_loss は負の値である必要があります")
            
            return True
            
        except json.JSONDecodeError as e:
            raise ConfigError(f"JSON形式エラー: {e}")
        except Exception as e:
            raise ConfigError(f"戦略ファイル読み込みエラー: {e}")
    
    def create_default_config(self):
        """デフォルト設定ファイルを作成"""
        # settings.jsonが存在しない場合の作成処理は既に実装済み
        pass


if __name__ == "__main__":
    validator = ConfigValidator()
    try:
        validator.validate_settings()
        validator.validate_strategies()
        print("✅ 設定ファイルの検証が完了しました")
    except ConfigError as e:
        print(f"❌ 設定エラー: {e}")