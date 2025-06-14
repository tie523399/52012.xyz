# 未使用檔案審核清單

## 測試檔案（從初期開發遺留）
以下檔案是測試用途，不在生產環境中使用：

### HTML 測試檔案
- [ ] `test.html` - 基本測試頁面
- [ ] `test-integration.html` - 整合測試頁面
- [ ] `test-711-api.html` - 7-11 API 測試工具
- [ ] `browser-test.html` - 瀏覽器相容性測試
- [ ] `performance-test.html` - 效能測試頁面

### JavaScript 測試檔案
- [ ] `fix-404-errors.js` - 修復 404 錯誤的臨時腳本
- [ ] `full-verification.js` - 完整驗證腳本

## 重複或備份檔案
以下檔案可能是重複版本：

### 可能的備份檔案
- [ ] 檢查是否有 `*_backup.html` 檔案
- [ ] 檢查是否有 `*_old.html` 檔案
- [ ] 檢查是否有 `*_copy.html` 檔案

## 未被引用的檔案
以下檔案在任何地方都沒有被連結：

### 孤立的 HTML 檔案
- [ ] `cvs_callback.html` - 舊版 7-11 回調頁面（已被 API 取代）

### 根目錄中的媒體檔案
- [ ] `background1.mp4` - 259KB 的影片檔案，需確認是否使用

## 可能過時的檔案
以下檔案可能已經過時：

### AWS Lambda 相關
- [ ] `aws-lambda/` 目錄 - 如果已遷移到 VPS，可能不需要

### Netlify 相關
- [ ] 任何 `netlify.toml` 或 Netlify 函數檔案

## 待整合的重複程式碼

### VFX.js 初始化（在多個頁面重複）
存在於以下檔案中：
- `sp2_product.html`
- `sp2_pods_product.html`
- `lana_a8000_product.html`
- `ilia_pods_product.html`
- `ilia_leather_product.html`
- `ilia_fabric_product.html`
- `ilia_disposable_product.html`
- `ilia_1_product.html`
- `hta_pods_product.html`
- `index.html`

### 重複的 header/footer HTML
每個產品頁面都有相同的：
- 導航列結構
- 頁尾內容
- 社交媒體連結

### 共用的 CSS 樣式
重複的樣式包括：
- `.vfx-logo` 效果
- `.pulse-button` 動畫
- `.product-card` 樣式
- 響應式媒體查詢

## 建議的整理行動

1. **建立 `/archive` 目錄**
   - 移動所有測試檔案到此目錄
   - 保留但不部署到生產環境

2. **整合共用元件**
   - 建立 `js/shared-components.js`
   - 建立 `css/shared-styles.css`
   - 建立 `js/vfx-initializer.js`

3. **清理根目錄**
   - 將測試檔案移到適當位置
   - 確認 `background1.mp4` 的使用情況

4. **更新 `.gitignore`**
   - 加入 `/archive` 目錄
   - 排除測試檔案

## 注意事項
- 在刪除任何檔案前，請先確認它們真的未被使用
- 建議先移動到 archive 目錄而非直接刪除
- 保留一份完整備份以防萬一 