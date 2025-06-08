@echo off
chcp 65001 >nul
echo Gmail通知設定スクリプト
echo.

echo 1. Gmailでアプリパスワードを作成してください:
echo    - https://myaccount.google.com/apppasswords
echo    - 2段階認証が有効である必要があります
echo.

echo 2. 環境変数を設定します...
echo.

set /p GMAIL_USER="Gmailアドレスを入力: "
set /p GMAIL_PASS="アプリパスワード(16文字)を入力: "

setx GMAIL_USERNAME "%GMAIL_USER%"
setx GMAIL_APP_PASSWORD "%GMAIL_PASS%"

echo.
echo 環境変数が設定されました。
echo PCを再起動するか、新しいコマンドプロンプトを開いてください。
echo.

pause