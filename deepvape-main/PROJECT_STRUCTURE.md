# DeepVape 專案結構重構說明

## 📁 新的專案結構

```
deepvape-main/
├── index.html                    # 首頁
├── cart.html                     # 購物車頁面
├── order_confirmation.html       # 訂單確認頁
├── cvs_callback.html            # 7-11 門市回調頁
├── /js                          # JavaScript 檔案
│   ├── config.js                # 網站配置
│   ├── store-selector.js        # 門市選擇功能
│   ├── content-manager.js       # 內容管理
│   ├── cart-logic.js            # 購物車邏輯
│   └── main.js                  # 主要入口檔案
├── /css                         # 樣式檔案
│   └── main.css                 # 主要樣式表
├── /images                      # 圖片資源
│   ├── /products               # 產品圖片
│   └── /ui                     # UI 相關圖片
├── /pages                       # 靜態頁面
│   ├── shopping_guide.html      # 購物指南
│   ├── shipping_info.html       # 配送資訊
│   ├── return_policy.html       # 退換貨政策
│   ├── faq.html                # 常見問題
│   └── brand_story.html        # 品牌故事
├── /components                  # 共用元件
│   └── common-components.js     # 共用元件系統
├── /data                        # 資料檔案
│   ├── prices.json             # 產品價格資料
│   └── announcements.json      # 公告資料
├── /backend                     # 後端程式碼
├── /admin                       # 管理後台
├── webpack.config.js            # Webpack 配置
├── package.json                 # 專案依賴配置
├── resource-tracker.json        # 資源追蹤系統
└── PROJECT_STRUCTURE.md         # 本文件
```

## 🔧 主要改進

### 1. **共用元件系統**
- 建立了 `common-components.js` 統一管理導航列、頁尾等重複元件
- 減少 HTML 重複程式碼，提升維護性

### 2. **依賴管理優化**
- 合併 `telegram_requirements.txt` 到主 `requirements.txt`
- 更新 `package.json` 加入 Webpack 相關依賴

### 3. **資源整理**
- 將圖片分類到 `images/products` 和 `images/ui`
- 將靜態頁面移至 `pages` 目錄
- 建立 `css` 目錄存放樣式檔案

### 4. **Webpack 打包系統**
- 建立 `webpack.config.js` 配置檔案
- 支援開發和生產環境打包
- 自動壓縮和優化資源

### 5. **資源追蹤系統**
- 建立 `resource-tracker.json` 記錄所有使用的資源
- 識別未使用和缺失的檔案
- 提供清理和優化建議

## 📋 使用指南

### 安裝依賴
```bash
npm install
```

### 開發模式
```bash
npm run dev      # 啟動後端伺服器
npm run serve    # 啟動 Webpack 開發伺服器
```

### 建置專案
```bash
npm run build    # 生產環境打包
npm run build:dev # 開發環境打包
```

### 監視檔案變更
```bash
npm run watch
```

## ⚠️ 待處理事項

1. **缺失檔案**
   - `nav_logo.png` - 需要建立或改用 `deepvape_logo_main.png`
   - `logoai.gif` - 需要建立或移除引用
   - `product-api-integration.js` - 需要建立或移除引用

2. **清理建議**
   - 移除所有 VFX.js 註解
   - 刪除未使用的 RTF 檔案
   - 清理 `cart_image` 目錄中未使用的圖片

3. **後續優化**
   - 實施圖片壓縮
   - 設置 CDN 加速
   - 加入 PWA 支援

## 🚀 部署注意事項

1. 確保所有環境變數已正確設置
2. 運行 `npm run build` 生成優化後的檔案
3. 部署 `dist` 目錄到伺服器
4. 確保後端 API 正常運作

## 📞 聯絡資訊

如有任何問題，請聯繫開發團隊。 