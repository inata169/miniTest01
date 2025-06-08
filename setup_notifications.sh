#!/bin/bash

echo "通知設定セットアップ"
echo ""

echo "通知方法を選択してください:"
echo "1. デスクトップ通知のみ（パスワード不要）"
echo "2. Gmail + デスクトップ通知（アプリパスワード必要）"
echo ""

read -p "選択 (1 または 2): " CHOICE

if [ "$CHOICE" = "1" ]; then
    echo ""
    echo "デスクトップ通知のみを設定します..."
    cp config/settings_desktop_only.json config/settings.json
    echo "設定完了: デスクトップポップアップとコンソール表示のみ"
    echo "パスワード設定は不要です。"
    echo ""
elif [ "$CHOICE" = "2" ]; then
    echo ""
    echo "Gmail + デスクトップ通知を設定します..."
    echo ""
    echo "1. Gmailでアプリパスワードを作成してください:"
    echo "   - https://myaccount.google.com/apppasswords"
    echo "   - 2段階認証が有効である必要があります"
    echo ""
    
    read -p "Gmailアドレスを入力: " GMAIL_USER
    read -p "アプリパスワード(16文字)を入力: " GMAIL_PASS
    read -p "通知先メールアドレスを入力: " RECIPIENT
    
    export GMAIL_USERNAME="$GMAIL_USER"
    export GMAIL_APP_PASSWORD="$GMAIL_PASS"
    
    # bashrcに環境変数を追加
    echo "export GMAIL_USERNAME=\"$GMAIL_USER\"" >> ~/.bashrc
    echo "export GMAIL_APP_PASSWORD=\"$GMAIL_PASS\"" >> ~/.bashrc
    
    echo ""
    echo "設定ファイルを更新しています..."
    
    # JSONファイルの recipients を更新
    sed -i "s/\"your_email@example.com\"/\"$RECIPIENT\"/g" config/settings.json
    
    echo ""
    echo "環境変数とメール設定が完了しました。"
    echo "新しいターミナルを開くか、source ~/.bashrc を実行してください。"
    echo ""
else
    echo "無効な選択です。1 または 2 を入力してください。"
    exit 1
fi

echo ""
read -p "通知設定テストを実行しますか？ (y/n): " TEST_CHOICE

if [ "$TEST_CHOICE" = "y" ] || [ "$TEST_CHOICE" = "Y" ]; then
    echo ""
    echo "通知テストを実行中..."
    python src/alert_manager.py
fi

echo ""
echo "セットアップ完了！"