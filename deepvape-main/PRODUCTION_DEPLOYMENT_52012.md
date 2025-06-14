# DeepVape 52012.xyz 生產環境部署指南

## 概述

本文檔詳細說明如何將 DeepVape 電商平台部署到 52012.xyz 域名的生產環境。

## 部署架構

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   使用者     │────▶│  Cloudflare  │────▶│    Nginx    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Node.js   │
                                        │  (Port 3000) │
                                        └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  External   │
                                        │    APIs     │
                                        │ (7-11, TG)  │
                                        └─────────────┘
```

## 系統需求

- Ubuntu 20.04 LTS 或更新版本
- 至少 2GB RAM
- 至少 20GB 磁碟空間
- Node.js 16.x 或更新版本
- Nginx 1.18 或更新版本

## 部署步驟

### 1. 準備工作

```bash
# 連接到 VPS
ssh root@your-vps-ip

# 下載專案
git clone https://github.com/your-repo/deepvape.git
cd deepvape
```

### 2. 執行自動化部署

```bash
# 設定執行權限
chmod +x scripts/deploy-52012.sh

# 執行部署腳本
./scripts/deploy-52012.sh
```

### 3. 配置環境變數

編輯 `/var/www/deepvape/backend/.env.production`：

```env
# Telegram 設定
TELEGRAM_BOT_TOKEN=your_actual_telegram_bot_token
TELEGRAM_CHAT_ID=your_actual_telegram_chat_id

# 7-11 API 設定
SEVEN_ELEVEN_API_KEY=your_actual_api_key
SEVEN_ELEVEN_API_SECRET=your_actual_api_secret

# 安全金鑰
JWT_SECRET=use_strong_random_string
SESSION_SECRET=use_another_strong_random_string
```

### 4. DNS 設定

在您的 DNS 提供商設定以下記錄：

```
A     @     your-vps-ip
A     www   your-vps-ip
```

### 5. 7-11 系統設定

在 7-11 商家後台更新以下設定：

- 回調 URL: `https://52012.xyz/api/711-callback`
- Webhook URL: `https://52012.xyz/api/711-webhook`

## 安全配置

### Nginx 安全標頭

已配置的安全標頭：
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=63072000
- Content-Security-Policy: [詳見配置檔]

### 速率限制

- 一般 API: 10 請求/秒
- Telegram API: 2 請求/分鐘
- 網頁請求: 30 請求/秒

### Fail2ban 規則

自動封鎖惡意 IP：
- SSH 暴力破解防護
- Nginx 請求限制
- Bot 搜尋防護

## 監控與維護

### 設定自動監控

```bash
# 編輯 crontab
crontab -e

# 加入監控任務（每 5 分鐘執行一次）
*/5 * * * * /var/www/deepvape/scripts/monitor-production.sh > /dev/null 2>&1
```

### 常用命令

```bash
# 服務管理
systemctl status deepvape       # 檢查服務狀態
systemctl restart deepvape      # 重啟服務
systemctl stop deepvape         # 停止服務
systemctl start deepvape        # 啟動服務

# 日誌查看
journalctl -u deepvape -f       # 即時查看應用日誌
tail -f /var/log/nginx/52012.xyz_access.log  # 查看訪問日誌
tail -f /var/log/nginx/52012.xyz_error.log   # 查看錯誤日誌

# SSL 證書
certbot renew --dry-run         # 測試證書更新
certbot renew                   # 更新證書

# 監控
./scripts/monitor-production.sh # 手動執行監控檢查
```

### 備份策略

建議設定每日備份：

```bash
# 建立備份腳本
cat > /root/backup-deepvape.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/deepvape"
DATE=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# 備份應用程式
tar -czf $BACKUP_DIR/app-$DATE.tar.gz /var/www/deepvape

# 備份 Nginx 配置
tar -czf $BACKUP_DIR/nginx-$DATE.tar.gz /etc/nginx

# 保留最近 7 天的備份
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /root/backup-deepvape.sh

# 加入 crontab (每天凌晨 3 點執行)
echo "0 3 * * * /root/backup-deepvape.sh" | crontab -
```

## 故障排除

### 問題 1: 服務無法啟動

```bash
# 檢查錯誤日誌
journalctl -u deepvape -n 50

# 檢查語法錯誤
cd /var/www/deepvape/backend
node -c server.js
```

### 問題 2: Nginx 502 錯誤

```bash
# 確認 Node.js 服務運行中
systemctl status deepvape

# 檢查端口
netstat -tlnp | grep 3000

# 重啟服務
systemctl restart deepvape
```

### 問題 3: SSL 證書問題

```bash
# 手動更新證書
certbot renew --force-renewal

# 檢查證書狀態
certbot certificates
```

## 性能優化

### 1. 啟用 HTTP/2

已在 Nginx 配置中啟用

### 2. Gzip 壓縮

已配置，壓縮等級 6

### 3. 靜態資源快取

- 圖片: 30 天
- CSS/JS: 1 年
- 字體: 1 年

### 4. Node.js 叢集模式

如需更高性能，可修改 systemd 服務使用 PM2：

```bash
npm install -g pm2
pm2 start backend/server.js -i max --name deepvape
pm2 save
pm2 startup
```

## 安全檢查清單

- [ ] 更改預設 SSH 端口
- [ ] 禁用 root SSH 登入
- [ ] 設定 SSH 金鑰認證
- [ ] 更新所有系統軟體包
- [ ] 配置防火牆規則
- [ ] 啟用 Fail2ban
- [ ] 設定定期備份
- [ ] 監控磁碟空間
- [ ] 設定日誌輪替
- [ ] 更新所有 API 金鑰

## 聯絡資訊

- 網站: https://52012.xyz
- 客服信箱: service@52012.xyz
- 技術支援: 請查看專案 README

## 版本資訊

- 部署日期: 2024-01-XX
- Node.js 版本: 16.x
- Nginx 版本: 1.18.x
- 系統: Ubuntu 20.04 LTS

---

**注意**: 請妥善保管所有 API 金鑰和密碼，定期更新系統和依賴套件。 