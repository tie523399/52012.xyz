#!/bin/bash

# DeepVape 部署腳本 - 52012.xyz
# 在 root 使用者下執行

set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 配置變數
DOMAIN="52012.xyz"
APP_DIR="/var/www/deepvape"
PM2_APP_NAME="deepvape-app"

echo -e "${GREEN}==================================="
echo "DeepVape 部署腳本 - 52012.xyz"
echo "===================================${NC}"

# 1. 系統更新和安裝必要套件
echo -e "${YELLOW}[1/10] 更新系統並安裝必要套件...${NC}"
apt update && apt upgrade -y
apt install -y nginx python3-pip python3-venv nodejs npm

# 2. 安裝 PM2
echo -e "${YELLOW}[2/10] 安裝 PM2...${NC}"
npm install -g pm2

# 3. 創建部署用戶
echo -e "${YELLOW}[3/10] 設置部署用戶...${NC}"
if ! id "deploy" &>/dev/null; then
    useradd -m -s /bin/bash deploy
    usermod -aG sudo deploy
    echo "deploy ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/deploy
fi

# 4. 設置部署目錄
echo -e "${YELLOW}[4/10] 設置部署目錄...${NC}"
mkdir -p $APP_DIR
chown -R deploy:deploy $APP_DIR

# 5. 設置 Nginx
echo -e "${YELLOW}[5/10] 配置 Nginx...${NC}"
cat > /etc/nginx/sites-available/$DOMAIN << EOL
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/current/static;
        expires 30d;
    }

    location /media {
        alias $APP_DIR/current/media;
        expires 30d;
    }
}
EOL

# 啟用站點
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 6. 安裝 SSL 證書
echo -e "${YELLOW}[6/10] 安裝 SSL 證書...${NC}"
apt install -y certbot python3-certbot-nginx
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# 7. 設置部署環境
echo -e "${YELLOW}[7/10] 設置部署環境...${NC}"
su - deploy << EOF
cd $APP_DIR

# 創建環境變數文件
cat > .env.production << EOL
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///deepvape_prod.db
PORT=5001
CORS_ORIGINS=https://$DOMAIN
ADMIN_USERNAME=admin
ADMIN_PASSWORD=$(openssl rand -base64 12)
EOL

# 創建應用目錄
mkdir -p current
EOF

# 8. 設置 PM2 配置
echo -e "${YELLOW}[8/10] 設置 PM2 配置...${NC}"
su - deploy << EOF
cd $APP_DIR
cat > ecosystem.config.js << EOL
module.exports = {
  apps: [{
    name: '$PM2_APP_NAME',
    script: 'wsgi.py',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
    },
    env_production: {
      NODE_ENV: 'production'
    }
  }]
}
EOL
EOF

# 9. 設置 Python 環境
echo -e "${YELLOW}[9/10] 設置 Python 環境...${NC}"
su - deploy << EOF
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
EOF

# 10. 設置開機自啟
echo -e "${YELLOW}[10/10] 設置開機自啟...${NC}"
pm2 startup
systemctl enable nginx

# 顯示部署資訊
echo -e "${GREEN}==================================="
echo "部署完成！"
echo "===================================${NC}"
echo ""
echo "應用資訊："
echo "- 域名: $DOMAIN"
echo "- 應用目錄: $APP_DIR/current"
echo "- PM2 應用名稱: $PM2_APP_NAME"
echo "- Nginx 配置: /etc/nginx/sites-available/$DOMAIN"
echo ""
echo "上傳檔案步驟："
echo "1. 使用 SCP 上傳檔案："
echo "   scp -r /path/to/your/local/files/* deploy@your-server-ip:$APP_DIR/current/"
echo ""
echo "2. 啟動應用："
echo "   cd $APP_DIR"
echo "   pm2 start ecosystem.config.js --env production"
echo ""
echo "常用指令："
echo "- 查看狀態: pm2 status"
echo "- 查看日誌: pm2 logs"
echo "- 重啟應用: pm2 restart $PM2_APP_NAME"
echo "- 監控資源: pm2 monit"
echo ""
echo -e "${YELLOW}請確保您的域名 $DOMAIN 已正確指向此服務器！${NC}" 