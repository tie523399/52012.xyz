# Deepvape 更新通知發送指南

## 📋 概述

本指南說明如何使用 Telegram 機器人發送 Deepvape 網站更新通知。

## 🚀 快速開始

### 1. 環境設置

首先需要設置環境變數：

```bash
# 設置 Telegram Bot Token
export TELEGRAM_BOT_TOKEN='your_bot_token_here'

# 設置通知聊天室 ID
export NOTIFICATION_CHAT_ID='your_chat_id_here'
```

### 2. 安裝依賴

```bash
cd backend
pip install python-telegram-bot
```

### 3. 發送通知

```bash
# 發送完整更新通知（包含價格表）
python send_update_notification.py
```

## 🤖 獲取 Bot Token

1. 在 Telegram 中搜尋 `@BotFather`
2. 發送 `/newbot` 創建新機器人
3. 按照指示設定機器人名稱和用戶名
4. 獲取 Bot Token

## 🆔 獲取聊天室 ID

### 方法一：私人聊天
1. 與機器人開始對話
2. 發送任意訊息
3. 訪問：`https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. 在回應中找到 `chat.id`

### 方法二：群組聊天
1. 將機器人加入群組
2. 在群組中發送訊息
3. 使用相同方法獲取群組 ID（通常是負數）

## 📤 通知內容

### 更新通知包含：
- 🎨 用戶體驗優化
- 📋 服務頁面完善
- 💬 客服系統升級
- 💰 價格系統統一

### 價格表通知包含：
- 🖥️ 主機系列價格
- 💨 煙彈系列價格
- 🔥 拋棄式系列價格
- 🚚 運費資訊
- ⚠️ 注意事項

## 🛠️ 自定義通知

可以修改 `send_update_notification.py` 中的文案：

```python
# 修改更新通知內容
notification_text = """
🚀 **您的自定義通知標題**

📅 **更新時間：** {update_time}

✨ **您的更新內容：**
• 項目一
• 項目二
...
"""
```

## 🔧 故障排除

### 常見錯誤：

1. **Token 錯誤**
   ```
   ❌ 發送通知失敗：Unauthorized
   ```
   - 檢查 `TELEGRAM_BOT_TOKEN` 是否正確

2. **聊天室 ID 錯誤**
   ```
   ❌ 發送通知失敗：Chat not found
   ```
   - 檢查 `NOTIFICATION_CHAT_ID` 是否正確
   - 確認機器人已加入目標聊天室

3. **權限問題**
   ```
   ❌ 發送通知失敗：Forbidden
   ```
   - 確認機器人有發送訊息的權限
   - 在群組中確認機器人是管理員（如需要）

## 📝 使用範例

```bash
# 設置環境變數
export TELEGRAM_BOT_TOKEN='1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
export NOTIFICATION_CHAT_ID='-1001234567890'

# 發送通知
cd /Users/yifubai/Downloads/DeepVape/backend
python send_update_notification.py
```

## 🎯 最佳實踐

1. **定期測試**：定期測試機器人功能確保正常運作
2. **備份 Token**：安全保存 Bot Token
3. **監控發送**：檢查發送日誌確認通知成功
4. **內容審核**：發送前檢查通知內容的準確性

## 📞 支援

如有問題請聯繫系統管理員或查看：
- Telegram Bot API 文檔
- python-telegram-bot 文檔 