#!/usr/bin/env python3
"""更新管理員密碼腳本"""

from app import app, db, Admin
from werkzeug.security import generate_password_hash

def update_admin_password():
    with app.app_context():
        admin = Admin.query.filter_by(username='admin').first()
        if admin:
            admin.password_hash = generate_password_hash('admin1122@@$$')
            db.session.commit()
            print('✅ 管理員密碼已更新為: admin1122@@$$')
        else:
            print('❌ 管理員帳號不存在')

if __name__ == '__main__':
    update_admin_password() 