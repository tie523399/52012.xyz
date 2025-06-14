# 🚀 深煙電子煙系統部署指南

## 系統架構說明

### 🌐 前端網站 (Netlify部署)
- **功能**: 客戶瀏覽商品、下單購買
- **特點**: 靜態網站，自動從後端API獲取最新數據
- **URL**: 部署到Netlify後獲得

### 🖥️ 後端系統 (本地或雲端運行)  
- **功能**: 提供API、管理後台、數據庫
- **部署方式**: 本地運行或部署到雲端服務器
- **端口**: 5000 (Flask應用)

### 🤖 Telegram管理機器人
- **功能**: 即時管理產品價格、庫存、公告
- **運行方式**: 獨立運行，不需要Web服務器
- **特點**: 24/7運行，實時更新數據庫

## 📱 關於實時更新問題

### 為什麼機器人修改後網站沒有實時更新？

1. **前端網站是靜態的**
   - Netlify托管的是靜態HTML/CSS/JS文件
   - 不會自動重新獲取數據

2. **解決方案**：
   - 刷新瀏覽器頁面即可看到最新數據
   - 前端會自動調用後端API獲取最新信息
   - 或實現自動刷新機制

### 🔄 實現自動更新的方法

#### 方法1: 定時刷新
```javascript
// 每30秒自動刷新產品數據
setInterval(() => {
    fetchProducts();
}, 30000);
```

#### 方法2: WebSocket實時通信
- 需要後端支持WebSocket
- 機器人修改時推送更新到前端

#### 方法3: 手動刷新提示
- 在頁面添加刷新按鈕
- 提示用戶定期刷新獲取最新數據

## 🚀 部署步驟

### 1. 後端部署 (必須先部署)

#### 本地運行:
```bash
cd backend
python3 app.py
```

#### 雲端部署 (Heroku/Railway/其他):
```bash
# 1. 修改配置
export FLASK_ENV=production
export DATABASE_URL=你的數據庫URL

# 2. 推送到雲端平台
git push heroku main
```

### 2. 前端部署 (Netlify)

#### 修改API配置:
```javascript
// 在前端代碼中修改API基礎URL
const API_BASE_URL = 'https://你的後端域名.herokuapp.com';
```

#### 部署到Netlify:
1. 將前端代碼推送到GitHub
2. 連接Netlify到GitHub倉庫
3. 設置構建配置
4. 部署完成

### 3. Telegram機器人部署

#### 本地運行:
```bash
cd backend
export TELEGRAM_BOT_TOKEN="你的機器人Token"
python3 simple_bot.py
```

#### 雲端運行:
- 可以部署到VPS服務器
- 或使用Heroku Worker
- 或使用Railway等平台

## 🔐 安全配置

### 環境變量設置:
```bash
# 數據庫
export DATABASE_URL="sqlite:///deepvape.db"

# Telegram
export TELEGRAM_BOT_TOKEN="你的機器人Token"

# 管理員帳號
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="admin1122@@$$"

# Flask配置
export FLASK_ENV="production"
export SECRET_KEY="你的密鑰"
```

## 📋 功能清單

### ✅ 已完成功能

#### 🤖 Telegram機器人:
- ✅ 產品價格管理 (影響所有變體)
- ✅ 變體庫存管理 (單獨/批量)
- ✅ 公告管理 (最多3條，自動刪除舊的)
- ✅ 統計報告
- ✅ 用戶登入驗證

#### 🌐 網站功能:
- ✅ 產品展示
- ✅ 庫存狀態顯示
- ✅ 公告系統
- ✅ 管理後台

#### 📦 庫存狀態:
- ✅ 數量 = 0: "產品缺貨"
- ✅ 數量 < 5: "庫存緊張" 
- ✅ 數量 < 10: "庫存不足"
- ✅ 數量 >= 10: "現貨供應"

#### 🔐 帳號信息:
- ✅ 帳號: admin
- ✅ 密碼: admin1122@@$$

## 🎯 使用流程

### 日常管理流程:
1. **使用Telegram機器人**:
   - `/login` 登入管理後台
   - 選擇"📦 產品管理"修改價格/庫存
   - 選擇"📢 公告管理"發布公告

2. **客戶購買流程**:
   - 訪問Netlify網站
   - 瀏覽產品(會顯示最新庫存狀態)
   - 查看公告信息
   - 下單購買

3. **數據同步**:
   - 機器人修改 → 數據庫更新
   - 網站API → 獲取最新數據
   - 客戶刷新 → 看到最新信息

## 🚨 注意事項

1. **機器人必須保持運行**
   - 機器人停止運行就無法接收Telegram消息
   - 建議部署到穩定的服務器

2. **後端API必須可訪問**
   - 前端網站需要調用後端API
   - 確保API URL正確配置

3. **數據庫備份**
   - 定期備份SQLite數據庫文件
   - 重要數據不要遺失

4. **環境變量安全**
   - 不要將密鑰提交到GitHub
   - 使用環境變量管理敏感信息

## 🛠️ 故障排除

### 機器人無法啟動:
```bash
# 檢查Token是否正確
echo $TELEGRAM_BOT_TOKEN

# 檢查依賴是否安裝
pip3 install -r telegram_requirements.txt
```

### 網站無法獲取數據:
1. 檢查後端是否運行
2. 檢查API URL配置
3. 檢查跨域設置

### 數據不同步:
1. 刷新瀏覽器頁面
2. 檢查機器人是否正常運行
3. 檢查數據庫連接

## 📞 技術支持

如有問題請檢查:
1. 日誌輸出信息
2. 網絡連接狀態  
3. 環境變量配置
4. 數據庫文件權限

---

**部署完成後，您將擁有:**
- 🌐 專業的電子煙商城網站
- 🤖 便捷的Telegram管理系統  
- 📱 實時的庫存和公告管理
- 🛒 完整的電商功能 