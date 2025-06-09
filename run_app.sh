#!/bin/bash
# アプリケーション実行用スクリプト

export PATH="$HOME/.local/bin:$PATH"
source .venv/bin/activate

echo "仮想環境を有効化しました"
echo "Python: $(python3 --version)"

# プログラム実行
python3 src/main.py --gui