# AWS Lambda 部署指南

## 📦 前置需求

1. 安裝 AWS CLI
2. 安裝 Serverless Framework：
   ```bash
   npm install -g serverless
   ```
3. 設定 AWS 認證

## 🚀 快速部署

### 1. 進入 AWS Lambda 目錄
```bash
cd aws-lambda
```

### 2. 設定環境變數
```bash
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"
```

### 3. 部署到 AWS
```bash
serverless deploy
```

### 4. 獲取 API Endpoint
部署成功後會顯示：
```
endpoints:
  POST - https://xxxxx.execute-api.ap-northeast-1.amazonaws.com/prod/send-telegram
```

### 5. 更新前端程式碼
在 `cart.html` 中更新 API endpoint：
```javascript
// AWS 或其他環境
apiEndpoint = 'https://xxxxx.execute-api.ap-northeast-1.amazonaws.com/prod/send-telegram';
```

## 🔧 手動部署（不使用 Serverless Framework）

### 1. 建立 Lambda 函數
1. 登入 AWS Console
2. 進入 Lambda 服務
3. 建立新函數
4. 選擇 Node.js 18.x
5. 上傳 `send-telegram.js`

### 2. 設定環境變數
在 Lambda 函數的配置中加入：
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 3. 建立 API Gateway
1. 建立 REST API
2. 建立資源和 POST 方法
3. 整合 Lambda 函數
4. 啟用 CORS
5. 部署 API

## 📊 監控與日誌

### CloudWatch 日誌
所有 Lambda 執行日誌都會記錄在 CloudWatch Logs

### 錯誤追蹤
檢查以下位置的日誌：
- Lambda 函數日誌
- API Gateway 日誌
- 瀏覽器 Console

## 💰 成本估算

### Lambda
- 前 100 萬次請求免費
- 每月 40 萬 GB-秒的計算時間免費

### API Gateway
- 前 100 萬次 API 呼叫免費
- 之後每百萬次約 $3.50 USD

一般電商網站的訂單量，通常都在免費額度內。

## 🔒 安全建議

1. **IAM 角色**：只給予最小必要權限
2. **API 金鑰**：考慮為 API Gateway 加入 API Key
3. **Rate Limiting**：設定 API 速率限制
4. **監控**：設定 CloudWatch 警報

## 🆘 故障排除

### 函數逾時
- 增加 Lambda 逾時時間（預設 3 秒）

### CORS 錯誤
- 確認 API Gateway 有正確設定 CORS headers

### 權限錯誤
- 檢查 Lambda 執行角色的權限

## 📝 測試指令

### 本地測試
```bash
serverless invoke local --function sendTelegram --path test-event.json
```

### 測試事件範例 (test-event.json)
```json
{
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"orderId\":\"TEST123\",\"orderDate\":\"2024-01-01T00:00:00Z\",\"customer\":{\"name\":\"測試客戶\",\"phone\":\"0912345678\"},\"store\":{\"id\":\"123\",\"name\":\"測試門市\",\"address\":\"測試地址\"},\"items\":[{\"name\":\"測試商品\",\"quantity\":1,\"price\":100}],\"subtotal\":100,\"shipping\":60,\"total\":160}"
}
```

---

需要更多協助？請參考 [AWS Lambda 文檔](https://docs.aws.amazon.com/lambda/) 或 [Serverless Framework 文檔](https://www.serverless.com/framework/docs) 