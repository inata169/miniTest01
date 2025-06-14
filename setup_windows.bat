@echo off
echo ================================
echo Japanese Stock Watchdog Setup
echo ================================

:: Check if virtual environment exists
if not exist "venv_windows" (
    echo Creating virtual environment...
    python -m venv venv_windows
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv_windows\Scripts\activate.bat

:: Upgrade pip and install basic tools
echo Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel

:: Install packages individually to avoid dependency conflicts
echo Installing core packages...
pip install --no-deps chardet
pip install --no-deps python-dotenv
pip install --no-deps requests
pip install --no-deps openpyxl
pip install --no-deps email-validator

:: Install packages with precompiled binaries (retry with fallbacks)
echo Installing scientific packages...
pip install --only-binary=all numpy==1.24.3 matplotlib==3.7.2 pandas==2.0.3
if errorlevel 1 (
    echo Trying alternative versions...
    pip install --only-binary=all numpy matplotlib pandas
    if errorlevel 1 (
        echo Installing without version constraints...
        pip install numpy matplotlib pandas
    )
)

:: Install remaining packages
echo Installing remaining packages...
pip install yfinance beautifulsoup4 lxml html5lib

:: Try to install J Quants API client (optional)
echo Installing J Quants API client...
pip install jquants-api-client --no-deps
if errorlevel 1 echo J Quants API client installation failed, continuing...

:: Verify critical packages
echo Verifying installations...
python -c "import matplotlib; print('matplotlib: OK')"
if errorlevel 1 (
    echo matplotlib installation failed, trying alternative method...
    pip install --upgrade matplotlib pillow
)
python -c "import numpy; print('numpy: OK')"
if errorlevel 1 echo WARNING: numpy not properly installed
python -c "import pandas; print('pandas: OK')"
if errorlevel 1 echo WARNING: pandas not properly installed

:: Create directories
echo Creating required directories...
if not exist "data\csv_imports" mkdir data\csv_imports
if not exist "data\backups" mkdir data\backups
if not exist "logs" mkdir logs
if not exist "charts" mkdir charts

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env configuration file...
    copy .env.example .env 2>nul || (
        echo # Environment Variables > .env
        echo JQUANTS_EMAIL= >> .env
        echo JQUANTS_REFRESH_TOKEN= >> .env
        echo DISCORD_WEBHOOK_URL= >> .env
        echo EMAIL_FROM= >> .env
        echo EMAIL_PASSWORD= >> .env
        echo EMAIL_TO= >> .env
    )
)

echo.
echo ================================
echo Setup completed successfully!
echo ================================
echo.
echo To run the application:
echo 1. Double-click run_app.bat
echo 2. Or run: python src/main.py --gui
echo.
pause