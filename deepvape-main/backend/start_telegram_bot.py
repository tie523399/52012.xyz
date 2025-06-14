#!/usr/bin/env python3
"""
Deepvape Telegram 機器人啟動腳本
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def main():
    """主函數"""
    print("🤖 Deepvape Telegram 管理機器人")
    print("=" * 50)
    
    # 檢查Token
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token or token == 'YOUR_BOT_TOKEN_HERE':
        print("❌ 未設定 TELEGRAM_BOT_TOKEN 環境變數")
        print("\n📋 設定步驟：")
        print("1. 在 Telegram 中搜尋 @BotFather")
        print("2. 發送 /newbot 創建新機器人")
        print("3. 按照指示設定機器人名稱和用戶名")
        print("4. 獲取 Token")
        print("5. 創建 .env 文件並添加：")
        print("   TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("\n💡 或者直接設定環境變數：")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    print(f"✅ Token 已設定: {token[:10]}...")
    
    # 檢查依賴
    try:
        import telegram
        from telegram.ext import Application
        print("✅ python-telegram-bot 已安裝")
    except ImportError:
        print("❌ 缺少依賴包")
        print("請執行：pip install -r telegram_requirements.txt")
        return
    
    # 檢查後台服務
    try:
        from app import app, db, Product, Announcement, Admin
        print("✅ 後台服務模組已載入")
    except ImportError as e:
        print(f"❌ 無法載入後台服務：{e}")
        print("請確保後台服務正常運行")
        return
    
    # 啟動機器人
    try:
        from telegram_admin_bot import AdminBot
        print("🚀 正在啟動機器人...")
        
        bot = AdminBot()
        print("✅ 機器人已啟動，等待命令...")
        print("\n📱 使用方式：")
        print("1. 在 Telegram 中搜尋您的機器人")
        print("2. 發送 /start 開始使用")
        print("3. 使用 /login 登入管理帳號")
        print("4. 使用 /help 查看所有命令")
        print("\n⚠️  按 Ctrl+C 停止機器人")
        print("=" * 50)
        
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 機器人已停止")
    except Exception as e:
        print(f"❌ 機器人啟動失敗：{e}")

if __name__ == '__main__':
    main() 