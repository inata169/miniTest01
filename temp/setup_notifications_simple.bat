@echo off
echo Notification Setup
echo.

echo Choose notification method:
echo 1. Desktop notifications only (no password required)
echo 2. Gmail + Desktop notifications (app password required)
echo.

set /p CHOICE="Select (1 or 2): "

if "%CHOICE%"=="1" (
    echo.
    echo Setting up desktop notifications only...
    if exist config\settings_desktop_only.json (
        copy config\settings_desktop_only.json config\settings.json >nul 2>&1
        echo Setup complete: Desktop popup and console display only
        echo No password setup required.
    ) else (
        echo Error: config\settings_desktop_only.json not found
    )
    echo.
    goto test
)

if "%CHOICE%"=="2" (
    echo.
    echo Setting up Gmail + Desktop notifications...
    echo.
    echo 1. Create Gmail app password at:
    echo    https://myaccount.google.com/apppasswords
    echo    (2-factor authentication must be enabled)
    echo.
    
    set /p GMAIL_USER="Enter Gmail address: "
    set /p GMAIL_PASS="Enter app password (16 chars): "
    set /p RECIPIENT="Enter notification email: "
    
    echo.
    echo Setting environment variables...
    setx GMAIL_USERNAME "%GMAIL_USER%" >nul 2>&1
    setx GMAIL_APP_PASSWORD "%GMAIL_PASS%" >nul 2>&1
    
    echo Updating config file...
    python -c "import json; import sys; f=open('config/settings.json','r',encoding='utf-8'); data=json.load(f); f.close(); data['notifications']['email']['enabled']=True; data['notifications']['email']['recipients']=['%RECIPIENT%']; f=open('config/settings.json','w',encoding='utf-8'); json.dump(data,f,indent=2,ensure_ascii=False); f.close(); print('Config file updated')" 2>nul
    
    if errorlevel 1 (
        echo Error: Failed to update config file
        echo Make sure Python is installed and accessible
        pause
        exit /b 1
    )
    
    echo.
    echo Environment variables and email setup completed.
    echo Please restart PC or open a new command prompt.
    echo.
    goto test
)

echo Invalid selection. Please enter 1 or 2.
pause
exit /b 1

:test
echo.
set /p TEST_CHOICE="Run notification test? (y/n): "

if /i "%TEST_CHOICE%"=="y" (
    echo.
    echo Running notification test...
    python src\alert_manager.py
    if errorlevel 1 (
        echo Test failed. Check Python and tkinter installation.
    )
)

echo.
echo Setup completed!
pause