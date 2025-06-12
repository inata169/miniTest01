@echo off
chcp 65001 >nul
echo 通知設定セットアップ
echo.

echo 通知方法を選択してください:
echo 1. デスクトップ通知のみ（パスワード不要）
echo 2. Gmail + デスクトップ通知（アプリパスワード必要）
echo.

set /p CHOICE="選択 (1 または 2): "

if "%CHOICE%"=="1" (
    echo.
    echo デスクトップ通知のみを設定します...
    if exist config\settings_desktop_only.json (
        copy config\settings_desktop_only.json config\settings.json >nul
        echo 設定完了: デスクトップポップアップとコンソール表示のみ
        echo パスワード設定は不要です。
    ) else (
        echo エラー: config\settings_desktop_only.json が見つかりません
    )
    echo.
) else if "%CHOICE%"=="2" (
    echo.
    echo Gmail + デスクトップ通知を設定します...
    echo.
    echo 1. Gmailでアプリパスワードを作成してください:
    echo    - https://myaccount.google.com/apppasswords
    echo    - 2段階認証が有効である必要があります
    echo.
    
    set /p GMAIL_USER="Gmailアドレスを入力: "
    set /p GMAIL_PASS="アプリパスワード(16文字)を入力: "
    set /p RECIPIENT="通知先メールアドレスを入力: "
    
    echo.
    echo 環境変数を設定中...
    setx GMAIL_USERNAME "%GMAIL_USER%" >nul
    setx GMAIL_APP_PASSWORD "%GMAIL_PASS%" >nul
    
    echo 設定ファイルを更新中...
    python -c "import json; f=open('config/settings.json','r',encoding='utf-8'); data=json.load(f); f.close(); data['notifications']['email']['enabled']=True; data['notifications']['email']['recipients']=['%RECIPIENT%']; f=open('config/settings.json','w',encoding='utf-8'); json.dump(data,f,indent=2,ensure_ascii=False); f.close(); print('設定ファイル更新完了')"
    
    echo.
    echo 環境変数とメール設定が完了しました。
    echo PCを再起動するか、新しいコマンドプロンプトを開いてください。
    echo.
) else (
    echo 無効な選択です。1 または 2 を入力してください。
    pause
    exit /b 1
)

echo.
set /p TEST_CHOICE="通知設定テストを実行しますか？ (y/n): "

if /i "%TEST_CHOICE%"=="y" (
    echo.
    echo 通知テストを実行中...
    python src\alert_manager.py
    if errorlevel 1 (
        echo テスト実行でエラーが発生しました。
        echo Pythonとtkinterがインストールされているか確認してください。
    )
)

echo.
echo セットアップ完了！
pause