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
        self.root.geometry("1300x910")  # 1000x700 * 1.3
        
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
        
        # タブ制御フレーム
        tab_control_frame = ttk.Frame(portfolio_frame)
        tab_control_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # サブタブ作成
        self.portfolio_notebook = ttk.Notebook(portfolio_frame)
        self.portfolio_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 保有銘柄タブ
        self.create_holdings_tab()
        
        # ウォッチリストタブ
        self.create_watchlist_tab()
        
        # 欲しい銘柄タブ
        self.create_wishlist_tab()
    
    def create_holdings_tab(self):
        """保有銘柄タブ作成"""
        holdings_tab_frame = ttk.Frame(self.portfolio_notebook)
        self.portfolio_notebook.add(holdings_tab_frame, text="保有銘柄")
        
        # サマリー表示制御
        self.control_frame = ttk.Frame(holdings_tab_frame)
        self.control_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.show_summary_var = tk.BooleanVar(value=True)
        summary_check = ttk.Checkbutton(self.control_frame, text="サマリー表示", 
                                       variable=self.show_summary_var, 
                                       command=self.toggle_summary_display)
        summary_check.pack(side=tk.LEFT)
        
        # サマリー情報
        self.summary_frame = ttk.LabelFrame(holdings_tab_frame, text="サマリー", padding=10)
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
        holdings_frame = ttk.LabelFrame(holdings_tab_frame, text="保有銘柄", padding=5)
        holdings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for holdings（条件表示列を追加）
        columns = ("condition_indicator", "symbol", "name", "quantity", "avg_cost", "current_price", "market_value", "profit_loss", "return_rate", "broker")
        self.holdings_tree = ttk.Treeview(holdings_frame, columns=columns, show="headings", height=15)
        
        # ソート用変数
        self.sort_column = None
        self.sort_reverse = False
        
        # 列ヘッダー設定
        headers = {
            "condition_indicator": "条件",
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
        button_frame = ttk.Frame(holdings_tab_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="株価更新", command=self.update_prices).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="表示更新", command=self.refresh_portfolio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="アラートテスト", command=self.test_alert).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="LINEテスト", command=self.test_line_alert).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Discordテスト", command=self.test_discord_alert).pack(side=tk.LEFT, padx=5)
    
    def create_watchlist_tab(self):
        """ウォッチリストタブ作成"""
        watchlist_tab_frame = ttk.Frame(self.portfolio_notebook)
        self.portfolio_notebook.add(watchlist_tab_frame, text="監視リスト")
        
        # 説明ラベル
        info_frame = ttk.Frame(watchlist_tab_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_label = ttk.Label(info_frame, text="📝 気になる銘柄を追加して監視できます", 
                              font=self.japanese_font_bold, foreground='#007bff')
        info_label.pack(pady=5)
        
        # 銘柄追加フレーム
        add_frame = ttk.LabelFrame(watchlist_tab_frame, text="銘柄追加", padding=10)
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 銘柄コード入力
        ttk.Label(add_frame, text="銘柄コード:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.watchlist_symbol_var = tk.StringVar()
        symbol_entry = ttk.Entry(add_frame, textvariable=self.watchlist_symbol_var, width=15)
        symbol_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 銘柄名入力（オプション）
        ttk.Label(add_frame, text="銘柄名:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.watchlist_name_var = tk.StringVar()
        name_entry = ttk.Entry(add_frame, textvariable=self.watchlist_name_var, width=20)
        name_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 目標価格入力（オプション）
        ttk.Label(add_frame, text="目標価格:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.watchlist_target_var = tk.StringVar()
        target_entry = ttk.Entry(add_frame, textvariable=self.watchlist_target_var, width=10)
        target_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # 追加ボタン
        ttk.Button(add_frame, text="追加", command=self.add_to_watchlist).grid(row=0, column=6, padx=10, pady=5)
        
        # ウォッチリスト一覧
        watchlist_frame = ttk.LabelFrame(watchlist_tab_frame, text="ウォッチリスト", padding=5)
        watchlist_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for watchlist
        watchlist_columns = ("condition_indicator", "symbol", "name", "current_price", "target_price", "change_percent", "dividend_yield", "per", "pbr", "status")
        self.watchlist_tree = ttk.Treeview(watchlist_frame, columns=watchlist_columns, show="headings", height=12)
        
        # 列ヘッダー設定
        watchlist_headers = {
            "condition_indicator": "条件",
            "symbol": "銘柄コード",
            "name": "銘柄名",
            "current_price": "現在価格",
            "target_price": "目標価格",
            "change_percent": "前日比",
            "dividend_yield": "配当利回り",
            "per": "PER",
            "pbr": "PBR",
            "status": "ステータス"
        }
        
        for col, header in watchlist_headers.items():
            self.watchlist_tree.heading(col, text=header)
            if col == "condition_indicator":
                self.watchlist_tree.column(col, width=60, anchor=tk.CENTER)
            elif col in ["symbol", "current_price", "target_price", "change_percent"]:
                self.watchlist_tree.column(col, width=80, anchor=tk.CENTER)
            elif col == "name":
                self.watchlist_tree.column(col, width=150, anchor=tk.W)
            else:
                self.watchlist_tree.column(col, width=70, anchor=tk.CENTER)
        
        # スクロールバー（ウォッチリスト）
        watchlist_scrollbar = ttk.Scrollbar(watchlist_frame, orient=tk.VERTICAL, command=self.watchlist_tree.yview)
        self.watchlist_tree.configure(yscrollcommand=watchlist_scrollbar.set)
        
        self.watchlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        watchlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ウォッチリストボタンフレーム
        watchlist_button_frame = ttk.Frame(watchlist_tab_frame)
        watchlist_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(watchlist_button_frame, text="価格更新", command=self.update_watchlist_prices).pack(side=tk.LEFT, padx=5)
        ttk.Button(watchlist_button_frame, text="選択削除", command=self.remove_from_watchlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(watchlist_button_frame, text="全て削除", command=self.clear_watchlist).pack(side=tk.LEFT, padx=5)
    
    def create_wishlist_tab(self):
        """欲しい銘柄タブ作成"""
        wishlist_tab_frame = ttk.Frame(self.portfolio_notebook)
        self.portfolio_notebook.add(wishlist_tab_frame, text="欲しい銘柄")
        
        # 説明ラベル
        info_frame = ttk.Frame(wishlist_tab_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_label = ttk.Label(info_frame, text="💝 将来購入したい銘柄を管理して、買いタイミングを逃さずキャッチ！", 
                              font=self.japanese_font_bold, foreground='#28a745')
        info_label.pack(pady=5)
        
        # 銘柄追加フレーム
        add_frame = ttk.LabelFrame(wishlist_tab_frame, text="欲しい銘柄追加", padding=10)
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 銘柄コード入力
        ttk.Label(add_frame, text="銘柄コード:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.wishlist_symbol_var = tk.StringVar()
        symbol_entry = ttk.Entry(add_frame, textvariable=self.wishlist_symbol_var, width=15)
        symbol_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 銘柄名入力
        ttk.Label(add_frame, text="銘柄名:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.wishlist_name_var = tk.StringVar()
        name_entry = ttk.Entry(add_frame, textvariable=self.wishlist_name_var, width=20)
        name_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 希望購入価格
        ttk.Label(add_frame, text="希望購入価格:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.wishlist_target_var = tk.StringVar()
        target_entry = ttk.Entry(add_frame, textvariable=self.wishlist_target_var, width=12)
        target_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # メモ
        ttk.Label(add_frame, text="メモ:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.wishlist_memo_var = tk.StringVar()
        memo_entry = ttk.Entry(add_frame, textvariable=self.wishlist_memo_var, width=50)
        memo_entry.grid(row=1, column=1, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 追加ボタン
        ttk.Button(add_frame, text="追加", command=self.add_to_wishlist_tab).grid(row=1, column=5, padx=10, pady=5)
        
        # 欲しい銘柄一覧
        wishlist_frame = ttk.LabelFrame(wishlist_tab_frame, text="欲しい銘柄一覧", padding=5)
        wishlist_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for wishlist
        wishlist_columns = ("match_level", "symbol", "name", "current_price", "target_price", "price_diff", "dividend_yield", "per", "pbr", "memo", "added_date")
        self.wishlist_tree = ttk.Treeview(wishlist_frame, columns=wishlist_columns, show="headings", height=15)
        
        # 列ヘッダー設定
        wishlist_headers = {
            "match_level": "条件一致度",
            "symbol": "銘柄コード",
            "name": "銘柄名",
            "current_price": "現在価格",
            "target_price": "希望価格",
            "price_diff": "価格差",
            "dividend_yield": "配当利回り",
            "per": "PER",
            "pbr": "PBR",
            "memo": "メモ",
            "added_date": "追加日"
        }
        
        for col, header in wishlist_headers.items():
            self.wishlist_tree.heading(col, text=header, command=lambda c=col: self.sort_wishlist_tab(c))
            if col == "match_level":
                self.wishlist_tree.column(col, width=100, anchor="center")
            elif col == "symbol":
                self.wishlist_tree.column(col, width=80, anchor="center")
            elif col == "name":
                self.wishlist_tree.column(col, width=180, anchor="w")
            elif col in ["current_price", "target_price", "price_diff"]:
                self.wishlist_tree.column(col, width=90, anchor="e")
            elif col in ["dividend_yield", "per", "pbr"]:
                self.wishlist_tree.column(col, width=70, anchor="e")
            elif col == "memo":
                self.wishlist_tree.column(col, width=200, anchor="w")
            elif col == "added_date":
                self.wishlist_tree.column(col, width=80, anchor="center")
        
        # スクロールバー
        wishlist_scrollbar = ttk.Scrollbar(wishlist_frame, orient=tk.VERTICAL, command=self.wishlist_tree.yview)
        self.wishlist_tree.configure(yscrollcommand=wishlist_scrollbar.set)
        
        self.wishlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        wishlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ボタンフレーム
        wishlist_button_frame = ttk.Frame(wishlist_tab_frame)
        wishlist_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(wishlist_button_frame, text="価格更新", command=self.update_wishlist_prices).pack(side=tk.LEFT, padx=5)
        ttk.Button(wishlist_button_frame, text="選択削除", command=self.remove_from_wishlist_tab).pack(side=tk.LEFT, padx=5)
        ttk.Button(wishlist_button_frame, text="全て削除", command=self.clear_wishlist_tab).pack(side=tk.LEFT, padx=5)
        ttk.Button(wishlist_button_frame, text="監視リストへ移動", command=self.move_to_watchlist_tab).pack(side=tk.LEFT, padx=5)
    
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
        """監視設定タブ作成"""
        watch_frame = ttk.Frame(self.notebook)
        self.notebook.add(watch_frame, text="監視設定")
        
        # メインの水平分割フレーム
        main_paned = ttk.PanedWindow(watch_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左側：設定パネル
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=3)
        
        # スクロール可能フレーム（左側）
        canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 戦略設定セクション
        self.create_strategy_config_ui(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 右側：説明パネル
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        # 説明セクション
        self.create_explanation_ui(right_frame)
    
    def create_strategy_config_ui(self, parent_frame):
        """戦略設定UIを作成"""
        # タイトル
        title_label = ttk.Label(parent_frame, text="アラート戦略設定", font=self.japanese_font_large)
        title_label.pack(pady=(10, 20))
        
        # 戦略選択フレーム
        strategy_frame = ttk.LabelFrame(parent_frame, text="戦略選択", padding=10)
        strategy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.strategy_var = tk.StringVar(value="default_strategy")
        strategies = [
            ("default_strategy", "デフォルト戦略（3条件中2条件）"),
            ("defensive_strategy", "守備的戦略（高配当重視）"),
            ("growth_strategy", "成長戦略（全条件必須）"),
            ("aggressive_strategy", "積極戦略（1条件でもOK）"),
            ("custom_strategy", "カスタム戦略")
        ]
        
        for value, text in strategies:
            ttk.Radiobutton(strategy_frame, text=text, variable=self.strategy_var, 
                           value=value, command=self.on_strategy_change).pack(anchor=tk.W, pady=2)
        
        # 評価モード設定フレーム
        mode_frame = ttk.LabelFrame(parent_frame, text="評価モード", padding=10)
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.condition_mode_var = tk.StringVar(value="any_two_of_three")
        modes = [
            ("strict_and", "全条件必須（AND）"),
            ("any_one", "1条件でもOK（OR）"),
            ("any_two_of_three", "3条件中2条件以上"),
            ("weighted_score", "重み付きスコア評価")
        ]
        
        for value, text in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.condition_mode_var, 
                           value=value).pack(anchor=tk.W, pady=2)
        
        # 買い条件設定フレーム
        buy_frame = ttk.LabelFrame(parent_frame, text="買い条件設定", padding=10)
        buy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 配当利回り
        dividend_frame = ttk.Frame(buy_frame)
        dividend_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dividend_frame, text="配当利回り 最低").pack(side=tk.LEFT)
        self.dividend_var = tk.DoubleVar(value=1.0)
        dividend_spin = ttk.Spinbox(dividend_frame, from_=0.0, to=10.0, increment=0.1, 
                                   textvariable=self.dividend_var, width=10)
        dividend_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(dividend_frame, text="% 以上").pack(side=tk.LEFT)
        
        # PER
        per_frame = ttk.Frame(buy_frame)
        per_frame.pack(fill=tk.X, pady=5)
        ttk.Label(per_frame, text="PER 最大").pack(side=tk.LEFT)
        self.per_var = tk.DoubleVar(value=40.0)
        per_spin = ttk.Spinbox(per_frame, from_=5.0, to=100.0, increment=1.0,
                              textvariable=self.per_var, width=10)
        per_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(per_frame, text="以下").pack(side=tk.LEFT)
        
        # PBR
        pbr_frame = ttk.Frame(buy_frame)
        pbr_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pbr_frame, text="PBR 最大").pack(side=tk.LEFT)
        self.pbr_var = tk.DoubleVar(value=4.0)
        pbr_spin = ttk.Spinbox(pbr_frame, from_=0.5, to=10.0, increment=0.1,
                              textvariable=self.pbr_var, width=10)
        pbr_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(pbr_frame, text="以下").pack(side=tk.LEFT)
        
        # 売り条件設定フレーム
        sell_frame = ttk.LabelFrame(parent_frame, text="売り条件設定", padding=10)
        sell_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 利益確定
        profit_frame = ttk.Frame(sell_frame)
        profit_frame.pack(fill=tk.X, pady=5)
        ttk.Label(profit_frame, text="利益確定").pack(side=tk.LEFT)
        self.profit_var = tk.DoubleVar(value=8.0)
        profit_spin = ttk.Spinbox(profit_frame, from_=1.0, to=50.0, increment=1.0,
                                 textvariable=self.profit_var, width=10)
        profit_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(profit_frame, text="% 以上").pack(side=tk.LEFT)
        
        # 損切り
        loss_frame = ttk.Frame(sell_frame)
        loss_frame.pack(fill=tk.X, pady=5)
        ttk.Label(loss_frame, text="損切り").pack(side=tk.LEFT)
        self.loss_var = tk.DoubleVar(value=-3.0)
        loss_spin = ttk.Spinbox(loss_frame, from_=-20.0, to=-1.0, increment=1.0,
                               textvariable=self.loss_var, width=10)
        loss_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(loss_frame, text="% 以下").pack(side=tk.LEFT)
        
        # 重み設定フレーム（weighted_score用）
        weight_frame = ttk.LabelFrame(parent_frame, text="重み設定（重み付きスコア評価時）", padding=10)
        weight_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 配当重み
        div_weight_frame = ttk.Frame(weight_frame)
        div_weight_frame.pack(fill=tk.X, pady=2)
        ttk.Label(div_weight_frame, text="配当利回り重み").pack(side=tk.LEFT)
        self.div_weight_var = tk.DoubleVar(value=0.4)
        ttk.Spinbox(div_weight_frame, from_=0.0, to=1.0, increment=0.1,
                   textvariable=self.div_weight_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # PER重み
        per_weight_frame = ttk.Frame(weight_frame)
        per_weight_frame.pack(fill=tk.X, pady=2)
        ttk.Label(per_weight_frame, text="PER重み").pack(side=tk.LEFT)
        self.per_weight_var = tk.DoubleVar(value=0.3)
        ttk.Spinbox(per_weight_frame, from_=0.0, to=1.0, increment=0.1,
                   textvariable=self.per_weight_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # PBR重み
        pbr_weight_frame = ttk.Frame(weight_frame)
        pbr_weight_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pbr_weight_frame, text="PBR重み").pack(side=tk.LEFT)
        self.pbr_weight_var = tk.DoubleVar(value=0.3)
        ttk.Spinbox(pbr_weight_frame, from_=0.0, to=1.0, increment=0.1,
                   textvariable=self.pbr_weight_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # 最小スコア
        min_score_frame = ttk.Frame(weight_frame)
        min_score_frame.pack(fill=tk.X, pady=2)
        ttk.Label(min_score_frame, text="最小スコア").pack(side=tk.LEFT)
        self.min_score_var = tk.DoubleVar(value=0.6)
        ttk.Spinbox(min_score_frame, from_=0.1, to=1.0, increment=0.1,
                   textvariable=self.min_score_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(button_frame, text="設定を保存", command=self.save_strategy_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="デフォルトに戻す", command=self.reset_strategy_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="設定をテスト", command=self.test_strategy_config).pack(side=tk.LEFT, padx=5)
    
    def on_strategy_change(self):
        """戦略選択時の処理"""
        strategy_name = self.strategy_var.get()
        if strategy_name != "custom_strategy":
            self.load_strategy_preset(strategy_name)
    
    def load_strategy_preset(self, strategy_name):
        """事前定義戦略をロード"""
        try:
            import json
            with open('config/strategies.json', 'r', encoding='utf-8') as f:
                strategies = json.load(f)
            
            if strategy_name in strategies:
                strategy = strategies[strategy_name]
                
                # 評価モード
                self.condition_mode_var.set(strategy.get('condition_mode', 'any_two_of_three'))
                
                # 買い条件
                buy_conditions = strategy.get('buy_conditions', {})
                self.dividend_var.set(buy_conditions.get('dividend_yield_min', 1.0))
                self.per_var.set(buy_conditions.get('per_max', 40.0))
                self.pbr_var.set(buy_conditions.get('pbr_max', 4.0))
                
                # 売り条件
                sell_conditions = strategy.get('sell_conditions', {})
                self.profit_var.set(sell_conditions.get('profit_target', 8.0))
                self.loss_var.set(sell_conditions.get('stop_loss', -3.0))
                
                # 重み
                weights = strategy.get('weights', {})
                self.div_weight_var.set(weights.get('dividend_weight', 0.4))
                self.per_weight_var.set(weights.get('per_weight', 0.3))
                self.pbr_weight_var.set(weights.get('pbr_weight', 0.3))
                self.min_score_var.set(strategy.get('min_score', 0.6))
                
        except Exception as e:
            print(f"戦略プリセット読み込みエラー: {e}")
    
    def save_strategy_config(self):
        """戦略設定を保存"""
        try:
            import json
            
            # 現在の設定を構築
            custom_strategy = {
                "condition_mode": self.condition_mode_var.get(),
                "buy_conditions": {
                    "dividend_yield_min": self.dividend_var.get(),
                    "per_max": self.per_var.get(),
                    "pbr_max": self.pbr_var.get()
                },
                "sell_conditions": {
                    "profit_target": self.profit_var.get(),
                    "stop_loss": self.loss_var.get()
                },
                "weights": {
                    "dividend_weight": self.div_weight_var.get(),
                    "per_weight": self.per_weight_var.get(),
                    "pbr_weight": self.pbr_weight_var.get()
                },
                "min_score": self.min_score_var.get()
            }
            
            # 既存設定を読み込み
            with open('config/strategies.json', 'r', encoding='utf-8') as f:
                strategies = json.load(f)
            
            # カスタム戦略を更新
            strategies['custom_strategy'] = custom_strategy
            
            # 設定を保存
            with open('config/strategies.json', 'w', encoding='utf-8') as f:
                json.dump(strategies, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", "戦略設定を保存しました。")
            
        except Exception as e:
            messagebox.showerror("エラー", f"設定保存に失敗しました: {e}")
    
    def reset_strategy_config(self):
        """設定をデフォルトに戻す"""
        self.strategy_var.set("default_strategy")
        self.load_strategy_preset("default_strategy")
    
    def test_strategy_config(self):
        """設定をテスト"""
        try:
            # テスト用のダミーデータで戦略をテスト
            test_stocks = [
                {"name": "テスト株A", "dividend": 2.5, "per": 15.0, "pbr": 1.5},
                {"name": "テスト株B", "dividend": 0.8, "per": 35.0, "pbr": 2.1},
                {"name": "テスト株C", "dividend": 3.2, "per": 12.0, "pbr": 0.9}
            ]
            
            results = []
            for stock in test_stocks:
                # 条件評価（簡易版）
                div_ok = stock["dividend"] >= self.dividend_var.get()
                per_ok = stock["per"] <= self.per_var.get()
                pbr_ok = stock["pbr"] <= self.pbr_var.get()
                
                mode = self.condition_mode_var.get()
                if mode == "strict_and":
                    alert = div_ok and per_ok and pbr_ok
                elif mode == "any_one":
                    alert = div_ok or per_ok or pbr_ok
                elif mode == "any_two_of_three":
                    alert = sum([div_ok, per_ok, pbr_ok]) >= 2
                elif mode == "weighted_score":
                    score = (div_ok * self.div_weight_var.get() + 
                            per_ok * self.per_weight_var.get() + 
                            pbr_ok * self.pbr_weight_var.get())
                    alert = score >= self.min_score_var.get()
                
                results.append(f"{stock['name']}: {'アラート発生' if alert else 'アラートなし'}")
            
            messagebox.showinfo("テスト結果", "\n".join(results))
            
        except Exception as e:
            messagebox.showerror("エラー", f"テストに失敗しました: {e}")
    
    def create_explanation_ui(self, parent_frame):
        """説明パネルを作成"""
        # スクロール可能フレーム（右側）
        exp_canvas = tk.Canvas(parent_frame, bg='#f8f9fa')
        exp_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=exp_canvas.yview)
        exp_scrollable = ttk.Frame(exp_canvas)
        
        exp_scrollable.bind(
            "<Configure>",
            lambda e: exp_canvas.configure(scrollregion=exp_canvas.bbox("all"))
        )
        
        exp_canvas.create_window((0, 0), window=exp_scrollable, anchor="nw")
        exp_canvas.configure(yscrollcommand=exp_scrollbar.set)
        
        # タイトル
        title_frame = tk.Frame(exp_scrollable, bg='#007bff', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=(5, 10))
        
        title_label = tk.Label(title_frame, text="📚 アラート戦略ガイド", 
                              font=(self.japanese_font.cget('family'), 14, 'bold'),
                              fg='white', bg='#007bff', pady=8)
        title_label.pack()
        
        # 基本概念の説明
        concept_frame = tk.LabelFrame(exp_scrollable, text="💡 基本概念", 
                                     font=(self.japanese_font.cget('family'), 11, 'bold'),
                                     fg='#28a745', pady=5, padx=5)
        concept_frame.pack(fill=tk.X, pady=5, padx=5)
        
        concept_text = """株価アラートは3つの指標で判断します：

🔹 配当利回り（年間配当÷株価×100）
  → 高いほど配当収入が多い
  
🔹 PER（株価収益率：株価÷1株利益）
  → 低いほど割安とされる
  
🔹 PBR（株価純資産倍率：株価÷1株純資産）
  → 低いほど割安とされる"""
        
        concept_label = tk.Label(concept_frame, text=concept_text, 
                                font=self.japanese_font, justify=tk.LEFT,
                                bg='#f8fff8', fg='#1e7e34', wraplength=280)
        concept_label.pack(fill=tk.X, padx=5, pady=5)
        
        # 評価モードの説明
        mode_frame = tk.LabelFrame(exp_scrollable, text="⚙️ 評価モード比較", 
                                  font=(self.japanese_font.cget('family'), 11, 'bold'),
                                  fg='#dc3545', pady=5, padx=5)
        mode_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # 各モードの説明を色分けして表示
        modes_data = [
            ("🔴 全条件必須（AND）", "3つ全てクリア", "厳格・少ないアラート", "#ffebee"),
            ("🟡 3条件中2条件以上", "3つ中2つクリア", "バランス・推奨", "#fff8e1"),
            ("🟢 1条件でもOK（OR）", "1つでもクリア", "緩い・多いアラート", "#e8f5e8"),
            ("🔵 重み付きスコア", "重要度で判定", "柔軟・カスタム", "#e3f2fd")
        ]
        
        for mode, condition, desc, bg_color in modes_data:
            mode_item_frame = tk.Frame(mode_frame, bg=bg_color, relief=tk.RIDGE, bd=1)
            mode_item_frame.pack(fill=tk.X, pady=2, padx=2)
            
            tk.Label(mode_item_frame, text=mode, font=(self.japanese_font.cget('family'), 10, 'bold'),
                    bg=bg_color, anchor=tk.W).pack(fill=tk.X, padx=5)
            tk.Label(mode_item_frame, text=f"条件: {condition}", 
                    font=self.japanese_font, bg=bg_color, anchor=tk.W).pack(fill=tk.X, padx=15)
            tk.Label(mode_item_frame, text=f"特徴: {desc}", 
                    font=self.japanese_font, bg=bg_color, anchor=tk.W).pack(fill=tk.X, padx=15, pady=(0,5))
        
        # 具体例
        example_frame = tk.LabelFrame(exp_scrollable, text="📈 具体例", 
                                     font=(self.japanese_font.cget('family'), 11, 'bold'),
                                     fg='#6f42c1', pady=5, padx=5)
        example_frame.pack(fill=tk.X, pady=5, padx=5)
        
        example_text = """例：トヨタ自動車（7203）
配当利回り: 2.8% ✅ (設定: 1.0%以上)
PER: 7.3 ✅ (設定: 40以下)  
PBR: 1.0 ✅ (設定: 4.0以下)

🔴 全条件必須 → ✅ アラート発生
🟡 3条件中2条件 → ✅ アラート発生  
🟢 1条件でもOK → ✅ アラート発生
🔵 重み付き(0.6) → ✅ アラート発生"""
        
        example_label = tk.Label(example_frame, text=example_text, 
                                font=self.japanese_font, justify=tk.LEFT,
                                bg='#faf5ff', fg='#6f42c1', wraplength=280)
        example_label.pack(fill=tk.X, padx=5, pady=5)
        
        # 推奨設定
        recommend_frame = tk.LabelFrame(exp_scrollable, text="🎯 推奨設定", 
                                       font=(self.japanese_font.cget('family'), 11, 'bold'),
                                       fg='#fd7e14', pady=5, padx=5)
        recommend_frame.pack(fill=tk.X, pady=5, padx=5)
        
        recommend_data = [
            ("💰 初心者", "3条件中2条件以上", "配当1%、PER40、PBR4"),
            ("🛡️ 安定志向", "重み付きスコア", "配当重視・高配当株狙い"),
            ("🚀 積極投資", "1条件でもOK", "PER重視・成長株狙い")
        ]
        
        for user_type, mode, setting in recommend_data:
            rec_frame = tk.Frame(recommend_frame, bg='#fff3cd', relief=tk.GROOVE, bd=1)
            rec_frame.pack(fill=tk.X, pady=2, padx=2)
            
            tk.Label(rec_frame, text=user_type, font=(self.japanese_font.cget('family'), 10, 'bold'),
                    bg='#fff3cd', anchor=tk.W).pack(fill=tk.X, padx=5)
            tk.Label(rec_frame, text=f"モード: {mode}", 
                    font=self.japanese_font, bg='#fff3cd', anchor=tk.W).pack(fill=tk.X, padx=15)
            tk.Label(rec_frame, text=f"設定: {setting}", 
                    font=self.japanese_font, bg='#fff3cd', anchor=tk.W).pack(fill=tk.X, padx=15, pady=(0,5))
        
        # 注意事項
        warning_frame = tk.LabelFrame(exp_scrollable, text="⚠️ 注意点", 
                                     font=(self.japanese_font.cget('family'), 11, 'bold'),
                                     fg='#dc3545', pady=5, padx=5)
        warning_frame.pack(fill=tk.X, pady=5, padx=5)
        
        warning_text = """• アラートは買い時の参考情報です
• 必ず自分で企業分析してから投資判断
• 過去の指標なので将来を保証しません
• リスク管理（損切り）も必ず設定
• 少額から始めて経験を積みましょう"""
        
        warning_label = tk.Label(warning_frame, text=warning_text, 
                                font=self.japanese_font, justify=tk.LEFT,
                                bg='#f8d7da', fg='#721c24', wraplength=280)
        warning_label.pack(fill=tk.X, padx=5, pady=5)
        
        exp_canvas.pack(side="left", fill="both", expand=True)
        exp_scrollbar.pack(side="right", fill="y")
    
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
                # symbolを文字列に変換
                symbol_str = str(symbol)
                
                # 疑似シンボルをスキップ
                if (symbol_str.startswith('PORTFOLIO_') or 
                    symbol_str.startswith('FUND_') or
                    symbol_str == 'STOCK_PORTFOLIO' or
                    symbol_str == 'TOTAL_PORTFOLIO'):
                    skipped_count += 1
                    continue
                
                stock_info = self.data_source.get_stock_info(symbol_str)
                if stock_info:
                    price_updates[symbol_str] = stock_info.current_price
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
                
                # 条件チェック（株価情報取得）
                try:
                    from data_sources import YahooFinanceDataSource
                    data_source = YahooFinanceDataSource()
                    
                    # シンボルを文字列に変換
                    symbol_str = str(holding['symbol'])
                    stock_info = data_source.get_stock_info(symbol_str)
                    
                    if stock_info:
                        conditions_met, _ = self.check_strategy_conditions(symbol_str, stock_info)
                        indicator = self.get_condition_indicator(conditions_met)
                    else:
                        conditions_met = 0
                        indicator = "😴様子見"
                except Exception as e:
                    print(f"条件チェックエラー ({holding['symbol']}): {e}")
                    conditions_met = 0
                    indicator = "😴様子見"
                
                values = (
                    indicator,
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
                
                # 色分け（条件マッチングを優先）
                tags = [f'condition_{conditions_met}']
                if holding['profit_loss'] > 0:
                    tags.append('profit')
                elif holding['profit_loss'] < 0:
                    tags.append('loss')
                
                self.holdings_tree.insert("", tk.END, values=values, tags=tags)
            
            # タグの色設定
            self.holdings_tree.tag_configure('profit', foreground='green')
            self.holdings_tree.tag_configure('loss', foreground='red')
            
            # 条件マッチング用の色分け（より鮮明で分かりやすく）
            self.holdings_tree.tag_configure('condition_3', background='#c8e6c9', foreground='#1b5e20', font=self.japanese_font_bold)  # 🔥買い頃！（濃い緑）
            self.holdings_tree.tag_configure('condition_2', background='#ffecb3', foreground='#e65100', font=self.japanese_font_bold)  # ⚡あと少し（オレンジ）
            self.holdings_tree.tag_configure('condition_1', background='#ffcdd2', foreground='#b71c1c', font=self.japanese_font_bold)  # 👀要注目（赤）
            self.holdings_tree.tag_configure('condition_0', background='#f5f5f5', foreground='#616161')  # 😴様子見（グレー）
            
        except Exception as e:
            messagebox.showerror("エラー", f"ポートフォリオ更新エラー: {str(e)}")
    
    def check_strategy_conditions(self, symbol, stock_info):
        """戦略条件をチェックして条件マッチ数を返す"""
        try:
            # デフォルト戦略を取得
            import json
            with open('config/strategies.json', 'r', encoding='utf-8') as f:
                strategies = json.load(f)
            
            strategy = strategies.get('default_strategy', {})
            buy_conditions = strategy.get('buy_conditions', {})
            
            # 各条件をチェック
            conditions_met = 0
            condition_details = []
            
            # 配当利回りチェック
            dividend_yield = (stock_info.dividend_yield or 0) * 100  # 小数から%に変換
            dividend_min = buy_conditions.get('dividend_yield_min', 1.0)
            if dividend_yield >= dividend_min:
                conditions_met += 1
                condition_details.append(f"配当 {dividend_yield:.1f}%≥{dividend_min}%")
            
            # PERチェック
            per = stock_info.pe_ratio or 0
            per_max = buy_conditions.get('per_max', 40.0)
            if per > 0 and per <= per_max:
                conditions_met += 1
                condition_details.append(f"PER {per:.1f}≤{per_max}")
            
            # PBRチェック
            pbr = stock_info.pb_ratio or 0
            pbr_max = buy_conditions.get('pbr_max', 4.0)
            if pbr > 0 and pbr <= pbr_max:
                conditions_met += 1
                condition_details.append(f"PBR {pbr:.1f}≤{pbr_max}")
            
            return conditions_met, condition_details
            
        except Exception as e:
            print(f"条件チェックエラー: {e}")
            return 0, []
    
    def get_condition_indicator(self, conditions_met):
        """条件マッチ数に応じた表示インジケーターを返す"""
        if conditions_met >= 3:
            return "🔥買い頃！"  # 3条件すべて満たす
        elif conditions_met == 2:
            return "⚡あと少し"  # 2条件満たす
        elif conditions_met == 1:
            return "👀要注目"  # 1条件満たす
        else:
            return "😴様子見"  # 条件満たさない
    
    def add_to_watchlist(self):
        """ウォッチリストに銘柄を追加"""
        symbol = self.watchlist_symbol_var.get().strip()
        name = self.watchlist_name_var.get().strip()
        target_price = self.watchlist_target_var.get().strip()
        
        if not symbol:
            messagebox.showerror("エラー", "銘柄コードを入力してください")
            return
        
        try:
            # 株価情報を取得
            from data_sources import YahooFinanceDataSource
            data_source = YahooFinanceDataSource()
            stock_info = data_source.get_stock_info(symbol)
            
            if not stock_info:
                messagebox.showerror("エラー", f"銘柄コード {symbol} の情報が取得できませんでした")
                return
            
            # 条件チェック
            conditions_met, condition_details = self.check_strategy_conditions(symbol, stock_info)
            indicator = self.get_condition_indicator(conditions_met)
            
            # ステータス決定
            if target_price:
                try:
                    target = float(target_price)
                    current = stock_info.current_price
                    if current <= target:
                        status = "🎯 目標達成"
                    else:
                        diff_percent = ((target - current) / current) * 100
                        status = f"📈 {diff_percent:+.1f}%"
                except ValueError:
                    status = "📊 監視中"
            else:
                status = "📊 監視中"
            
            # ツリーに追加
            values = (
                indicator,
                symbol,
                name or stock_info.name,
                f"¥{stock_info.current_price:,.0f}",
                f"¥{target_price}" if target_price else "未設定",
                f"{stock_info.change_percent:+.2f}%",
                f"{(stock_info.dividend_yield or 0) * 100:.1f}%",
                f"{stock_info.pe_ratio:.1f}" if stock_info.pe_ratio else "N/A",
                f"{stock_info.pb_ratio:.1f}" if stock_info.pb_ratio else "N/A",
                status
            )
            
            # 条件マッチング数に応じた色分け
            tags = [f'condition_{conditions_met}']
            
            self.watchlist_tree.insert("", tk.END, values=values, tags=tags)
            
            # 色設定
            self.watchlist_tree.tag_configure('condition_3', background='#d4edda', foreground='#155724')
            self.watchlist_tree.tag_configure('condition_2', background='#fff3cd', foreground='#856404')
            self.watchlist_tree.tag_configure('condition_1', background='#f8d7da', foreground='#721c24')
            self.watchlist_tree.tag_configure('condition_0', background='#f1f3f4', foreground='#5f6368')
            
            # 入力フィールドをクリア
            self.watchlist_symbol_var.set("")
            self.watchlist_name_var.set("")
            self.watchlist_target_var.set("")
            
            messagebox.showinfo("成功", f"銘柄 {symbol} をウォッチリストに追加しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"ウォッチリスト追加エラー: {e}")
    
    def update_watchlist_prices(self):
        """ウォッチリストの価格を更新"""
        try:
            from data_sources import YahooFinanceDataSource
            data_source = YahooFinanceDataSource()
            
            # 既存のアイテムを更新
            for item in self.watchlist_tree.get_children():
                values = self.watchlist_tree.item(item)['values']
                symbol = values[1]
                
                # 株価情報を取得
                stock_info = data_source.get_stock_info(symbol)
                if stock_info:
                    # 条件チェック
                    conditions_met, _ = self.check_strategy_conditions(symbol, stock_info)
                    indicator = self.get_condition_indicator(conditions_met)
                    
                    # 目標価格チェック
                    target_price_str = values[4]
                    if target_price_str != "未設定":
                        try:
                            target = float(target_price_str.replace("¥", "").replace(",", ""))
                            current = stock_info.current_price
                            if current <= target:
                                status = "🎯 目標達成"
                            else:
                                diff_percent = ((target - current) / current) * 100
                                status = f"📈 {diff_percent:+.1f}%"
                        except ValueError:
                            status = "📊 監視中"
                    else:
                        status = "📊 監視中"
                    
                    # 値を更新
                    new_values = (
                        indicator,
                        symbol,
                        values[2],  # 銘柄名
                        f"¥{stock_info.current_price:,.0f}",
                        values[4],  # 目標価格
                        f"{stock_info.change_percent:+.2f}%",
                        f"{(stock_info.dividend_yield or 0) * 100:.1f}%",
                        f"{stock_info.pe_ratio:.1f}" if stock_info.pe_ratio else "N/A",
                        f"{stock_info.pb_ratio:.1f}" if stock_info.pb_ratio else "N/A",
                        status
                    )
                    
                    # 条件マッチング数に応じた色分け
                    tags = [f'condition_{conditions_met}']
                    
                    self.watchlist_tree.item(item, values=new_values, tags=tags)
                    
            messagebox.showinfo("完了", "ウォッチリストの価格を更新しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"価格更新エラー: {e}")
    
    def remove_from_watchlist(self):
        """選択した銘柄をウォッチリストから削除"""
        selected_items = self.watchlist_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "削除する銘柄を選択してください")
            return
        
        for item in selected_items:
            self.watchlist_tree.delete(item)
        
        messagebox.showinfo("完了", f"{len(selected_items)}件の銘柄を削除しました")
    
    def clear_watchlist(self):
        """ウォッチリストを全てクリア"""
        if messagebox.askyesno("確認", "ウォッチリストを全て削除しますか？"):
            for item in self.watchlist_tree.get_children():
                self.watchlist_tree.delete(item)
            messagebox.showinfo("完了", "ウォッチリストをクリアしました")
    
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
        ttk.Label(scrollable_frame, text="🏦 楽天証券からCSVファイルを取得する方法", 
                 font=self.japanese_font_large).pack(pady=(10, 5))
        
        rakuten_steps = [
            "1. 楽天証券のウェブページにアクセスし、ログインします。",
            "2. マイメニュー → 資産残高・保有商品をクリックします。",
            "3. 「CSVで保存」ボタンをクリックします。",
            "4. assetbalance(all)_YYYYMMDD.csv ファイルがダウンロードされます。",
            "📝 新フォーマット（2025年版）に対応済み"
        ]
        
        for step in rakuten_steps:
            ttk.Label(scrollable_frame, text=step, wraplength=550, justify=tk.LEFT, font=self.japanese_font).pack(anchor=tk.W, padx=10, pady=2)
        
        # SBI証券セクション
        ttk.Label(scrollable_frame, text="\n🏦 SBI証券からCSVファイルを取得する方法", 
                 font=self.japanese_font_large).pack(pady=(20, 5))
        
        sbi_steps = [
            "1. SBI証券のウェブページにアクセスし、ログインします。",
            "2. 口座管理 → 口座（円建）をクリックします。",
            "3. 保有証券をクリックし、「CSVダウンロード」をクリックします。",
            "4. SaveFile.csv ファイルがダウンロードされます。",
            "💡 特定口座・一般口座・NISA口座すべてに対応"
        ]
        
        for step in sbi_steps:
            ttk.Label(scrollable_frame, text=step, wraplength=550, justify=tk.LEFT, font=self.japanese_font).pack(anchor=tk.W, padx=10, pady=2)
        
        # 注意事項
        ttk.Label(scrollable_frame, text="\n📋 重要な注意事項", 
                 font=self.japanese_font_large).pack(pady=(20, 5))
        
        notes = [
            "🔤 CSVファイルは日本語（Shift-JIS）エンコーディングで保存されています。",
            "🤖 このアプリは自動的にエンコーディングを判定して読み込みます。",
            "🏢 インポート時に証券会社を選択するか、自動判定を使用してください。",
            "📄 ファイル名は変更可能ですが、内容は変更しないでください。",
            "🔄 楽天証券の新フォーマット（2025年版）に完全対応済みです。",
            "⚡ v1.2.0では処理速度が大幅に向上しました。",
            "📊 データはSQLiteデータベースに安全に保存されます。"
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
    
    def test_line_alert(self):
        """LINE通知機能をテスト"""
        try:
            self.update_status("LINE通知テストを実行中...")
            
            # LINE通知テスト（非同期）
            threading.Thread(
                target=self._send_line_test, 
                daemon=True
            ).start()
            
        except Exception as e:
            messagebox.showerror("エラー", f"LINEテストエラー: {str(e)}")
            self.update_status("準備完了")
    
    def _send_line_test(self):
        """LINE通知テストを非同期実行"""
        try:
            # AlertManagerのLINE通知テスト機能を使用
            success = self.alert_manager.test_line_notification()
            
            # メインスレッドでGUIを更新
            self.root.after(0, self._line_test_completed, success)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self._line_test_error, error_msg)
    
    def _line_test_completed(self, success):
        """LINE通知テスト完了時の処理"""
        if success:
            self.update_status("LINE通知テスト完了")
            messagebox.showinfo(
                "LINE通知テスト", 
                "LINE通知テストを送信しました。\n"
                "LINEアプリで通知を確認してください。\n\n"
                "通知が届かない場合は、トークン設定を確認してください。"
            )
        else:
            self.update_status("LINE通知設定エラー")
            messagebox.showwarning(
                "LINE通知エラー", 
                "LINE通知の設定に問題があります。\n"
                "詳細はコンソールメッセージを確認してください。"
            )
    
    def _line_test_error(self, error_msg):
        """LINE通知テストエラー時の処理"""
        self.update_status(f"LINE通知テストエラー: {error_msg}")
        messagebox.showerror(
            "エラー", f"LINE通知テスト送信エラー: {error_msg}"
        )
    
    def test_discord_alert(self):
        """Discord通知機能をテスト"""
        try:
            self.update_status("Discord通知テストを実行中...")
            
            # Discord通知テスト（非同期）
            threading.Thread(
                target=self._send_discord_test, 
                daemon=True
            ).start()
            
        except Exception as e:
            messagebox.showerror("エラー", f"Discordテストエラー: {str(e)}")
            self.update_status("準備完了")
    
    def _send_discord_test(self):
        """Discord通知テストを非同期実行"""
        try:
            # AlertManagerのDiscord通知テスト機能を使用
            success = self.alert_manager.test_discord_notification()
            
            # メインスレッドでGUIを更新
            self.root.after(0, self._discord_test_completed, success)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self._discord_test_error, error_msg)
    
    def _discord_test_completed(self, success):
        """Discord通知テスト完了時の処理"""
        if success:
            self.update_status("Discord通知テスト完了")
            messagebox.showinfo(
                "Discord通知テスト", 
                "Discord通知テストを送信しました。\n"
                "Discordサーバーで通知を確認してください。\n\n"
                "通知が届かない場合は、WebhookURL設定を確認してください。"
            )
        else:
            self.update_status("Discord通知設定エラー")
            messagebox.showwarning(
                "Discord通知エラー", 
                "Discord通知の設定に問題があります。\n"
                "詳細はコンソールメッセージを確認してください。"
            )
    
    def _discord_test_error(self, error_msg):
        """Discord通知テストエラー時の処理"""
        self.update_status(f"Discord通知テストエラー: {error_msg}")
        messagebox.showerror(
            "エラー", f"Discord通知テスト送信エラー: {error_msg}"
        )
    
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
            "📈 日本株式投資を支援する無料オープンソースツール\n"
            "🏦 SBI証券・楽天証券のCSVインポート対応\n"
            "📊 リアルタイム株価監視とアラート機能\n\n"
            "🔄 データソース: Yahoo Finance API (無料)\n"
            "📧 通知: Discord, Gmail, LINE, デスクトップ\n"
            "📋 ログ機能: 詳細な動作履歴を記録\n\n"
            "💰 収益率 = (評価金額 ÷ 取得金額 - 1) × 100%\n"
            "📋 ※テーブルヘッダークリックでソート可能\n\n"
            "🚀 v1.2.0の新機能:\n"
            "✅ 強化されたアラートシステム (4つの評価モード)\n"
            "⚡ バッチ処理による高速化 (3-5倍向上)\n"
            "📝 包括的ログシステム\n"
            "🔧 設定検証とエラーハンドリング改善\n"
            "🎯 現実的な市場条件に対応した戦略設定"
        )
    
    def add_to_wishlist_tab(self):
        """欲しい銘柄タブに銘柄を追加"""
        symbol = self.wishlist_symbol_var.get().strip()
        name = self.wishlist_name_var.get().strip()
        target_price = self.wishlist_target_var.get().strip()
        memo = self.wishlist_memo_var.get().strip()
        
        if not symbol:
            messagebox.showerror("エラー", "銘柄コードを入力してください")
            return
        
        try:
            # 株価情報を取得
            from data_sources import YahooFinanceDataSource
            data_source = YahooFinanceDataSource()
            stock_info = data_source.get_stock_info(symbol)
            
            if not stock_info:
                messagebox.showerror("エラー", f"銘柄コード {symbol} の情報が取得できませんでした")
                return
            
            # 条件チェック
            conditions_met, condition_details = self.check_strategy_conditions(symbol, stock_info)
            indicator = self.get_condition_indicator(conditions_met)
            
            # 価格差計算
            if target_price:
                try:
                    target_price_float = float(target_price)
                    price_diff = stock_info.current_price - target_price_float
                    price_diff_str = f"¥{price_diff:+,.0f}"
                except:
                    price_diff_str = "N/A"
            else:
                price_diff_str = "N/A"
            
            # 欲しい銘柄一覧に追加
            from datetime import datetime
            values = (
                indicator,
                symbol,
                name or stock_info.name,
                f"¥{stock_info.current_price:,.0f}",
                f"¥{target_price}" if target_price else "未設定",
                price_diff_str,
                f"{(stock_info.dividend_yield or 0) * 100:.1f}%",
                f"{stock_info.pe_ratio:.1f}" if stock_info.pe_ratio else "N/A",
                f"{stock_info.pb_ratio:.1f}" if stock_info.pb_ratio else "N/A",
                memo,
                datetime.now().strftime("%Y-%m-%d")
            )
            
            self.wishlist_tree.insert("", tk.END, values=values)
            
            # 入力欄をクリア
            self.wishlist_symbol_var.set("")
            self.wishlist_name_var.set("")
            self.wishlist_target_var.set("")
            self.wishlist_memo_var.set("")
            
            messagebox.showinfo("成功", f"銘柄 {symbol} を欲しい銘柄リストに追加しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"銘柄追加エラー: {str(e)}")
    
    def remove_from_wishlist_tab(self):
        """選択された欲しい銘柄を削除"""
        selected_items = self.wishlist_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "削除する銘柄を選択してください")
            return
        
        for item in selected_items:
            self.wishlist_tree.delete(item)
        
        messagebox.showinfo("成功", f"{len(selected_items)}件の銘柄を削除しました")
    
    def clear_wishlist_tab(self):
        """欲しい銘柄リストをすべてクリア"""
        if messagebox.askyesno("確認", "欲しい銘柄リストをすべて削除しますか？"):
            for item in self.wishlist_tree.get_children():
                self.wishlist_tree.delete(item)
            messagebox.showinfo("成功", "欲しい銘柄リストをクリアしました")
    
    def move_to_watchlist_tab(self):
        """選択された欲しい銘柄を監視リストに移動"""
        selected_items = self.wishlist_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "移動する銘柄を選択してください")
            return
        
        moved_count = 0
        for item in selected_items:
            values = self.wishlist_tree.item(item)['values']
            symbol = values[1]
            name = values[2]
            
            # 監視リストに追加
            try:
                watchlist_values = (
                    values[0],  # 条件一致度
                    symbol,
                    name,
                    values[3],  # 現在価格
                    values[4],  # 目標価格
                    "0.00%",    # 変化率
                    values[6],  # 配当利回り
                    values[7],  # PER
                    values[8],  # PBR
                    "監視中"    # ステータス
                )
                self.watchlist_tree.insert("", tk.END, values=watchlist_values)
                moved_count += 1
            except Exception as e:
                print(f"移動エラー ({symbol}): {e}")
        
        # 移動した銘柄を欲しい銘柄リストから削除
        for item in selected_items:
            self.wishlist_tree.delete(item)
        
        messagebox.showinfo("成功", f"{moved_count}件の銘柄を監視リストに移動しました")
    
    def update_wishlist_prices(self):
        """欲しい銘柄の価格を更新"""
        messagebox.showinfo("更新中", "欲しい銘柄の価格更新を開始します")
        threading.Thread(target=self._update_wishlist_prices_thread, daemon=True).start()
    
    def _update_wishlist_prices_thread(self):
        """欲しい銘柄価格更新のバックグラウンド処理"""
        try:
            from data_sources import YahooFinanceDataSource
            data_source = YahooFinanceDataSource()
            
            items = self.wishlist_tree.get_children()
            updated_count = 0
            
            for item in items:
                values = list(self.wishlist_tree.item(item)['values'])
                symbol = values[1]
                
                # 株価情報を取得
                stock_info = data_source.get_stock_info(symbol)
                if stock_info:
                    # 条件チェック
                    conditions_met, _ = self.check_strategy_conditions(symbol, stock_info)
                    indicator = self.get_condition_indicator(conditions_met)
                    
                    # 価格差計算
                    target_price_str = values[4]
                    if target_price_str != "未設定":
                        try:
                            target_price_float = float(target_price_str.replace("¥", "").replace(",", ""))
                            price_diff = stock_info.current_price - target_price_float
                            price_diff_str = f"¥{price_diff:+,.0f}"
                        except:
                            price_diff_str = "N/A"
                    else:
                        price_diff_str = "N/A"
                    
                    # 値を更新
                    values[0] = indicator
                    values[3] = f"¥{stock_info.current_price:,.0f}"
                    values[5] = price_diff_str
                    values[6] = f"{(stock_info.dividend_yield or 0) * 100:.1f}%"
                    values[7] = f"{stock_info.pe_ratio:.1f}" if stock_info.pe_ratio else "N/A"
                    values[8] = f"{stock_info.pb_ratio:.1f}" if stock_info.pb_ratio else "N/A"
                    
                    self.wishlist_tree.item(item, values=values)
                    updated_count += 1
            
            self.root.after(0, lambda: messagebox.showinfo(
                "完了", f"欲しい銘柄の価格更新が完了しました。\n更新件数: {updated_count}件"
            ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "エラー", f"価格更新エラー: {str(e)}"
            ))
    
    def sort_wishlist_tab(self, column):
        """欲しい銘柄のソート機能"""
        # 簡単なソート実装
        data = []
        for item in self.wishlist_tree.get_children():
            values = self.wishlist_tree.item(item)['values']
            data.append(values)
        
        # 列インデックスを取得
        columns = ["match_level", "symbol", "name", "current_price", "target_price", 
                  "price_diff", "dividend_yield", "per", "pbr", "memo", "added_date"]
        col_index = columns.index(column)
        
        # ソート
        try:
            data.sort(key=lambda x: float(str(x[col_index]).replace("¥", "").replace(",", "").replace("%", "").replace("+", "")))
        except:
            data.sort(key=lambda x: str(x[col_index]))
        
        # Treeviewを再構築
        for item in self.wishlist_tree.get_children():
            self.wishlist_tree.delete(item)
        
        for values in data:
            self.wishlist_tree.insert("", tk.END, values=values)
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()