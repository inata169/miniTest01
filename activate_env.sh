#!/bin/bash
# 仮想環境アクティベーション用スクリプト

export PATH="$HOME/.local/bin:$PATH"
source .venv/bin/activate

# PythonコマンドをpythonとしてaliasEを設定（仮想環境内でのみ）
alias python=python3

echo "仮想環境がアクティベートされました"
echo "Python: $(python3 --version)"
echo "パッケージ確認: pip list でパッケージ一覧を表示できます"
echo "実行例: python3 src/main.py --gui"