#!/bin/bash

# DeepVape 部署腳本
# 在部署使用者下執行

set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 配置變數
APP_DIR="/var/www/deepvape"
REPO_URL="https://github.com/YOUR_USERNAME/deepvape.git"
BRANCH="main"
PM2_APP_NAME="deepvape-app"

echo -e "${GREEN}==================================="
echo "DeepVape 部署腳本"
echo "===================================${NC}"

# 檢查是否為 deploy 使用者
if [ "$USER" != "deploy" ]; then
    echo -e "${RED}請以 deploy 使用者執行此腳本${NC}"
    exit 1
fi

# 1. 停止應用（如果正在執行）
echo -e "${YELLOW}[1/8] 停止現有應用...${NC}"
pm2 stop $PM2_APP_NAME 2>/dev/null || true

# 2. 備份當前版本
if [ -d "$APP_DIR/current" ]; then
    echo -e "${YELLOW}[2/8] 備份當前版本...${NC}"
    BACKUP_DIR="$APP_DIR/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$APP_DIR/backups"
    cp -r "$APP_DIR/current" "$BACKUP_DIR"
    
    # 保留最近 5 個備份
    cd "$APP_DIR/backups"
    ls -t | tail -n +6 | xargs -r rm -rf
fi

# 3. 拉取最新程式碼
echo -e "${YELLOW}[3/8] 拉取最新程式碼...${NC}"
cd "$APP_DIR"
if [ ! -d "$APP_DIR/repo" ]; then
    git clone $REPO_URL repo
fi
cd repo
git fetch origin
git reset --hard origin/$BRANCH
git pull origin $BRANCH

# 4. 安裝依賴
echo -e "${YELLOW}[4/8] 安裝依賴套件...${NC}"
npm ci --production --legacy-peer-deps

# 5. 建置專案
echo -e "${YELLOW}[5/8] 建置生產版本...${NC}"
npm run build:prod

# 6. 部署新版本
echo -e "${YELLOW}[6/8] 部署新版本...${NC}"
if [ -L "$APP_DIR/current" ]; then
    rm "$APP_DIR/current"
fi
ln -s "$APP_DIR/repo" "$APP_DIR/current"

# 7. 複製環境變數檔案
echo -e "${YELLOW}[7/8] 設定環境變數...${NC}"
if [ -f "$APP_DIR/.env.production" ]; then
    cp "$APP_DIR/.env.production" "$APP_DIR/current/.env"
else
    echo -e "${RED}警告：找不到 .env.production 檔案${NC}"
    echo -e "${YELLOW}請建立 $APP_DIR/.env.production 檔案${NC}"
fi

# 8. 啟動應用
echo -e "${YELLOW}[8/8] 啟動應用...${NC}"
cd "$APP_DIR/current"
pm2 start ecosystem.config.js --env production
pm2 save

# 檢查應用狀態
sleep 3
pm2 status

# 健康檢查
echo -e "${GREEN}執行健康檢查...${NC}"
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health || echo "500")
if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "${GREEN}✓ 應用健康檢查通過${NC}"
else
    echo -e "${RED}✗ 應用健康檢查失敗 (HTTP $HEALTH_CHECK)${NC}"
    echo -e "${YELLOW}檢查 PM2 日誌：pm2 logs${NC}"
fi

# 顯示部署資訊
echo -e "${GREEN}==================================="
echo "部署完成！"
echo "===================================${NC}"
echo ""
echo "應用狀態："
echo "- 應用目錄: $APP_DIR/current"
echo "- PM2 應用名稱: $PM2_APP_NAME"
echo "- Git 分支: $BRANCH"
echo "- Git Commit: $(cd $APP_DIR/repo && git rev-parse --short HEAD)"
echo ""
echo "常用指令："
echo "- 查看狀態: pm2 status"
echo "- 查看日誌: pm2 logs"
echo "- 重啟應用: pm2 restart $PM2_APP_NAME"
echo "- 監控資源: pm2 monit"
echo ""
echo -e "${YELLOW}記得設定 Nginx 並申請 SSL 憑證！${NC}" 