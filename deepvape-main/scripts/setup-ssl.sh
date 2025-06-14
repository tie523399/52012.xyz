#!/bin/bash

# DeepVape SSL 憑證設定腳本
# 使用 Let's Encrypt 申請免費 SSL 憑證

set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 檢查是否為 root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}此腳本必須以 root 權限執行${NC}" 
   exit 1
fi

echo -e "${GREEN}==================================="
echo "DeepVape SSL 憑證設定"
echo "===================================${NC}"

# 取得網域名稱
read -p "請輸入您的網域名稱 (例如: 52012.xyz): " DOMAIN
read -p "是否包含 www 子網域? (y/n): " INCLUDE_WWW
read -p "請輸入您的電子郵件地址 (用於 Let's Encrypt 通知): " EMAIL

# 設定網域參數
if [[ $INCLUDE_WWW == "y" || $INCLUDE_WWW == "Y" ]]; then
    DOMAINS="-d $DOMAIN -d www.$DOMAIN"
    NGINX_DOMAINS="$DOMAIN www.$DOMAIN"
else
    DOMAINS="-d $DOMAIN"
    NGINX_DOMAINS="$DOMAIN"
fi

# 1. 備份現有 Nginx 設定
echo -e "${YELLOW}[1/5] 備份 Nginx 設定...${NC}"
if [ -f "/etc/nginx/sites-available/deepvape" ]; then
    cp /etc/nginx/sites-available/deepvape /etc/nginx/sites-available/deepvape.backup.$(date +%Y%m%d_%H%M%S)
fi

# 2. 建立臨時 Nginx 設定（用於驗證）
echo -e "${YELLOW}[2/5] 建立臨時 Nginx 設定...${NC}"
cat > /etc/nginx/sites-available/deepvape-temp << EOF
server {
    listen 80;
    server_name $NGINX_DOMAINS;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 404;
    }
}
EOF

# 建立驗證目錄
mkdir -p /var/www/certbot

# 啟用臨時設定
ln -sf /etc/nginx/sites-available/deepvape-temp /etc/nginx/sites-enabled/deepvape
nginx -t && systemctl reload nginx

# 3. 申請 SSL 憑證
echo -e "${YELLOW}[3/5] 申請 SSL 憑證...${NC}"
certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    $DOMAINS

# 4. 更新 Nginx 設定
echo -e "${YELLOW}[4/5] 更新 Nginx 設定...${NC}"
cat > /etc/nginx/sites-available/deepvape << EOF
# HTTP 重定向到 HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $NGINX_DOMAINS;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS 主設定
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $NGINX_DOMAINS;
    
    # SSL 憑證
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL 設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/chain.pem;
    
    # 安全標頭
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval';" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 根目錄
    root /var/www/deepvape/current/dist;
    index index.html;
    
    # 日誌
    access_log /var/log/nginx/deepvape-access.log;
    error_log /var/log/nginx/deepvape-error.log;
    
    # Gzip 壓縮
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml image/svg+xml;
    
    # 靜態檔案快取
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|pdf|txt|woff|woff2|ttf|svg|webp)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 主應用路由
    location / {
        try_files \$uri \$uri/ @nodejs;
    }
    
    # Node.js 應用代理
    location @nodejs {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API 路由
    location /api {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        add_header Cache-Control "no-store, no-cache, must-revalidate";
    }
    
    # 健康檢查
    location /health {
        proxy_pass http://127.0.0.1:3000;
        access_log off;
    }
    
    # 防止訪問隱藏檔案
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # 錯誤頁面
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
    
    client_max_body_size 10M;
}
EOF

# 移除臨時設定
rm -f /etc/nginx/sites-available/deepvape-temp

# 測試並重新載入 Nginx
nginx -t && systemctl reload nginx

# 5. 設定自動更新
echo -e "${YELLOW}[5/5] 設定憑證自動更新...${NC}"
cat > /etc/cron.d/certbot-renew << EOF
# 每天凌晨 2:30 檢查並更新憑證
30 2 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# 測試自動更新
certbot renew --dry-run

echo -e "${GREEN}==================================="
echo "SSL 憑證設定完成！"
echo "===================================${NC}"
echo ""
echo "憑證資訊："
echo "- 網域: $NGINX_DOMAINS"
echo "- 憑證路徑: /etc/letsencrypt/live/$DOMAIN/"
echo "- 有效期限: 90 天（自動更新）"
echo ""
echo "測試 HTTPS："
echo "- https://$DOMAIN"
if [[ $INCLUDE_WWW == "y" || $INCLUDE_WWW == "Y" ]]; then
    echo "- https://www.$DOMAIN"
fi
echo ""
echo -e "${GREEN}✓ SSL 憑證已成功安裝並設定自動更新${NC}" 