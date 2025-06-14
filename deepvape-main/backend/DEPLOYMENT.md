# Deepvape 後台管理系統部署指南

## 🚀 快速部署

### 1. 環境準備

**系統要求：**
- Python 3.8+
- PostgreSQL 12+ 或 MySQL 8.0+（可選，默認使用 SQLite）
- Nginx（生產環境推薦）
- SSL 證書（HTTPS 必需）

### 2. 本地部署

```bash
# 克隆項目
git clone <your-repo-url>
cd image_vape/backend

# 運行部署腳本
chmod +x deploy.sh
./deploy.sh

# 手動啟動（如果需要）
source venv/bin/activate
python3 wsgi.py
```

### 3. Docker 部署

```bash
# 使用 Docker Compose（推薦）
docker-compose up -d

# 或單獨構建
docker build -t deepvape-backend .
docker run -p 5001:5001 deepvape-backend
```

### 4. 生產環境部署

#### 4.1 使用 Gunicorn + Nginx

```bash
# 安裝依賴
pip install -r requirements.txt

# 配置環境變量
cp env.example .env
# 編輯 .env 文件

# 啟動 Gunicorn
gunicorn -c gunicorn.conf.py wsgi:application
```

#### 4.2 Nginx 配置

```nginx
# 複製並修改 nginx.conf
cp nginx.conf /etc/nginx/sites-available/deepvape
ln -s /etc/nginx/sites-available/deepvape /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

## 🔧 配置說明

### 環境變量

| 變量名 | 說明 | 默認值 | 必需 |
|--------|------|--------|------|
| `FLASK_ENV` | 運行環境 | `development` | 否 |
| `SECRET_KEY` | 應用密鑰 | 隨機生成 | **是** |
| `DATABASE_URL` | 數據庫連接 | SQLite | 否 |
| `PORT` | 服務端口 | `5001` | 否 |
| `CORS_ORIGINS` | 允許的域名 | `*` | **是** |
| `ADMIN_USERNAME` | 管理員用戶名 | `admin` | 否 |
| `ADMIN_PASSWORD` | 管理員密碼 | `admin123` | **是** |

### 數據庫配置

**PostgreSQL:**
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/deepvape
```

**MySQL:**
```bash
MYSQL_URL=mysql+pymysql://username:password@localhost:3306/deepvape
```

**SQLite（默認）:**
```bash
DATABASE_URL=sqlite:///deepvape_prod.db
```

## 🌐 雲端部署

### Heroku

```bash
# 安裝 Heroku CLI
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev

# 設定環境變量
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ADMIN_PASSWORD=your-secure-password

# 部署
git push heroku main
```

### DigitalOcean App Platform

1. 連接 GitHub 倉庫
2. 設定環境變量
3. 選擇 Python 運行時
4. 設定啟動命令：`gunicorn -c gunicorn.conf.py wsgi:application`

### AWS EC2

```bash
# 安裝依賴
sudo apt update
sudo apt install python3-pip nginx postgresql

# 部署應用
git clone <your-repo>
cd image_vape/backend
./deploy.sh

# 配置 Nginx
sudo cp nginx.conf /etc/nginx/sites-available/deepvape
sudo ln -s /etc/nginx/sites-available/deepvape /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 設定 SSL（Let's Encrypt）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 🔒 安全配置

### 1. SSL/TLS 設定

```bash
# 生成自簽證書（測試用）
openssl req -x509 -newkey rsa:4096 -keyout private.key -out certificate.crt -days 365 -nodes

# 或使用 Let's Encrypt
certbot certonly --webroot -w /var/www/html -d yourdomain.com
```

### 2. 防火牆設定

```bash
# UFW 配置
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. 定期備份

```bash
# 數據庫備份腳本
#!/bin/bash
pg_dump deepvape > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 📊 監控與日誌

### 健康檢查

```bash
# 檢查應用狀態
curl http://localhost:5001/health
```

### 日誌查看

```bash
# Gunicorn 日誌
tail -f logs/deepvape.log

# Nginx 日誌
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Docker 日誌
docker-compose logs -f web
```

## 🚨 故障排除

### 常見問題

1. **數據庫連接失敗**
   - 檢查 `DATABASE_URL` 配置
   - 確認數據庫服務運行中

2. **靜態文件無法訪問**
   - 檢查 `UPLOAD_FOLDER` 權限
   - 確認 Nginx 配置正確

3. **CORS 錯誤**
   - 設定正確的 `CORS_ORIGINS`
   - 檢查前端域名配置

### 性能優化

1. **數據庫優化**
   ```sql
   -- 添加索引
   CREATE INDEX idx_product_active ON product(is_active);
   CREATE INDEX idx_product_category ON product(category_id);
   ```

2. **緩存配置**
   - 使用 Redis 緩存
   - 啟用 Nginx 靜態文件緩存

3. **負載均衡**
   ```nginx
   upstream backend {
       server 127.0.0.1:5001;
       server 127.0.0.1:5002;
   }
   ```

## 📞 技術支援

如有部署問題，請檢查：
1. 系統日誌：`/var/log/syslog`
2. 應用日誌：`logs/deepvape.log`
3. 數據庫日誌
4. Nginx 錯誤日誌

---

**注意：** 生產環境部署前請務必：
- 更改默認密碼
- 設定強密鑰
- 配置 HTTPS
- 設定防火牆
- 定期備份數據 