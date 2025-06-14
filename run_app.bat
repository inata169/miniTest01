@echo off
echo ================================
echo Japanese Stock Watchdog
echo ================================

:: Check if virtual environment exists
if not exist "venv_windows" (
    echo Virtual environment not found!
    echo Please run setup_windows.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv_windows\Scripts\activate.bat

:: Set SSL environment variables for Windows
set CURL_CA_BUNDLE=
set SSL_CERT_FILE=

:: Check if main.py exists
if not exist "src\main.py" (
    echo ERROR: src\main.py not found!
    echo Make sure you're running this from the project root directory.
    pause
    exit /b 1
)

:: Run the application
echo Starting Japanese Stock Watchdog...
python src\main.py --gui

:: Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    echo Check the error message above.
    pause
)