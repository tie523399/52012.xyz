# 7-11 門市選擇 API 整合指南

## 📌 重要觀念

**7-11 API 的運作流程：**
1. 我們開啟 7-11 的電子地圖網址：`https://emap.presco.com.tw/c2cemap.ashx`
2. 在 URL 參數中提供**我們的回調 URL**（必須是公開可訪問的）
3. 使用者在 7-11 地圖選擇門市後，7-11 會 **POST** 門市資料到我們的回調 URL
4. 我們的伺服器接收並處理這個 POST 請求

⚠️ **關鍵點：回調 URL 必須是公開可訪問的，不能是 localhost！**

## 🔧 實作方式

### 1. 伺服器端 - 處理 7-11 POST 回調

```javascript
// server.js
app.post('/api/711-callback', (req, res) => {
    // 7-11 會 POST 這些資料
    const storeData = {
        storeId: req.body.CVSStoreID,
        storeName: req.body.CVSStoreName,
        storeAddress: req.body.CVSAddress,
        storePhone: req.body.CVSTelephone
    };
    
    // 回傳 HTML 頁面，通知前端
    res.send(`
        <html>
        <body>
            <script>
                // 通知開啟此視窗的父視窗
                window.opener.postMessage({
                    type: 'STORE_SELECTED',
                    data: ${JSON.stringify(storeData)}
                }, '*');
                
                // 關閉視窗
                setTimeout(() => window.close(), 1000);
            </script>
        </body>
        </html>
    `);
});
```

### 2. 前端 - 開啟 7-11 地圖

```javascript
// store-selector.js
openStoreMap() {
    // 生產環境：使用實際網域
    const callbackUrl = 'https://yourdomain.com/api/711-callback';
    
    // 建構 7-11 地圖 URL
    const mapUrl = 'https://emap.presco.com.tw/c2cemap.ashx' + 
                  '?eshopid=870' +
                  '&servicetype=1' +
                  '&url=' + encodeURIComponent(callbackUrl);
    
    // 開啟新視窗
    window.open(mapUrl, 'StoreMap', 'width=1000,height=700');
    
    // 監聽回調訊息
    window.addEventListener('message', (event) => {
        if (event.data.type === 'STORE_SELECTED') {
            // 處理門市資料
            console.log('選擇的門市:', event.data.data);
        }
    });
}
```

## 🛠️ 開發環境解決方案

由於 7-11 API 需要公開 URL，在本地開發時有以下解決方案：

### 方案 1：使用 ngrok（推薦）

1. 安裝 ngrok：
   ```bash
   npm install -g ngrok
   ```

2. 啟動本地伺服器：
   ```bash
   npm start  # 在 port 3000
   ```

3. 使用 ngrok 建立公開 URL：
   ```bash
   ngrok http 3000
   ```

4. 設定回調 URL：
   ```javascript
   // 使用 ngrok 提供的 URL
   const callbackUrl = 'https://abc123.ngrok.io/api/711-callback';
   ```

### 方案 2：部署到測試伺服器

將應用部署到測試環境（如 Heroku、Netlify、Vercel），使用真實的公開 URL。

### 方案 3：手動輸入門市資訊

在開發時使用手動輸入功能，避免依賴 7-11 API：

```javascript
// 快速填入測試資料
function quickFillTestStore() {
    const testStore = {
        storeId: '250094',
        storeName: '京達門市',
        storeAddress: '台中市豐原區中正路805號'
    };
    // 填入表單...
}
```

## 📝 7-11 API 參數說明

### 請求參數（GET）
- `eshopid`: 廠商代碼（例如：870）
- `servicetype`: 服務類型（1 = 取貨付款）
- `url`: 回調 URL（必須 URL encode）

### 回傳參數（POST）
- `CVSStoreID`: 門市代號
- `CVSStoreName`: 門市名稱
- `CVSAddress`: 門市地址
- `CVSTelephone`: 門市電話

## 🔍 除錯技巧

1. **檢查回調 URL**：
   ```javascript
   console.log('回調 URL:', callbackUrl);
   console.log('完整地圖 URL:', mapUrl);
   ```

2. **監控 POST 請求**：
   ```javascript
   app.post('/api/711-callback', (req, res) => {
       console.log('收到 7-11 回調:');
       console.log('Headers:', req.headers);
       console.log('Body:', req.body);
       // ...
   });
   ```

3. **測試工具**：
   在瀏覽器 Console 執行：
   ```javascript
   // 模擬 7-11 回調
   DEEPVAPE_DEV.testStoreCallback({
       storeId: '123456',
       storeName: '測試門市'
   });
   ```

## ⚠️ 常見問題

### Q1: 為什麼在 localhost 無法使用？
A: 7-11 的伺服器需要能夠訪問您的回調 URL。localhost 只能在您的電腦上訪問，外部無法連接。

### Q2: 如何在開發時測試？
A: 使用 ngrok 或類似工具建立臨時的公開 URL，或使用手動輸入功能。

### Q3: 回調沒有收到資料？
A: 檢查：
- 回調 URL 是否正確且可公開訪問
- 伺服器是否正確處理 POST 請求
- 是否有防火牆或安全設定阻擋請求

## 📚 相關檔案

- `/server.js` - 伺服器端回調處理
- `/js/store-selector.js` - 前端門市選擇器
- `/js/config.js` - 配置檔案
- `/api/711-callback` - 回調端點

## 🚀 部署檢查清單

- [ ] 回調 URL 使用 HTTPS（生產環境）
- [ ] 伺服器正確處理 POST 請求
- [ ] 前端正確監聽 message 事件
- [ ] 錯誤處理機制完善
- [ ] 開發環境有替代方案 