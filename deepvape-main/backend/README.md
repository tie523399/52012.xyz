# Deepvape 後台管理系統

## 🎯 系統概述

Deepvape 後台管理系統是一個功能完整的電商後台，提供網站公告管理、產品數據管理、批量操作等功能。

## 🚀 快速開始

### 1. 安裝依賴

```bash
cd backend
pip install -r requirements.txt
```

### 2. 啟動系統

```bash
python run.py
```

### 3. 訪問後台

- 後台地址：http://localhost:5000
- 默認帳號：admin
- 默認密碼：admin123

## 📋 主要功能

### 1. 網站公告功能

- ✅ 創建和管理網站公告
- ✅ 設定公告優先級（高/中/低）
- ✅ 設定公告顯示時間範圍
- ✅ 公告啟用/停用控制
- ✅ 自動顯示在前台網站

**功能特色：**
- 高優先級公告會有閃爍動畫效果
- 支援定時顯示和自動過期
- 用戶可關閉公告，系統會記住選擇

### 2. 產品數據管理

#### 單個產品管理
- ✅ 新增/編輯/刪除產品
- ✅ 產品圖片上傳
- ✅ 產品規格設定
- ✅ 產品變體管理（顏色、口味等）
- ✅ SEO 設定
- ✅ 產品狀態控制

#### 批量操作功能
- ✅ **批量修改價格**
  - 按百分比調整（如：+10%、-15%）
  - 按固定金額調整（如：+50、-100）
- ✅ **批量更新庫存**
  - 增加庫存數量
  - 設定為指定數量
- ✅ **批量設定標籤**
  - 熱門、新品、安心選擇、精選等
  - 自定義標籤文字
- ✅ **批量啟用/停用產品**
- ✅ **批量刪除產品**

### 3. 數據庫管理

- ✅ SQLite 數據庫
- ✅ 完整的數據模型
- ✅ 自動初始化
- ✅ 數據關聯管理

## 🔗 API 接口

### 公告 API

```http
GET /api/announcements
```

返回所有活躍的公告，按優先級排序。

**響應示例：**
```json
[
  {
    "id": 1,
    "title": "新品上市",
    "content": "🎉 新品上市！全館滿 $1500 免運費 🚚",
    "priority": 3
  }
]
```

### 產品 API

```http
GET /api/products
GET /api/products?category=hosts
GET /api/products?featured=true
```

**參數：**
- `category`: 按分類篩選（hosts, pods, disposable）
- `featured`: 只返回精選產品

```http
GET /api/products/<id>
```

獲取單個產品詳情。

## 📁 目錄結構

```
backend/
├── app.py              # 主應用程序
├── run.py              # 啟動腳本
├── requirements.txt    # Python 依賴
├── README.md          # 說明文件
├── templates/         # HTML 模板
│   ├── base.html      # 基礎模板
│   ├── login.html     # 登入頁面
│   └── admin/         # 後台頁面
│       ├── dashboard.html
│       ├── announcements.html
│       ├── announcement_form.html
│       ├── products.html
│       └── product_form.html
├── static/            # 靜態文件
│   └── uploads/       # 上傳文件
│       └── products/  # 產品圖片
└── deepvape.db       # SQLite 數據庫（自動生成）
```

## 🎨 界面特色

- 🌟 現代化響應式設計
- 🎯 直觀的操作界面
- 📱 移動端友好
- 🎨 深色主題配色
- ⚡ 流暢的動畫效果

## 🔧 技術棧

- **後端：** Flask + SQLAlchemy
- **數據庫：** SQLite
- **前端：** Bootstrap 5 + Font Awesome
- **圖片處理：** Pillow

## 📊 數據模型

### Admin（管理員）
- id, username, password_hash, created_at

### Announcement（公告）
- id, title, content, is_active, priority
- start_date, end_date, created_at, updated_at

### Category（分類）
- id, name, slug, description, is_active, sort_order

### Product（產品）
- id, name, description, price, original_price
- stock_quantity, category_id, main_image, images
- specifications, variants, is_active, is_featured
- badge_type, badge_text, meta_title, meta_description

## 🚀 部署說明

### 開發環境
```bash
python run.py
```

### 生產環境
建議使用 Gunicorn：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔒 安全注意事項

1. **修改默認密碼**：首次登入後請立即修改管理員密碼
2. **HTTPS 部署**：生產環境請使用 HTTPS
3. **數據備份**：定期備份 SQLite 數據庫文件
4. **訪問控制**：建議設置防火牆限制後台訪問

## 🆘 常見問題

### Q: 無法上傳圖片？
A: 確保 `static/uploads/products/` 目錄存在且有寫入權限。

### Q: 前台無法顯示公告？
A: 檢查前台網站是否正確調用 API 接口，確保 CORS 設定正確。

### Q: 批量操作沒有效果？
A: 確保選中了要操作的產品，檢查瀏覽器控制台是否有錯誤信息。

## 📞 技術支援

如有問題，請檢查：
1. Python 版本（建議 3.8+）
2. 依賴包是否正確安裝
3. 數據庫文件權限
4. 網絡連接狀況

---

**Deepvape 後台管理系統** - 讓電商管理更簡單！ 🎉 