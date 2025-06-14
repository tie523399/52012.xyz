#!/usr/bin/env python3
"""
WSGI 入口文件
用於 Gunicorn、uWSGI 等 WSGI 服務器部署
"""

import os
from app import create_app, init_db

# 從環境變量獲取配置
config_name = os.environ.get('FLASK_ENV', 'production')

# 創建應用實例
application = create_app(config_name)

# 在應用上下文中初始化數據庫
with application.app_context():
    init_db()

if __name__ == "__main__":
    application.run() 