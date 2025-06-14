# DeepVape 電子煙購物網站

一個現代化的電子煙購物網站，具備完整的產品展示、購物車功能和後台管理系統。

## 🌟 主要功能

### 前端功能
- **產品展示**: 主機、煙彈、拋棄式電子煙產品展示
- **響應式設計**: 支援桌面和手機瀏覽
- **購物車系統**: 本地儲存的購物車功能
- **門市選擇**: 7-11、全家、萊爾富取貨點選擇
- **訂單確認**: 完整的訂單確認流程
- **客服整合**: LINE 客服連結和 QR Code

### 後端功能
- **Flask 後台**: 完整的後台管理系統
- **產品管理**: 價格、庫存、狀態管理
- **公告系統**: 重要公告發佈（最多3條）
- **庫存狀態**: 自動庫存狀態顯示
- **API 介面**: RESTful API 支援

### Telegram 機器人
- **管理機器人**: 通過 Telegram 管理產品和公告
- **價格管理**: 修改價格影響所有變體
- **庫存管理**: 獨立變體庫存管理
- **安全認證**: 管理員密碼保護

## 📦 產品系列

### 主機系列
- **SP2 一代主機** - 智能溫控系統 (NT$ 650)
- **ILIA 一代主機** - 經典設計，新手首選 (NT$ 650)
- **ILIA 皮革主機** - 高級皮革外觀 (NT$ 650)
- **ILIA 布紋主機** - 時尚布紋質感 (NT$ 650)
- **HTA 黑桃主機** - 黑桃系列主機 (NT$ 450)

### 煙彈系列
- **SP2 煙彈** - 多種口味選擇 (NT$ 350)
- **ILIA 煙彈** - 陶瓷芯霧化器 (NT$ 300)
- **LANA 煙彈** - 創新口味，順滑口感 (NT$ 280)
- **HTA 煙彈** - 黑桃系列煙彈 (NT$ 260)

### 拋棄式系列
- **ILIA 拋棄式四代** - 6500口大容量 (NT$ 320)
- **LANA A8000 拋棄式** - 8000口超長續航 (NT$ 320)

## 🛠️ 技術架構

### 前端技術
- **HTML5/CSS3**: 現代化網頁標準
- **JavaScript**: 動態交互功能
- **響應式設計**: 適配各種螢幕尺寸
- **Font Awesome**: 圖標庫
- **LocalStorage**: 本地資料儲存

### 後端技術
- **Flask**: Python Web 框架
- **SQLite**: 輕量級資料庫
- **SQLAlchemy**: ORM 資料庫操作
- **RESTful API**: 標準 API 設計

### Telegram 機器人
- **python-telegram-bot**: Telegram Bot API
- **Flask 整合**: 直接操作後台資料庫
- **多用戶支援**: 獨立會話管理

## 📁 專案結構

```
DeepVape/
├── index.html                 # 首頁
├── cart.html                 # 購物車頁面
├── order_confirmation.html   # 訂單確認頁面
├── shopping_guide.html       # 購物說明
├── store_search_demo.html    # 門市搜尋
├── cvs_callback.html         # 取貨回調
├── 
├── 產品頁面/
│   ├── sp2_product.html      # SP2 主機
│   ├── ilia_1_product.html   # ILIA 一代主機
│   ├── ilia_fabric_product.html # ILIA 布紋主機
│   ├── ilia_leather_product.html # ILIA 皮革主機
│   ├── hta_vape_product.html # HTA 主機
│   ├── sp2_pods_product.html # SP2 煙彈
│   ├── ilia_pods_product.html # ILIA 煙彈
│   ├── lana_pods_product.html # LANA 煙彈
│   ├── hta_pods_product.html # HTA 煙彈
│   ├── ilia_disposable_product.html # ILIA 拋棄式
│   └── lana_a8000_product.html # LANA A8000
├── 
├── backend/                   # 後台系統
│   ├── app.py                # Flask 主應用
│   ├── simple_bot.py         # 簡化版 Telegram 機器人
│   ├── deepvape_dev.db       # SQLite 資料庫
│   ├── requirements.txt      # Python 依賴
│   └── templates/            # 網頁模板
├── 
├── 產品圖片/
│   ├── sp2_d/               # SP2 主機圖片
│   ├── ilia_1/              # ILIA 一代圖片
│   ├── ilia_Bu/             # ILIA 布紋圖片
│   ├── ilia_L/              # ILIA 皮革圖片
│   ├── hta_vape/            # HTA 主機圖片
│   ├── hta_pods/            # HTA 煙彈圖片
│   ├── lana_pods/           # LANA 煙彈圖片
│   ├── ilia_a_4/            # ILIA 拋棄式圖片
│   └── lana_a8000/          # LANA A8000 圖片
└── 
└── 品牌資源/
    ├── logo.png             # 主要 Logo
    ├── nav_logo.png         # 導航 Logo
    ├── hero1.png            # 首頁橫幅
    └── S__16834578.jpg      # LINE 客服 QR Code
```

## 🚀 部署說明

### 1. 前端部署
- 將所有 HTML、CSS、JS 檔案上傳到 Web 伺服器
- 確保圖片資源路徑正確
- 配置 HTTPS（建議）

### 2. 後台部署
   ```bash
cd backend
   pip install -r requirements.txt
python app.py
```

### 3. Telegram 機器人
```bash
cd backend
export TELEGRAM_BOT_TOKEN="your_bot_token"
python simple_bot.py
   ```

## ⚙️ 配置說明

### 環境變數
- `TELEGRAM_BOT_TOKEN`: Telegram 機器人 Token
- `ADMIN_PASSWORD`: 管理員密碼（預設：admin1122@@$$）

### 資料庫配置
- 使用 SQLite，檔案位於 `backend/deepvape_dev.db`
- 首次運行會自動建立資料表和範例資料

### API 配置
- 後台 API 預設運行在 `http://localhost:5000`
- 可在前端 JavaScript 中修改 `API_BASE_URL`

## 🛡️ 安全功能

### Telegram 機器人安全
- 管理員密碼保護
- 獨立會話管理
- 操作記錄追蹤

### 資料驗證
- 輸入資料檢驗
- SQL 注入防護
- XSS 攻擊防護

## 📊 庫存狀態系統

### 庫存狀態定義
- **現貨供應** (≥10件): 充足庫存
- **庫存不足** (5-9件): 庫存偏低
- **庫存緊張** (1-4件): 急需補貨
- **產品缺貨** (0件): 暫時缺貨

### 自動狀態更新
- 庫存變更時自動更新狀態
- 網頁實時顯示庫存狀態
- 低庫存警告提醒

## 🔧 維護說明

### 日常維護
1. **價格更新**: 使用 Telegram 機器人或後台管理
2. **庫存管理**: 定期檢查並補充庫存
3. **公告管理**: 及時更新重要公告（最多3條）
4. **圖片管理**: 定期檢查圖片連結是否正常

### 故障排除
1. **機器人無法啟動**: 檢查 Token 配置和網路連線
2. **資料庫錯誤**: 檢查資料庫檔案權限
3. **API 無法連線**: 確認後台服務運行狀態
4. **圖片無法顯示**: 檢查圖片路徑和檔案存在性

## 📞 聯絡方式

- **LINE 客服**: https://line.me/ti/p/euNh8K-s3e
- **客服專線**: 0800-XXX-XXX
- **Email**: service@52012.xyz
- **服務時間**: 週一至週五 09:00-18:00

## 📄 重要提醒

⚠️ **年齡限制**: 本網站及產品僅供 18 歲以上成年人使用
⚠️ **健康警告**: 吸菸有害健康，請遵守當地相關法規
⚠️ **使用說明**: 請詳閱產品使用說明書，正確使用產品

## 🔄 更新日誌

### v2.0 (2024-12)
- ✅ 新增 LANA 煙彈產品頁面
- ✅ 重新設計 ILIA 布紋主機頁面
- ✅ 移除所有直接購買按鈕
- ✅ 更新所有產品價格
- ✅ 改善 logo 點擊連結
- ✅ 整理專案檔案結構

### v1.0 (2024-11)
- 🎉 初始版本發佈
- 🎉 完整的購物網站功能
- 🎉 後台管理系統
- 🎉 Telegram 機器人管理