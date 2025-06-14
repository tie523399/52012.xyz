# DeepVape Vultr Ubuntu 22.04 部署指南

本指南詳細說明如何將 DeepVape 專案部署到 Vultr VPS (Ubuntu 22.04 x64)。

## 📋 前置需求

- Vultr VPS (建議規格：2GB RAM, 2 CPU cores, 50GB SSD)
- Ubuntu 22.04 x64
- 已註冊的網域名稱
- SSH 金鑰對
- Git 儲存庫（GitHub/GitLab）

## 🚀 部署步驟

### 1. 建立 Vultr VPS

1. 登入 [Vultr](https://www.vultr.com/)
2. 選擇 "Deploy New Server"
3. 選擇伺服器配置：
   - Server Type: Cloud Compute
   - Server Location: 選擇接近目標用戶的地區
   - Server Image: Ubuntu 22.04 x64
   - Server Size: 至少 55 GB SSD, 2 GB RAM
4. 添加 SSH 金鑰
5. 設定主機名稱：`deepvape-prod`
6. 部署伺服器

### 2. DNS 設定

在您的網域註冊商設定 DNS：

```
A     @      YOUR_VULTR_IP
A     www    YOUR_VULTR_IP
```

等待 DNS 傳播（可能需要 5-30 分鐘）。

### 3. 初始伺服器設定

SSH 連線到伺服器：

```bash
ssh root@YOUR_VULTR_IP
```

執行伺服器設定腳本：

```bash
# 下載設定腳本
wget https://raw.githubusercontent.com/YOUR_USERNAME/deepvape/main/scripts/setup-server.sh
chmod +x setup-server.sh

# 執行設定
./setup-server.sh
```

腳本會自動完成：
- ✅ 系統更新
- ✅ 安裝 Node.js 18.x
- ✅ 安裝 PM2
- ✅ 安裝 Nginx
- ✅ 安裝 Certbot
- ✅ 設定防火牆
- ✅ 建立部署使用者
- ✅ 系統優化

### 4. 設定部署使用者

切換到 deploy 使用者：

```bash
su - deploy
```

設定 SSH 金鑰：

```bash
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_SSH_KEY" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 5. 準備應用程式

克隆您的儲存庫：

```bash
cd /var/www/deepvape
git clone https://github.com/YOUR_USERNAME/deepvape.git repo
```

建立環境變數檔案：

```bash
# 複製範例檔案
cp repo/config/env.production.example /var/www/deepvape/.env.production

# 編輯環境變數
nano /var/www/deepvape/.env.production
```

重要設定項目：
- `TELEGRAM_BOT_TOKEN`: Telegram 機器人 Token
- `TELEGRAM_CHAT_ID`: Telegram 聊天 ID
- `SESSION_SECRET`: 隨機生成的長字串
- 其他 API 金鑰和設定

### 6. 部署應用程式

執行部署腳本：

```bash
cd /var/www/deepvape/repo/scripts
chmod +x deploy.sh
./deploy.sh
```

### 7. 設定 Nginx

複製 Nginx 設定：

```bash
sudo cp /var/www/deepvape/repo/nginx/deepvape.conf /etc/nginx/sites-available/deepvape
sudo ln -s /etc/nginx/sites-available/deepvape /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 8. 申請 SSL 憑證

執行 SSL 設定腳本：

```bash
sudo /var/www/deepvape/repo/scripts/setup-ssl.sh
```

輸入：
- 您的網域名稱（例如：52012.xyz）
- 是否包含 www 子網域
- Email 地址

### 9. 驗證部署

檢查各項服務：

```bash
# PM2 狀態
pm2 status

# Nginx 狀態
sudo systemctl status nginx

# 應用健康檢查
curl http://localhost:3000/health

# HTTPS 測試
curl https://yourdomain.com
```

## 📁 目錄結構

```
/var/www/deepvape/
├── current/              # 當前運行版本（符號連結）
├── repo/                 # Git 儲存庫
├── backups/              # 版本備份
├── .env.production       # 生產環境變數
└── logs/                 # 應用日誌

/var/log/
├── nginx/                # Nginx 日誌
└── pm2/                  # PM2 日誌
```

## 🔧 維護指令

### PM2 管理

```bash
# 查看狀態
pm2 status

# 查看日誌
pm2 logs

# 重啟應用
pm2 restart deepvape-app

# 監控資源
pm2 monit

# 查看詳細資訊
pm2 show deepvape-app
```

### 更新應用

```bash
cd /var/www/deepvape/repo/scripts
./deploy.sh
```

### 備份管理

```bash
# 手動備份
cd /var/www/deepvape
cp -r current backups/manual_$(date +%Y%m%d_%H%M%S)

# 查看備份
ls -la backups/

# 還原備份
pm2 stop deepvape-app
rm current
ln -s backups/BACKUP_NAME current
pm2 start deepvape-app
```

### 日誌管理

```bash
# Nginx 日誌
sudo tail -f /var/log/nginx/deepvape-access.log
sudo tail -f /var/log/nginx/deepvape-error.log

# PM2 日誌
pm2 logs --lines 100

# 清理舊日誌
pm2 flush
```

## 🔒 安全建議

1. **定期更新系統**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **設定自動安全更新**
   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. **監控登入嘗試**
   ```bash
   sudo tail -f /var/log/auth.log
   ```

4. **設定 fail2ban**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

5. **定期備份**
   - 設定自動備份到外部儲存
   - 測試還原程序

## 🚨 故障排除

### 應用無法啟動

1. 檢查 PM2 日誌：`pm2 logs`
2. 檢查環境變數：`cat /var/www/deepvape/.env.production`
3. 檢查 Node.js 版本：`node -v`

### Nginx 502 錯誤

1. 確認應用正在運行：`pm2 status`
2. 檢查 Nginx 錯誤日誌：`sudo tail -f /var/log/nginx/deepvape-error.log`
3. 確認代理設定正確

### SSL 憑證問題

1. 檢查憑證狀態：`sudo certbot certificates`
2. 手動更新：`sudo certbot renew`
3. 檢查 Nginx SSL 設定

### 效能問題

1. 監控資源使用：`pm2 monit`
2. 檢查系統資源：`htop`
3. 優化 PM2 實例數量
4. 考慮升級 VPS 規格

## 📊 監控建議

1. **設定 PM2 監控**
   ```bash
   pm2 install pm2-logrotate
   pm2 set pm2-logrotate:max_size 10M
   pm2 set pm2-logrotate:retain 7
   ```

2. **設定系統監控**
   - 使用 Vultr 的監控面板
   - 考慮安裝 Netdata 或 Prometheus

3. **設定警報**
   - 設定 PM2 email 通知
   - 使用 Telegram 通知重要事件

## 📞 支援資源

- [Vultr 文件](https://www.vultr.com/docs/)
- [Ubuntu 22.04 文件](https://ubuntu.com/server/docs)
- [PM2 文件](https://pm2.keymetrics.io/docs/)
- [Nginx 文件](https://nginx.org/en/docs/)
- [Let's Encrypt 文件](https://letsencrypt.org/docs/)

---

## ✅ 部署檢查清單

- [ ] VPS 已建立並可透過 SSH 連線
- [ ] DNS 已正確設定並解析
- [ ] 伺服器初始設定完成
- [ ] 應用程式已成功部署
- [ ] Nginx 已設定並運行
- [ ] SSL 憑證已安裝
- [ ] 環境變數已正確設定
- [ ] PM2 正在管理應用程式
- [ ] 可透過 HTTPS 訪問網站
- [ ] 備份策略已實施
- [ ] 監控已設定

祝您部署順利！ 🚀 