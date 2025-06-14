# 7-11 門市選擇整合 - 最終方案

## 核心理解

1. **localhost:3000 不是 7-11 的 API** - 這只是範例中您的伺服器位址
2. **7-11 需要公開可訪問的 URL** - 他們的伺服器無法訪問您的 localhost
3. **POST 資料的挑戰** - 純前端無法直接讀取 POST body

## 實作方案（不使用 Netlify Functions）

### 1. 依賴 URL 參數方式

我們假設 7-11 API 會將門市資料同時附加在 URL 參數中（許多 API 都這樣做）：

```javascript
// store-selector.js
// 生產環境使用
callbackUrl = window.location.origin + '/cvs_callback.html';

// cvs_callback.html 會處理：
// - URL 參數 (?CVSStoreID=xxx&CVSStoreName=xxx)
// - Hash 參數 (#CVSStoreID=xxx&CVSStoreName=xxx)
// - 隱藏表單欄位
```

### 2. 開發環境解決方案

```javascript
// 選項 A: 使用 ngrok
// 1. 啟動本地伺服器: npm run dev
// 2. 暴露到公網: ngrok http 8888
// 3. 設定 config:
window.SITE_CONFIG = {
    DEVELOPMENT_CALLBACK_URL: 'https://your-id.ngrok.io/cvs_callback.html'
};

// 選項 B: 使用測試功能
// cvs_callback.html 包含測試按鈕，可模擬門市選擇
```

### 3. 資料流程

```
用戶選擇門市
    ↓
開啟 7-11 地圖 (https://emap.presco.com.tw/c2cemap.ashx)
    ↓
7-11 發送資料到回調 URL
    ↓
cvs_callback.html 從 URL 參數讀取資料
    ↓
顯示門市資訊供確認
    ↓
使用 postMessage 回傳給主視窗
```

## 關鍵檔案

1. **js/store-selector.js**
   - 處理開啟 7-11 地圖
   - 設定回調 URL
   - 接收選擇結果

2. **cvs_callback.html**
   - 接收 7-11 回調
   - 解析門市資料
   - 回傳給主視窗

## 測試方式

### 生產環境
直接使用即可，7-11 會將資料發送到：
```
https://52012.xyz/cvs_callback.html?CVSStoreID=xxx&CVSStoreName=xxx...
```

### 開發環境
1. 點擊測試按鈕模擬門市選擇
2. 使用 ngrok 建立公開 URL
3. 部署到測試環境進行實際測試

## 注意事項

1. **如果 7-11 只使用純 POST**
   - 這個方案會失敗
   - 需要後端 API 處理（在 backend/app.py 添加路由）
   - 或使用其他服務（如 Cloudflare Workers）

2. **跨域問題**
   - 使用 postMessage 進行跨視窗通訊
   - 確保檢查訊息來源

3. **參數名稱**
   - 支援多種可能的參數名稱
   - CVSStoreID / storeId / StoreID
   - CVSStoreName / storeName / StoreName
   - 等等...

## 故障排除

```javascript
// 在瀏覽器控制台檢查：
// 1. 查看 URL 參數
console.log(window.location.search);

// 2. 查看所有參數
console.log(Object.fromEntries(new URLSearchParams(window.location.search)));

// 3. 檢查 referrer
console.log(document.referrer);
```

---

這是最簡單的實作方式，不需要額外的後端服務或 Netlify Functions。 