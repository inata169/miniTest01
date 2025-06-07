import unittest
import tempfile
import os
from unittest.mock import patch
import sys

# テスト用にパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from csv_parser import CSVParser, Holding


class TestCSVParser(unittest.TestCase):
    """CSVパーサーのテストクラス"""
    
    def setUp(self):
        self.parser = CSVParser()
    
    def test_parse_number(self):
        """数値変換テスト"""
        # 正常なケース
        self.assertEqual(self.parser._parse_number("1000"), 1000.0)
        self.assertEqual(self.parser._parse_number("1,000"), 1000.0)
        self.assertEqual(self.parser._parse_number("+500"), 500.0)
        self.assertEqual(self.parser._parse_number("¥1,000"), 1000.0)
        
        # エラーケース
        self.assertEqual(self.parser._parse_number(""), 0.0)
        self.assertEqual(self.parser._parse_number("-"), 0.0)
        self.assertEqual(self.parser._parse_number("abc"), 0.0)
        self.assertEqual(self.parser._parse_number(None), 0.0)
    
    def test_detect_encoding(self):
        """エンコーディング検出テスト"""
        # テストファイル作成
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write("test,data\n1,2")
            temp_path = f.name
        
        try:
            encoding = self.parser.detect_encoding(temp_path)
            self.assertIn(encoding, ['utf-8', 'cp932'])
        finally:
            os.unlink(temp_path)
    
    def test_detect_broker_format(self):
        """ブローカー形式検出テスト"""
        # SBI形式のテストファイル
        sbi_content = '''
保有商品一覧

銘柄コード,銘柄名,保有株数,,取得単価,現在値,取得金額,評価金額,評価損益
"7203","トヨタ自動車",100,,2500,2600,250000,260000,+10000
'''
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(sbi_content)
            temp_path = f.name
        
        try:
            format_type = self.parser.detect_broker_format(temp_path)
            self.assertEqual(format_type, 'sbi')
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()