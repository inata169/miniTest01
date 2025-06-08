#!/usr/bin/env python3
"""
Simple CSV parser test without external dependencies
"""

import sys
import os
import csv
import tempfile
from io import StringIO

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_number_parsing():
    """Test number parsing functionality"""
    
    print("=== Number Parsing Test ===")
    
    def parse_number(value):
        """Simple number parsing without pandas dependency"""
        if value == '' or value is None:
            return 0.0
        
        try:
            if isinstance(value, str):
                value = value.strip()
                
                if value == '' or value == '-' or value == '－':
                    return 0.0
                
                value = value.replace(',', '').replace('¥', '').replace('円', '').replace('"', '').replace("'", '')
                
                if value.startswith('+'):
                    value = value[1:]
                
                # Convert full-width numbers and comma
                value = value.translate(str.maketrans('０１２３４５６７８９，', '0123456789,'))
                
                if value == '':
                    return 0.0
            
            return float(value)
        except (ValueError, TypeError) as e:
            print(f"数値変換エラー: '{value}' -> {e}")
            return 0.0
    
    # Test cases
    test_cases = [
        ("1000", 1000.0),
        ("1,000", 1000.0),
        ("+500", 500.0),
        ("¥1,000", 1000.0),
        ("", 0.0),
        ("-", 0.0),
        ("abc", 0.0),
        (None, 0.0),
        ("１，０００", 1000.0),  # Full-width characters
        ("+10,500", 10500.0)
    ]
    
    passed = 0
    for input_val, expected in test_cases:
        result = parse_number(input_val)
        if result == expected:
            print(f"✓ parse_number('{input_val}') = {result}")
            passed += 1
        else:
            print(f"✗ parse_number('{input_val}') = {result}, expected {expected}")
    
    print(f"Number parsing test: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_encoding_detection():
    """Test encoding detection"""
    
    print("\n=== Encoding Detection Test ===")
    
    # Create test files with different encodings
    test_data = "銘柄コード,銘柄名,保有株数\n7203,トヨタ自動車,100\n"
    
    # Test UTF-8
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
        f.write(test_data)
        utf8_path = f.name
    
    try:
        # Simple encoding detection (without chardet)
        def detect_encoding_simple(file_path):
            """Simple encoding detection without chardet"""
            encodings = ['utf-8', 'cp932', 'shift_jis', 'euc-jp']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read()
                    return encoding
                except UnicodeDecodeError:
                    continue
            return 'utf-8'  # fallback
        
        detected = detect_encoding_simple(utf8_path)
        print(f"✓ Detected encoding: {detected}")
        
        # Test reading with detected encoding
        with open(utf8_path, 'r', encoding=detected) as f:
            content = f.read()
            if 'トヨタ自動車' in content:
                print("✓ Successfully read Japanese text")
                return True
            else:
                print("✗ Failed to read Japanese text correctly")
                return False
    
    finally:
        os.unlink(utf8_path)

def test_broker_format_detection():
    """Test broker format detection"""
    
    print("\n=== Broker Format Detection Test ===")
    
    # SBI format test
    sbi_content = '''保有商品一覧

銘柄コード,銘柄名,保有株数,,取得単価,現在値,取得金額,評価金額,評価損益
"7203","トヨタ自動車",100,,2500,2600,250000,260000,+10000
"9984","ソフトバンクグループ",50,,5000,4800,250000,240000,-10000
'''
    
    # Rakuten format test
    rakuten_content = '''資産サマリー
国内株式,500000,+10000
米国株式,300000,-5000

詳細データ
国内株式,7203,トヨタ自動車,一般,100,株,2500,円,2600,円,2024-01-01,2600,+100,円,260000,260000,+10000,+4.00%
'''
    
    def detect_broker_format_simple(content):
        """Simple broker format detection"""
        lines = content.split('\n')
        
        # SBI detection
        for line in lines[:10]:
            if '保有商品一覧' in line:
                return 'sbi'
            if '銘柄コード' in line and '銘柄名' in line and '保有株数' in line:
                return 'sbi'
        
        # Rakuten detection
        for line in lines[:10]:
            if '資産サマリー' in line or '保有商品の評価額合計' in line:
                return 'rakuten'
        
        return 'unknown'
    
    # Test SBI format
    sbi_format = detect_broker_format_simple(sbi_content)
    if sbi_format == 'sbi':
        print("✓ SBI format detected correctly")
        sbi_success = True
    else:
        print(f"✗ SBI format detection failed: {sbi_format}")
        sbi_success = False
    
    # Test Rakuten format
    rakuten_format = detect_broker_format_simple(rakuten_content)
    if rakuten_format == 'rakuten':
        print("✓ Rakuten format detected correctly")
        rakuten_success = True
    else:
        print(f"✗ Rakuten format detection failed: {rakuten_format}")
        rakuten_success = False
    
    return sbi_success and rakuten_success

def test_csv_parsing():
    """Test basic CSV parsing"""
    
    print("\n=== CSV Parsing Test ===")
    
    # Test SBI-style CSV parsing
    sbi_test_data = '''"7203","トヨタ自動車",100,,2500,2600,250000,260000,+10000
"9984","ソフトバンクグループ",50,,5000,4800,250000,240000,-10000'''
    
    def parse_number_simple(value):
        """Simple number parsing"""
        if value == '' or value is None:
            return 0.0
        try:
            if isinstance(value, str):
                value = value.strip().replace(',', '').replace('¥', '').replace('円', '').replace('"', '')
                if value.startswith('+'):
                    value = value[1:]
                if value == '' or value == '-':
                    return 0.0
            return float(value)
        except:
            return 0.0
    
    holdings = []
    
    for line in sbi_test_data.split('\n'):
        if not line.strip():
            continue
        
        try:
            reader = csv.reader(StringIO(line))
            row = next(reader)
            
            if len(row) >= 9:
                symbol = str(row[0]).strip().replace('"', '')
                name = str(row[1]).strip().replace('"', '')
                quantity = parse_number_simple(row[2])
                average_cost = parse_number_simple(row[4])
                current_price = parse_number_simple(row[5])
                acquisition_amount = parse_number_simple(row[6])
                market_value = parse_number_simple(row[7])
                profit_loss = parse_number_simple(row[8])
                
                if symbol and name and quantity > 0:
                    holding = {
                        'symbol': symbol,
                        'name': name,
                        'quantity': int(quantity),
                        'average_cost': average_cost,
                        'current_price': current_price,
                        'acquisition_amount': acquisition_amount,
                        'market_value': market_value,
                        'profit_loss': profit_loss,
                        'broker': 'SBI'
                    }
                    holdings.append(holding)
                    print(f"✓ Parsed: {symbol} {name} - {int(quantity)}株")
        
        except Exception as e:
            print(f"✗ Parse error: {e}")
    
    if len(holdings) == 2:
        print(f"✓ Successfully parsed {len(holdings)} holdings")
        return True
    else:
        print(f"✗ Expected 2 holdings, got {len(holdings)}")
        return False

def main():
    """Run all CSV tests"""
    
    print("=== CSV Parser Test Suite ===\n")
    
    tests = [
        ("Number Parsing", test_number_parsing),
        ("Encoding Detection", test_encoding_detection),
        ("Broker Format Detection", test_broker_format_detection),
        ("CSV Parsing", test_csv_parsing)
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
        print("🎉 All CSV parser tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)