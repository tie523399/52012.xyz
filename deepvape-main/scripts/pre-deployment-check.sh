#!/bin/bash

# DeepVape 部署前檢查腳本
# 確保所有準備工作已完成

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DOMAIN="52012.xyz"
ERRORS=0
WARNINGS=0

echo -e "${GREEN}DeepVape 部署前檢查 - ${DOMAIN}${NC}"
echo "=================================="

# 檢查函數
check() {
    local description=$1
    local command=$2
    
    echo -n "檢查 $description... "
    
    if eval $command > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((ERRORS++))
        return 1
    fi
}

warn_check() {
    local description=$1
    local command=$2
    
    echo -n "檢查 $description... "
    
    if eval $command > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${YELLOW}!${NC}"
        ((WARNINGS++))
        return 1
    fi
}

# 系統檢查
echo -e "\n${YELLOW}系統需求檢查${NC}"
echo "-------------------"
check "作業系統是否為 Ubuntu" "grep -i ubuntu /etc/os-release"
check "Node.js 是否已安裝" "which node"
check "NPM 是否已安裝" "which npm"
check "Git 是否已安裝" "which git"

# 檔案結構檢查
echo -e "\n${YELLOW}專案檔案檢查${NC}"
echo "-------------------"
check "後端目錄存在" "[ -d backend ]"
check "前端檔案存在" "[ -f index.html ]"
check "Nginx 配置存在" "[ -f nginx/52012.xyz.conf ]"
check "Systemd 服務檔案存在" "[ -f systemd/deepvape.service ]"
check "部署腳本存在" "[ -f scripts/deploy-52012.sh ]"
check "域名更新腳本存在" "[ -f scripts/update-domain.js ]"

# 配置檔案檢查
echo -e "\n${YELLOW}配置檔案檢查${NC}"
echo "-------------------"
check "生產環境配置存在" "[ -f backend/config/production.config.js ]"
warn_check "環境變數範本" "[ -f backend/.env.example ]"

# 域名替換檢查
echo -e "\n${YELLOW}域名配置檢查${NC}"
echo "-------------------"
OLD_DOMAIN_COUNT=$(grep -r "deepvape\.\(com\|org\)" --include="*.html" --include="*.js" --include="*.json" --include="*.xml" --include="*.conf" --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null | wc -l || echo 0)
if [ "$OLD_DOMAIN_COUNT" -gt 0 ]; then
    echo -e "舊域名引用... ${YELLOW}! 發現 $OLD_DOMAIN_COUNT 處未更新${NC}"
    ((WARNINGS++))
else
    echo -e "舊域名引用... ${GREEN}✓ 已全部更新${NC}"
fi

# 安全檢查
echo -e "\n${YELLOW}安全設定檢查${NC}"
echo "-------------------"
check "監控腳本存在" "[ -f scripts/monitor-production.sh ]"
check "腳本執行權限" "[ -x scripts/deploy-52012.sh ]"

# Node.js 版本檢查
echo -e "\n${YELLOW}版本檢查${NC}"
echo "-------------------"
NODE_VERSION=$(node -v 2>/dev/null | cut -d'v' -f2)
if [ -n "$NODE_VERSION" ]; then
    MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1)
    if [ "$MAJOR_VERSION" -ge 16 ]; then
        echo -e "Node.js 版本 (v$NODE_VERSION)... ${GREEN}✓${NC}"
    else
        echo -e "Node.js 版本 (v$NODE_VERSION)... ${YELLOW}! 建議使用 16.x 或更新版本${NC}"
        ((WARNINGS++))
    fi
fi

# 依賴檢查
echo -e "\n${YELLOW}依賴套件檢查${NC}"
echo "-------------------"
if [ -f backend/package.json ]; then
    cd backend
    if npm list --depth=0 > /dev/null 2>&1; then
        echo -e "後端依賴完整性... ${GREEN}✓${NC}"
    else
        echo -e "後端依賴完整性... ${YELLOW}! 需要執行 npm install${NC}"
        ((WARNINGS++))
    fi
    cd ..
fi

# API 金鑰提醒
echo -e "\n${YELLOW}API 金鑰提醒${NC}"
echo "-------------------"
echo "請確保您已準備以下資訊："
echo "1. Telegram Bot Token"
echo "2. Telegram Chat ID"
echo "3. 7-11 API Key"
echo "4. 7-11 API Secret"
echo "5. VPS 伺服器 IP 地址"

# 總結
echo -e "\n${YELLOW}檢查結果${NC}"
echo "=================================="
echo -e "錯誤: ${ERRORS}"
echo -e "警告: ${WARNINGS}"

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "\n${GREEN}✓ 所有檢查通過！可以開始部署。${NC}"
    else
        echo -e "\n${YELLOW}! 有 ${WARNINGS} 個警告，但可以繼續部署。${NC}"
    fi
    echo -e "\n下一步："
    echo "1. 將專案上傳到 VPS"
    echo "2. SSH 連接到 VPS"
    echo "3. 執行: sudo ./scripts/deploy-52012.sh"
    exit 0
else
    echo -e "\n${RED}✗ 發現 ${ERRORS} 個錯誤，請修正後再部署。${NC}"
    exit 1
fi 