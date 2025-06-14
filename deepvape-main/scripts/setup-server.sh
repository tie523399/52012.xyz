#!/bin/bash

# DeepVape Server Setup Script for Ubuntu 22.04
# 在 Vultr VPS 上執行此腳本進行初始設定

set -e

echo "==================================="
echo "DeepVape 伺服器設定腳本"
echo "適用於 Ubuntu 22.04 LTS"
echo "==================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查是否為 root 使用者
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}此腳本必須以 root 權限執行${NC}" 
   exit 1
fi

# 1. 更新系統
echo -e "${GREEN}[1/10] 更新系統套件...${NC}"
apt update && apt upgrade -y

# 2. 安裝基本工具
echo -e "${GREEN}[2/10] 安裝基本工具...${NC}"
apt install -y curl wget git vim ufw build-essential software-properties-common

# 3. 設定防火牆
echo -e "${GREEN}[3/10] 設定防火牆...${NC}"
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 4. 安裝 Node.js 18.x
echo -e "${GREEN}[4/10] 安裝 Node.js 18.x...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 5. 安裝 PM2
echo -e "${GREEN}[5/10] 安裝 PM2...${NC}"
npm install -g pm2
pm2 startup systemd -u deploy --hp /home/deploy

# 6. 安裝 Nginx
echo -e "${GREEN}[6/10] 安裝 Nginx...${NC}"
apt install -y nginx

# 7. 安裝 Certbot
echo -e "${GREEN}[7/10] 安裝 Certbot...${NC}"
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot

# 8. 建立部署使用者
echo -e "${GREEN}[8/10] 建立部署使用者...${NC}"
if ! id "deploy" &>/dev/null; then
    useradd -m -s /bin/bash deploy
    usermod -aG sudo deploy
    echo -e "${YELLOW}請為 deploy 使用者設定密碼：${NC}"
    passwd deploy
fi

# 9. 建立應用目錄
echo -e "${GREEN}[9/10] 建立應用目錄...${NC}"
mkdir -p /var/www/deepvape
chown -R deploy:deploy /var/www/deepvape

# PM2 日誌目錄
mkdir -p /var/log/pm2
chown -R deploy:deploy /var/log/pm2

# 10. 設定 Node.js 生產環境
echo -e "${GREEN}[10/10] 設定生產環境...${NC}"
cat > /etc/environment << EOF
NODE_ENV="production"
EOF

# 建立交換檔案（如果記憶體少於 2GB）
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
if [ $TOTAL_MEM -lt 2048 ]; then
    echo -e "${YELLOW}記憶體少於 2GB，建立 2GB 交換檔案...${NC}"
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# 優化系統設定
echo -e "${GREEN}優化系統設定...${NC}"
cat > /etc/sysctl.d/99-deepvape.conf << EOF
# 網路優化
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15

# 檔案系統優化
fs.file-max = 65535
EOF
sysctl -p /etc/sysctl.d/99-deepvape.conf

# 設定 ulimit
cat > /etc/security/limits.d/99-deepvape.conf << EOF
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
EOF

echo -e "${GREEN}==================================="
echo "伺服器初始設定完成！"
echo "==================================="
echo ""
echo "下一步："
echo "1. 以 deploy 使用者登入"
echo "2. 上傳您的 SSH 金鑰到 /home/deploy/.ssh/authorized_keys"
echo "3. 複製 Nginx 設定檔案"
echo "4. 執行 deploy.sh 部署應用"
echo ""
echo -e "${YELLOW}系統資訊：${NC}"
echo "Node.js 版本: $(node -v)"
echo "NPM 版本: $(npm -v)"
echo "Nginx 版本: $(nginx -v 2>&1)"
echo ""
echo -e "${RED}建議重新啟動伺服器以套用所有設定${NC}" 