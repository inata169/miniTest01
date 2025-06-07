# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-07

### Added
- 初回リリース
- SBI証券・楽天証券のCSVインポート機能
- Yahoo Finance APIを使用した株価取得
- リアルタイム損益計算
- 投資戦略別アラート機能
- デスクトップ・メール・コンソール通知
- tkinter GUIインターフェース
- SQLiteデータベースによるポートフォリオ管理
- 複数口座（NISA、一般等）対応
- 日本株・米国株両対応
- 完全無料での利用

### Technical Details
- Python 3.8+ サポート
- Shift-JIS エンコーディング完全対応
- 自動CSVフォーマット判定
- 疑似シンボル処理
- エラーハンドリング強化
- 設定ファイルバリデーション
- ログ機能
- テストスイート

### Security
- ローカルデータ保存
- パスワード等の機密情報非保存
- Yahoo Finance API利用規約準拠

## [Unreleased]

### Planned Features
- チャート表示（ローソク足、移動平均線）
- 機械学習による株価予測
- LINE通知連携
- Web UIインターフェース
- バックテスト機能
- より高度なテクニカル分析
- ポートフォリオ最適化提案
- 税務計算支援