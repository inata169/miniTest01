#!/bin/bash

# Ubuntu/Linux向け日本株ウォッチドッグ自動セットアップスクリプト
# 使用方法: chmod +x setup_ubuntu.sh && ./setup_ubuntu.sh

echo "=== 日本株ウォッチドッグ Ubuntu版 自動セットアップ ==="
echo ""

# 基本的なシステム情報表示
echo "OS情報:"
cat /etc/os-release | grep PRETTY_NAME
echo "Python バージョン:"
python3 --version
echo ""

# 1. システムパッケージの更新とインストール
echo "1. システムパッケージを更新しています..."
sudo apt update

echo "2. 必要なシステムパッケージをインストールしています..."
sudo apt install -y python3-pip python3-venv python3-dev python3-tk curl git
sudo apt install -y fonts-noto-cjk fonts-noto-cjk-extra  # 日本語フォント

# 2. uv（高速Pythonパッケージマネージャ）のインストール
echo "3. uv（高速パッケージマネージャ）をインストールしています..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# 3. 仮想環境の作成
echo "4. Python仮想環境を作成しています..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# 4. 仮想環境の有効化
echo "5. 仮想環境を有効化しています..."
source .venv/bin/activate

# 5. 依存関係のインストール
echo "6. Python依存関係をインストールしています..."
if command -v uv &> /dev/null; then
    echo "   uv使用（高速）:"
    uv pip install -r requirements.txt
    uv pip install jquants-api-client python-dotenv matplotlib
else
    echo "   pip使用（標準）:"
    pip3 install --timeout 300 -r requirements.txt
    pip3 install jquants-api-client python-dotenv matplotlib
fi

# 6. 設定ファイルの準備
echo "7. 設定ファイルを準備しています..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   .env.example から .env を作成しました"
        echo "   ※後で .env ファイルを編集してAPI設定を行ってください"
    else
        echo "   警告: .env.example が見つかりません"
    fi
fi

# 7. 実行権限の付与
echo "8. スクリプト実行権限を設定しています..."
chmod +x run_app.sh
chmod +x activate_env.sh
chmod +x setup_notifications.sh

# 8. ディレクトリの作成
echo "9. 必要なディレクトリを作成しています..."
mkdir -p data/csv_imports
mkdir -p data/backups
mkdir -p logs
mkdir -p charts

# 9. GUI動作確認
echo "10. GUI動作環境を確認しています..."
if [ -n "$DISPLAY" ]; then
    echo "   ✅ DISPLAY環境変数が設定されています: $DISPLAY"
elif [ -n "$WAYLAND_DISPLAY" ]; then
    echo "   ✅ Wayland環境が検出されました: $WAYLAND_DISPLAY"
else
    echo "   ⚠️  GUI環境が検出されませんでした"
    echo "   WSLの場合は以下を実行してください："
    echo "   export DISPLAY=:0"
    echo "   またはX11サーバー（VcXsrv等）をインストールしてください"
fi

# 10. テスト実行
echo ""
echo "=== セットアップ完了 ==="
echo ""
echo "✅ Ubuntu版 日本株ウォッチドッグのセットアップが完了しました！"
echo ""
echo "📋 次の手順："
echo "1. API設定: nano .env  （J Quants API、Gmail、Discord等）"
echo "2. アプリ起動: ./run_app.sh"
echo "3. 設定完了後、デスクトップにショートカット作成も可能です"
echo ""
echo "🔧 便利コマンド："
echo "   ./activate_env.sh     # 仮想環境を有効化"
echo "   ./run_app.sh          # アプリケーション起動"
echo "   ./setup_notifications.sh  # 通知設定ヘルパー"
echo ""
echo "📚 詳細は README.md をご覧ください"
echo ""

# 11. 動作テスト（オプション）
read -p "動作テストを実行しますか？ (y/N): " test_run
if [[ $test_run =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧪 動作テストを実行しています..."
    python3 src/version.py
    echo ""
    echo "✅ テスト完了。問題なければ ./run_app.sh でアプリを起動してください"
fi

echo ""
echo "🎉 セットアップスクリプトが正常に完了しました！"