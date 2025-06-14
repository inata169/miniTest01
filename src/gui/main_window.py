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
from data_sources import YahooFinanceDataSource, MultiDataSource
from database import DatabaseManager
from alert_manager import AlertManager, Alert
from version import get_version_info
from dividend_visualizer import DividendVisualizer
from market_indices import MarketIndicesManager


class ToolTip:
    """ツールチップクラス"""
    
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event):
        """マウスオーバー時"""
        self.show_tooltip(event)
    
    def on_leave(self, event):
        """マウス離脱時"""
        self.hide_tooltip()
    
    def on_motion(self, event):
        """マウス移動時"""
        if self.tooltip_window:
            self.update_tooltip_position(event)
    
    def show_tooltip(self, event):
        """ツールチップ表示"""
        if not self.text:
            return
            
        if self.tooltip_window:
            return
        
        x = event.x_root + 15
        y = event.y_root + 10
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # ツールチップスタイル
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9),
            justify=tk.LEFT,
            padx=5,
            pady=3
        )
        label.pack()
    
    def update_tooltip_position(self, event):
        """ツールチップ位置更新"""
        if self.tooltip_window:
            x = event.x_root + 15
            y = event.y_root + 10
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
    
    def hide_tooltip(self):
        """ツールチップ非表示"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def update_text(self, new_text):
        """ツールチップテキスト更新"""
        self.text = new_text


class MainWindow:
    """メインGUIウィンドウクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("日本株ウォッチドッグ (Japanese Stock Watchdog)")
        self.root.geometry("1300x930")  # 1000x700 * 1.3 + 20px
        
        # 日本語フォント設定
        self.setup_japanese_font()
        
        # 初期化フラグ
        self.initialization_complete = False
        self.data_loading = False
        
        # 基本クラス初期化（軽量）
        self.csv_parser = CSVParser()
        self.db = DatabaseManager()
        self.alert_manager = AlertManager()
        
        # データソースは遅延初期化
        self.data_source = None
        self.dividend_visualizer = DividendVisualizer()
        self.market_indices_manager = MarketIndicesManager()
        
        # GUI先行表示
        self.setup_ui()
        self.update_status("起動中... データを読み込んでいます")
        
        # 非同期でデータ読み込み開始
        self.root.after(100, self.async_load_portfolio_data)
        
        # グローバルクリックイベントでコンテキストメニューをクリーンアップ
        self.root.bind('<Button-1>', self._on_global_click, add='+')
    
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
        
        # 市場指数パネル
        self.create_market_indices_panel(main_frame)
        
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
        
        # 初期データ読み込み（UIが構築された後）
        self.root.after(100, self.load_initial_data)
    
    def create_market_indices_panel(self, parent):
        """市場指数パネルを作成"""
        # 市場指数フレーム
        indices_frame = ttk.LabelFrame(parent, text="📊 主要市場指数", padding=10)
        indices_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 指数表示ラベルのフレーム
        display_frame = ttk.Frame(indices_frame)
        display_frame.pack(fill=tk.X)
        
        # 指数ラベルを格納する辞書
        self.indices_labels = {}
        
        # 横1列のレイアウト
        indices_data = [
            ('nikkei', '📈 日経平均: データ読み込み中...', 0, 0),
            ('topix', '📊 TOPIX: データ読み込み中...', 0, 1),
            ('dow', '🇺🇸 ダウ平均: データ読み込み中...', 0, 2),
            ('sp500', '🇺🇸 S&P500: データ読み込み中...', 0, 3)
        ]
        
        for key, default_text, row, col in indices_data:
            # S&P500の表示幅を広くする
            width = 32 if key == 'sp500' else 28
            label = tk.Label(display_frame, text=default_text, 
                           font=self.japanese_font, anchor='w', width=width)
            label.grid(row=row, column=col, padx=5, pady=5, sticky='w')
            self.indices_labels[key] = label
        
        # 更新ボタンフレーム
        button_frame = ttk.Frame(indices_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 更新ボタン
        update_btn = ttk.Button(button_frame, text="🔄 指数更新", 
                               command=self.update_market_indices)
        update_btn.pack(side=tk.LEFT)
        
        # 自動更新チェックボックス（設定を復元）
        self.auto_update_indices = tk.BooleanVar(value=self.load_monitoring_setting('auto_update_indices', True))
        auto_update_cb = ttk.Checkbutton(button_frame, text="自動更新 (5分間隔)", 
                                       variable=self.auto_update_indices,
                                       command=self.save_monitoring_settings)
        auto_update_cb.pack(side=tk.LEFT, padx=(10, 0))
        
        # 最終更新時刻ラベル
        self.indices_last_update_label = tk.Label(button_frame, 
                                                text="最終更新: 未取得", 
                                                font=("Arial", 8),
                                                fg="gray")
        self.indices_last_update_label.pack(side=tk.RIGHT)
        
        # 初期データ読み込み（非同期）
        self.root.after(2000, self.update_market_indices)
        
        # 自動更新タイマー（5分間隔）
        self.schedule_indices_update()
    
    def schedule_indices_update(self):
        """市場指数の自動更新をスケジュール"""
        if self.auto_update_indices.get():
            self.update_market_indices()
        
        # 5分後に再実行
        self.root.after(300000, self.schedule_indices_update)  # 300000ms = 5分
    
    def update_market_indices(self):
        """市場指数を更新"""
        def update_in_background():
            """バックグラウンドで指数を取得"""
            try:
                # 指数データを取得
                indices = self.market_indices_manager.get_all_indices()
                
                # UIを更新（メインスレッドで実行）
                def update_ui():
                    try:
                        if hasattr(self, 'indices_last_update_label') and self.indices_last_update_label.winfo_exists():
                            self.indices_last_update_label.config(text="更新中...")
                        
                        for key, index_info in indices.items():
                            if key in self.indices_labels and self.indices_labels[key].winfo_exists():
                                display_text = self.market_indices_manager.format_index_display(index_info)
                                
                                # 色分け
                                color = "black"
                                if index_info.change > 0:
                                    color = "green"
                                elif index_info.change < 0:
                                    color = "red"
                                
                                self.indices_labels[key].config(text=display_text, fg=color)
                        
                        # 最終更新時刻を更新
                        if hasattr(self, 'indices_last_update_label') and self.indices_last_update_label.winfo_exists():
                            from datetime import datetime
                            now = datetime.now().strftime("%H:%M:%S")
                            self.indices_last_update_label.config(text=f"最終更新: {now}")
                        
                    except Exception as e:
                        print(f"市場指数UI更新エラー: {e}")
                        if hasattr(self, 'indices_last_update_label') and self.indices_last_update_label.winfo_exists():
                            self.indices_last_update_label.config(text="更新エラー")
                
                # メインスレッドかどうかチェックしてからUI更新を実行
                try:
                    self.root.after(0, update_ui)
                except RuntimeError:
                    # メインループが終了している場合は何もしない
                    pass
                
            except Exception as e:
                print(f"市場指数取得エラー: {e}")
                try:
                    self.root.after(0, lambda: self.indices_last_update_label.config(text="取得エラー") if hasattr(self, 'indices_last_update_label') and self.indices_last_update_label.winfo_exists() else None)
                except RuntimeError:
                    # メインループが終了している場合は何もしない
                    pass
        
        # バックグラウンドスレッドで実行
        import threading
        thread = threading.Thread(target=update_in_background, daemon=True)
        thread.start()
    
    def load_initial_data(self):
        """初期データを読み込み"""
        try:
            self.update_status("💾 欲しい銘柄データを読み込み中...")
            self.load_wishlist_data()
            
            self.update_status("👀 監視リストデータを読み込み中...")
            self.load_watchlist_data()
            
            self.update_status("✅ 準備完了！日本株ウォッチドッグをお楽しみください")
            
            # 3秒後に通常のステータスに戻す
            self.root.after(3000, lambda: self.update_status("待機中 - CSVインポートまたは株価更新をお試しください"))
            
        except Exception as e:
            print(f"初期データ読み込みエラー: {e}")
            self.update_status("⚠️ 初期データ読み込み中にエラーが発生しました")
    
    def create_menu(self):
        """メニューバー作成"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="💼 ファイル", menu=file_menu)
        file_menu.add_command(label="📂 CSVインポート", command=lambda: self.notebook.select(1))
        file_menu.add_command(label="💾 データエクスポート", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="⚙️ 設定", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 終了", command=self.root.quit)
        
        # 表示メニュー
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="👁️ 表示", menu=view_menu)
        view_menu.add_command(label="🔄 ポートフォリオ更新", command=self.refresh_portfolio)
        view_menu.add_command(label="📈 株価更新", command=self.update_prices)
        view_menu.add_command(label="👀 監視リスト更新", command=self.update_watchlist_prices)
        view_menu.add_command(label="💝 欲しい銘柄更新", command=self.update_wishlist_prices)
        view_menu.add_separator()
        view_menu.add_command(label="📊 ポートフォリオタブ", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="📥 インポートタブ", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="🔍 監視タブ", command=lambda: self.notebook.select(2))
        view_menu.add_command(label="🚨 アラートタブ", command=lambda: self.notebook.select(3))
        
        # ツールメニュー
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 ツール", menu=tools_menu)
        tools_menu.add_command(label="🧪 アラートテスト", command=self.test_alert_system)
        tools_menu.add_command(label="🔔 通知設定", command=self.show_notification_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label="📋 戦略設定", command=self.show_strategy_settings)
        tools_menu.add_command(label="📈 配当分析", command=self.show_dividend_analysis)
        tools_menu.add_separator()
        tools_menu.add_command(label="🗑️ アラート履歴クリア", command=self.clear_alert_history)
        tools_menu.add_command(label="🧹 データベースクリーンアップ", command=self.cleanup_database)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ ヘルプ", menu=help_menu)
        help_menu.add_command(label="📋 CSVファイル取得方法", command=self.show_csv_help)
        help_menu.add_command(label="📚 使い方ガイド", command=self.show_user_guide)
        help_menu.add_command(label="⌨️ ショートカットキー", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="🔗 GitHub", command=self.open_github)
        help_menu.add_command(label="📧 フィードバック", command=self.show_feedback)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ バージョン情報", command=self.show_about)
    
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
        
        # 配当履歴タブ
        self.create_dividend_history_tab()
    
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
        
        # ツールチップ設定
        self.holdings_tooltip = ToolTip(self.holdings_tree, "")
        self.holdings_tree.bind("<Motion>", self.on_holdings_motion)
        self.holdings_tree.bind("<Leave>", self.on_holdings_leave)
        
        # 右クリックコンテキストメニュー
        self.holdings_tree.bind("<Button-3>", self.show_holdings_context_menu)  # 右クリック
        
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
        ttk.Button(button_frame, text="選択削除", command=self.delete_selected_holdings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="全て削除", command=self.delete_all_holdings).pack(side=tk.LEFT, padx=5)
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
        
        # 右クリックイベントバインディング
        self.watchlist_tree.bind("<Button-3>", self.show_watchlist_context_menu)  # 右クリック
        
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
        
        # 右クリックイベントバインディング
        self.wishlist_tree.bind("<Button-3>", self.show_wishlist_context_menu)  # 右クリック
        
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
    
    def create_dividend_history_tab(self):
        """配当履歴タブ作成"""
        dividend_tab_frame = ttk.Frame(self.portfolio_notebook)
        self.portfolio_notebook.add(dividend_tab_frame, text="配当履歴")
        
        # 上部：銘柄選択とコントロール
        control_frame = ttk.Frame(dividend_tab_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="銘柄選択:", font=self.japanese_font).pack(side=tk.LEFT, padx=5)
        
        self.dividend_symbol_var = tk.StringVar()
        symbol_entry = ttk.Entry(control_frame, textvariable=self.dividend_symbol_var, width=10)
        symbol_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="履歴取得", command=self.load_dividend_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="チャート表示", command=self.show_dividend_chart).pack(side=tk.LEFT, padx=5)
        
        # 年数選択
        ttk.Label(control_frame, text="期間:", font=self.japanese_font).pack(side=tk.LEFT, padx=(20, 5))
        self.dividend_years_var = tk.StringVar(value="5")
        years_combo = ttk.Combobox(control_frame, textvariable=self.dividend_years_var, 
                                  values=["3", "5", "10"], width=5, state="readonly")
        years_combo.pack(side=tk.LEFT, padx=5)
        
        # 中央：配当履歴テーブル
        history_frame = ttk.LabelFrame(dividend_tab_frame, text="配当履歴", padding=5)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配当履歴Treeview
        dividend_columns = ("year", "dividend", "growth_rate", "yield_estimate")
        self.dividend_tree = ttk.Treeview(history_frame, columns=dividend_columns, show="headings", height=12)
        
        # ヘッダー設定
        dividend_headers = {
            "year": "年度",
            "dividend": "配当金 (円)",
            "growth_rate": "成長率 (%)",
            "yield_estimate": "利回り推定 (%)"
        }
        
        for col, header in dividend_headers.items():
            self.dividend_tree.heading(col, text=header)
            if col == "year":
                self.dividend_tree.column(col, width=80, anchor=tk.CENTER)
            elif col == "dividend":
                self.dividend_tree.column(col, width=120, anchor=tk.E)
            else:
                self.dividend_tree.column(col, width=100, anchor=tk.E)
        
        # スクロールバー
        dividend_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.dividend_tree.yview)
        self.dividend_tree.configure(yscrollcommand=dividend_scrollbar.set)
        
        self.dividend_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dividend_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 下部：サマリー情報
        summary_frame = ttk.LabelFrame(dividend_tab_frame, text="配当分析サマリー", padding=10)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # サマリーラベル
        self.dividend_summary_labels = {}
        summary_info = [
            ("avg_growth", "平均成長率"),
            ("trend_analysis", "トレンド分析"),
            ("investment_score", "投資評価"),
            ("next_prediction", "来年予想")
        ]
        
        for i, (key, label) in enumerate(summary_info):
            ttk.Label(summary_frame, text=f"{label}:", font=self.japanese_font).grid(row=0, column=i*2, sticky=tk.W, padx=5)
            self.dividend_summary_labels[key] = ttk.Label(summary_frame, text="-", font=self.japanese_font_bold)
            self.dividend_summary_labels[key].grid(row=0, column=i*2+1, sticky=tk.W, padx=10)
    
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
        
        self.strategy_var = tk.StringVar(value=self.load_monitoring_setting('selected_strategy', "default_strategy"))
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
        
        self.condition_mode_var = tk.StringVar(value=self.load_monitoring_setting('condition_mode', "any_two_of_three"))
        modes = [
            ("strict_and", "全条件必須（AND）"),
            ("any_one", "1条件でもOK（OR）"),
            ("any_two_of_three", "3条件中2条件以上"),
            ("weighted_score", "重み付きスコア評価")
        ]
        
        for value, text in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.condition_mode_var, 
                           value=value, command=self.save_monitoring_settings).pack(anchor=tk.W, pady=2)
        
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
        # 戦略選択を保存
        self.save_monitoring_settings()
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
    
    def load_monitoring_setting(self, key, default_value):
        """監視設定を読み込み"""
        try:
            import json
            settings_file = "config/gui_settings.json"
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get('monitoring_ui', {}).get(key, default_value)
            return default_value
        except Exception:
            return default_value
    
    def save_monitoring_settings(self):
        """監視設定を保存"""
        try:
            import json
            settings_file = "config/gui_settings.json"
            
            # 既存設定を読み込み
            settings = {}
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # 監視UI設定を更新
            if 'monitoring_ui' not in settings:
                settings['monitoring_ui'] = {}
            
            settings['monitoring_ui']['auto_update_indices'] = self.auto_update_indices.get()
            
            # 戦略選択設定も保存
            if hasattr(self, 'strategy_var'):
                settings['monitoring_ui']['selected_strategy'] = self.strategy_var.get()
            
            # 評価モード設定も保存
            if hasattr(self, 'condition_mode_var'):
                settings['monitoring_ui']['condition_mode'] = self.condition_mode_var.get()
            
            # 設定を保存
            os.makedirs("config", exist_ok=True)
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"監視設定保存エラー: {e}")
    
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
            
            # 有効な銘柄シンボルをフィルタリング
            valid_symbols = []
            skipped_count = 0
            
            for symbol in symbols:
                try:
                    if symbol is None:
                        skipped_count += 1
                        continue
                    symbol_str = str(symbol).strip()
                    if not symbol_str:
                        skipped_count += 1
                        continue
                except (TypeError, AttributeError):
                    skipped_count += 1
                    continue
                
                # 疑似シンボルをスキップ（より厳密なチェック）
                if (symbol_str.startswith('PORTFOLIO_') or 
                    symbol_str.startswith('FUND_') or
                    symbol_str == 'STOCK_PORTFOLIO' or
                    symbol_str == 'TOTAL_PORTFOLIO' or
                    len(symbol_str) > 10):  # 通常の銘柄コードは10文字以下
                    print(f"疑似シンボルをスキップ: {symbol_str}")
                    skipped_count += 1
                    continue
                
                valid_symbols.append(symbol_str)
            
            # バッチ処理で株価取得（API制限対策）
            price_updates = {}
            error_count = 0
            
            if valid_symbols:
                self.update_status(f"株価取得中... ({len(valid_symbols)}銘柄)")
                
                # 小バッチに分割してレート制限を回避
                batch_size = 5
                for i in range(0, len(valid_symbols), batch_size):
                    batch = valid_symbols[i:i+batch_size]
                    
                    try:
                        # バッチで取得（J Quants API優先）
                        batch_results = self.data_source.get_multiple_stocks(batch)
                        
                        for symbol, stock_info in batch_results.items():
                            if stock_info:
                                price_updates[symbol] = stock_info.current_price
                            else:
                                error_count += 1
                        
                        # プログレス更新
                        progress = min(i + batch_size, len(valid_symbols))
                        self.update_status(f"株価取得中... ({progress}/{len(valid_symbols)})")
                        
                        # バッチ間でレート制限対策（J Quantsは不要だが、Yahoo Finance用）
                        if i + batch_size < len(valid_symbols):
                            import time
                            time.sleep(0.5)  # 0.5秒待機
                            
                    except Exception as e:
                        print(f"バッチ取得エラー: {e}")
                        # 個別フォールバック
                        for symbol in batch:
                            try:
                                stock_info = self.data_source.get_stock_info(symbol)
                                if stock_info:
                                    price_updates[symbol] = stock_info.current_price
                                else:
                                    error_count += 1
                            except:
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
                        conditions_met, _, sell_signal = self.check_strategy_conditions(symbol_str, stock_info)
                        indicator = self.get_condition_indicator(conditions_met, sell_signal)
                        # 売り信号がある場合は条件数を特別扱い
                        if sell_signal:
                            conditions_met = 99  # 売り信号用の特別値
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
            
            # 条件マッチング用の色分け（売り信号を含む）
            self.holdings_tree.tag_configure('condition_99', background='#ffebee', foreground='#c62828', font=self.japanese_font_bold)  # 💰利確/⛔損切り（ピンク）
            self.holdings_tree.tag_configure('condition_3', background='#c8e6c9', foreground='#1b5e20', font=self.japanese_font_bold)   # 🔥買い頃！（濃い緑）
            self.holdings_tree.tag_configure('condition_2', background='#fff3e0', foreground='#ef6c00', font=self.japanese_font_bold)   # ⚡検討中（薄いオレンジ）
            self.holdings_tree.tag_configure('condition_1', background='#e3f2fd', foreground='#1976d2', font=self.japanese_font_bold)   # 👀監視中（青）
            self.holdings_tree.tag_configure('condition_0', background='#f5f5f5', foreground='#616161')                               # 😴様子見（グレー）
            
        except Exception as e:
            messagebox.showerror("エラー", f"ポートフォリオ更新エラー: {str(e)}")
    
    def check_strategy_conditions(self, symbol, stock_info):
        """戦略条件をチェックして条件マッチ数と売買判定を返す"""
        try:
            # デフォルト戦略を取得
            import json
            with open('config/strategies.json', 'r', encoding='utf-8') as f:
                strategies = json.load(f)
            
            strategy = strategies.get('default_strategy', {})
            buy_conditions = strategy.get('buy_conditions', {})
            sell_conditions = strategy.get('sell_conditions', {})
            
            # 買い条件チェック
            buy_conditions_met = 0
            buy_details = []
            
            # 配当利回りチェック（Yahoo Financeは小数形式で返す）
            dividend_yield = (stock_info.dividend_yield or 0)
            dividend_min = buy_conditions.get('dividend_yield_min', 2.0)
            if dividend_yield >= dividend_min:
                buy_conditions_met += 1
                buy_details.append(f"配当 {dividend_yield:.1f}%≥{dividend_min}%")
            
            # PERチェック（厳しく設定）
            per = stock_info.pe_ratio or 0
            per_max = buy_conditions.get('per_max', 15.0)
            if per > 0 and per <= per_max:
                buy_conditions_met += 1
                buy_details.append(f"PER {per:.1f}≤{per_max}")
            
            # PBRチェック（厳しく設定）
            pbr = stock_info.pb_ratio or 0
            pbr_max = buy_conditions.get('pbr_max', 1.5)
            if pbr > 0 and pbr <= pbr_max:
                buy_conditions_met += 1
                buy_details.append(f"PBR {pbr:.1f}≤{pbr_max}")
            
            # 売り条件チェック（保有銘柄用）
            sell_signal = self.check_sell_conditions(symbol, stock_info, sell_conditions)
            
            return buy_conditions_met, buy_details, sell_signal
            
        except Exception as e:
            print(f"条件チェックエラー: {e}")
            return 0, [], None
    
    def check_sell_conditions(self, symbol, stock_info, sell_conditions):
        """売り条件をチェック"""
        try:
            # データベースから保有情報を取得
            holdings = self.db.get_all_holdings()
            holding_info = next((h for h in holdings if str(h['symbol']) == str(symbol)), None)
            
            if not holding_info:
                return None
            
            # 利益率計算
            acquisition_amount = holding_info.get('acquisition_amount', 0) or 0
            market_value = holding_info.get('market_value', 0) or 0
            profit_rate = ((market_value / acquisition_amount) - 1) * 100 if acquisition_amount > 0 else 0
            
            # 利益確定条件
            profit_target = sell_conditions.get('profit_target', 15.0)
            if profit_rate >= profit_target:
                return f"💰利確推奨 (+{profit_rate:.1f}%)"
            
            # 損切り条件
            stop_loss = sell_conditions.get('stop_loss', -8.0)
            if profit_rate <= stop_loss:
                return f"⛔損切り推奨 ({profit_rate:.1f}%)"
            
            return None
            
        except Exception as e:
            print(f"売り条件チェックエラー: {e}")
            return None
    
    def get_condition_indicator(self, conditions_met, sell_signal=None):
        """条件マッチ数と売り信号に応じた表示インジケーターを返す"""
        # 売り信号が最優先
        if sell_signal:
            return sell_signal
        
        # 買い条件の評価（より厳格に）
        if conditions_met >= 3:
            return "🔥買い頃！"  # 3条件すべて満たす
        elif conditions_met == 2:
            return "⚡検討中"    # 2条件満たす（表現を控えめに）
        elif conditions_met == 1:
            return "👀監視中"    # 1条件満たす
        else:
            return "😴様子見"    # 条件満たさない
    
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
            conditions_met, condition_details, sell_signal = self.check_strategy_conditions(symbol, stock_info)
            indicator = self.get_condition_indicator(conditions_met, sell_signal)
            
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
                f"{(stock_info.dividend_yield or 0):.1f}%",
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
            
            # データベースに保存
            target_price_float = None
            if target_price:
                try:
                    target_price_float = float(target_price)
                except:
                    pass
            
            success = self.db.add_to_watchlist(
                symbol=symbol,
                name=name or stock_info.name,
                strategy_name="default_strategy",
                target_buy_price=target_price_float,
                target_sell_price=None
            )
            
            if not success:
                messagebox.showwarning("警告", "データベースへの保存に失敗しました")
            
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
                
                # 型変換による安全性確保
                try:
                    if symbol is None:
                        continue
                    symbol_str = str(symbol).strip()
                    if not symbol_str or symbol_str.startswith('PORTFOLIO_'):
                        continue
                    symbol = symbol_str
                except (TypeError, AttributeError):
                    continue
                
                # 株価情報を取得
                stock_info = data_source.get_stock_info(symbol)
                if stock_info:
                    # 条件チェック
                    conditions_met, _, sell_signal = self.check_strategy_conditions(symbol, stock_info)
                    indicator = self.get_condition_indicator(conditions_met, sell_signal)
                    
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
                        f"{(stock_info.dividend_yield or 0):.1f}%",
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

    def async_load_portfolio_data(self):
        """非同期でポートフォリオデータを読み込み"""
        if self.data_loading:
            return
            
        self.data_loading = True
        
        def load_in_background():
            """バックグラウンドでデータ読み込み"""
            try:
                # データソースの遅延初期化（J Quants APIを優先）
                if self.data_source is None:
                    self.update_status_thread_safe("データソース初期化中...")
                    from data_sources import MultiDataSource
                    from dotenv import load_dotenv
                    import os
                    
                    load_dotenv()
                    jquants_email = os.getenv('JQUANTS_EMAIL')
                    jquants_password = os.getenv('JQUANTS_PASSWORD') 
                    refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
                    
                    self.data_source = MultiDataSource(jquants_email, jquants_password, refresh_token)
                
                # ポートフォリオデータを読み込み
                self.update_status_thread_safe("ポートフォリオデータ読み込み中...")
                self.root.after(0, self.refresh_portfolio)
                
                # アラート履歴を読み込み
                self.update_status_thread_safe("アラート履歴読み込み中...")
                self.root.after(0, self.refresh_alerts)
                
                # 完了
                self.initialization_complete = True
                self.data_loading = False
                self.update_status_thread_safe("準備完了")
                
            except Exception as e:
                self.update_status_thread_safe(f"初期化エラー: {e}")
                self.data_loading = False
        
        # バックグラウンドスレッドで実行
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def update_status_thread_safe(self, message):
        """スレッドセーフなステータス更新"""
        self.root.after(0, lambda: self.update_status(message))
    
    def load_portfolio_data(self):
        """起動時にポートフォリオデータを読み込み（互換性のため残存）"""
        if not self.initialization_complete:
            self.async_load_portfolio_data()
        else:
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
            "📈 日本株式市場をリアルタイム監視する完全無料ツール\n"
            "🏦 SBI証券・楽天証券CSVインポート完全対応\n"
            "📊 日本株・米国株のリアルタイム株価監視\n\n"
            "🔄 データソース: J Quants API（日本株専用・無料）\n"
            "📈 フォールバック: Yahoo Finance API（世界株式対応）\n"
            "📧 通知: Discord, Gmail, デスクトップ通知\n\n"
            "💰 収益率計算: (評価金額 ÷ 取得金額 - 1) × 100%\n"
            "📊 財務指標: PER・PBR・ROE・配当利回り表示\n"
            "📈 配当分析: 過去5年間の配当履歴グラフ\n\n"
            "🎯 v1.4.4の主要機能:\n"
            "✅ Windows完全対応（ワンクリック起動）\n"
            "⚡ J Quants API統合（レート制限回避）\n"
            "🔍 マウスホバー銘柄詳細表示\n"
            "📊 主要市場指数リアルタイム表示\n"
            "🎨 配当可視化と投資判断支援\n\n"
            "🌟 サラリーマン投資家の皆様へ:\n"
            "⏰ 忙しい毎日でも効率的な投資判断をサポート\n"
            "💸 完全無料・オープンソースで安心利用"
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
            conditions_met, condition_details, sell_signal = self.check_strategy_conditions(symbol, stock_info)
            indicator = self.get_condition_indicator(conditions_met, sell_signal)
            
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
                f"{(stock_info.dividend_yield or 0):.1f}%",
                f"{stock_info.pe_ratio:.1f}" if stock_info.pe_ratio else "N/A",
                f"{stock_info.pb_ratio:.1f}" if stock_info.pb_ratio else "N/A",
                memo,
                datetime.now().strftime("%Y-%m-%d")
            )
            
            self.wishlist_tree.insert("", tk.END, values=values)
            
            # データベースに保存
            target_price_float = None
            if target_price:
                try:
                    target_price_float = float(target_price)
                except:
                    pass
            
            success = self.db.add_to_wishlist(
                symbol=symbol,
                name=name or stock_info.name,
                target_price=target_price_float,
                memo=memo
            )
            
            if not success:
                messagebox.showwarning("警告", "データベースへの保存に失敗しました")
            
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
                try:
                    if len(values) < 2 or values[1] is None:
                        continue
                    symbol = str(values[1]).strip()
                    if not symbol:
                        continue
                except (TypeError, AttributeError, IndexError):
                    continue
                
                # 株価情報を取得
                stock_info = data_source.get_stock_info(symbol)
                if stock_info:
                    # 条件チェック
                    conditions_met, _, sell_signal = self.check_strategy_conditions(symbol, stock_info)
                    indicator = self.get_condition_indicator(conditions_met, sell_signal)
                    
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
                    values[6] = f"{(stock_info.dividend_yield or 0):.1f}%"
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
    
    def delete_selected_holdings(self):
        """選択した保有銘柄を削除"""
        selected_items = self.holdings_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "削除する銘柄を選択してください。")
            return
        
        # 削除確認
        selected_count = len(selected_items)
        result = messagebox.askyesno(
            "削除確認", 
            f"選択した{selected_count}件の保有銘柄を削除しますか？\n\n"
            "この操作は元に戻せません。"
        )
        
        if result:
            try:
                deleted_symbols = []
                for item in selected_items:
                    values = self.holdings_tree.item(item, "values")
                    symbol = values[1]  # 銘柄コード列
                    
                    # データベースから削除
                    self.db.delete_holding(symbol)
                    deleted_symbols.append(symbol)
                
                # 表示を更新
                self.refresh_portfolio()
                
                messagebox.showinfo(
                    "削除完了", 
                    f"{len(deleted_symbols)}件の保有銘柄を削除しました:\n" + 
                    ", ".join(deleted_symbols)
                )
                
            except Exception as e:
                messagebox.showerror("エラー", f"削除中にエラーが発生しました:\n{e}")
    
    def delete_all_holdings(self):
        """全ての保有銘柄を削除"""
        # 現在の保有銘柄数を確認
        holdings_count = len(self.holdings_tree.get_children())
        if holdings_count == 0:
            messagebox.showinfo("情報", "削除する保有銘柄がありません。")
            return
        
        # 削除確認（二重確認）
        result = messagebox.askyesno(
            "全削除確認", 
            f"全ての保有銘柄（{holdings_count}件）を削除しますか？\n\n"
            "⚠️ この操作は元に戻せません！ ⚠️\n\n"
            "本当に削除しますか？"
        )
        
        if result:
            # 二重確認
            final_result = messagebox.askyesno(
                "最終確認", 
                "本当に全ての保有銘柄を削除しますか？\n\n"
                "この操作は取り消しできません。",
                icon="warning"
            )
            
            if final_result:
                try:
                    # データベースから全削除
                    deleted_count = self.db.delete_all_holdings()
                    
                    # 表示を更新
                    self.refresh_portfolio()
                    
                    messagebox.showinfo(
                        "削除完了", 
                        f"全ての保有銘柄（{deleted_count}件）を削除しました。"
                    )
                    
                except Exception as e:
                    messagebox.showerror("エラー", f"削除中にエラーが発生しました:\n{e}")

    def on_holdings_motion(self, event):
        """保有銘柄テーブルでのマウス移動"""
        item = self.holdings_tree.identify_row(event.y)
        if item:
            values = self.holdings_tree.item(item, "values")
            if values and len(values) > 1:
                symbol = values[1]  # 銘柄コード
                
                # 株価詳細情報を取得してツールチップに表示
                self.show_stock_tooltip(symbol, event)
        else:
            self.holdings_tooltip.hide_tooltip()
    
    def on_holdings_leave(self, event):
        """保有銘柄テーブルからマウスが離れた"""
        self.holdings_tooltip.hide_tooltip()
    
    def show_stock_tooltip(self, symbol, event):
        """株価詳細ツールチップを表示"""
        if not symbol or not self.data_source:
            return
        
        # 疑似シンボルの場合はスキップ
        if (symbol.startswith('PORTFOLIO_') or 
            symbol.startswith('FUND_') or
            symbol == 'STOCK_PORTFOLIO' or
            symbol == 'TOTAL_PORTFOLIO'):
            # 投資信託などの基本情報のみ表示
            tooltip_text = f"📋 {symbol}\\n"
            tooltip_text += "━━━━━━━━━━━━━━━━━━━━━━\\n"
            tooltip_text += "💼 投資信託・ETF\\n"
            tooltip_text += "ℹ️  詳細情報は証券会社サイトで確認"
            
            self.holdings_tooltip.update_text(tooltip_text)
            if not self.holdings_tooltip.tooltip_window:
                self.holdings_tooltip.show_tooltip(event)
            return
        
        try:
            # データソースから詳細情報を取得
            stock_info = self.data_source.get_stock_info(symbol)
            
            if stock_info:
                # ツールチップテキスト作成
                tooltip_text = f"📊 {stock_info.name} ({symbol})\\n"
                tooltip_text += f"━━━━━━━━━━━━━━━━━━━━━━\\n"
                tooltip_text += f"💰 現在価格: ¥{stock_info.current_price:,.0f}\\n"
                
                if stock_info.pe_ratio:
                    tooltip_text += f"📈 PER: {stock_info.pe_ratio:.2f}\\n"
                else:
                    tooltip_text += f"📈 PER: データなし\\n"
                
                if stock_info.pb_ratio:
                    tooltip_text += f"📊 PBR: {stock_info.pb_ratio:.2f}\\n"
                else:
                    tooltip_text += f"📊 PBR: データなし\\n"
                
                if stock_info.dividend_yield:
                    tooltip_text += f"💎 配当利回り: {stock_info.dividend_yield:.2f}%\\n"
                else:
                    tooltip_text += f"💎 配当利回り: データなし\\n"
                
                if stock_info.market_cap:
                    if stock_info.market_cap >= 1000000000000:  # 1兆円以上
                        cap_text = f"{stock_info.market_cap/1000000000000:.1f}兆円"
                    elif stock_info.market_cap >= 100000000000:  # 1000億円以上
                        cap_text = f"{stock_info.market_cap/100000000000:.1f}千億円"
                    else:
                        cap_text = f"{stock_info.market_cap/100000000:.0f}億円"
                    tooltip_text += f"🏢 時価総額: {cap_text}\\n"
                
                tooltip_text += f"📅 更新: {datetime.now().strftime('%H:%M:%S')}"
                
                # ツールチップ更新
                self.holdings_tooltip.update_text(tooltip_text)
                
                # 位置調整
                x = event.x_root + 15
                y = event.y_root + 10
                if self.holdings_tooltip.tooltip_window:
                    self.holdings_tooltip.tooltip_window.wm_geometry(f"+{x}+{y}")
                else:
                    self.holdings_tooltip.show_tooltip(event)
            else:
                # データ取得失敗
                self.holdings_tooltip.update_text(f"❌ {symbol}\\nデータ取得失敗")
                if not self.holdings_tooltip.tooltip_window:
                    self.holdings_tooltip.show_tooltip(event)
                    
        except Exception as e:
            # エラー時
            self.holdings_tooltip.update_text(f"⚠️ {symbol}\\nエラー: {str(e)[:50]}")
            if not self.holdings_tooltip.tooltip_window:
                self.holdings_tooltip.show_tooltip(event)

    def show_holdings_context_menu(self, event):
        """保有銘柄の右クリックコンテキストメニュー表示"""
        try:
            # 既存のコンテキストメニューをクリーンアップ
            self._cleanup_context_menu()
            
            # クリックされた項目を特定
            item = self.holdings_tree.identify('item', event.x, event.y)
            if not item:
                return
            
            # 項目を選択状態にする
            self.holdings_tree.selection_set(item)
            
            # 銘柄コードを取得
            values = self.holdings_tree.item(item, 'values')
            if not values or len(values) < 2:
                return
            
            # 型安全性を確保
            try:
                symbol = str(values[1]).strip()
                if not symbol:
                    return
            except (TypeError, AttributeError):
                return
            
            # 疑似シンボルの場合はメニューを表示しない
            if (symbol.startswith('PORTFOLIO_') or 
                symbol.startswith('FUND_') or
                symbol == 'STOCK_PORTFOLIO' or
                symbol == 'TOTAL_PORTFOLIO'):
                return
            
            # コンテキストメニュー作成（インスタンス変数として保存）
            self._context_menu = tk.Menu(self.root, tearoff=0)
            
            # 安全なコマンド関数を作成
            def make_command(action_symbol, action_type):
                def command():
                    try:
                        if action_type == 'dividend_history':
                            self.show_dividend_history_for_symbol(action_symbol)
                        elif action_type == 'dividend_chart':
                            self.show_dividend_chart_for_symbol(action_symbol)
                        elif action_type == 'delete':
                            self.delete_selected_holding(action_symbol)
                        elif action_type == 'test_alert':
                            self.test_alert_for_symbol(action_symbol)
                    except Exception as e:
                        messagebox.showerror("エラー", f"操作中にエラーが発生しました: {e}")
                return command
            
            # メニュー項目追加
            self._context_menu.add_command(
                label=f"Show {symbol} Dividend History",
                command=make_command(symbol, 'dividend_history')
            )
            self._context_menu.add_command(
                label=f"Show {symbol} Dividend Chart", 
                command=make_command(symbol, 'dividend_chart')
            )
            self._context_menu.add_separator()
            self._context_menu.add_command(
                label=f"Delete {symbol}",
                command=make_command(symbol, 'delete')
            )
            self._context_menu.add_command(
                label="Delete All Holdings",
                command=self.delete_all_holdings
            )
            self._context_menu.add_separator()
            self._context_menu.add_command(
                label=f"Test Alert for {symbol}",
                command=make_command(symbol, 'test_alert')
            )
            
            # メニュー表示（安全な位置決め付き）
            self._safe_menu_post(self._context_menu, event.x_root, event.y_root)
            
        except Exception as e:
            self.update_status(f"コンテキストメニューエラー: {e}")
            messagebox.showerror("エラー", f"メニュー表示中にエラーが発生しました: {e}")

    def show_wishlist_context_menu(self, event):
        """欲しい銘柄の右クリックコンテキストメニュー表示"""
        try:
            # 既存のコンテキストメニューをクリーンアップ
            self._cleanup_context_menu()
            
            # クリックされた項目を特定
            item = self.wishlist_tree.identify('item', event.x, event.y)
            if not item:
                return
            
            # 項目を選択状態にする
            self.wishlist_tree.selection_set(item)
            
            # 銘柄コードを取得
            values = self.wishlist_tree.item(item, 'values')
            if not values or len(values) < 2:
                return
            
            # 型安全性を確保
            try:
                symbol = str(values[1]).strip()
                if not symbol:
                    return
            except (TypeError, AttributeError):
                return
            
            # 疑似シンボルの場合はメニューを表示しない
            if (symbol.startswith('PORTFOLIO_') or 
                symbol.startswith('FUND_') or
                symbol == 'STOCK_PORTFOLIO' or
                symbol == 'TOTAL_PORTFOLIO'):
                return
            
            # コンテキストメニュー作成（インスタンス変数として保存）
            self._context_menu = tk.Menu(self.root, tearoff=0)
            
            # 安全なコマンド関数を作成
            def make_wishlist_command(action_symbol, action_type):
                def command():
                    try:
                        if action_type == 'dividend_history':
                            self.show_dividend_history_for_symbol(action_symbol)
                        elif action_type == 'dividend_chart':
                            self.show_dividend_chart_for_symbol(action_symbol)
                        elif action_type == 'delete':
                            self.delete_from_wishlist_by_symbol(action_symbol)
                        elif action_type == 'test_alert':
                            self.test_alert_for_symbol(action_symbol)
                    except Exception as e:
                        messagebox.showerror("エラー", f"操作中にエラーが発生しました: {e}")
                return command
            
            # メニュー項目追加
            self._context_menu.add_command(
                label=f"📈 {symbol} の配当履歴表示",
                command=make_wishlist_command(symbol, 'dividend_history')
            )
            self._context_menu.add_command(
                label=f"📊 {symbol} の配当チャート生成", 
                command=make_wishlist_command(symbol, 'dividend_chart')
            )
            self._context_menu.add_separator()
            self._context_menu.add_command(
                label=f"🗑️ {symbol} を削除",
                command=make_wishlist_command(symbol, 'delete')
            )
            self._context_menu.add_separator()
            self._context_menu.add_command(
                label=f"🧪 {symbol} のアラートテスト",
                command=make_wishlist_command(symbol, 'test_alert')
            )
            
            # メニュー表示（安全な位置決め付き）
            self._safe_menu_post(self._context_menu, event.x_root, event.y_root)
            
        except Exception as e:
            self.update_status(f"欲しい銘柄メニューエラー: {e}")
            messagebox.showerror("エラー", f"メニュー表示中にエラーが発生しました: {e}")
    
    def show_watchlist_context_menu(self, event):
        """監視リストの右クリックコンテキストメニュー表示"""
        try:
            # 既存のコンテキストメニューをクリーンアップ
            self._cleanup_context_menu()
            
            # クリックされた項目を特定
            item = self.watchlist_tree.identify('item', event.x, event.y)
            if not item:
                return
            
            # 項目を選択状態にする
            self.watchlist_tree.selection_set(item)
            
            # 銘柄コードを取得
            values = self.watchlist_tree.item(item, 'values')
            if not values or len(values) < 2:
                return
            
            # 型安全性を確保
            try:
                symbol = str(values[1]).strip()
                if not symbol:
                    return
            except (TypeError, AttributeError):
                return
            
            # 疑似シンボルの場合はメニューを表示しない
            if (symbol.startswith('PORTFOLIO_') or 
                symbol.startswith('FUND_') or
                symbol == 'STOCK_PORTFOLIO' or
                symbol == 'TOTAL_PORTFOLIO'):
                return
            
            # コンテキストメニュー作成（インスタンス変数として保存）
            self._context_menu = tk.Menu(self.root, tearoff=0)
            
            # 安全なコマンド関数を作成
            def make_watchlist_command(action_symbol, action_type):
                def command():
                    try:
                        if action_type == 'dividend_history':
                            self.show_dividend_history_for_symbol(action_symbol)
                        elif action_type == 'dividend_chart':
                            self.show_dividend_chart_for_symbol(action_symbol)
                        elif action_type == 'delete':
                            self.delete_from_watchlist_by_symbol(action_symbol)
                        elif action_type == 'test_alert':
                            self.test_alert_for_symbol(action_symbol)
                    except Exception as e:
                        messagebox.showerror("エラー", f"操作中にエラーが発生しました: {e}")
                return command
            
            # メニュー項目追加
            self._context_menu.add_command(
                label=f"📈 {symbol} の配当履歴表示",
                command=make_watchlist_command(symbol, 'dividend_history')
            )
            self._context_menu.add_command(
                label=f"📊 {symbol} の配当チャート生成", 
                command=make_watchlist_command(symbol, 'dividend_chart')
            )
            self._context_menu.add_separator()
            self._context_menu.add_command(
                label=f"🗑️ {symbol} を削除",
                command=make_watchlist_command(symbol, 'delete')
            )
            self._context_menu.add_separator()
            self._context_menu.add_command(
                label=f"🧪 {symbol} のアラートテスト",
                command=make_watchlist_command(symbol, 'test_alert')
            )
            
            # メニュー表示（安全な位置決め付き）
            self._safe_menu_post(self._context_menu, event.x_root, event.y_root)
            
        except Exception as e:
            self.update_status(f"監視リストメニューエラー: {e}")
            messagebox.showerror("エラー", f"メニュー表示中にエラーが発生しました: {e}")
    
    def delete_from_wishlist_by_symbol(self, symbol):
        """欲しい銘柄から削除"""
        try:
            result = messagebox.askyesno("確認", f"銘柄 {symbol} を欲しい銘柄リストから削除しますか？")
            if result:
                # データベースから削除
                success = self.db.delete_from_wishlist(symbol)
                if success:
                    # Treeviewから削除
                    for item in self.wishlist_tree.get_children():
                        values = self.wishlist_tree.item(item, 'values')
                        if values and len(values) > 1 and values[1] == symbol:
                            self.wishlist_tree.delete(item)
                            break
                    
                    self.update_status(f"欲しい銘柄削除完了: {symbol}")
                    messagebox.showinfo("完了", f"銘柄 {symbol} を欲しい銘柄リストから削除しました")
                else:
                    messagebox.showerror("エラー", "削除に失敗しました")
        except Exception as e:
            self.update_status(f"欲しい銘柄削除エラー: {e}")
            messagebox.showerror("エラー", f"削除中にエラーが発生しました: {e}")
    
    def delete_from_watchlist_by_symbol(self, symbol):
        """監視リストから削除"""
        try:
            result = messagebox.askyesno("確認", f"銘柄 {symbol} を監視リストから削除しますか？")
            if result:
                # データベースから削除
                success = self.db.delete_from_watchlist(symbol)
                if success:
                    # Treeviewから削除
                    for item in self.watchlist_tree.get_children():
                        values = self.watchlist_tree.item(item, 'values')
                        if values and len(values) > 1 and values[1] == symbol:
                            self.watchlist_tree.delete(item)
                            break
                    
                    self.update_status(f"監視リスト削除完了: {symbol}")
                    messagebox.showinfo("完了", f"銘柄 {symbol} を監視リストから削除しました")
                else:
                    messagebox.showerror("エラー", "削除に失敗しました")
        except Exception as e:
            self.update_status(f"監視リスト削除エラー: {e}")
            messagebox.showerror("エラー", f"削除中にエラーが発生しました: {e}")

    def show_dividend_history_for_symbol(self, symbol):
        """指定銘柄の配当履歴を配当履歴タブに表示"""
        try:
            # 配当履歴タブに移動
            self.portfolio_notebook.select(3)  # 配当履歴タブ（0:保有, 1:ウォッチ, 2:欲しい, 3:配当履歴）
            
            # 銘柄コードを設定
            self.dividend_symbol_var.set(symbol)
            
            # 履歴取得を実行
            self.load_dividend_history()
            
        except Exception as e:
            self.update_status(f"配当履歴表示エラー: {e}")
            messagebox.showerror("エラー", f"配当履歴表示中にエラーが発生しました: {e}")

    def show_dividend_chart_for_symbol(self, symbol):
        """指定銘柄の配当グラフを表示"""
        try:
            # 配当履歴タブに移動
            self.portfolio_notebook.select(3)  # 配当履歴タブ
            
            # 銘柄コードを設定
            self.dividend_symbol_var.set(symbol)
            
            # グラフ表示を実行
            self.show_dividend_chart()
            
        except Exception as e:
            self.update_status(f"配当グラフ表示エラー: {e}")
            messagebox.showerror("エラー", f"配当グラフ表示中にエラーが発生しました: {e}")

    def delete_selected_holding(self, symbol):
        """指定銘柄を削除"""
        try:
            result = messagebox.askyesno("確認", f"銘柄 {symbol} を削除しますか？")
            if not result:
                return
            
            # データベースから削除
            self.db.delete_holding_by_symbol(symbol)
            
            # ポートフォリオ表示を更新
            self.load_portfolio_data()
            
            self.update_status(f"銘柄削除完了: {symbol}")
            messagebox.showinfo("完了", f"銘柄 {symbol} を削除しました")
            
        except Exception as e:
            self.update_status(f"銘柄削除エラー: {e}")
            messagebox.showerror("エラー", f"銘柄削除中にエラーが発生しました: {e}")

    def delete_all_holdings(self):
        """全銘柄削除"""
        try:
            result = messagebox.askyesno("確認", "全ての保有銘柄を削除しますか？\n\nこの操作は元に戻せません。")
            if not result:
                return
            
            # 二重確認
            result2 = messagebox.askyesno("最終確認", "本当に全ての保有銘柄を削除しますか？")
            if not result2:
                return
            
            # データベースから全削除
            holdings = self.db.get_all_holdings()
            count = len(holdings)
            
            for holding in holdings:
                self.db.delete_holding_by_symbol(holding['symbol'])
            
            # ポートフォリオ表示を更新
            self.load_portfolio_data()
            
            self.update_status(f"全銘柄削除完了: {count}件")
            messagebox.showinfo("完了", f"{count}件の銘柄を削除しました")
            
        except Exception as e:
            self.update_status(f"全銘柄削除エラー: {e}")
            messagebox.showerror("エラー", f"全銘柄削除中にエラーが発生しました: {e}")

    def test_alert_for_symbol(self, symbol):
        """指定銘柄のアラートテスト"""
        try:
            self.update_status(f"アラートテスト中: {symbol}")
            
            # データソース確認
            if not self.data_source:
                from dotenv import load_dotenv
                import os
                load_dotenv()
                
                jquants_email = os.getenv('JQUANTS_EMAIL')
                jquants_password = os.getenv('JQUANTS_PASSWORD')
                refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
                
                self.data_source = MultiDataSource(jquants_email, jquants_password, refresh_token)
            
            # 株価情報取得
            stock_info = self.data_source.get_stock_info(symbol)
            
            if not stock_info:
                messagebox.showwarning("警告", f"銘柄 {symbol} の株価データを取得できませんでした")
                return
            
            # テストアラート送信
            per_text = f"PER: {stock_info.pe_ratio:.2f}" if stock_info.pe_ratio else "PER: N/A"
            pbr_text = f"PBR: {stock_info.pb_ratio:.2f}" if stock_info.pb_ratio else "PBR: N/A" 
            dividend_text = f"配当利回り: {stock_info.dividend_yield:.2f}%" if stock_info.dividend_yield else "配当利回り: N/A"
            roe_text = f"ROE: {stock_info.roe:.2f}%" if stock_info.roe else "ROE: N/A"
            
            test_message = (f"🧪 アラートテスト\n"
                           f"銘柄: {stock_info.name} ({symbol})\n"
                           f"現在価格: ¥{stock_info.current_price:,.0f}\n"
                           f"{per_text}\n"
                           f"{pbr_text}\n"
                           f"{dividend_text}\n"
                           f"{roe_text}\n"
                           f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # アラート送信
            test_alert = Alert(
                symbol=symbol,
                alert_type="test",
                message=test_message,
                triggered_price=stock_info.current_price,
                strategy_name="manual_test",
                timestamp=datetime.now()
            )
            self.alert_manager.send_alert(test_alert)
            
            self.update_status(f"アラートテスト完了: {symbol}")
            messagebox.showinfo("完了", f"銘柄 {symbol} のテストアラートを送信しました")
            
        except Exception as e:
            self.update_status(f"アラートテストエラー: {e}")
            messagebox.showerror("エラー", f"アラートテスト中にエラーが発生しました: {e}")

    def load_dividend_history(self):
        """配当履歴を読み込み"""
        symbol = self.dividend_symbol_var.get().strip()
        if not symbol:
            messagebox.showwarning("警告", "銘柄コードを入力してください")
            return
        
        try:
            years = int(self.dividend_years_var.get())
            
            # データソース確認
            if not self.data_source:
                from dotenv import load_dotenv
                import os
                load_dotenv()
                
                jquants_email = os.getenv('JQUANTS_EMAIL')
                jquants_password = os.getenv('JQUANTS_PASSWORD') 
                refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
                
                self.data_source = MultiDataSource(jquants_email, jquants_password, refresh_token)
            
            self.update_status(f"配当履歴取得中: {symbol}")
            
            # 配当履歴取得
            dividend_history = self.data_source.get_dividend_history(symbol, years)
            
            # テーブルクリア
            for item in self.dividend_tree.get_children():
                self.dividend_tree.delete(item)
            
            if not dividend_history:
                self.update_status(f"配当履歴なし: {symbol}")
                messagebox.showinfo("情報", f"銘柄 {symbol} の配当履歴が見つかりませんでした")
                return
            
            # 成長率計算とテーブル更新
            self._update_dividend_table(symbol, dividend_history)
            
            # サマリー更新
            self._update_dividend_summary(dividend_history)
            
            self.update_status(f"配当履歴表示完了: {symbol} ({len(dividend_history)}年分)")
            
        except Exception as e:
            self.update_status("配当履歴取得エラー")
            messagebox.showerror("エラー", f"配当履歴取得中にエラーが発生しました: {e}")
    
    def _update_dividend_table(self, symbol, dividend_history):
        """配当テーブルを更新"""
        # 現在価格取得（利回り計算用）
        current_price = None
        if self.data_source:
            stock_info = self.data_source.get_stock_info(symbol)
            if stock_info:
                current_price = stock_info.current_price
        
        # 年度順にソート
        sorted_history = sorted(dividend_history, key=lambda x: x['year'])
        
        for i, record in enumerate(sorted_history):
            year = record['year']
            dividend = record['dividend']
            
            # 成長率計算
            if i > 0:
                prev_dividend = sorted_history[i-1]['dividend']
                if prev_dividend > 0:
                    growth_rate = ((dividend - prev_dividend) / prev_dividend) * 100
                else:
                    growth_rate = 0
            else:
                growth_rate = 0
            
            # 利回り推定
            yield_estimate = ""
            if current_price and dividend > 0:
                yield_rate = (dividend / current_price) * 100
                yield_estimate = f"{yield_rate:.2f}"
            
            # テーブル挿入
            self.dividend_tree.insert("", "end", values=(
                year,
                f"¥{dividend:.1f}",
                f"{growth_rate:+.1f}" if growth_rate != 0 else "-",
                yield_estimate
            ))
    
    def _update_dividend_summary(self, dividend_history):
        """配当サマリーを更新"""
        if len(dividend_history) < 2:
            # データ不足
            self.dividend_summary_labels["avg_growth"].config(text="データ不足")
            self.dividend_summary_labels["trend_analysis"].config(text="要データ追加")
            self.dividend_summary_labels["investment_score"].config(text="評価不可")
            self.dividend_summary_labels["next_prediction"].config(text="予想不可")
            return
        
        # 成長率計算
        sorted_history = sorted(dividend_history, key=lambda x: x['year'])
        growth_rates = []
        
        for i in range(1, len(sorted_history)):
            prev_dividend = sorted_history[i-1]['dividend']
            current_dividend = sorted_history[i]['dividend']
            if prev_dividend > 0:
                growth_rate = ((current_dividend - prev_dividend) / prev_dividend) * 100
                growth_rates.append(growth_rate)
        
        # 平均成長率
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        self.dividend_summary_labels["avg_growth"].config(text=f"{avg_growth:+.2f}%/年")
        
        # トレンド分析
        positive_count = sum(1 for rate in growth_rates if rate > 0)
        positive_ratio = positive_count / len(growth_rates) if growth_rates else 0
        
        if positive_ratio >= 0.8:
            trend_text = "Excellent"
        elif positive_ratio >= 0.6:
            trend_text = "Stable"
        elif positive_ratio >= 0.4:
            trend_text = "Average"
        else:
            trend_text = "Caution"
        
        self.dividend_summary_labels["trend_analysis"].config(text=trend_text)
        
        # 投資評価
        if avg_growth > 5:
            score_text = "High Rating"
        elif avg_growth > 0:
            score_text = "Good"
        elif avg_growth > -5:
            score_text = "Average"
        else:
            score_text = "Poor"
        
        self.dividend_summary_labels["investment_score"].config(text=score_text)
        
        # 来年予想
        if growth_rates:
            latest_dividend = sorted_history[-1]['dividend']
            predicted_dividend = latest_dividend * (1 + avg_growth / 100)
            self.dividend_summary_labels["next_prediction"].config(text=f"¥{predicted_dividend:.1f}")
        else:
            self.dividend_summary_labels["next_prediction"].config(text="予想不可")
    
    def show_dividend_chart(self):
        """配当チャートを表示"""
        symbol = self.dividend_symbol_var.get().strip()
        if not symbol:
            messagebox.showwarning("警告", "銘柄コードを入力してください")
            return
        
        try:
            years = int(self.dividend_years_var.get())
            
            # データソース確認
            if not self.data_source:
                from dotenv import load_dotenv
                import os
                load_dotenv()
                
                jquants_email = os.getenv('JQUANTS_EMAIL')
                jquants_password = os.getenv('JQUANTS_PASSWORD')
                refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
                
                self.data_source = MultiDataSource(jquants_email, jquants_password, refresh_token)
            
            self.update_status(f"チャート作成中: {symbol}")
            
            # 配当履歴取得
            dividend_history = self.data_source.get_dividend_history(symbol, years)
            
            if not dividend_history:
                messagebox.showinfo("情報", f"銘柄 {symbol} の配当履歴が見つかりませんでした")
                return
            
            # 現在価格取得
            current_price = None
            stock_info = self.data_source.get_stock_info(symbol)
            if stock_info:
                current_price = stock_info.current_price
            
            # チャート作成
            chart_path = self.dividend_visualizer.create_dividend_chart(
                symbol, dividend_history, current_price)
            
            if chart_path:
                self.update_status(f"チャート作成完了: {chart_path}")
                
                # チャートファイルを開く
                try:
                    import subprocess
                    if platform.system() == "Windows":
                        os.startfile(chart_path)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", chart_path])
                    else:  # Linux/WSL
                        # WSL環境の場合はWindowsのエクスプローラーで開く
                        if 'microsoft' in platform.uname().release.lower():
                            # WSL環境
                            windows_path = chart_path.replace('/mnt/c', 'C:').replace('/', '\\')
                            subprocess.run(["cmd.exe", "/c", "start", windows_path], check=False)
                        else:
                            subprocess.run(["xdg-open", chart_path])
                except Exception as file_open_error:
                    # ファイルオープンに失敗した場合はパスだけ表示
                    print(f"ファイルオープンエラー: {file_open_error}")
                    
                messagebox.showinfo("完了", f"配当チャートを作成しました:\\n{chart_path}")
            else:
                messagebox.showerror("エラー", "チャート作成に失敗しました")
                
        except Exception as e:
            self.update_status("チャート作成エラー")
            messagebox.showerror("エラー", f"チャート作成中にエラーが発生しました: {e}")

    def load_wishlist_data(self):
        """データベースから欲しい銘柄データを読み込み"""
        try:
            wishlist_data = self.db.get_wishlist()
            
            # Treeviewをクリア
            for item in self.wishlist_tree.get_children():
                self.wishlist_tree.delete(item)
            
            # データを表示
            for item in wishlist_data:
                symbol = item['symbol']
                name = item['name']
                target_price = item.get('target_price')
                memo = item.get('memo', '')
                
                # 株価情報を取得（簡単な表示のため、現在価格のみ）
                try:
                    if not hasattr(self, 'data_source') or self.data_source is None:
                        from dotenv import load_dotenv
                        import os
                        load_dotenv()
                        
                        jquants_email = os.getenv('JQUANTS_EMAIL')
                        jquants_password = os.getenv('JQUANTS_PASSWORD')
                        refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
                        
                        self.data_source = MultiDataSource(jquants_email, jquants_password, refresh_token)
                    
                    stock_info = self.data_source.get_stock_info(symbol)
                    
                    if stock_info:
                        # 条件チェック
                        conditions_met, condition_details, sell_signal = self.check_strategy_conditions(symbol, stock_info)
                        indicator = self.get_condition_indicator(conditions_met, sell_signal)
                        
                        # 価格差計算
                        if target_price:
                            price_diff = stock_info.current_price - target_price
                            price_diff_str = f"¥{price_diff:+,.0f}"
                        else:
                            price_diff_str = "N/A"
                        
                        values = (
                            indicator,
                            symbol,
                            name,
                            f"¥{stock_info.current_price:,.0f}",
                            f"¥{target_price:.0f}" if target_price else "未設定",
                            price_diff_str,
                            f"{(stock_info.dividend_yield or 0):.1f}%",
                            f"{stock_info.pe_ratio:.1f}" if stock_info.pe_ratio else "N/A",
                            f"{stock_info.pb_ratio:.1f}" if stock_info.pb_ratio else "N/A",
                            memo,
                            item['created_at'][:10] if item.get('created_at') else ""
                        )
                        
                        self.wishlist_tree.insert("", tk.END, values=values)
                    else:
                        # 株価データ取得失敗時のデフォルト表示
                        values = (
                            "❓ 不明",
                            symbol,
                            name,
                            "取得失敗",
                            f"¥{target_price:.0f}" if target_price else "未設定",
                            "N/A",
                            "N/A",
                            "N/A",
                            "N/A",
                            memo,
                            item['created_at'][:10] if item.get('created_at') else ""
                        )
                        
                        self.wishlist_tree.insert("", tk.END, values=values)
                        
                except Exception as e:
                    print(f"欲しい銘柄データ読み込みエラー ({symbol}): {e}")
                    
        except Exception as e:
            print(f"欲しい銘柄データ読み込みエラー: {e}")

    def load_watchlist_data(self):
        """データベースから監視リストデータを読み込み"""
        try:
            watchlist_data = self.db.get_watchlist()
            
            # Treeviewをクリア
            for item in self.watchlist_tree.get_children():
                self.watchlist_tree.delete(item)
            
            # データを表示
            for item in watchlist_data:
                symbol = item['symbol']
                name = item['name']
                target_buy_price = item.get('target_buy_price')
                
                # 株価情報を取得
                try:
                    if not hasattr(self, 'data_source') or self.data_source is None:
                        from dotenv import load_dotenv
                        import os
                        load_dotenv()
                        
                        jquants_email = os.getenv('JQUANTS_EMAIL')
                        jquants_password = os.getenv('JQUANTS_PASSWORD')
                        refresh_token = os.getenv('JQUANTS_REFRESH_TOKEN')
                        
                        self.data_source = MultiDataSource(jquants_email, jquants_password, refresh_token)
                    
                    stock_info = self.data_source.get_stock_info(symbol)
                    
                    if stock_info:
                        # 条件チェック
                        conditions_met, condition_details, sell_signal = self.check_strategy_conditions(symbol, stock_info)
                        indicator = self.get_condition_indicator(conditions_met, sell_signal)
                        
                        # ステータス決定
                        if target_buy_price:
                            current = stock_info.current_price
                            if current <= target_buy_price:
                                status = "🎯 目標達成"
                            else:
                                diff_percent = ((target_buy_price - current) / current) * 100
                                status = f"📈 {diff_percent:+.1f}%"
                        else:
                            status = "📊 監視中"
                        
                        values = (
                            indicator,
                            symbol,
                            name,
                            f"¥{stock_info.current_price:,.0f}",
                            f"¥{target_buy_price:.0f}" if target_buy_price else "未設定",
                            f"{stock_info.change_percent:+.2f}%" if stock_info.change_percent else "N/A",
                            f"{(stock_info.dividend_yield or 0):.1f}%",
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
                    else:
                        # 株価データ取得失敗時のデフォルト表示
                        values = (
                            "❓ 不明",
                            symbol,
                            name,
                            "取得失敗",
                            f"¥{target_buy_price:.0f}" if target_buy_price else "未設定",
                            "N/A",
                            "N/A",
                            "N/A",
                            "N/A",
                            "📊 監視中"
                        )
                        
                        self.watchlist_tree.insert("", tk.END, values=values)
                        
                except Exception as e:
                    print(f"監視リストデータ読み込みエラー ({symbol}): {e}")
                    
        except Exception as e:
            print(f"監視リストデータ読み込みエラー: {e}")

    def export_data(self):
        """データエクスポート機能（プレースホルダー）"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo("データエクスポート", "データエクスポート機能は現在開発中です。")

    def show_settings(self):
        """設定画面表示（プレースホルダー）"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo("設定", "設定画面は現在開発中です。\n現在の設定は config/settings.json ファイルで変更できます。")

    def test_alert_system(self):
        """アラートシステムテスト"""
        try:
            self.alert_manager.test_notifications()
        except Exception as e:
            messagebox.showerror("エラー", f"アラートテストエラー: {e}")

    def show_notification_settings(self):
        """通知設定画面表示（プレースホルダー）"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo("通知設定", "通知設定画面は現在開発中です。\n現在の設定は .env ファイルで変更できます。")

    def show_strategy_settings(self):
        """戦略設定画面表示（プレースホルダー）"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo("戦略設定", "戦略設定画面は現在開発中です。\n現在の設定は config/strategies.json ファイルで変更できます。")

    def cleanup_database(self):
        """データベースクリーンアップ"""
        try:
            result = messagebox.askyesno("データベースクリーンアップ", 
                "データベースの最適化を実行しますか？\n（古いデータの削除や断片化の解消を行います）")
            if result:
                # データベースのVACUUMコマンドを実行
                import sqlite3
                with sqlite3.connect(self.db.db_path) as conn:
                    conn.execute("VACUUM")
                    conn.commit()
                messagebox.showinfo("完了", "データベースのクリーンアップが完了しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"データベースクリーンアップエラー: {e}")

    def clear_alert_history(self):
        """アラート履歴クリア"""
        try:
            result = messagebox.askyesno("アラート履歴クリア", 
                "すべてのアラート履歴を削除しますか？\n（この操作は取り消せません）")
            if result:
                success = self.db.clear_alerts()
                if success:
                    messagebox.showinfo("完了", "アラート履歴をクリアしました。")
                    self.refresh_ui()
                else:
                    messagebox.showerror("エラー", "アラート履歴のクリアに失敗しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"アラート履歴クリアエラー: {e}")

    def show_dividend_analysis(self):
        """配当分析画面表示"""
        try:
            holdings = self.db.get_all_holdings()
            if not holdings:
                messagebox.showinfo("配当分析", "保有銘柄がありません。\nまずCSVインポートで銘柄を追加してください。")
                return
            
            # 配当分析ウィンドウの表示
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("配当分析")
            analysis_window.geometry("600x400")
            
            label = tk.Label(analysis_window, 
                text="配当分析機能\n\n個別銘柄の配当分析は、\nポートフォリオタブで銘柄を右クリックして\n「配当履歴表示」を選択してください。",
                font=("Arial", 12), pady=20)
            label.pack()
            
        except Exception as e:
            messagebox.showerror("エラー", f"配当分析エラー: {e}")

    def show_user_guide(self):
        """使い方ガイド表示"""
        guide_text = """
🚀 日本株ウォッチドッグ - 使い方ガイド

📋 基本操作:
1. CSVインポート: SBI証券・楽天証券のCSVファイルをインポート
2. 株価更新: 「株価更新」ボタンで最新価格を取得
3. 監視設定: 監視タブで買い条件・売り条件を設定
4. 配当分析: 銘柄を右クリック → 配当履歴表示

🔧 設定ファイル:
- .env: API認証情報（J Quants, Gmail, Discord）
- config/settings.json: アプリケーション設定
- config/strategies.json: 投資戦略設定

📚 詳細ドキュメント:
README.md ファイルをご参照ください。
        """
        messagebox.showinfo("使い方ガイド", guide_text)

    def show_shortcuts(self):
        """ショートカットキー表示"""
        shortcuts_text = """
⌨️ ショートカットキー

📋 タブ切り替え:
Ctrl+1: ポートフォリオタブ
Ctrl+2: CSVインポートタブ
Ctrl+3: 監視タブ
Ctrl+4: 欲しい銘柄タブ

🔄 操作:
F5: 株価更新
Ctrl+S: データ保存
Ctrl+Q: アプリ終了

🖱️ マウス操作:
右クリック: コンテキストメニュー表示
ダブルクリック: 詳細表示（銘柄による）
        """
        messagebox.showinfo("ショートカットキー", shortcuts_text)

    def open_github(self):
        """GitHub リポジトリを開く"""
        import webbrowser
        try:
            webbrowser.open("https://github.com/inata169/miniTest01")
        except Exception as e:
            messagebox.showerror("エラー", f"ブラウザでGitHubを開けませんでした: {e}")

    def show_feedback(self):
        """フィードバック情報表示"""
        feedback_text = """
📧 フィードバック・お問い合わせ

🐛 バグ報告:
GitHub Issues をご利用ください
https://github.com/inata169/miniTest01/issues

💡 機能要求:
GitHub Discussions でご提案ください
https://github.com/inata169/miniTest01/discussions

📚 質問・サポート:
README.md の使い方ガイドを確認後、
GitHub Issues でお気軽にお尋ねください

🤝 貢献:
CONTRIBUTING.md をご参照ください

開発者: inata169
共同開発者: Claude Code
        """
        messagebox.showinfo("フィードバック", feedback_text)

    def _cleanup_context_menu(self):
        """コンテキストメニューをクリーンアップ"""
        if hasattr(self, '_context_menu') and self._context_menu:
            try:
                self._context_menu.unpost()
                self._context_menu.destroy()
            except:
                pass
            self._context_menu = None

    def _safe_menu_post(self, menu, x, y):
        """安全にメニューを表示（画面境界チェック付き）"""
        try:
            # 画面サイズを取得
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # メニューの概算サイズ
            menu_width = 250
            menu_height = 150
            
            # 画面境界をチェックして位置を調整
            if x + menu_width > screen_width:
                x = screen_width - menu_width - 10
            if y + menu_height > screen_height:
                y = screen_height - menu_height - 10
            
            # 最小位置制限
            x = max(10, x)
            y = max(10, y)
            
            # メニューを表示
            menu.post(x, y)
            menu.focus_set()
            
            # クリックでメニューを閉じるイベントをバインド
            def close_menu(event=None):
                self._cleanup_context_menu()
            
            self.root.bind('<Button-1>', close_menu, add='+')
            self.root.bind('<Escape>', close_menu, add='+')
            
        except Exception as e:
            print(f"メニュー表示エラー: {e}")
            self._cleanup_context_menu()

    def _on_global_click(self, event):
        """グローバルクリックイベント（コンテキストメニューのクリーンアップ用）"""
        # コンテキストメニューが表示されている場合のみクリーンアップ
        if hasattr(self, '_context_menu') and self._context_menu:
            # クリックされた位置がメニュー外の場合のみクリーンアップ
            try:
                # メニューのウィンドウが存在するかチェック
                menu_window = self._context_menu.winfo_toplevel()
                if menu_window and menu_window.winfo_exists():
                    # メニュー内のクリックかチェック
                    x, y = event.x_root, event.y_root
                    menu_x = menu_window.winfo_rootx()
                    menu_y = menu_window.winfo_rooty()
                    menu_w = menu_window.winfo_width()
                    menu_h = menu_window.winfo_height()
                    
                    # メニュー外のクリックの場合のみクリーンアップ
                    if not (menu_x <= x <= menu_x + menu_w and menu_y <= y <= menu_y + menu_h):
                        self._cleanup_context_menu()
                else:
                    self._cleanup_context_menu()
            except:
                # エラーが発生した場合は安全にクリーンアップ
                self._cleanup_context_menu()

    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()