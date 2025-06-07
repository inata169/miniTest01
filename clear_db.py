#!/usr/bin/env python3
"""
個人データクリアスクリプト
日本株ウォッチドッグの個人データを安全に削除します
"""

import os
import argparse
import shutil
from datetime import datetime
import glob


class DataCleaner:
    """個人データクリア用クラス"""
    
    def __init__(self):
        self.db_path = "data/portfolio.db"
        self.backup_dir = "data/backups"
        self.csv_dir = "data/csv_imports"
        self.logs_dir = "logs"
    
    def backup_before_clear(self):
        """削除前にバックアップを作成"""
        if not os.path.exists(self.db_path):
            return False
        
        # バックアップディレクトリ作成
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # タイムスタンプ付きバックアップファイル名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"portfolio_backup_{timestamp}.db")
        
        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"📁 バックアップ作成: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ バックアップ作成エラー: {e}")
            return False
    
    def clear_database(self, backup=True):
        """データベースをクリア"""
        if os.path.exists(self.db_path):
            if backup:
                print("🔄 データベースをバックアップ中...")
                self.backup_before_clear()
            
            os.remove(self.db_path)
            print(f"🗑️  データベース削除: {self.db_path}")
            return True
        else:
            print(f"ℹ️  データベースファイルは存在しません: {self.db_path}")
            return False
    
    def clear_csv_files(self):
        """インポート済みCSVファイルをクリア"""
        if not os.path.exists(self.csv_dir):
            print(f"ℹ️  CSVディレクトリは存在しません: {self.csv_dir}")
            return 0
        
        csv_files = glob.glob(os.path.join(self.csv_dir, "*.csv"))
        
        if not csv_files:
            print("ℹ️  削除するCSVファイルはありません")
            return 0
        
        print(f"📄 {len(csv_files)} 個のCSVファイルを削除中...")
        for csv_file in csv_files:
            try:
                os.remove(csv_file)
                print(f"   - {os.path.basename(csv_file)}")
            except Exception as e:
                print(f"❌ CSVファイル削除エラー ({csv_file}): {e}")
        
        return len(csv_files)
    
    def clear_logs(self):
        """ログファイルをクリア"""
        if not os.path.exists(self.logs_dir):
            print(f"ℹ️  ログディレクトリは存在しません: {self.logs_dir}")
            return 0
        
        log_files = glob.glob(os.path.join(self.logs_dir, "*.log*"))
        
        if not log_files:
            print("ℹ️  削除するログファイルはありません")
            return 0
        
        print(f"📝 {len(log_files)} 個のログファイルを削除中...")
        for log_file in log_files:
            try:
                os.remove(log_file)
                print(f"   - {os.path.basename(log_file)}")
            except Exception as e:
                print(f"❌ ログファイル削除エラー ({log_file}): {e}")
        
        return len(log_files)
    
    def clear_all(self, backup=True):
        """全ての個人データをクリア"""
        print("🧹 個人データの完全クリアを開始...")
        print("=" * 50)
        
        # データベースクリア
        db_cleared = self.clear_database(backup)
        
        # CSVファイルクリア
        csv_count = self.clear_csv_files()
        
        # ログクリア
        log_count = self.clear_logs()
        
        print("=" * 50)
        print("✅ クリア完了")
        print(f"   - データベース: {'削除済み' if db_cleared else '元々存在せず'}")
        print(f"   - CSVファイル: {csv_count} 個削除")
        print(f"   - ログファイル: {log_count} 個削除")
        
        if backup and db_cleared:
            print(f"   - バックアップ: {self.backup_dir} に保存済み")
        
        print("\n次回起動時に新しいデータベースが作成されます")
    
    def list_data_files(self):
        """現在のデータファイル一覧を表示"""
        print("📊 現在のデータファイル:")
        print("=" * 30)
        
        # データベース
        if os.path.exists(self.db_path):
            size = os.path.getsize(self.db_path)
            print(f"🗄️  データベース: {self.db_path} ({size:,} bytes)")
        else:
            print("🗄️  データベース: なし")
        
        # CSVファイル
        csv_files = glob.glob(os.path.join(self.csv_dir, "*.csv")) if os.path.exists(self.csv_dir) else []
        print(f"📄 CSVファイル: {len(csv_files)} 個")
        for csv_file in csv_files:
            size = os.path.getsize(csv_file)
            print(f"   - {os.path.basename(csv_file)} ({size:,} bytes)")
        
        # ログファイル
        log_files = glob.glob(os.path.join(self.logs_dir, "*.log*")) if os.path.exists(self.logs_dir) else []
        print(f"📝 ログファイル: {len(log_files)} 個")
        for log_file in log_files:
            size = os.path.getsize(log_file)
            print(f"   - {os.path.basename(log_file)} ({size:,} bytes)")
        
        # バックアップファイル
        backup_files = glob.glob(os.path.join(self.backup_dir, "*.db")) if os.path.exists(self.backup_dir) else []
        print(f"💾 バックアップ: {len(backup_files)} 個")
        for backup_file in backup_files:
            size = os.path.getsize(backup_file)
            print(f"   - {os.path.basename(backup_file)} ({size:,} bytes)")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="日本株ウォッチドッグの個人データをクリア",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python clear_db.py                    # データベースのみクリア（バックアップ付き）
  python clear_db.py --all              # 全データクリア（バックアップ付き）
  python clear_db.py --all --no-backup  # 全データクリア（バックアップなし）
  python clear_db.py --csv              # CSVファイルのみクリア
  python clear_db.py --logs             # ログファイルのみクリア
  python clear_db.py --list             # データファイル一覧表示
        """
    )
    
    parser.add_argument('--all', action='store_true', 
                       help='全ての個人データをクリア（データベース、CSV、ログ）')
    parser.add_argument('--csv', action='store_true',
                       help='CSVファイルのみクリア')
    parser.add_argument('--logs', action='store_true',
                       help='ログファイルのみクリア')
    parser.add_argument('--no-backup', action='store_true',
                       help='バックアップを作成しない')
    parser.add_argument('--list', action='store_true',
                       help='現在のデータファイル一覧を表示')
    
    args = parser.parse_args()
    
    cleaner = DataCleaner()
    
    # データファイル一覧表示
    if args.list:
        cleaner.list_data_files()
        return
    
    # 確認プロンプト
    if not args.list:
        print("⚠️  この操作により個人データが削除されます")
        if not args.no_backup:
            print("💾 データベースのバックアップを作成します")
        
        response = input("続行しますか？ (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ 操作をキャンセルしました")
            return
    
    backup = not args.no_backup
    
    # 個別オプション処理
    if args.csv:
        cleaner.clear_csv_files()
    elif args.logs:
        cleaner.clear_logs()
    elif args.all:
        cleaner.clear_all(backup)
    else:
        # デフォルト: データベースのみクリア
        cleaner.clear_database(backup)
        print("次回起動時に新しいデータベースが作成されます")


if __name__ == "__main__":
    main()