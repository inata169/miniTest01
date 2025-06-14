@echo off
echo ================================
echo Matplotlib 緊急修復スクリプト
echo ================================

:: 仮想環境有効化
call venv_windows\Scripts\activate.bat

echo matplotlibをインストール中...
pip install matplotlib
if errorlevel 1 (
    echo 別の方法でmatplotlibをインストール中...
    pip install --upgrade matplotlib pillow
    if errorlevel 1 (
        echo プリビルドバイナリでmatplotlibをインストール中...
        pip install --only-binary=all matplotlib
    )
)

echo 依存関係も確認中...
pip install numpy pandas

echo 動作確認中...
python -c "import matplotlib; print('matplotlib: OK')"
python -c "import numpy; print('numpy: OK')"
python -c "import pandas; print('pandas: OK')"

echo.
echo アプリを起動してみてください:
echo python src/main.py --gui
echo.
pause