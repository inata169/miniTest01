import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
from datetime import datetime

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csv_parser import CSVParser
from data_sources import YahooFinanceDataSource
from database import DatabaseManager


class MainWindow:
    """メインGUIウィンドウクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("日本株ウォッチドッグ (Japanese Stock Watchdog)")
        self.root.geometry("1000x700")
        
        # クラス初期化
        self.csv_parser = CSVParser()
        self.data_source = YahooFinanceDataSource()
        self.db = DatabaseManager()
        
        self.setup_ui()
        self.load_portfolio_data()
    
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
        help_menu.add_command(label="バージョン情報", command=self.show_about)
    
    def create_portfolio_tab(self):
        """ポートフォリオタブ作成"""
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="ポートフォリオ")
        
        # サマリー情報
        summary_frame = ttk.LabelFrame(portfolio_frame, text="サマリー", padding=10)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
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
            ttk.Label(summary_frame, text=f"{label}:").grid(row=0, column=i*2, sticky=tk.W, padx=5)
            self.summary_labels[key] = ttk.Label(summary_frame, text="¥0", font=("Arial", 10, "bold"))
            self.summary_labels[key].grid(row=0, column=i*2+1, sticky=tk.W, padx=5)
        
        # 保有銘柄一覧
        holdings_frame = ttk.LabelFrame(portfolio_frame, text="保有銘柄", padding=5)
        holdings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for holdings
        columns = ("symbol", "name", "quantity", "avg_cost", "current_price", "market_value", "profit_loss", "return_rate", "broker")
        self.holdings_tree = ttk.Treeview(holdings_frame, columns=columns, show="headings", height=15)
        
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
            self.holdings_tree.heading(col, text=header)
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
        
        ttk.Label(watch_frame, text="監視機能は今後実装予定です", font=("Arial", 12)).pack(pady=50)
    
    def create_alert_tab(self):
        """アラート履歴タブ作成"""
        alert_frame = ttk.Frame(self.notebook)
        self.notebook.add(alert_frame, text="アラート履歴")
        
        ttk.Label(alert_frame, text="アラート履歴は今後実装予定です", font=("Arial", 12)).pack(pady=50)
    
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
    
    def load_portfolio_data(self):
        """起動時にポートフォリオデータを読み込み"""
        self.refresh_portfolio()
    
    def update_status(self, message):
        """ステータス更新"""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def show_import_result(self, text):
        """インポート結果表示"""
        def update_text():
            self.import_text.delete(1.0, tk.END)
            self.import_text.insert(1.0, text)
        
        self.root.after(0, update_text)
    
    def show_about(self):
        """バージョン情報表示"""
        messagebox.showinfo(
            "日本株ウォッチドッグについて",
            "日本株ウォッチドッグ v1.0\n\n"
            "日本株式投資を支援する無料ツール\n"
            "SBI証券・楽天証券のCSVインポート対応\n\n"
            "データソース: Yahoo Finance (無料)"
        )
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()