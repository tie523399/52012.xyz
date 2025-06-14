# 7-11 門市選擇 API 整合解決方案

## 問題說明

7-11 門市選擇 API 的主要挑戰：
1. 7-11 會使用 POST 方法發送門市資料到回調 URL
2. 純前端 JavaScript 無法直接讀取 POST body
3. localhost 無法作為回調 URL（7-11 伺服器無法訪問）

## 解決方案

### 方案 1：依賴 GET 參數（推薦）

許多第三方 API（包括 7-11）會同時在 URL 參數中提供資料，即使主要使用 POST 方法。

**實作方式：**
- 使用 `cvs_callback.html` 作為回調頁面
- 頁面會嘗試從多個來源讀取資料：
  - URL 參數（GET）
  - Hash 參數
  - 隱藏的表單欄位

**優點：**
- 不需要後端處理
- 實作簡單
- 適合靜態網站部署

**缺點：**
- 如果 7-11 只使用純 POST，則無法接收資料

### 方案 2：使用現有後端 API

在 `backend/app.py` 添加路由處理 POST 回調：

```python
@app.route('/api/711-callback', methods=['POST'])
def handle_711_callback():
    """處理 7-11 門市選擇回調"""
    try:
        # 獲取 POST 資料
        store_data = request.form.to_dict() or request.get_json()
        
        # 標準化參數名稱
        normalized_data = {
            'storeId': store_data.get('CVSStoreID') or store_data.get('storeId', ''),
            'storeName': store_data.get('CVSStoreName') or store_data.get('storeName', ''),
            'storeAddress': store_data.get('CVSAddress') or store_data.get('storeAddress', ''),
            'storePhone': store_data.get('CVSTelephone') or store_data.get('storePhone', '')
        }
        
        # 建構重定向 URL
        query_params = urllib.parse.urlencode(normalized_data)
        redirect_url = f"{request.host_url}cvs_callback.html?{query_params}"
        
        return redirect(redirect_url, code=302)
        
    except Exception as e:
        # 錯誤處理
        error_url = f"{request.host_url}cvs_callback.html?error=processing_failed"
        return redirect(error_url, code=302)
```

### 方案 3：開發環境解決方案

開發時使用以下方法之一：

1. **ngrok 暴露本地服務**
   ```bash
   # 如果使用後端 API
   ngrok http 3000
   
   # 如果只使用前端
   ngrok http 8888
   ```

2. **使用測試門市功能**
   - cvs_callback.html 包含測試按鈕
   - 可以模擬門市選擇流程

3. **部署到測試環境**
   - 使用實際的公開 URL 進行測試

## 實際整合流程

```mermaid
graph TB
    A[用戶點擊選擇門市] --> B[開啟 7-11 地圖]
    B --> C{7-11 發送資料}
    C -->|GET 參數| D[cvs_callback.html 直接處理]
    C -->|POST 到 API| E[/api/711-callback]
    E --> F[重定向到 cvs_callback.html?params]
    D --> G[顯示門市資訊]
    F --> G
    G --> H[用戶確認]
    H --> I[回傳資料到購物車]
```

## 配置說明

### 生產環境
```javascript
// 使用前端直接處理
callbackUrl = window.location.origin + '/cvs_callback.html';

// 或使用後端 API
callbackUrl = window.location.origin + '/api/711-callback';
```

### 開發環境
```javascript
// config.js
window.SITE_CONFIG = {
    // 使用 ngrok URL
    DEVELOPMENT_CALLBACK_URL: 'https://your-ngrok-id.ngrok.io/cvs_callback.html'
};
```

## 測試檢查清單

- [ ] 確認回調 URL 是公開可訪問的
- [ ] 測試 GET 參數是否能正確解析
- [ ] 確認跨視窗通訊正常運作
- [ ] 驗證門市資料正確顯示
- [ ] 檢查錯誤處理機制

## 故障排除

1. **收不到門市資料**
   - 檢查瀏覽器控制台的日誌
   - 確認回調 URL 正確
   - 檢查是否有跨域問題

2. **開發環境無法測試**
   - 使用 ngrok 或類似工具
   - 使用測試門市功能
   - 部署到測試環境

3. **資料格式問題**
   - 檢查 7-11 API 文檔的參數名稱
   - 確認參數編碼正確 