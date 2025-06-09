#!/usr/bin/env python3
"""
フォント調査用スクリプト
"""
import tkinter as tk
from tkinter import font as tkFont

def check_available_fonts():
    """利用可能なフォントを調査"""
    root = tk.Tk()
    root.withdraw()  # ウィンドウを隠す
    
    # 利用可能なフォント一覧を取得
    available_fonts = sorted(tkFont.families())
    
    print("=== 利用可能なフォント一覧 ===")
    for i, font_name in enumerate(available_fonts, 1):
        print(f"{i:3d}: {font_name}")
    
    print(f"\n総数: {len(available_fonts)} フォント")
    
    # 日本語フォントの候補を検索
    japanese_candidates = [
        "Noto Sans CJK JP", "Noto Sans CJK", "Noto Sans", 
        "DejaVu Sans", "Liberation Sans", "Ubuntu", "Arial Unicode MS",
        "Yu Gothic", "Meiryo", "MS Gothic", "Hiragino Sans"
    ]
    
    print("\n=== 日本語フォント候補の確認 ===")
    found_fonts = []
    for candidate in japanese_candidates:
        if candidate in available_fonts:
            found_fonts.append(candidate)
            print(f"✓ {candidate}")
        else:
            print(f"✗ {candidate}")
    
    print(f"\n見つかった日本語フォント: {len(found_fonts)} 個")
    
    # デフォルトフォントの情報
    print("\n=== デフォルトフォント情報 ===")
    try:
        default_font = tkFont.nametofont("TkDefaultFont")
        print(f"フォント名: {default_font.actual('family')}")
        print(f"サイズ: {default_font.actual('size')}")
        print(f"太字: {default_font.actual('weight')}")
    except Exception as e:
        print(f"デフォルトフォント取得エラー: {e}")
    
    root.destroy()
    return found_fonts

def test_japanese_display():
    """日本語表示をテスト"""
    root = tk.Tk()
    root.title("日本語フォントテスト")
    root.geometry("600x400")
    
    test_text = "日本株ウォッチドッグ - ポートフォリオ管理"
    
    # 利用可能なフォントを取得
    available_fonts = tkFont.families()
    candidates = ["Noto Sans CJK JP", "DejaVu Sans", "Liberation Sans", "Ubuntu", "Arial"]
    
    row = 0
    for font_name in candidates:
        if font_name in available_fonts:
            try:
                font_obj = tkFont.Font(family=font_name, size=12)
                label = tk.Label(root, text=f"{font_name}: {test_text}", font=font_obj)
                label.pack(pady=5, anchor='w')
                print(f"表示テスト: {font_name}")
            except Exception as e:
                print(f"フォントエラー {font_name}: {e}")
    
    # デフォルトフォントでのテスト
    default_label = tk.Label(root, text=f"デフォルト: {test_text}")
    default_label.pack(pady=5, anchor='w')
    
    root.mainloop()

if __name__ == "__main__":
    print("フォント調査を開始します...")
    found_fonts = check_available_fonts()
    
    if found_fonts:
        print(f"\n推奨フォント: {found_fonts[0]}")
    else:
        print("\n警告: 日本語フォントが見つかりませんでした")
    
    print("\n日本語表示テストを開始しますか？ (y/N)")
    response = input().lower()
    if response == 'y':
        test_japanese_display()