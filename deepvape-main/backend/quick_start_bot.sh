#!/bin/bash

echo "🤖 Deepvape Telegram 機器人快速啟動"
echo "=================================="

# 檢查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝"
    exit 1
fi

echo "✅ Python3 已安裝: $(python3 --version)"

# 檢查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安裝"
    exit 1
fi

echo "✅ pip3 已安裝"

# 安裝依賴
echo "📦 安裝依賴包..."
pip3 install -r telegram_requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 依賴安裝失敗"
    exit 1
fi

echo "✅ 依賴安裝完成"

# 檢查Token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠️  未設定 TELEGRAM_BOT_TOKEN 環境變數"
    echo ""
    echo "請按照以下步驟設定："
    echo "1. 在 Telegram 中搜尋 @BotFather"
    echo "2. 發送 /newbot 創建機器人"
    echo "3. 獲取 Token 後執行："
    echo "   export TELEGRAM_BOT_TOKEN='your_token_here'"
    echo "4. 重新執行此腳本"
    exit 1
fi

echo "✅ Token 已設定"

# 測試機器人
echo "🔍 測試機器人配置..."
python3 test_telegram_bot.py

if [ $? -ne 0 ]; then
    echo "❌ 機器人測試失敗"
    exit 1
fi

echo "✅ 機器人測試通過"

# 啟動機器人
echo "🚀 啟動機器人..."
python3 start_telegram_bot.py 