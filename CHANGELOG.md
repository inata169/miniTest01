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

## [1.3.0] - 2025-12-13

### 🔄 Data Source Revolution
- **J Quants API統合**: Yahoo Finance制限問題を完全解決
- **マルチデータソース**: J Quants → Yahoo Finance 自動フォールバック
- **レート制限回避**: 429 Too Many Requests エラーの完全排除
- **日本株特化**: 東証データ直接提供で高品質データ取得

### 🔐 Security Enhancement  
- **.env対応**: 業界標準セキュリティベストプラクティス採用
- **環境変数管理**: 全認証情報を.envファイルで一元管理
- **Git除外**: .envファイル自動除外でセキュリティ強化
- **後方互換性**: 既存JSON設定ファイルも継続利用可能

### 🛠️ Technical Implementation
- **MultiDataSource**: 堅牢なフォールバック機能実装
- **python-dotenv**: 環境変数自動読み込み機能
- **型注釈強化**: types-python-dateutil, types-requests追加
- **詳細ガイド**: .env.example完全設定テンプレート

### Added
- J Quants API client (jquants-api-client>=1.8.0)
- Environment variable support (python-dotenv>=1.1.0) 
- Multi-source data architecture
- Comprehensive security documentation
- Enhanced error handling and logging

### Changed
- Primary data source: J Quants API (Yahoo Finance as fallback)
- Configuration loading: .env → JSON files priority
- Documentation: Updated for v1.3.0 features
- Dependencies: Added new required packages

### Fixed
- Yahoo Finance rate limiting issues (completely resolved)
- API 429 error handling
- Security vulnerabilities in credential storage

## [1.2.1] - 2025-12-01

### 🎯 UI Enhancement & Bug Fixes
- **価格更新エラー修正**: "'int' object has no attribute 'startswith'" 解決
- **欲しい銘柄タブ**: 将来購入予定銘柄の体系的管理
- **条件マッチング視覚化**: 🔥買い頃！⚡検討中👀監視中😴様子見表示
- **売りシグナル**: 💰売り頃！⚠️損切り条件の視覚化

### Added
- 希望購入価格設定機能
- 投資条件充足度リアルタイム表示
- 投資メモ機能
- ワンクリック監視リスト移動

### Fixed
- 整数型銘柄コード処理エラー
- 堅牢な型変換実装
- f-string処理改善

## [1.1.0] - 2025-06-01

### Alert System
- **アラートテスト機能**: 通知システム動作確認
- **アラート履歴**: 過去アラートの色分け表示
- **デスクトップ通知改善**: emoji付きアイコン表示

### Table Enhancement
- **カラムソート**: 全カラムのクリックソート対応
- **ソート指標**: 矢印による方向表示
- **数値ソート**: 通貨・パーセント値の適切処理

### UI Improvement
- **日本語フォント自動検出**: OS最適フォント選択
- **色分けアラート**: アラート種別の視覚的区別
- **ステータスメッセージ改善**: ユーザーフィードバック向上

### Added
- Discord通知 (LINE Notify終了対応)
- uvパッケージ管理サポート
- 簡単起動スクリプト (./run_app.sh)

## [Unreleased]

### Planned Features
- チャート表示（ローソク足、移動平均線）
- 機械学習による株価予測
- Web UIインターフェース
- バックテスト機能
- より高度なテクニカル分析
- ポートフォリオ最適化提案
- 税務計算支援