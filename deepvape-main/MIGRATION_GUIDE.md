# DeepVape Netlify 到 Vultr VPS 遷移指南

## 概述
本指南說明如何將 DeepVape 專案從 Netlify 遷移到 Vultr Ubuntu 22.04 VPS。

## 遷移步驟

### 1. 準備 VPS 環境

```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝必要軟體
sudo apt install -y nodejs npm nginx certbot python3-certbot-nginx git

# 安裝 PM2
sudo npm install -g pm2

# 建立專案目錄
sudo mkdir -p /var/www/deepvape
sudo chown -R $USER:$USER /var/www/deepvape
```

### 2. 部署應用程式

```bash
# 複製專案到 VPS
cd /var/www/deepvape
git clone https://github.com/your-repo/deepvape.git .

# 安裝依賴
npm install

# 建立環境變數檔案
cp .env.example .env
nano .env  # 編輯並填入實際值

# 建立必要目錄
mkdir -p dist error_pages

# 建構前端資源
npm run build
```

### 3. 設定環境變數

建立 `.env` 檔案並設定以下變數：

```env
# 基本設定
NODE_ENV=production
PORT=3000
HOST=0.0.0.0

# Telegram Bot 設定
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# CORS 設定
CORS_ORIGINS=https://52012.xyz,https://52012.xyz
```

### 4. 配置 Nginx

```bash
# 複製 Nginx 配置
sudo cp nginx/deepvape.conf /etc/nginx/sites-available/deepvape

# 建立符號連結
sudo ln -s /etc/nginx/sites-available/deepvape /etc/nginx/sites-enabled/

# 測試配置
sudo nginx -t

# 重啟 Nginx
sudo systemctl restart nginx
```

### 5. 設定 SSL 證書

```bash
# 取得 Let's Encrypt 證書
sudo certbot --nginx -d 52012.xyz -d www.52012.xyz

# 設定自動更新
sudo systemctl enable certbot.timer
```

### 6. 啟動應用程式

```bash
# 使用 PM2 啟動應用
pm2 start ecosystem.config.js --env production

# 儲存 PM2 設定
pm2 save

# 設定開機自動啟動
pm2 startup systemd
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $USER --hp /home/$USER
```

### 7. 設定防火牆

```bash
# 允許必要的端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## API 端點更新

### 前端配置 (js/config.js)

前端已經配置為使用相對路徑的 API 端點：

- `/api/send-telegram` - Telegram 通知
- `/api/711-callback` - 7-11 門市回調
- `/api/health` - 健康檢查
- `/api/prices` - 價格資料
- `/api/announcements` - 公告資料

### 後端路由 (server.js)

所有 API 路由都在 `/api` 前綴下：

```javascript
app.use('/api', apiRouter);
```

## 測試部署

### 1. 檢查服務狀態

```bash
# 檢查 PM2 狀態
pm2 status

# 檢查 Nginx 狀態
sudo systemctl status nginx

# 查看應用日誌
pm2 logs deepvape
```

### 2. 測試 API 端點

```bash
# 健康檢查
curl https://52012.xyz/api/health

# 價格資料
curl https://52012.xyz/api/prices

# 公告資料
curl https://52012.xyz/api/announcements
```

### 3. 測試功能

1. **7-11 門市選擇**：確保回調 URL 正確設定為 `https://52012.xyz/api/711-callback`
2. **Telegram 通知**：提交測試訂單，檢查是否收到通知
3. **靜態資源**：檢查圖片、CSS、JS 檔案是否正確載入

## 監控與維護

### 日誌位置

- Nginx 存取日誌：`/var/log/nginx/deepvape_access.log`
- Nginx 錯誤日誌：`/var/log/nginx/deepvape_error.log`
- PM2 應用日誌：`pm2 logs`

### 常用命令

```bash
# 重啟應用
pm2 restart deepvape

# 重新載入應用（零停機時間）
pm2 reload deepvape

# 監控資源使用
pm2 monit

# 更新程式碼
cd /var/www/deepvape
git pull
npm install
npm run build
pm2 reload deepvape
```

## 故障排除

### 502 Bad Gateway

1. 檢查 Node.js 應用是否運行：`pm2 status`
2. 檢查端口是否正確：`netstat -tlnp | grep 3000`
3. 查看錯誤日誌：`pm2 logs --err`

### SSL 證書問題

1. 檢查證書狀態：`sudo certbot certificates`
2. 手動更新證書：`sudo certbot renew`

### API 無法存取

1. 檢查 CORS 設定
2. 確認防火牆規則
3. 查看 Nginx 錯誤日誌

## 備份策略

### 每日備份腳本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/deepvape"
DATE=$(date +%Y%m%d)

# 備份資料檔案
mkdir -p $BACKUP_DIR/$DATE
cp -r /var/www/deepvape/data $BACKUP_DIR/$DATE/

# 備份環境變數
cp /var/www/deepvape/.env $BACKUP_DIR/$DATE/

# 刪除 7 天前的備份
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} +
```

設定 cron job：
```bash
0 2 * * * /home/ubuntu/backup.sh
```

## 效能優化

1. **啟用 HTTP/2**：已在 Nginx 配置中啟用
2. **Gzip 壓縮**：已配置
3. **靜態資源快取**：已設定適當的快取標頭
4. **PM2 叢集模式**：已配置自動擴展

## 安全建議

1. 定期更新系統和軟體包
2. 使用強密碼和 SSH 金鑰認證
3. 限制 SSH 存取 IP
4. 定期檢查日誌檔案
5. 設定監控和警報

## 結論

遷移完成後，DeepVape 將運行在更可控、更高效能的環境中，具有：

- ✅ 完整的後端 API 支援
- ✅ Telegram 訂單通知
- ✅ 7-11 門市選擇整合
- ✅ SSL/TLS 加密
- ✅ 自動擴展和負載平衡
- ✅ 完整的監控和日誌 