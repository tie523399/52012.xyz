# Gunicorn 配置文件
import os
import multiprocessing

# 服務器配置
bind = f"0.0.0.0:{os.environ.get('PORT', '5001')}"
workers = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# 應用配置
wsgi_module = "wsgi:application"
preload_app = True

# 日誌配置
accesslog = "-"  # 輸出到 stdout
errorlog = "-"   # 輸出到 stderr
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 進程配置
user = os.environ.get('USER', None)
group = os.environ.get('GROUP', None)
tmp_upload_dir = None

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL 配置（如果需要）
keyfile = os.environ.get('SSL_KEYFILE', None)
certfile = os.environ.get('SSL_CERTFILE', None)

# 重啟配置
reload = os.environ.get('FLASK_ENV') == 'development'
reload_extra_files = ['templates/', 'static/'] if reload else []

# 性能調優
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else None 