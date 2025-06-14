#!/bin/bash

# DeepVape 52012.xyz 部署腳本
# 自動化部署到 Ubuntu VPS

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
DOMAIN="52012.xyz"
DEPLOY_USER="deepvape"
DEPLOY_DIR="/var/www/deepvape"
NGINX_CONFIG="/etc/nginx/sites-available/${DOMAIN}"
SYSTEMD_SERVICE="/etc/systemd/system/deepvape.service"

echo -e "${GREEN}DeepVape 部署腳本 - ${DOMAIN}${NC}"
echo "=================================="

# 檢查是否為 root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}此腳本必須以 root 身份執行${NC}" 
   exit 1
fi

# 1. 更新系統
echo -e "\n${YELLOW}步驟 1: 更新系統${NC}"
apt update && apt upgrade -y

# 2. 安裝必要軟體
echo -e "\n${YELLOW}步驟 2: 安裝必要軟體${NC}"
apt install -y nginx nodejs npm git certbot python3-certbot-nginx ufw fail2ban

# 3. 建立部署使用者
echo -e "\n${YELLOW}步驟 3: 建立部署使用者${NC}"
if ! id "$DEPLOY_USER" &>/dev/null; then
    useradd -m -s /bin/bash $DEPLOY_USER
    echo -e "${GREEN}使用者 $DEPLOY_USER 已建立${NC}"
else
    echo -e "${GREEN}使用者 $DEPLOY_USER 已存在${NC}"
fi

# 4. 建立目錄結構
echo -e "\n${YELLOW}步驟 4: 建立目錄結構${NC}"
mkdir -p $DEPLOY_DIR/{dist,backend,uploads,logs,error_pages}
mkdir -p /var/log/deepvape
chown -R $DEPLOY_USER:$DEPLOY_USER $DEPLOY_DIR
chown -R $DEPLOY_USER:$DEPLOY_USER /var/log/deepvape

# 5. 複製檔案
echo -e "\n${YELLOW}步驟 5: 複製檔案到部署目錄${NC}"
cp -r ./* $DEPLOY_DIR/
chown -R $DEPLOY_USER:$DEPLOY_USER $DEPLOY_DIR

# 6. 執行域名更新腳本
echo -e "\n${YELLOW}步驟 6: 更新域名為 ${DOMAIN}${NC}"
cd $DEPLOY_DIR
sudo -u $DEPLOY_USER node scripts/update-domain.js

# 7. 安裝 Node.js 依賴
echo -e "\n${YELLOW}步驟 7: 安裝 Node.js 依賴${NC}"
cd $DEPLOY_DIR/backend
sudo -u $DEPLOY_USER npm install --production

# 8. 設定環境變數檔案
echo -e "\n${YELLOW}步驟 8: 設定環境變數${NC}"
if [ ! -f "$DEPLOY_DIR/backend/.env.production" ]; then
    cat > $DEPLOY_DIR/backend/.env.production << EOF
NODE_ENV=production
PORT=3000
HOST=127.0.0.1
DOMAIN=${DOMAIN}
FRONTEND_URL=https://${DOMAIN}
API_URL=https://${DOMAIN}/api
CORS_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
SEVEN_ELEVEN_API_KEY=your_api_key
SEVEN_ELEVEN_API_SECRET=your_api_secret
JWT_SECRET=$(openssl rand -base64 32)
SESSION_SECRET=$(openssl rand -base64 32)
EOF
    chown $DEPLOY_USER:$DEPLOY_USER $DEPLOY_DIR/backend/.env.production
    chmod 600 $DEPLOY_DIR/backend/.env.production
    echo -e "${YELLOW}請編輯 $DEPLOY_DIR/backend/.env.production 並填入正確的 API 金鑰${NC}"
fi

# 9. 設定 Nginx
echo -e "\n${YELLOW}步驟 9: 設定 Nginx${NC}"
cp $DEPLOY_DIR/nginx/52012.xyz.conf $NGINX_CONFIG
ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 建立錯誤頁面
cat > $DEPLOY_DIR/error_pages/50x.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>服務暫時無法使用</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #e74c3c; }
    </style>
</head>
<body>
    <h1>服務暫時無法使用</h1>
    <p>我們正在進行系統維護，請稍後再試。</p>
    <p>如有緊急需求，請聯繫：service@${DOMAIN}</p>
</body>
</html>
EOF

# 10. 設定 SSL 證書
echo -e "\n${YELLOW}步驟 10: 設定 SSL 證書${NC}"
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email service@$DOMAIN --redirect

# 11. 設定 Systemd 服務
echo -e "\n${YELLOW}步驟 11: 設定 Systemd 服務${NC}"
cp $DEPLOY_DIR/systemd/deepvape.service $SYSTEMD_SERVICE
systemctl daemon-reload
systemctl enable deepvape
systemctl start deepvape

# 12. 設定防火牆
echo -e "\n${YELLOW}步驟 12: 設定防火牆${NC}"
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload

# 13. 設定 Fail2ban
echo -e "\n${YELLOW}步驟 13: 設定 Fail2ban${NC}"
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/*error.log

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
logpath = /var/log/nginx/*access.log
maxretry = 2
EOF

systemctl restart fail2ban

# 14. 設定日誌輪替
echo -e "\n${YELLOW}步驟 14: 設定日誌輪替${NC}"
cat > /etc/logrotate.d/deepvape << EOF
/var/log/deepvape/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $DEPLOY_USER $DEPLOY_USER
    sharedscripts
    postrotate
        systemctl reload deepvape >/dev/null 2>&1 || true
    endscript
}
EOF

# 15. 測試服務
echo -e "\n${YELLOW}步驟 15: 測試服務${NC}"
nginx -t
systemctl status deepvape --no-pager

# 16. 顯示服務狀態
echo -e "\n${GREEN}部署完成！${NC}"
echo "=================================="
echo -e "網站: https://${DOMAIN}"
echo -e "API: https://${DOMAIN}/api"
echo -e "\n服務狀態："
systemctl is-active nginx deepvape

echo -e "\n${YELLOW}重要提醒：${NC}"
echo "1. 請編輯 $DEPLOY_DIR/backend/.env.production 填入正確的 API 金鑰"
echo "2. 請在 7-11 系統中更新回調 URL 為: https://${DOMAIN}/api/711-callback"
echo "3. 請更新 DNS 記錄指向此伺服器 IP"
echo "4. 請定期檢查日誌: journalctl -u deepvape -f"
echo "5. 監控 Nginx 狀態: curl http://127.0.0.1:9615/nginx_status"

echo -e "\n${GREEN}常用命令：${NC}"
echo "重啟服務: systemctl restart deepvape"
echo "查看日誌: journalctl -u deepvape -f"
echo "重載 Nginx: systemctl reload nginx"
echo "更新證書: certbot renew" 