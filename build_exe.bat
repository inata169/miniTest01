@echo off
title 日本株ウォッチドッグ - EXE作成ツール
chcp 65001 > nul
echo ========================================
echo 日本株ウォッチドッグ EXE作成ツール
echo ========================================
echo.

echo 📋 作業ディレクトリ: %CD%
echo.

echo 🔍 Python環境をチェック中...
python --version
if errorlevel 1 (
    echo ❌ Pythonが見つかりません
    echo Python 3.8以上をインストールしてください
    pause
    exit /b 1
)
echo.

echo 📦 依存関係をインストール中...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依存関係のインストールに失敗しました
    pause
    exit /b 1
)
echo.

echo 🔨 EXEファイルを作成中...
python build_exe.py
if errorlevel 1 (
    echo ❌ EXE作成に失敗しました
    pause
    exit /b 1
)

echo.
echo 🎉 EXE作成完了!
echo 📁 配布ファイル: dist\フォルダ
echo 🎯 起動方法: dist\JapaneseStockWatchdog.exe
echo.

pause