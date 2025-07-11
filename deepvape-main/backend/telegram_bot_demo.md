# Deepvape Telegram 管理機器人功能演示

## 🎯 機器人概述

Deepvape Telegram 管理機器人是一個強大的遠端管理工具，讓您可以通過 Telegram 聊天界面管理網站的產品價格、庫存和公告，無需登入後台網站。

## 📱 使用場景

### 場景1：緊急調價
**情況**：發現競爭對手降價，需要立即調整產品價格
**解決方案**：
1. 在 Telegram 中發送 `/products`
2. 點擊需要調價的產品
3. 點擊「💰 修改價格」
4. 輸入新價格，立即生效

### 場景2：批量促銷
**情況**：週末促銷活動，所有產品打8折
**解決方案**：
1. 發送 `/products`
2. 點擊「📊 批量調價」
3. 輸入 `-20`（降價20%）
4. 所有產品價格自動調整

### 場景3：庫存預警
**情況**：收到低庫存通知，需要緊急補貨
**解決方案**：
1. 發送 `/stats` 查看庫存狀況
2. 發送 `/products` 查看具體產品
3. 點擊「📦 批量補貨」自動補充低庫存產品

### 場景4：緊急公告
**情況**：系統維護，需要發布緊急公告
**解決方案**：
1. 發送 `/announcements`
2. 點擊「➕ 新增公告」
3. 輸入標題和內容
4. 公告立即在網站顯示

## 🔧 功能詳解

### 🔐 安全認證
```
用戶: /login
機器人: 請輸入您的用戶名：
用戶: admin
機器人: 請輸入密碼：
用戶: admin123
機器人: ✅ 登入成功！歡迎，admin！
```

### 📊 系統監控
```
用戶: /status
機器人: 
🟢 系統狀態：正常運行

📊 數據統計：
• 總產品數：9
• 啟用產品：9
• 總公告數：2
• 活躍公告：1

⏰ 檢查時間：2024-06-10 19:30:25
🌐 後台地址：http://192.168.2.16:5001
```

### 💰 產品管理
```
用戶: /products
機器人: 顯示產品列表，每個產品包含：
✅🟢 RELX 悅刻五代 - NT$1200 (25)
✅🔴 IQOS 3 DUO - NT$2800 (5)
...

點擊產品後顯示詳細操作：
📦 產品詳情
名稱：RELX 悅刻五代
價格：NT$ 1200
庫存：25 件
狀態：✅ 啟用

[💰 修改價格] [📦 修改庫存]
[❌ 停用] [🏷️ 修改標籤]
```

### 📢 公告管理
```
用戶: /announcements
機器人: 顯示公告列表：
✅🔴 系統維護通知...
❌🟡 新品上市公告...

點擊公告後顯示：
📢 公告詳情
標題：系統維護通知
內容：本網站將於今晚進行系統維護...
狀態：✅ 啟用
優先級：🔴 高

[📝 編輯內容] [🏷️ 編輯標題]
[❌ 停用] [🟡 中優先級]
[🗑️ 刪除公告]
```

## 🚀 快速開始

### 1. 創建機器人
1. 在 Telegram 搜尋 `@BotFather`
2. 發送 `/newbot`
3. 設定機器人名稱：`Deepvape 管理機器人`
4. 設定用戶名：`deepvape_admin_bot`
5. 獲取 Token

### 2. 配置環境
```bash
cd backend
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
pip3 install -r telegram_requirements.txt
```

### 3. 啟動機器人
```bash
python3 start_telegram_bot.py
```

### 4. 開始使用
1. 在 Telegram 搜尋您的機器人
2. 發送 `/start`
3. 發送 `/login` 並輸入後台帳號密碼
4. 開始管理！

## 💡 使用技巧

### 快速操作
- 使用 `/products` 快速查看所有產品狀態
- 使用 `/stats` 監控系統健康狀況
- 批量操作節省時間

### 安全建議
- 定期更改後台密碼
- 不要在公共群組中使用機器人
- 重要操作前先確認

### 效率提升
- 收藏常用命令
- 設定快捷回覆
- 使用批量功能處理多個項目

## 📈 進階功能

### 自動化腳本
可以結合其他工具創建自動化流程：
- 定時價格監控
- 庫存預警通知
- 銷售報告推送

### 多用戶管理
- 設定多個管理員帳號
- 不同權限級別
- 操作日誌記錄

### 數據分析
- 價格變動歷史
- 庫存變化趨勢
- 操作頻率統計

## 🔧 故障排除

### 常見問題
1. **機器人無回應**
   - 檢查網路連接
   - 確認 Token 正確
   - 重啟機器人服務

2. **登入失敗**
   - 確認使用後台帳號密碼
   - 檢查數據庫連接
   - 查看錯誤日誌

3. **操作失敗**
   - 確認後台服務運行
   - 檢查數據庫權限
   - 查看詳細錯誤信息

### 日誌分析
機器人會記錄所有操作：
- 用戶登入/登出
- 產品價格修改
- 庫存變更
- 公告管理

## 📞 支援聯繫

如需技術支援，請提供：
1. 錯誤截圖
2. 操作步驟
3. 系統環境
4. 錯誤日誌

---

**🎉 開始使用 Deepvape Telegram 管理機器人，讓管理變得更簡單！** 