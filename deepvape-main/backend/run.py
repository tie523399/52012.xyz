#!/usr/bin/env python3
"""
Deepvape 後台管理系統啟動腳本
"""

import os
import sys
from app import app, init_db

def main():
    """主函數"""
    print("🚀 正在啟動 Deepvape 後台管理系統...")
    
    # 初始化數據庫
    print("📊 初始化數據庫...")
    init_db()
    print("✅ 數據庫初始化完成")
    
    # 顯示登入資訊
    print("\n" + "="*50)
    print("🎯 Deepvape 後台管理系統")
    print("="*50)
    print("🌐 後台地址: http://localhost:5001")
    print("👤 默認帳號: admin")
    print("🔑 默認密碼: admin123")
    print("="*50)
    print("\n📋 系統功能:")
    print("• 網站公告管理")
    print("• 產品數據管理")
    print("• 批量操作功能")
    print("• 圖片上傳管理")
    print("• API 接口服務")
    print("\n🔗 API 端點:")
    print("• GET /api/announcements - 獲取公告")
    print("• GET /api/products - 獲取產品列表")
    print("• GET /api/products/<id> - 獲取產品詳情")
    print("\n⚠️  請確保前台網站運行在 http://localhost:3000")
    print("="*50)
    
    try:
        # 啟動應用
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 感謝使用 Deepvape 後台管理系統！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 啟動失敗: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 