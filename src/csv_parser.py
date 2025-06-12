import csv
import chardet
import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Holding:
    """保有銘柄データクラス"""
    symbol: str
    name: str
    quantity: int
    average_cost: float
    current_price: float
    acquisition_amount: float
    market_value: float
    profit_loss: float
    broker: str
    account_type: str = ''


class CSVParser:
    """SBI証券・楽天証券のCSVファイルをパースするクラス"""
    
    def __init__(self):
        self.encoding_candidates = ['shift_jis', 'cp932', 'utf-8', 'euc-jp']
    
    def detect_encoding(self, file_path: str) -> str:
        """ファイルのエンコーディングを自動検出"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                detected_encoding = result['encoding']
                
                # Shift-JISの場合はcp932を使用（より広範囲の文字をサポート）
                if detected_encoding and 'shift_jis' in detected_encoding.lower():
                    return 'cp932'
                elif detected_encoding:
                    return detected_encoding
                else:
                    return 'cp932'  # デフォルトはcp932
        except Exception:
            return 'cp932'
    
    def detect_broker_format(self, file_path: str) -> str:
        """ブローカーのフォーマットを自動検出"""
        encoding = self.detect_encoding(file_path)
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                lines = content.split('\n')
                
                # 楽天証券の判定（より確実に）
                for line in lines[:10]:
                    if '■資産合計欄' in line:
                        return 'rakuten'
                    if '保有商品の評価額合計' in line:
                        return 'rakuten'
                    if '時価評価額[円]' in line and '前日比[円]' in line:
                        return 'rakuten'
                    if 'assetbalance' in file_path.lower():
                        return 'rakuten'
                
                # SBI証券の判定
                for line in lines[:10]:
                    if '保有商品一覧' in line:
                        return 'sbi'
                    if '銘柄コード' in line and '銘柄名' in line and '保有株数' in line:
                        return 'sbi'
                    if line.startswith('"') and ',' in line and line.count('"') >= 4:
                        # 楽天証券でない場合のみSBIと判定
                        if '■資産合計欄' not in content:
                            return 'sbi'
                
                # ファイル名からの推測
                filename = file_path.lower()
                if 'sbi' in filename or 'savefile' in filename:
                    return 'sbi'
                elif 'rakuten' in filename or '楽天' in filename or 'assetbalance' in filename:
                    return 'rakuten'
                
                return 'unknown'
        except Exception as e:
            print(f"フォーマット検出エラー: {e}")
            return 'unknown'
    
    def parse_sbi_csv(self, file_path: str) -> List[Holding]:
        """SBI証券のCSVをパース"""
        encoding = self.detect_encoding(file_path)
        holdings = []
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            # データ行を特定（実際のSBIフォーマットに合わせて）
            data_start_index = 0
            for i, line in enumerate(lines):
                if '銘柄コード' in line and '銘柄名' in line:
                    data_start_index = i + 1
                    break
            
            # データ行を処理
            for line in lines[data_start_index:]:
                line = line.strip()
                if not line or line.startswith('※') or '合計' in line:
                    continue
                
                # ヘッダー行や説明行をスキップ
                if any(header_word in line for header_word in 
                       ['基準価額', '取得金額', '評価額', '評価損益', '分配金受取方法', '売却注文中', '再投資']):
                    continue
                
                try:
                    # CSV行をパース（引用符を考慮）
                    import csv
                    from io import StringIO
                    reader = csv.reader(StringIO(line))
                    row = next(reader)
                    
                    if len(row) >= 9:  # 最低限必要な列数
                        # SBI証券のフォーマット：銘柄コード,銘柄名,保有株数,空,取得単価,現在値,取得金額,評価金額,評価損益
                        symbol = str(row[0]).strip().replace('"', '')
                        name = str(row[1]).strip().replace('"', '')
                        
                        # 有効な銘柄コードかどうか事前チェック
                        if not symbol or (not symbol.isdigit() and not symbol.isalpha()):
                            continue
                            
                        quantity = self._parse_number(row[2])
                        # row[3] は空の列
                        average_cost = self._parse_number(row[4])
                        current_price = self._parse_number(row[5])
                        acquisition_amount = self._parse_number(row[6])
                        market_value = self._parse_number(row[7])
                        profit_loss = self._parse_number(row[8])
                        
                        # 有効な銘柄かチェック（日本株4桁または米国株アルファベット）
                        is_valid_symbol = (
                            (symbol.isdigit() and len(symbol) == 4) or  # 日本株
                            (symbol.isalpha() and len(symbol) <= 5)     # 米国株等
                        )
                        
                        if is_valid_symbol and name and quantity > 0:
                            holdings.append(Holding(
                                symbol=symbol,
                                name=name,
                                quantity=int(quantity),
                                average_cost=average_cost,
                                current_price=current_price,
                                acquisition_amount=acquisition_amount,
                                market_value=market_value,
                                profit_loss=profit_loss,
                                broker='SBI',
                                account_type='一般'
                            ))
                            print(f"SBI: {symbol} {name} を追加")
                
                except Exception as e:
                    # パースエラーは詳細ログを出さない（ヘッダー行等のため）
                    continue
        
        except Exception as e:
            print(f"SBI CSVパースエラー: {e}")
        
        return holdings
    
    def parse_rakuten_csv(self, file_path: str) -> List[Holding]:
        """楽天証券のCSVをパース（2025年新フォーマット対応）"""
        encoding = self.detect_encoding(file_path)
        holdings = []
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            print("楽天証券CSVを解析中...")
            
            # ヘッダー行を探す
            header_found = False
            data_start_index = 0
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # ヘッダー行を探す: "種別","銘柄コード・ティッカー","銘柄","口座"...
                if '種別' in line and '銘柄コード・ティッカー' in line and '銘柄' in line:
                    header_found = True
                    data_start_index = i + 1
                    print(f"楽天証券のヘッダーを発見（{i+1}行目）")
                    break
            
            if not header_found:
                # フォールバック: 保有商品詳細の後から探す
                for i, line in enumerate(lines):
                    if '■ 保有商品詳細' in line:
                        data_start_index = i + 2  # ヘッダーの次の行から
                        header_found = True
                        print(f"楽天証券のデータ開始行を推定（{data_start_index+1}行目から）")
                        break
            
            if header_found:
                print(f"個別銘柄データの処理を開始（{data_start_index+1}行目から）")
                
                # 個別銘柄データを処理
                for i in range(data_start_index, len(lines)):
                    line = lines[i].strip()
                    if not line:
                        continue
                    
                    try:
                        # CSV行をパース
                        import csv
                        from io import StringIO
                        reader = csv.reader(StringIO(line))
                        row = next(reader)
                        
                        # 新フォーマット: "種別","銘柄コード・ティッカー","銘柄","口座","保有数量","［単位］","平均取得価額","［単位］","現在値","［単位］",...
                        # インデックス:      0      1                    2     3        4           5         6           7        8       9
                        if (len(row) >= 18 and 
                            row[0] and ('国内株式' in row[0] or '米国株式' in row[0] or '投資信託' in row[0]) and
                            row[2] and len(row[2]) > 0):  # 銘柄名が存在
                            asset_type = str(row[0]).strip()
                            symbol = str(row[1]).strip() if row[1] else ''  # 投資信託は空の場合がある
                            name = str(row[2]).strip()
                            account_type = str(row[3]).strip() if len(row) > 3 else '一般'
                            quantity = self._parse_number(row[4]) if len(row) > 4 else 0
                            unit1 = str(row[5]).strip() if len(row) > 5 else ''
                            acquisition_price = self._parse_number(row[6]) if len(row) > 6 else 0
                            unit2 = str(row[7]).strip() if len(row) > 7 else ''
                            current_price = self._parse_number(row[8]) if len(row) > 8 else 0
                            unit3 = str(row[9]).strip() if len(row) > 9 else ''
                            market_value_yen = self._parse_number(row[14]) if len(row) > 14 else 0
                            profit_loss_yen = self._parse_number(row[16]) if len(row) > 16 else 0
                            
                            # 有効な銘柄かチェック
                            if name and quantity > 0:
                                # 投資信託の場合、銘柄コードがないので名前から生成
                                if not symbol and '投資信託' in asset_type:
                                    # 投資信託用の疑似シンボル生成
                                    symbol = f"FUND_{hash(name) % 100000:05d}"
                                elif not symbol:
                                    # その他の場合は名前から生成
                                    symbol = f"STOCK_{hash(name) % 100000:05d}"
                                
                                # 取得金額を計算（投資信託の単位問題対応）
                                if '投資信託' in asset_type and acquisition_price > 0:
                                    # 投資信託の場合、評価額-損益から取得金額を逆算
                                    acquisition_amount = max(0, market_value_yen - profit_loss_yen)
                                elif acquisition_price > 0:
                                    # 株式の場合、通常の計算
                                    acquisition_amount = quantity * acquisition_price
                                else:
                                    # その他の場合、評価額-損益から逆算
                                    acquisition_amount = max(0, market_value_yen - profit_loss_yen)
                                
                                # 現在価格が不明な場合、評価額から逆算
                                if current_price <= 0 and quantity > 0:
                                    current_price = market_value_yen / quantity
                                
                                holdings.append(Holding(
                                    symbol=symbol,
                                    name=name,
                                    quantity=int(quantity),
                                    average_cost=acquisition_price,
                                    current_price=current_price,
                                    acquisition_amount=acquisition_amount,
                                    market_value=market_value_yen,
                                    profit_loss=profit_loss_yen,
                                    broker='楽天',
                                    account_type=account_type
                                ))
                                print(f"楽天: {symbol} {name} を追加（{account_type}, {asset_type}）")
                        
                        # 投資信託の場合（銘柄コードが空で、銘柄名のみの場合）
                        elif (len(row) >= 17 and 
                              row[0] and ('投資信託' in row[0]) and
                              not row[1] and row[2]):  # 銘柄コードが空で銘柄名のみ
                            
                            symbol = f"FUND_{len(holdings)}"  # 投資信託用の疑似シンボル
                            name = str(row[2]).strip()
                            account_type = str(row[3]).strip() if len(row) > 3 else '一般'
                            quantity = self._parse_number(row[4]) if len(row) > 4 else 0
                            acquisition_price = self._parse_number(row[6]) if len(row) > 6 else 0
                            current_price = self._parse_number(row[8]) if len(row) > 8 else 0
                            market_value_yen = self._parse_number(row[14]) if len(row) > 14 else 0
                            profit_loss_yen = self._parse_number(row[16]) if len(row) > 16 else 0
                            
                            if name and quantity > 0:
                                acquisition_amount = max(0, market_value_yen - profit_loss_yen)
                                
                                if current_price <= 0 and quantity > 0:
                                    current_price = market_value_yen / quantity
                                
                                holdings.append(Holding(
                                    symbol=symbol,
                                    name=name,
                                    quantity=int(quantity),
                                    average_cost=acquisition_price,
                                    current_price=current_price,
                                    acquisition_amount=acquisition_amount,
                                    market_value=market_value_yen,
                                    profit_loss=profit_loss_yen,
                                    broker='楽天',
                                    account_type=account_type
                                ))
                                print(f"楽天: {name} を追加（投資信託・{account_type}）")
                    
                    except Exception as e:
                        # パースエラーは無視
                        continue
            
            # 個別銘柄データが見つからない場合のみ、サマリーデータから処理
            if not holdings:
                print("個別銘柄データが見つかりません。サマリーデータを処理中...")
                
                for line in lines:
                    if '国内株式' in line or '米国株式' in line:
                        try:
                            import csv
                            from io import StringIO
                            reader = csv.reader(StringIO(line))
                            row = next(reader)
                            
                            if len(row) >= 3:
                                category = row[0].strip()
                                evaluation_amount = self._parse_number(row[1])
                                profit_loss = self._parse_number(row[2])
                                
                                if evaluation_amount > 0:
                                    holdings.append(Holding(
                                        symbol=f"PORTFOLIO_{category.replace('株式', '').strip()}",
                                        name=f"楽天証券-{category}",
                                        quantity=1,
                                        average_cost=evaluation_amount - profit_loss,
                                        current_price=evaluation_amount,
                                        acquisition_amount=evaluation_amount - profit_loss,
                                        market_value=evaluation_amount,
                                        profit_loss=profit_loss,
                                        broker='楽天',
                                        account_type='サマリー'
                                    ))
                                    print(f"楽天: {category} サマリーを追加")
                        except:
                            continue
            else:
                print(f"個別銘柄データを {len(holdings)} 件取得しました")
        
        except Exception as e:
            print(f"楽天 CSVパースエラー: {e}")
        
        return holdings
    
    def _parse_number(self, value) -> float:
        """数値文字列を float に変換（日本の数値フォーマット対応）"""
        if value == '' or value is None:
            return 0.0
        
        try:
            # 文字列の場合、日本の数値フォーマットを処理
            if isinstance(value, str):
                # 前後の空白を除去
                value = value.strip()
                
                # 空文字列やハイフンは0として扱う
                if value == '' or value == '-' or value == '－':
                    return 0.0
                
                # カンマ、円記号、引用符を除去
                value = value.replace(',', '').replace('¥', '').replace('円', '').replace('"', '').replace("'", '')
                
                # プラス記号を処理
                if value.startswith('+'):
                    value = value[1:]
                
                # 全角数字を半角に変換
                value = value.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
                
                # 再度空文字列チェック
                if value == '':
                    return 0.0
            
            return float(value)
        except (ValueError, TypeError) as e:
            print(f"数値変換エラー: '{value}' -> {e}")
            return 0.0
    
    def parse_csv(self, file_path: str) -> List[Holding]:
        """CSVファイルを自動判定してパース"""
        print(f"CSVファイルを解析中: {file_path}")
        
        broker_format = self.detect_broker_format(file_path)
        print(f"検出されたフォーマット: {broker_format}")
        
        if broker_format == 'sbi':
            print("SBI証券形式として処理します")
            return self.parse_sbi_csv(file_path)
        elif broker_format == 'rakuten':
            print("楽天証券形式として処理します")
            return self.parse_rakuten_csv(file_path)
        else:
            # より詳細なエラー情報を提供
            encoding = self.detect_encoding(file_path)
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    first_lines = [f.readline().strip() for _ in range(5)]
                
                error_msg = f"不明なCSVフォーマット: {file_path}\n"
                error_msg += f"検出エンコーディング: {encoding}\n"
                error_msg += "ファイルの最初の5行:\n"
                for i, line in enumerate(first_lines, 1):
                    error_msg += f"  {i}: {line[:100]}...\n"
                
                raise ValueError(error_msg)
            except Exception as e:
                raise ValueError(f"CSVファイル読み込みエラー: {file_path} - {str(e)}")


if __name__ == "__main__":
    # テスト用
    parser = CSVParser()
    
    # テストファイルがある場合の例
    # holdings = parser.parse_csv("test_sbi.csv")
    # for holding in holdings:
    #     print(f"{holding.symbol}: {holding.name} - {holding.quantity}株")