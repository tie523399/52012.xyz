#!/bin/bash

# DeepVape 部署後測試腳本
# 驗證所有主要功能是否正常運作

DOMAIN="52012.xyz"
API_BASE="https://${DOMAIN}/api"
PASSED=0
FAILED=0

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}DeepVape 部署後測試 - ${DOMAIN}${NC}"
echo "=================================="

# 測試函數
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=$3
    
    echo -n "測試 $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓ (HTTP $response)${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ (預期 $expected_code, 實際 $response)${NC}"
        ((FAILED++))
        return 1
    fi
}

# 測試函數（含回應內容）
test_content() {
    local name=$1
    local url=$2
    local search_string=$3
    
    echo -n "測試 $name... "
    response=$(curl -s "$url")
    
    if echo "$response" | grep -q "$search_string"; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ (未找到預期內容)${NC}"
        ((FAILED++))
        return 1
    fi
}

# 1. 前端頁面測試
echo -e "\n${YELLOW}前端頁面測試${NC}"
echo "-------------------"
test_endpoint "首頁" "https://${DOMAIN}/" "200"
test_endpoint "SP2 產品頁" "https://${DOMAIN}/sp2_product.html" "200"
test_endpoint "購物車頁面" "https://${DOMAIN}/cart.html" "200"
test_endpoint "常見問題" "https://${DOMAIN}/pages/faq.html" "200"

# 2. API 端點測試
echo -e "\n${YELLOW}API 端點測試${NC}"
echo "-------------------"
test_endpoint "健康檢查" "${API_BASE}/health" "200"
test_endpoint "價格查詢" "${API_BASE}/prices" "200"
test_endpoint "公告查詢" "${API_BASE}/announcements" "200"
test_endpoint "門市搜尋" "${API_BASE}/search-stores?city=台北市&district=中正區" "200"

# 3. 靜態資源測試
echo -e "\n${YELLOW}靜態資源測試${NC}"
echo "-------------------"
test_endpoint "Logo 圖片" "https://${DOMAIN}/logo1.png" "200"
test_endpoint "CSS 檔案" "https://${DOMAIN}/css/shared-styles.css" "200"
test_endpoint "JS 檔案" "https://${DOMAIN}/js/shared-components.js" "200"

# 4. SSL/安全測試
echo -e "\n${YELLOW}SSL/安全測試${NC}"
echo "-------------------"
echo -n "檢查 HTTPS 重定向... "
http_response=$(curl -s -o /dev/null -w "%{http_code}" -L "http://${DOMAIN}/")
if [ "$http_response" = "200" ]; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((FAILED++))
fi

echo -n "檢查安全標頭... "
headers=$(curl -s -I "https://${DOMAIN}/" | grep -E "X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security")
if [ -n "$headers" ]; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((FAILED++))
fi

# 5. 回應時間測試
echo -e "\n${YELLOW}效能測試${NC}"
echo "-------------------"
echo -n "首頁載入時間... "
time_taken=$(curl -s -o /dev/null -w "%{time_total}" "https://${DOMAIN}/")
time_ms=$(echo "$time_taken * 1000" | bc)
time_int=${time_ms%.*}

if [ "$time_int" -lt 1000 ]; then
    echo -e "${GREEN}✓ ${time_ms}ms${NC}"
    ((PASSED++))
elif [ "$time_int" -lt 3000 ]; then
    echo -e "${YELLOW}! ${time_ms}ms (較慢)${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ ${time_ms}ms (過慢)${NC}"
    ((FAILED++))
fi

# 6. 錯誤頁面測試
echo -e "\n${YELLOW}錯誤處理測試${NC}"
echo "-------------------"
test_endpoint "404 錯誤頁面" "https://${DOMAIN}/non-existent-page" "404"

# 7. API 功能測試
echo -e "\n${YELLOW}API 功能測試${NC}"
echo "-------------------"
echo -n "測試價格 API 回應格式... "
prices_response=$(curl -s "${API_BASE}/prices")
if echo "$prices_response" | grep -q "SP2"; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((FAILED++))
fi

# 總結
echo -e "\n${YELLOW}測試總結${NC}"
echo "=================================="
echo -e "通過: ${GREEN}${PASSED}${NC}"
echo -e "失敗: ${RED}${FAILED}${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ 所有測試通過！部署成功。${NC}"
    
    echo -e "\n${YELLOW}下一步建議：${NC}"
    echo "1. 在 7-11 系統測試門市選擇功能"
    echo "2. 發送測試訂單確認 Telegram 通知"
    echo "3. 測試完整購物流程"
    echo "4. 設定監控告警"
    exit 0
else
    echo -e "\n${RED}✗ 有 ${FAILED} 個測試失敗，請檢查部署。${NC}"
    
    echo -e "\n${YELLOW}故障排除建議：${NC}"
    echo "1. 檢查服務狀態: systemctl status nginx deepvape"
    echo "2. 查看錯誤日誌: journalctl -u deepvape -n 50"
    echo "3. 檢查 Nginx 日誌: tail -f /var/log/nginx/52012.xyz_error.log"
    echo "4. 確認 DNS 設定是否生效: nslookup ${DOMAIN}"
    exit 1
fi 