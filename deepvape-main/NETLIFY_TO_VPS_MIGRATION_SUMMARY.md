# Netlify 到 Vultr VPS 遷移總結

## 完成的工作

### 1. ✅ 建立完整的後端伺服器 (`server.js`)
- **Express 伺服器**：處理所有 API 請求
- **API 路由器**：組織化的 API 端點管理
- **靜態檔案服務**：開發環境支援
- **錯誤處理**：完整的錯誤處理中間件
- **安全標頭**：生產環境安全性設定

### 2. ✅ 實作所有 API 端點
- **`/api/health`** - 健康檢查
- **`/api/prices`** - 價格資料 API
- **`/api/announcements`** - 公告資料 API  
- **`/api/send-telegram`** - Telegram 通知 API
- **`/api/711-callback`** - 7-11 門市回調處理

### 3. ✅ 資料管理
- **`data/prices.json`** - 產品價格資料
- **`data/announcements.json`** - 網站公告資料
- 伺服器啟動時自動載入資料檔案

### 4. ✅ 前端配置更新 (`js/config.js`)
- **API 基礎 URL**：自動偵測開發/生產環境
- **統一的 API 方法**：`window.API` 物件
- **請求輔助函數**：`window.apiRequest()`
- **開發工具**：API 測試功能

### 5. ✅ Nginx 生產環境配置 (`nginx/deepvape.conf`)
- **SSL/TLS 支援**：Let's Encrypt 整合
- **HTTP/2**：效能優化
- **反向代理**：將 API 請求轉發到 Node.js
- **靜態檔案快取**：優化載入速度
- **安全設定**：防護常見攻擊
- **速率限制**：API 保護

### 6. ✅ 部署相關檔案
- **`env.example`** - 環境變數範例
- **`MIGRATION_GUIDE.md`** - 詳細遷移指南
- **`scripts/test-apis.js`** - API 測試腳本

## API 端點對應

| 功能 | Netlify Function | VPS API 端點 |
|-----|-----------------|--------------|
| Telegram 通知 | `/.netlify/functions/send-telegram` | `/api/send-telegram` |
| 7-11 回調 | `cvs_callback.html` | `/api/711-callback` |
| 健康檢查 | N/A | `/api/health` |
| 價格資料 | 靜態 JSON | `/api/prices` |
| 公告資料 | 靜態 JSON | `/api/announcements` |

## 部署檢查清單

### 前置準備
- [ ] Vultr Ubuntu 22.04 VPS
- [ ] 域名 DNS 指向 VPS IP
- [ ] SSH 金鑰設定

### 伺服器設定
- [ ] 安裝 Node.js 18.x
- [ ] 安裝 Nginx
- [ ] 安裝 PM2
- [ ] 設定防火牆

### 應用部署
- [ ] Clone 專案到 `/var/www/deepvape`
- [ ] 執行 `npm install`
- [ ] 建立 `.env` 檔案
- [ ] 執行 `npm run build`
- [ ] 設定 Nginx
- [ ] 取得 SSL 證書

### 啟動服務
- [ ] 啟動 PM2：`npm run pm2:start`
- [ ] 測試 API：`node scripts/test-apis.js`
- [ ] 驗證網站功能

## 主要改進

1. **完整的後端控制**：不再依賴 Netlify Functions
2. **更好的效能**：Nginx 處理靜態檔案，Node.js 專注於 API
3. **可擴展性**：PM2 叢集模式支援自動擴展
4. **成本效益**：固定月費，無 serverless 函數限制
5. **監控能力**：完整的日誌和監控選項

## 測試命令

```bash
# 本地開發
npm run dev

# 建構生產版本
npm run build

# 測試 API
node scripts/test-apis.js

# 部署前檢查
npm run deploy:check

# PM2 操作
npm run pm2:start    # 啟動
npm run pm2:reload   # 重新載入
npm run pm2:logs     # 查看日誌
```

## 環境變數設定

必要的環境變數：
```env
NODE_ENV=production
PORT=3000
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
CORS_ORIGINS=https://52012.xyz,https://52012.xyz
```

## 注意事項

1. **7-11 API 回調**：確保在 7-11 系統中更新回調 URL 為 `https://52012.xyz/api/711-callback`
2. **Telegram 設定**：需要有效的 Bot Token 和 Chat ID
3. **SSL 證書**：使用 Let's Encrypt 自動更新
4. **備份策略**：定期備份 `data/` 目錄和 `.env` 檔案

## 遷移後的架構

```
使用者 <-> Nginx (443/80) <-> Node.js (3000) <-> 資料檔案
                |
                └-> 靜態檔案 (dist/)
```

## 支援與維護

- 查看日誌：`pm2 logs`
- 監控狀態：`pm2 monit`
- 更新程式碼：`git pull && npm install && npm run build && pm2 reload`

遷移已完成準備！🎉 