#!/bin/bash

# Deepvape 後台管理系統部署腳本

set -e  # 遇到錯誤立即退出

echo "🚀 開始部署 Deepvape 後台管理系統..."

# 檢查 Python 版本
python3 --version

# 創建虛擬環境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
fi

# 激活虛擬環境
echo "🔧 激活虛擬環境..."
source venv/bin/activate

# 升級 pip
echo "⬆️ 升級 pip..."
pip install --upgrade pip

# 安裝依賴
echo "📚 安裝依賴套件..."
pip install -r requirements.txt

# 檢查環境變量文件
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到 .env 文件，請複製 env.example 並配置環境變量"
    cp env.example .env
    echo "📝 已創建 .env 文件，請編輯後重新運行部署"
    exit 1
fi

# 載入環境變量
echo "🔐 載入環境變量..."
export $(cat .env | grep -v '^#' | xargs)

# 創建必要目錄
echo "📁 創建必要目錄..."
mkdir -p logs
mkdir -p static/uploads/products

# 初始化數據庫
echo "🗄️ 初始化數據庫..."
python3 -c "
from wsgi import application
with application.app_context():
    from app import init_db
    init_db()
    print('數據庫初始化完成')
"

# 檢查配置
echo "✅ 檢查配置..."
python3 -c "
from wsgi import application
print(f'Flask 環境: {application.config.get(\"ENV\", \"未設定\")}')
print(f'Debug 模式: {application.config.get(\"DEBUG\", False)}')
print(f'數據庫 URI: {application.config.get(\"SQLALCHEMY_DATABASE_URI\", \"未設定\")[:50]}...')
print(f'上傳目錄: {application.config.get(\"UPLOAD_FOLDER\", \"未設定\")}')
"

echo "🎉 部署完成！"
echo ""
echo "啟動命令："
echo "  開發模式: python3 wsgi.py"
echo "  生產模式: gunicorn -c gunicorn.conf.py wsgi:application"
echo ""
echo "訪問地址: http://localhost:${PORT:-5001}" 