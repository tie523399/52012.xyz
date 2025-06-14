#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, Product

def update_prices():
    """更新所有產品價格"""
    
    # 價格更新對照表
    price_updates = {
        # 主機價格
        'SP2 一代主機': 650,
        'ILIA 一代主機': 650,
        'ILIA 皮革主機': 650,
        'ILIA 哩亞布紋主機': 650,
        'HTA 黑桃主機': 450,
        
        # 煙彈價格
        'ILIA 發光煙彈': 300,
        'SP2 煙彈': 350,
        'HTA 煙彈': 260,
        
        # 拋棄式價格
        'ILIA 拋棄式四代': 320,
    }
    
    with app.app_context():
        print("=== 開始更新產品價格 ===")
        
        for product_name, new_price in price_updates.items():
            # 查找產品（使用模糊匹配）
            product = Product.query.filter(Product.name.contains(product_name.replace(' 一代主機', '').replace(' 主機', ''))).first()
            
            if not product:
                # 如果沒找到，嘗試直接匹配
                product = Product.query.filter(Product.name == product_name).first()
            
            if product:
                old_price = product.price
                product.price = float(new_price)
                print(f"✅ {product.name}: NT$ {old_price} → NT$ {new_price}")
            else:
                print(f"❌ 找不到產品: {product_name}")
        
        # 提交更改
        db.session.commit()
        print("\n=== 價格更新完成 ===")
        
        # 顯示更新後的所有產品價格
        print("\n=== 更新後的產品價格 ===")
        products = Product.query.all()
        for p in products:
            print(f"{p.id}: {p.name} - NT$ {p.price}")

if __name__ == "__main__":
    update_prices() 