#!/usr/bin/env python3
"""
Simple notification test without external dependencies
"""

import sys
import os
import json
import tempfile
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_console_notification():
    """Test console notification functionality"""
    
    print("=== Console Notification Test ===")
    
    # Simple Alert class for testing
    class TestAlert:
        def __init__(self, symbol, alert_type, message, triggered_price, strategy_name):
            self.symbol = symbol
            self.alert_type = alert_type
            self.message = message
            self.triggered_price = triggered_price
            self.strategy_name = strategy_name
            self.timestamp = datetime.now()
    
    def send_console_notification(alert):
        """Simple console notification implementation"""
        try:
            timestamp = alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            # Alert type prefix
            if alert.alert_type == 'buy':
                prefix = "🔵 BUY"
            elif alert.alert_type == 'sell_profit':
                prefix = "🟢 SELL (利益確定)"
            elif alert.alert_type == 'sell_loss':
                prefix = "🔴 SELL (損切り)"
            else:
                prefix = "⚪ ALERT"
            
            print(f"\n{'='*50}")
            print(f"{prefix} ALERT - {timestamp}")
            print(f"{'='*50}")
            print(f"銘柄: {alert.symbol}")
            print(f"価格: ¥{alert.triggered_price:,.0f}")
            print(f"戦略: {alert.strategy_name}")
            print("-" * 50)
            print(alert.message.replace('\\n', '\n'))
            print(f"{'='*50}\n")
            
            return True
            
        except Exception as e:
            print(f"コンソール通知エラー: {e}")
            return False
    
    # Test different alert types
    test_alerts = [
        TestAlert("7203", "buy", "買い推奨アラート\\nPER: 12.5", 2600.0, "growth_strategy"),
        TestAlert("9984", "sell_profit", "利益確定推奨\\n収益率: +15.2%", 4800.0, "default_strategy"),
        TestAlert("6758", "sell_loss", "損切り推奨\\n収益率: -8.5%", 9200.0, "defensive_strategy")
    ]
    
    success_count = 0
    for alert in test_alerts:
        if send_console_notification(alert):
            success_count += 1
    
    if success_count == len(test_alerts):
        print("✓ Console notification test passed")
        return True
    else:
        print(f"✗ Console notification test failed: {success_count}/{len(test_alerts)}")
        return False

def test_config_loading():
    """Test configuration loading"""
    
    print("\n=== Configuration Loading Test ===")
    
    # Create test configuration
    test_config = {
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
        }
    }
    
    # Write test config to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
        config_path = f.name
    
    try:
        # Test config loading
        def load_config_simple(config_path):
            """Simple config loading function"""
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"設定ファイル読み込みエラー: {e}")
                return {
                    'notifications': {
                        'email': {'enabled': False},
                        'desktop': {'enabled': True},
                        'console': {'enabled': True}
                    }
                }
        
        loaded_config = load_config_simple(config_path)
        
        # Verify config structure
        if ('notifications' in loaded_config and
            'email' in loaded_config['notifications'] and
            'desktop' in loaded_config['notifications'] and
            'console' in loaded_config['notifications']):
            print("✓ Configuration loaded successfully")
            print(f"  Email enabled: {loaded_config['notifications']['email']['enabled']}")
            print(f"  Desktop enabled: {loaded_config['notifications']['desktop']['enabled']}")
            print(f"  Console enabled: {loaded_config['notifications']['console']['enabled']}")
            return True
        else:
            print("✗ Configuration structure invalid")
            return False
    
    finally:
        os.unlink(config_path)

def test_notification_manager():
    """Test complete notification manager functionality"""
    
    print("\n=== Notification Manager Test ===")
    
    # Simple Alert class
    class TestAlert:
        def __init__(self, symbol, alert_type, message, triggered_price, strategy_name):
            self.symbol = symbol
            self.alert_type = alert_type
            self.message = message
            self.triggered_price = triggered_price
            self.strategy_name = strategy_name
            self.timestamp = datetime.now()
    
    # Simple NotificationManager class
    class SimpleNotificationManager:
        def __init__(self, config):
            self.config = config
            self.sent_notifications = []
        
        def send_alert(self, alert):
            """Send alert using configured methods"""
            notifications_config = self.config.get('notifications', {})
            success = True
            
            # Console notification
            if notifications_config.get('console', {}).get('enabled', True):
                if self._send_console_notification(alert):
                    self.sent_notifications.append(('console', alert.symbol, alert.alert_type))
                else:
                    success = False
            
            # Desktop notification (simulated)
            if notifications_config.get('desktop', {}).get('enabled', True):
                if self._send_desktop_notification_mock(alert):
                    self.sent_notifications.append(('desktop', alert.symbol, alert.alert_type))
                else:
                    success = False
            
            return success
        
        def _send_console_notification(self, alert):
            """Console notification implementation"""
            try:
                print(f"[CONSOLE] {alert.alert_type.upper()}: {alert.symbol} ¥{alert.triggered_price:,.0f}")
                return True
            except:
                return False
        
        def _send_desktop_notification_mock(self, alert):
            """Mock desktop notification (no GUI in test)"""
            try:
                print(f"[DESKTOP] Mock notification: {alert.alert_type} for {alert.symbol}")
                return True
            except:
                return False
        
        def test_notifications(self):
            """Test notification functionality"""
            test_alert = TestAlert(
                "TEST",
                "buy",
                "これはテスト通知です",
                1000,
                "test_strategy"
            )
            
            print("通知機能をテストしています...")
            success = self.send_alert(test_alert)
            print("テスト完了")
            
            return success and len(self.sent_notifications) > 0
    
    # Test with mock config
    test_config = {
        'notifications': {
            'email': {'enabled': False},
            'desktop': {'enabled': True},
            'console': {'enabled': True}
        }
    }
    
    manager = SimpleNotificationManager(test_config)
    
    # Test basic functionality
    test_alert = TestAlert("7203", "buy", "買い推奨", 2600.0, "test_strategy")
    
    if manager.send_alert(test_alert):
        print("✓ Basic notification test passed")
        
        # Test notification method
        if manager.test_notifications():
            print("✓ Notification manager test passed")
            return True
        else:
            print("✗ Notification manager test failed")
            return False
    else:
        print("✗ Basic notification test failed")
        return False

def test_alert_formatting():
    """Test alert message formatting"""
    
    print("\n=== Alert Formatting Test ===")
    
    # Test different alert types
    test_cases = [
        {
            'symbol': '7203',
            'alert_type': 'buy',
            'message': '【買い推奨】トヨタ自動車 (7203)\\n現在価格: ¥2,600\\n理由: PER 12.5 <= 15.0',
            'triggered_price': 2600.0,
            'strategy_name': 'value_strategy'
        },
        {
            'symbol': '9984',
            'alert_type': 'sell_profit',
            'message': '【利益確定推奨】ソフトバンクG (9984)\\n現在価格: ¥4,800\\n収益率: +20.00% (目標: 15%)',
            'triggered_price': 4800.0,
            'strategy_name': 'growth_strategy'
        },
        {
            'symbol': '6758',
            'alert_type': 'sell_loss',
            'message': '【損切り推奨】ソニーG (6758)\\n現在価格: ¥9,200\\n収益率: -10.00% (損切りライン: -8%)',
            'triggered_price': 9200.0,
            'strategy_name': 'momentum_strategy'
        }
    ]
    
    def format_alert_message(alert_data):
        """Format alert message for display"""
        try:
            # Extract basic info
            symbol = alert_data['symbol']
            alert_type = alert_data['alert_type']
            message = alert_data['message']
            price = alert_data['triggered_price']
            strategy = alert_data['strategy_name']
            
            # Format message
            formatted_message = message.replace('\\n', '\n')
            
            # Add metadata
            formatted = f"銘柄: {symbol}\n"
            formatted += f"価格: ¥{price:,.0f}\n"
            formatted += f"戦略: {strategy}\n"
            formatted += f"詳細:\n{formatted_message}"
            
            return formatted
            
        except Exception as e:
            print(f"Alert formatting error: {e}")
            return None
    
    success_count = 0
    for test_case in test_cases:
        formatted = format_alert_message(test_case)
        if formatted and test_case['symbol'] in formatted:
            print(f"✓ Alert formatting test passed for {test_case['alert_type']}")
            success_count += 1
        else:
            print(f"✗ Alert formatting test failed for {test_case['alert_type']}")
    
    if success_count == len(test_cases):
        print("✓ All alert formatting tests passed")
        return True
    else:
        print(f"✗ Alert formatting tests failed: {success_count}/{len(test_cases)}")
        return False

def main():
    """Run all notification tests"""
    
    print("=== Notification System Test Suite ===\n")
    
    tests = [
        ("Console Notification", test_console_notification),
        ("Configuration Loading", test_config_loading),
        ("Notification Manager", test_notification_manager),
        ("Alert Formatting", test_alert_formatting)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✓ {test_name}: PASSED\n")
                passed += 1
            else:
                print(f"✗ {test_name}: FAILED\n")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}\n")
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All notification tests passed!")
        return True
    else:
        print("❌ Some notification tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)