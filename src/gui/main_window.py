import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkFont
import os
import sys
import threading
from datetime import datetime
import platform

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csv_parser import CSVParser
from data_sources import YahooFinanceDataSource
from database import DatabaseManager
from alert_manager import AlertManager
from version import get_version_info


class MainWindow:
    """メインGUIウィンドウクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("日本株ウォッチドッグ (Japanese Stock Watchdog)")
        self.root.geometry("1000x700")
        
        # 日本語フォント設定
        self.setup_japanese_font()
        
        # クラス初期化
        self.csv_parser = CSVParser()
        self.data_source = YahooFinanceDataSource()
        self.db = DatabaseManager()
        self.alert_manager = AlertManager()
        
        self.setup_ui()
        self.load_portfolio_data()
    
    def setup_japanese_font(self):
        """日本語フォントを設定"""
        system = platform.system()
        
        if system == "Windows":
            # Windows用フォント
            font_families = ["Yu Gothic UI", "Meiryo UI", "MS Gothic", "Arial Unicode MS"]
        elif system == "Darwin":  # macOS
            font_families = ["Hiragino Sans", "Arial Unicode MS", "Helvetica"]
        else:  # Linux
            font_families = ["Noto Sans CJK JP", "DejaVu Sans", "Liberation Sans", "Arial Unicode MS"]
        
        # 利用可能なフォントを検索
        available_fonts = tkFont.families()
        selected_font = None
        
        for font_family in font_families:
            if font_family in available_fonts:
                selected_font = font_family
                break
        
        if not selected_font:
            selected_font = "TkDefaultFont"
        
        # デフォルトフォントを設定
        self.default_font = tkFont.nametofont("TkDefaultFont")
        self.default_font.configure(family=selected_font, size=9)
        
        # その他のフォントも設定
        for font_name in ["TkTextFont", "TkHeadingFont", "TkMenuFont"]:
            try:
                font_obj = tkFont.nametofont(font_name)
                font_obj.configure(family=selected_font)
            except:
                pass
        
        # カスタムフォントを作成
        self.japanese_font = tkFont.Font(family=selected_font, size=9)
        self.japanese_font_bold = tkFont.Font(family=selected_font, size=9, weight="bold")
        self.japanese_font_large = tkFont.Font(family=selected_font, size=12)
    
    def setup_ui(self):
        """UIを構築"""
        # メニューバー
        self.create_menu()
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タブコントロール
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # ポートフォリオタブ
        self.create_portfolio_tab()
        
        # CSVインポートタブ
        self.create_import_tab()
        
        # 監視タブ
        self.create_watch_tab()
        
        # アラート履歴タブ
        self.create_alert_tab()
        
        # ステータスバー
        self.create_status_bar()
    
    def create_menu(self):
        """メニューバー作成"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="CSVインポート", command=self.import_csv)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.root.quit)
        
        # 表示メニュー
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="表示", menu=view_menu)
        view_menu.add_command(label="ポートフォリオ更新", command=self.refresh_portfolio)
        view_menu.add_command(label="株価更新", command=self.update_prices)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="CSVファイル取得方法", command=self.show_csv_help)
        help_menu.add_separator()
        help_menu.add_command(label="バージョン情報", command=self.show_about)
    
    def create_portfolio_tab(self):
        """ポートフォリオタブ作成"""
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="ポートフォリオ")
        
        # サマリー表示制御
        self.control_frame = ttk.Frame(portfolio_frame)
        self.control_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.show_summary_var = tk.BooleanVar(value=True)
        summary_check = ttk.Checkbutton(self.control_frame, text="サマリー表示", 
                                       variable=self.show_summary_var, 
                                       command=self.toggle_summary_display)
        summary_check.pack(side=tk.LEFT)
        
        # サマリー情報
        self.summary_frame = ttk.LabelFrame(portfolio_frame, text="サマリー", padding=10)
        self.summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # サマリーラベル
        self.summary_labels = {}
        summary_info = [
            ("total_stocks", "銘柄数"),
            ("total_acquisition", "取得金額"),
            ("total_market_value", "評価金額"),
            ("total_profit_loss", "損益"),
            ("return_rate", "収益率")
        ]
        
        for i, (key, label) in enumerate(summary_info):
            ttk.Label(self.summary_frame, text=f"{label}:", font=self.japanese_font).grid(row=0, column=i*2, sticky=tk.W, padx=5)
            self.summary_labels[key] = ttk.Label(self.summary_frame, text="¥0", font=self.japanese_font_bold)
            self.summary_labels[key].grid(row=0, column=i*2+1, sticky=tk.W, padx=5)
        
        # 保有銘柄一覧
        holdings_frame = ttk.LabelFrame(portfolio_frame, text="保有銘柄", padding=5)
        holdings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for holdings
        columns = ("symbol", "name", "quantity", "avg_cost", "current_price", "market_value", "profit_loss", "return_rate", "broker")
        self.holdings_tree = ttk.Treeview(holdings_frame, columns=columns, show="headings", height=15)
        
        # ソート用変数
        self.sort_column = None
        self.sort_reverse = False
        
        # 列ヘッダー設定
        headers = {
            "symbol": "銘柄コード",
            "name": "銘柄名", 
            "quantity": "保有数",
            "avg_cost": "平均取得価格",
            "current_price": "現在価格",
            "market_value": "評価金額",
            "profit_loss": "損益",
            "return_rate": "収益率",
            "broker": "証券会社"
        }
        
        for col, header in headers.items():
            self.holdings_tree.heading(col, text=header, command=lambda c=col: self.sort_treeview(c))
            self.holdings_tree.column(col, width=100, anchor=tk.CENTER)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(holdings_frame, orient=tk.VERTICAL, command=self.holdings_tree.yview)
        self.holdings_tree.configure(yscrollcommand=scrollbar.set)
        
        self.holdings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ボタンフレーム
        button_frame = ttk.Frame(portfolio_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="株価更新", command=self.update_prices).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="表示更新", command=self.refresh_portfolio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="アラートテスト", command=self.test_alert).pack(side=tk.LEFT, padx=5)
    
    def create_import_tab(self):
        """CSVインポートタブ作成"""
        import_frame = ttk.Frame(self.notebook)
        self.notebook.add(import_frame, text="CSVインポート")
        
        # インポート設定
        settings_frame = ttk.LabelFrame(import_frame, text="インポート設定", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # ファイル選択
        ttk.Label(settings_frame, text="CSVファイル:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(settings_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(settings_frame, text="参照", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)
        
        # 証券会社選択
        ttk.Label(settings_frame, text="証券会社:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.broker_var = tk.StringVar(value="自動判定")
        broker_combo = ttk.Combobox(settings_frame, textvariable=self.broker_var, 
                                   values=["自動判定", "SBI証券", "楽天証券"], state="readonly")
        broker_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # インポートボタン
        ttk.Button(settings_frame, text="インポート実行", command=self.import_csv).grid(row=2, column=1, pady=10)
        
        # インポート結果表示
        result_frame = ttk.LabelFrame(import_frame, text="インポート結果", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.import_text = tk.Text(result_frame, height=20, wrap=tk.WORD)
        import_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.import_text.yview)
        self.import_text.configure(yscrollcommand=import_scrollbar.set)
        
        self.import_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        import_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_watch_tab(self):
        """監視タブ作成"""
        watch_frame = ttk.Frame(self.notebook)
        self.notebook.add(watch_frame, text="監視設定")
        
        ttk.Label(watch_frame, text="監視機能は今後実装予定です", font=self.japanese_font_large).pack(pady=50)
    
    def create_alert_tab(self):
        """アラート履歴タブ作成"""
        alert_frame = ttk.Frame(self.notebook)
        self.notebook.add(alert_frame, text="アラート履歴")
        
        # アラート履歴表示
        alert_list_frame = ttk.LabelFrame(alert_frame, text="アラート履歴", padding=5)
        alert_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # アラート履歴用Treeview
        alert_columns = ("timestamp", "symbol", "alert_type", "message")
        self.alert_tree = ttk.Treeview(alert_list_frame, columns=alert_columns, show="headings", height=15)
        
        # 列ヘッダー設定
        alert_headers = {
            "timestamp": "日時",
            "symbol": "銘柄",
            "alert_type": "種類",
            "message": "メッセージ"
        }
        
        for col, header in alert_headers.items():
            self.alert_tree.heading(col, text=header)
            if col == "message":
                self.alert_tree.column(col, width=400, anchor=tk.W)
            else:
                self.alert_tree.column(col, width=120, anchor=tk.CENTER)
        
        # スクロールバー
        alert_scrollbar = ttk.Scrollbar(alert_list_frame, orient=tk.VERTICAL, command=self.alert_tree.yview)
        self.alert_tree.configure(yscrollcommand=alert_scrollbar.set)
        
        self.alert_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        alert_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ボタンフレーム
        alert_button_frame = ttk.Frame(alert_frame)
        alert_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(alert_button_frame, text="履歴更新", command=self.refresh_alerts).pack(side=tk.LEFT, padx=5)
        ttk.Button(alert_button_frame, text="履歴クリア", command=self.clear_alerts).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self):
        """ステータスバー作成"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="準備完了")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def browse_file(self):
        """ファイル選択ダイアログ"""
        file_path = filedialog.askopenfilename(
            title="CSVファイルを選択",
            filetypes=[("CSVファイル", "*.csv"), ("全てのファイル", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def import_csv(self):
        """CSVインポート実行"""
        file_path = self.file_path_var.get()
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("エラー", "有効なCSVファイルを選択してください")
            return
        
        # 非同期でインポート実行
        threading.Thread(target=self._import_csv_thread, args=(file_path,), daemon=True).start()
    
    def _import_csv_thread(self, file_path):
        """CSVインポートのバックグラウンド処理"""
        try:
            self.update_status("CSVファイルを解析中...")
            self.progress.start()
            
            # CSVパース
            holdings = self.csv_parser.parse_csv(file_path)
            
            if not holdings:
                self.show_import_result("エラー: CSVファイルからデータを読み込めませんでした")
                return
            
            self.update_status("データベースに保存中...")
            
            # データベースに保存
            inserted_count = self.db.insert_holdings(holdings)
            
            # 結果表示
            result_text = f"インポート完了!\n\n"
            result_text += f"処理日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += f"ファイル: {os.path.basename(file_path)}\n"
            result_text += f"証券会社: {holdings[0].broker if holdings else '不明'}\n"
            result_text += f"インポート件数: {inserted_count} 件\n\n"
            
            result_text += "インポートされた銘柄:\n"
            for holding in holdings:
                result_text += f"  {holding.symbol}: {holding.name} ({holding.quantity:,}株)\n"
            
            self.show_import_result(result_text)
            
            # ポートフォリオ表示を更新
            self.root.after(0, self.refresh_portfolio)
            
        except Exception as e:
            self.show_import_result(f"エラー: {str(e)}")
        
        finally:
            self.progress.stop()
            self.update_status("準備完了")
    
    def update_prices(self):
        """株価情報を更新"""
        threading.Thread(target=self._update_prices_thread, daemon=True).start()
    
    def _update_prices_thread(self):
        """株価更新のバックグラウンド処理"""
        try:
            self.update_status("株価情報を取得中...")
            self.progress.start()
            
            # データベースから銘柄一覧取得
            holdings = self.db.get_all_holdings()
            symbols = [h['symbol'] for h in holdings]
            
            if not symbols:
                self.update_status("更新する銘柄がありません")
                return
            
            # 株価取得
            price_updates = {}
            skipped_count = 0
            error_count = 0
            
            for symbol in symbols:
                # 疑似シンボルをスキップ
                if (symbol.startswith('PORTFOLIO_') or 
                    symbol.startswith('FUND_') or
                    symbol == 'STOCK_PORTFOLIO' or
                    symbol == 'TOTAL_PORTFOLIO'):
                    skipped_count += 1
                    continue
                
                stock_info = self.data_source.get_stock_info(symbol)
                if stock_info:
                    price_updates[symbol] = stock_info.current_price
                else:
                    error_count += 1
            
            # データベース更新
            total_symbols = len(symbols)
            updated_count = len(price_updates)
            
            if price_updates:
                self.db.update_current_prices(price_updates)
            
            # ステータス更新
            status_parts = []
            if updated_count > 0:
                status_parts.append(f"{updated_count}銘柄を更新")
            if skipped_count > 0:
                status_parts.append(f"{skipped_count}銘柄をスキップ")
            if error_count > 0:
                status_parts.append(f"{error_count}銘柄でエラー")
            
            status_message = f"株価更新完了: {', '.join(status_parts)}"
            self.update_status(status_message)
            
            # 表示更新（更新がなくても表示を更新）
            self.root.after(0, self.refresh_portfolio)
        
        except Exception as e:
            self.update_status(f"株価更新エラー: {str(e)}")
        
        finally:
            self.progress.stop()
    
    def refresh_portfolio(self):
        """ポートフォリオ表示を更新"""
        try:
            # サマリー更新
            summary = self.db.get_portfolio_summary()
            
            # 安全な値の取得
            total_stocks = summary.get('total_stocks', 0) or 0
            total_acquisition = summary.get('total_acquisition', 0) or 0
            total_market_value = summary.get('total_market_value', 0) or 0
            total_profit_loss = summary.get('total_profit_loss', 0) or 0
            return_rate = summary.get('return_rate', 0) or 0
            
            self.summary_labels['total_stocks'].config(text=f"{total_stocks} 銘柄")
            self.summary_labels['total_acquisition'].config(text=f"¥{total_acquisition:,.0f}")
            self.summary_labels['total_market_value'].config(text=f"¥{total_market_value:,.0f}")
            
            profit_color = "green" if total_profit_loss >= 0 else "red"
            self.summary_labels['total_profit_loss'].config(
                text=f"¥{total_profit_loss:+,.0f}", 
                foreground=profit_color
            )
            
            self.summary_labels['return_rate'].config(
                text=f"{return_rate:+.2f}%", 
                foreground=profit_color
            )
            
            # 保有銘柄一覧更新
            for item in self.holdings_tree.get_children():
                self.holdings_tree.delete(item)
            
            holdings = self.db.get_all_holdings()
            for holding in holdings:
                # 安全な計算
                acquisition_amount = holding.get('acquisition_amount', 0) or 0
                market_value = holding.get('market_value', 0) or 0
                return_rate = ((market_value / acquisition_amount) - 1) * 100 if acquisition_amount > 0 else 0
                
                values = (
                    holding['symbol'],
                    holding['name'][:15] + "..." if len(holding['name']) > 15 else holding['name'],
                    f"{holding['quantity']:,}",
                    f"¥{holding['average_cost']:,.0f}",
                    f"¥{holding['current_price']:,.0f}",
                    f"¥{holding['market_value']:,.0f}",
                    f"¥{holding['profit_loss']:+,.0f}",
                    f"{return_rate:+.2f}%",
                    holding['broker']
                )
                
                # 色分け
                tags = []
                if holding['profit_loss'] > 0:
                    tags.append('profit')
                elif holding['profit_loss'] < 0:
                    tags.append('loss')
                
                self.holdings_tree.insert("", tk.END, values=values, tags=tags)
            
            # タグの色設定
            self.holdings_tree.tag_configure('profit', foreground='green')
            self.holdings_tree.tag_configure('loss', foreground='red')
            
        except Exception as e:
            messagebox.showerror("エラー", f"ポートフォリオ更新エラー: {str(e)}")
    
    def refresh_alerts(self):
        """アラート履歴を更新"""
        try:
            # アラート履歴をクリア
            for item in self.alert_tree.get_children():
                self.alert_tree.delete(item)
            
            # データベースからアラート履歴を取得
            alerts = self.db.get_alerts(50)  # 最新50件
            
            if not alerts:
                # サンプルデータを表示
                sample_alert = (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "---",
                    "情報",
                    "アラート履歴はここに表示されます。「アラートテスト」ボタンで動作確認できます。"
                )
                self.alert_tree.insert("", tk.END, values=sample_alert)
                return
            
            # アラートタイプの日本語化（絵文字付き）
            alert_type_map = {
                'buy': '💰 買い推奨',
                'sell_profit': '✅ 利益確定',
                'sell_loss': '⚠️ 損切り', 
                'test': '🧪 テスト',
                'info': '📊 情報',
                'warning': '🚨 警告'
            }
            
            for alert in alerts:
                alert_type_str = alert_type_map.get(alert['alert_type'], f"📈 {alert['alert_type']}")
                
                # メッセージを短縮
                message = alert['message'][:80] + "..." if len(alert['message']) > 80 else alert['message']
                
                values = (
                    alert['created_at'],
                    alert['symbol'],
                    alert_type_str,
                    message
                )
                
                # アラートタイプに応じた色分け
                tags = []
                if alert['alert_type'] == 'buy':
                    tags.append('buy_alert')
                elif alert['alert_type'] in ['sell_profit']:
                    tags.append('profit_alert')
                elif alert['alert_type'] in ['sell_loss', 'warning']:
                    tags.append('warning_alert')
                else:
                    tags.append('info_alert')
                
                self.alert_tree.insert("", tk.END, values=values, tags=tags)
            
            # アラート履歴の色分け設定
            self.alert_tree.tag_configure('buy_alert', foreground='blue')
            self.alert_tree.tag_configure('profit_alert', foreground='green')
            self.alert_tree.tag_configure('warning_alert', foreground='red')
            self.alert_tree.tag_configure('info_alert', foreground='black')
                
        except Exception as e:
            messagebox.showerror("エラー", f"アラート履歴更新エラー: {str(e)}")
    
    def clear_alerts(self):
        """アラート履歴をクリア"""
        result = messagebox.askyesno(
            "確認", 
            "アラート履歴をすべてクリアしますか？\nこの操作は取り消せません。"
        )
        if result:
            try:
                # データベースのアラート履歴をクリア
                self.db.clear_alerts()
                
                # 表示もクリア
                for item in self.alert_tree.get_children():
                    self.alert_tree.delete(item)
                
                messagebox.showinfo("完了", "アラート履歴をクリアしました。")
                
            except Exception as e:
                messagebox.showerror("エラー", f"アラート履歴クリアエラー: {str(e)}")

    def load_portfolio_data(self):
        """起動時にポートフォリオデータを読み込み"""
        self.refresh_portfolio()
        self.refresh_alerts()
    
    def update_status(self, message):
        """ステータス更新"""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def show_import_result(self, text):
        """インポート結果表示"""
        def update_text():
            self.import_text.delete(1.0, tk.END)
            self.import_text.insert(1.0, text)
        
        self.root.after(0, update_text)
    
    def toggle_summary_display(self):
        """サマリー表示の切り替え"""
        if self.show_summary_var.get():
            # コントロールフレームの後に配置
            self.summary_frame.pack(fill=tk.X, padx=5, pady=5, after=self.control_frame)
        else:
            self.summary_frame.pack_forget()
    
    def show_csv_help(self):
        """CSVファイル取得方法のヘルプを表示"""
        help_window = tk.Toplevel(self.root)
        help_window.title("CSVファイル取得方法")
        help_window.geometry("600x700")
        help_window.resizable(True, True)
        
        # スクロール可能なフレーム
        canvas = tk.Canvas(help_window)
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 楽天証券セクション
        ttk.Label(scrollable_frame, text="楽天証券からCSVファイルを取得する方法", 
                 font=self.japanese_font_large).pack(pady=(10, 5))
        
        rakuten_steps = [
            "1. 楽天証券のウェブページにアクセスし、ログインします。",
            "2. マイメニューの資産残高・保有商品をクリックします。",
            "3. CSVで保存をクリックします。",
            "4. assetbalance(all)_***.csvというファイルがダウンロードされたことを確認します。"
        ]
        
        for step in rakuten_steps:
            ttk.Label(scrollable_frame, text=step, wraplength=550, justify=tk.LEFT, font=self.japanese_font).pack(anchor=tk.W, padx=10, pady=2)
        
        # SBI証券セクション
        ttk.Label(scrollable_frame, text="\nSBI証券からCSVファイルを取得する方法", 
                 font=self.japanese_font_large).pack(pady=(20, 5))
        
        sbi_steps = [
            "1. SBI証券のウェブページにアクセスし、ログインします。",
            "2. 口座管理の口座（円建）をクリックします。",
            "3. 保有証券をクリックし、CSVダウンロードをクリックします。",
            "4. SaveFile.csvというファイルがダウンロードされたことを確認します。"
        ]
        
        for step in sbi_steps:
            ttk.Label(scrollable_frame, text=step, wraplength=550, justify=tk.LEFT, font=self.japanese_font).pack(anchor=tk.W, padx=10, pady=2)
        
        # 注意事項
        ttk.Label(scrollable_frame, text="\n注意事項", 
                 font=self.japanese_font_large).pack(pady=(20, 5))
        
        notes = [
            "• CSVファイルは日本語（Shift-JIS）エンコーディングで保存されています。",
            "• このアプリケーションは自動的にエンコーディングを判定してファイルを読み込みます。",
            "• インポート時に証券会社を選択するか、自動判定を使用してください。",
            "• ファイル名は変更しても問題ありませんが、内容は変更しないでください。"
        ]
        
        for note in notes:
            ttk.Label(scrollable_frame, text=note, wraplength=550, justify=tk.LEFT, font=self.japanese_font).pack(anchor=tk.W, padx=10, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイールでスクロール
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def sort_treeview(self, column):
        """Treeviewのソート機能"""
        # 同じ列をクリックした場合は昇順/降順を切り替え
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # 現在のデータを取得
        data = []
        for item in self.holdings_tree.get_children():
            values = self.holdings_tree.item(item)['values']
            tags = self.holdings_tree.item(item)['tags']
            data.append((values, tags))
        
        # ソートキーを決定
        def sort_key(item):
            values = item[0]
            col_index = list(self.holdings_tree['columns']).index(column)
            value = values[col_index]
            
            # 数値列の場合は数値としてソート
            if column in ['quantity', 'avg_cost', 'current_price', 'market_value', 'profit_loss', 'return_rate']:
                try:
                    # 文字列から数値を抽出
                    import re
                    numeric_value = re.sub(r'[¥,+%]', '', str(value))
                    return float(numeric_value)
                except:
                    return 0
            else:
                # 文字列としてソート
                return str(value)
        
        # ソート実行
        data.sort(key=sort_key, reverse=self.sort_reverse)
        
        # Treeviewを再構築
        for item in self.holdings_tree.get_children():
            self.holdings_tree.delete(item)
        
        for values, tags in data:
            self.holdings_tree.insert("", tk.END, values=values, tags=tags)
        
        # ヘッダーに矢印を表示
        headers = {
            "symbol": "銘柄コード",
            "name": "銘柄名", 
            "quantity": "保有数",
            "avg_cost": "平均取得価格",
            "current_price": "現在価格",
            "market_value": "評価金額",
            "profit_loss": "損益",
            "return_rate": "収益率",
            "broker": "証券会社"
        }
        
        for col, header in headers.items():
            if col == column:
                arrow = " ↓" if self.sort_reverse else " ↑"
                self.holdings_tree.heading(col, text=header + arrow)
            else:
                self.holdings_tree.heading(col, text=header)

    def test_alert(self):
        """アラート機能をテスト"""
        try:
            self.update_status("アラートテストを実行中...")
            
            # テストアラート送信
            test_message = (
                "🚨 アラートテスト 🚨\n\n"
                f"テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                "銘柄: 7203 (トヨタ自動車)\n"
                "アラート種類: 買い推奨\n"
                "理由: テスト用のサンプルアラートです\n\n"
                "このアラートが表示されれば通知機能は正常に動作しています。"
            )
            
            # アラート送信（非同期）
            threading.Thread(
                target=self._send_test_alert, 
                args=(test_message,), 
                daemon=True
            ).start()
            
        except Exception as e:
            messagebox.showerror("エラー", f"アラートテストエラー: {str(e)}")
            self.update_status("準備完了")
    
    def _send_test_alert(self, message):
        """テストアラートを非同期送信"""
        try:
            # AlertManagerのtest_notifications機能を使用
            self.alert_manager.test_notifications()
            
            # AlertオブジェクトをインポートしてからTESTアラートを作成
            from stock_monitor import Alert
            
            test_alert = Alert(
                symbol="TEST",
                alert_type="test",
                message=message,
                triggered_price=2500.0,
                strategy_name="test_strategy",
                timestamp=datetime.now()
            )
            
            # アラート送信
            self.alert_manager.send_alert(test_alert)
            
            # データベースにもアラートを記録
            self.db.log_alert(
                symbol="TEST",
                alert_type="test", 
                message="テスト用のサンプルアラートです",
                triggered_price=2500.0,
                strategy_name="test_strategy"
            )
            
            self.update_status("アラートテスト完了")
            
            # アラート履歴を更新
            self.root.after(1000, self.refresh_alerts)
            
            # GUIにメッセージ表示
            self.root.after(0, lambda: messagebox.showinfo(
                "アラートテスト", 
                "アラートテストを送信しました。\n"
                "設定されている通知方法で確認してください。\n\n"
                "- デスクトップ通知\n"
                "- メール通知（設定済みの場合）\n"
                "- コンソール出力"
            ))
            
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"アラートテストエラー: {error_msg}")
            self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                "エラー", f"アラートテスト送信エラー: {msg}"
            ))

    def show_about(self):
        """バージョン情報表示"""
        version_info = get_version_info()
        messagebox.showinfo(
            "日本株ウォッチドッグについて",
            f"日本株ウォッチドッグ v{version_info['version']}\n"
            f"リリース: {version_info['release_name']}\n\n"
            "日本株式投資を支援する無料ツール\n"
            "SBI証券・楽天証券のCSVインポート対応\n\n"
            "データソース: Yahoo Finance (無料)\n\n"
            "収益率 = (評価金額 ÷ 取得金額 - 1) × 100%\n"
            "※ヘッダークリックでソート可能\n\n"
            "新機能:\n"
            "- アラート機能テスト\n"
            "- テーブルソート機能\n"
            "- 日本語フォント対応"
        )
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()