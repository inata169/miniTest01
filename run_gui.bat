@echo off
echo 日本株ウォッチドッグを起動中...
cd /d "%~dp0"
python src/main.py --gui
pause