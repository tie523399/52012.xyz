#!/bin/bash

# DeepVape 生產環境監控腳本
# 檢查服務狀態並發送警報

DOMAIN="52012.xyz"
API_URL="https://${DOMAIN}/api"
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-""}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-""}
LOG_FILE="/var/log/deepvape/monitor.log"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 記錄函數
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# 發送 Telegram 通知
send_telegram() {
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=$1" \
            -d "parse_mode=HTML" > /dev/null
    fi
}

# 檢查服務狀態
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}✓ $service 運行正常${NC}"
        return 0
    else
        echo -e "${RED}✗ $service 已停止${NC}"
        log "警告: $service 服務已停止"
        send_telegram "⚠️ <b>DeepVape 警報</b>%0A服務 <code>$service</code> 已停止！"
        return 1
    fi
}

# 檢查 API 健康狀態
check_api_health() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/health")
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ API 健康檢查通過${NC}"
        return 0
    else
        echo -e "${RED}✗ API 健康檢查失敗 (HTTP $response)${NC}"
        log "警告: API 健康檢查失敗，HTTP 狀態碼: $response"
        send_telegram "⚠️ <b>DeepVape 警報</b>%0AAPI 健康檢查失敗！%0AHTTP 狀態碼: $response"
        return 1
    fi
}

# 檢查磁碟空間
check_disk_space() {
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -lt 80 ]; then
        echo -e "${GREEN}✓ 磁碟使用率: ${usage}%${NC}"
    elif [ "$usage" -lt 90 ]; then
        echo -e "${YELLOW}! 磁碟使用率: ${usage}% (警告)${NC}"
        log "警告: 磁碟使用率達到 ${usage}%"
        send_telegram "⚠️ <b>DeepVape 警告</b>%0A磁碟使用率: ${usage}%"
    else
        echo -e "${RED}✗ 磁碟使用率: ${usage}% (危險)${NC}"
        log "錯誤: 磁碟使用率達到 ${usage}%"
        send_telegram "🚨 <b>DeepVape 緊急</b>%0A磁碟使用率: ${usage}%！"
    fi
}

# 檢查記憶體使用
check_memory() {
    local total=$(free -m | awk 'NR==2{print $2}')
    local used=$(free -m | awk 'NR==2{print $3}')
    local percent=$((used * 100 / total))
    
    if [ "$percent" -lt 80 ]; then
        echo -e "${GREEN}✓ 記憶體使用率: ${percent}%${NC}"
    elif [ "$percent" -lt 90 ]; then
        echo -e "${YELLOW}! 記憶體使用率: ${percent}% (警告)${NC}"
        log "警告: 記憶體使用率達到 ${percent}%"
    else
        echo -e "${RED}✗ 記憶體使用率: ${percent}% (危險)${NC}"
        log "錯誤: 記憶體使用率達到 ${percent}%"
        send_telegram "🚨 <b>DeepVape 緊急</b>%0A記憶體使用率: ${percent}%！"
    fi
}

# 檢查 SSL 證書
check_ssl_certificate() {
    local expiry=$(echo | openssl s_client -servername ${DOMAIN} -connect ${DOMAIN}:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
    local expiry_epoch=$(date -d "$expiry" +%s)
    local current_epoch=$(date +%s)
    local days_left=$(( (expiry_epoch - current_epoch) / 86400 ))
    
    if [ "$days_left" -gt 30 ]; then
        echo -e "${GREEN}✓ SSL 證書剩餘天數: ${days_left} 天${NC}"
    elif [ "$days_left" -gt 7 ]; then
        echo -e "${YELLOW}! SSL 證書剩餘天數: ${days_left} 天 (需要更新)${NC}"
        log "警告: SSL 證書將在 ${days_left} 天後過期"
        send_telegram "⚠️ <b>DeepVape 警告</b>%0ASSL 證書將在 ${days_left} 天後過期！"
    else
        echo -e "${RED}✗ SSL 證書剩餘天數: ${days_left} 天 (緊急)${NC}"
        log "錯誤: SSL 證書將在 ${days_left} 天後過期"
        send_telegram "🚨 <b>DeepVape 緊急</b>%0ASSL 證書將在 ${days_left} 天後過期！"
    fi
}

# 檢查回應時間
check_response_time() {
    local start=$(date +%s%N)
    curl -s -o /dev/null "${API_URL}/health"
    local end=$(date +%s%N)
    local response_time=$(( (end - start) / 1000000 ))
    
    if [ "$response_time" -lt 1000 ]; then
        echo -e "${GREEN}✓ API 回應時間: ${response_time}ms${NC}"
    elif [ "$response_time" -lt 3000 ]; then
        echo -e "${YELLOW}! API 回應時間: ${response_time}ms (較慢)${NC}"
        log "警告: API 回應時間較慢: ${response_time}ms"
    else
        echo -e "${RED}✗ API 回應時間: ${response_time}ms (過慢)${NC}"
        log "錯誤: API 回應時間過慢: ${response_time}ms"
        send_telegram "⚠️ <b>DeepVape 警告</b>%0AAPI 回應時間過慢: ${response_time}ms"
    fi
}

# 主函數
main() {
    echo -e "${GREEN}DeepVape 生產環境監控${NC}"
    echo "========================="
    echo "時間: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 執行所有檢查
    check_service "nginx"
    check_service "deepvape"
    check_api_health
    check_disk_space
    check_memory
    check_ssl_certificate
    check_response_time
    
    echo ""
    echo "監控完成"
    log "監控檢查完成"
}

# 執行主函數
main

# 如果作為 cron job 執行，可以加入以下行到 crontab:
# */5 * * * * /var/www/deepvape/scripts/monitor-production.sh > /dev/null 2>&1 