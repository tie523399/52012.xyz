#!/bin/bash

# DeepVape 快速開始腳本
# 協助準備部署到 Vultr

set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "======================================"
echo "   DeepVape 部署準備工具"
echo "   Vultr Ubuntu 22.04 部署"
echo "======================================"
echo -e "${NC}"

# 檢查必要工具
echo -e "${YELLOW}檢查必要工具...${NC}"

check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ $1 未安裝${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 已安裝${NC}"
        return 0
    fi
}

all_tools_installed=true
check_tool git || all_tools_installed=false
check_tool node || all_tools_installed=false
check_tool npm || all_tools_installed=false

if [ "$all_tools_installed" = false ]; then
    echo -e "${RED}請先安裝缺少的工具後再執行此腳本${NC}"
    exit 1
fi

# 收集部署資訊
echo -e "\n${YELLOW}請提供以下部署資訊：${NC}"

# Git 儲存庫
read -p "您的 GitHub 使用者名稱: " GITHUB_USERNAME
read -p "Git 儲存庫名稱 (預設: deepvape): " REPO_NAME
REPO_NAME=${REPO_NAME:-deepvape}

# Vultr 資訊
read -p "Vultr VPS IP 位址: " VULTR_IP
read -p "您的網域名稱 (例如: 52012.xyz): " DOMAIN

# Telegram 設定
echo -e "\n${YELLOW}Telegram Bot 設定（用於訂單通知）：${NC}"
read -p "Telegram Bot Token: " TELEGRAM_BOT_TOKEN
read -p "Telegram Chat ID: " TELEGRAM_CHAT_ID

# 生成設定摘要
echo -e "\n${GREEN}======================================"
echo "設定摘要"
echo "======================================"
echo -e "${NC}"
echo "Git 儲存庫: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo "Vultr IP: ${VULTR_IP}"
echo "網域: ${DOMAIN}"
echo "Telegram Bot: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo ""

read -p "確認以上資訊正確嗎？(y/n): " CONFIRM
if [[ $CONFIRM != "y" && $CONFIRM != "Y" ]]; then
    echo -e "${RED}已取消${NC}"
    exit 1
fi

# 更新部署腳本
echo -e "\n${YELLOW}更新部署腳本...${NC}"

# 更新 deploy.sh
if [ -f "deploy.sh" ]; then
    sed -i.bak "s|https://github.com/YOUR_USERNAME/deepvape.git|https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git|g" deploy.sh
    echo -e "${GREEN}✓ deploy.sh 已更新${NC}"
fi

# 更新 ecosystem.config.js
if [ -f "../ecosystem.config.js" ]; then
    sed -i.bak "s|YOUR_VULTR_IP|${VULTR_IP}|g" ../ecosystem.config.js
    sed -i.bak "s|git@github.com:YOUR_USERNAME/deepvape.git|git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git|g" ../ecosystem.config.js
    echo -e "${GREEN}✓ ecosystem.config.js 已更新${NC}"
fi

# 建立部署資訊檔案
cat > deployment-info.txt << EOF
DeepVape 部署資訊
生成時間: $(date)

=== 伺服器資訊 ===
Vultr IP: ${VULTR_IP}
網域: ${DOMAIN}
SSH: ssh root@${VULTR_IP}

=== Git 儲存庫 ===
URL: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}
分支: main

=== 環境變數 ===
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}

=== 部署步驟 ===
1. 上傳程式碼到 GitHub:
   git remote add origin https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git
   git push -u origin main

2. SSH 連線到伺服器:
   ssh root@${VULTR_IP}

3. 執行伺服器設定:
   wget https://raw.githubusercontent.com/${GITHUB_USERNAME}/${REPO_NAME}/main/scripts/setup-server.sh
   chmod +x setup-server.sh
   ./setup-server.sh

4. 部署應用程式（以 deploy 使用者）:
   su - deploy
   cd /var/www/deepvape/repo/scripts
   ./deploy.sh

5. 設定 SSL:
   sudo ./setup-ssl.sh
EOF

echo -e "${GREEN}✓ 部署資訊已儲存到 deployment-info.txt${NC}"

# 建立 .env.production
echo -e "\n${YELLOW}建立生產環境設定檔...${NC}"
cat > ../.env.production << EOF
# DeepVape 生產環境設定
NODE_ENV=production
PORT=3000
HOST=0.0.0.0

# 網域設定
DOMAIN=${DOMAIN}
FRONTEND_URL=https://${DOMAIN}
API_URL=https://${DOMAIN}/api

# Telegram 設定
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}

# 會話密鑰（請更改為隨機字串）
SESSION_SECRET=$(openssl rand -base64 32)

# 其他設定請參考 config/env.production.example
EOF

echo -e "${GREEN}✓ .env.production 已建立${NC}"

# 顯示下一步指示
echo -e "\n${GREEN}======================================"
echo "準備完成！"
echo "======================================"
echo -e "${NC}"
echo "下一步："
echo ""
echo "1. 提交並推送程式碼到 GitHub:"
echo -e "   ${BLUE}git add ."
echo -e "   git commit -m \"配置 Vultr 部署\""
echo -e "   git remote add origin https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
echo -e "   git push -u origin main${NC}"
echo ""
echo "2. 登入 Vultr 建立 VPS"
echo ""
echo "3. 設定 DNS A 記錄:"
echo -e "   ${BLUE}A    @     ${VULTR_IP}"
echo -e "   A    www   ${VULTR_IP}${NC}"
echo ""
echo "4. SSH 連線到伺服器並開始部署:"
echo -e "   ${BLUE}ssh root@${VULTR_IP}${NC}"
echo ""
echo -e "${YELLOW}詳細部署步驟請參考 DEPLOYMENT_GUIDE.md${NC}"
echo -e "${GREEN}祝您部署順利！ 🚀${NC}" 