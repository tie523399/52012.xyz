# DeepVape 52012.xyz 部署總結

## 已完成工作

### 1. 域名更新 ✅
- 執行 `scripts/update-domain.js` 腳本
- 成功替換 **135 處**域名引用
- 更新 **29 個**檔案
- 所有 deepvape.com/org 已替換為 52012.xyz

### 2. Nginx 配置 ✅
- 建立 `nginx/52012.xyz.conf` 完整配置
- 包含 SSL 設定（Let's Encrypt）
- 配置反向代理到 Node.js (Port 3000)
- 實施速率限制：
  - 一般 API: 10 請求/秒
  - Telegram API: 2 請求/分鐘
  - 網頁請求: 30 請求/秒
- 安全標頭已配置
- Gzip 壓縮已啟用

### 3. 後端配置 ✅
- 建立 `backend/config/production.config.js`
- 設定 CORS 允許 52012.xyz
- 配置 7-11 回調 URL
- 設定安全中間件（Helmet）
- 配置速率限制

### 4. Systemd 服務 ✅
- 建立 `systemd/deepvape.service`
- 配置自動重啟
- 設定資源限制
- 日誌輸出到 journald

### 5. 部署腳本 ✅
- `scripts/deploy-52012.sh` - 自動化部署腳本
- `scripts/monitor-production.sh` - 生產環境監控
- `scripts/pre-deployment-check.sh` - 部署前檢查
- `scripts/update-domain.js` - 域名更新工具

### 6. 安全措施 ✅
- Fail2ban 配置
- 防火牆規則 (UFW)
- SSL/TLS 現代化配置
- 安全標頭實施
- 敏感檔案保護

### 7. 文檔 ✅
- `PRODUCTION_DEPLOYMENT_52012.md` - 完整部署指南
- `DEPLOYMENT_SUMMARY_52012.md` - 本文檔

## 部署檢查清單

### 部署前準備
- [x] 域名更新完成
- [x] Nginx 配置準備
- [x] 後端配置準備
- [x] Systemd 服務準備
- [x] 部署腳本準備
- [ ] VPS 伺服器準備
- [ ] DNS 記錄更新
- [ ] API 金鑰準備

### 需要準備的資訊
1. **VPS 存取**
   - SSH 金鑰或密碼
   - 伺服器 IP 地址

2. **API 金鑰**
   - Telegram Bot Token
   - Telegram Chat ID
   - 7-11 API Key
   - 7-11 API Secret

3. **域名設定**
   - DNS A 記錄指向 VPS IP
   - www 子域名設定

## 部署步驟摘要

```bash
# 1. 上傳專案到 VPS
scp -r deepvape-main/ root@your-vps-ip:/root/

# 2. SSH 連接到 VPS
ssh root@your-vps-ip

# 3. 執行部署腳本
cd /root/deepvape-main
chmod +x scripts/deploy-52012.sh
sudo ./scripts/deploy-52012.sh

# 4. 配置環境變數
nano /var/www/deepvape/backend/.env.production

# 5. 重啟服務
systemctl restart deepvape
```

## 部署後驗證

### 1. 服務狀態檢查
```bash
systemctl status nginx
systemctl status deepvape
```

### 2. API 健康檢查
```bash
curl https://52012.xyz/api/health
```

### 3. SSL 證書檢查
```bash
curl -I https://52012.xyz
```

### 4. 監控設定
```bash
# 設定定期監控
crontab -e
# 加入：
*/5 * * * * /var/www/deepvape/scripts/monitor-production.sh
```

## 重要提醒

1. **7-11 系統更新**
   - 回調 URL: `https://52012.xyz/api/711-callback`
   - Webhook URL: `https://52012.xyz/api/711-webhook`

2. **定期維護**
   - SSL 證書自動更新（Let's Encrypt）
   - 日誌檔案輪替
   - 系統更新

3. **備份策略**
   - 每日自動備份
   - 保留 7 天備份

4. **監控告警**
   - 服務停止
   - 磁碟空間不足
   - 記憶體使用過高
   - SSL 證書即將過期

## 技術支援

如遇到問題，請檢查：
- 應用日誌：`journalctl -u deepvape -f`
- Nginx 日誌：`/var/log/nginx/52012.xyz_error.log`
- 監控日誌：`/var/log/deepvape/monitor.log`

---

**部署日期**: 2024-01-XX  
**專案版本**: 1.0.0  
**目標域名**: https://52012.xyz 