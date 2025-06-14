@echo off
echo ================================
echo Minimal Installation for Windows
echo ================================

:: Activate virtual environment
call venv_windows\Scripts\activate.bat

:: Install only essential packages without dependencies
echo Installing minimal packages...
pip install --no-deps chardet
pip install --no-deps python-dotenv
pip install --no-deps requests
pip install --no-deps beautifulsoup4
pip install --no-deps lxml

:: Try to run without J Quants API (Yahoo Finance only)
echo.
echo Attempting to start application with minimal setup...
set CURL_CA_BUNDLE=
set SSL_CERT_FILE=
python src\main.py --gui

pause