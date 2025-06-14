#!/usr/bin/env python3
"""
初始化產品變體系統並添加示例數據
"""

from app import app, db, Product, ProductVariant, VariantType, VariantValue

def init_variant_system():
    """初始化變體系統"""
    with app.app_context():
        print("🔧 創建數據庫表格...")
        db.create_all()
        
        print("🎨 創建變體類型...")
        create_default_variant_types()
        
        print("🏷️ 創建變體值...")
        create_default_variant_values()
        
        print("📦 為現有產品創建示例變體...")
        create_sample_variants()
        
        print("✅ 變體系統初始化完成！")

def create_default_variant_types():
    """創建預設變體類型"""
    default_types = [
        {'name': 'flavor', 'display_name': '口味'},
        {'name': 'color', 'display_name': '顏色'},
        {'name': 'size', 'display_name': '尺寸'},
        {'name': 'strength', 'display_name': '濃度'}
    ]
    
    for type_data in default_types:
        existing = VariantType.query.filter_by(name=type_data['name']).first()
        if not existing:
            variant_type = VariantType(**type_data)
            db.session.add(variant_type)
            print(f"  ✅ 創建變體類型: {type_data['display_name']}")
    
    db.session.commit()

def create_default_variant_values():
    """創建預設變體值"""
    default_values = {
        'flavor': [
            {'value': 'mint', 'display_name': '薄荷'},
            {'value': 'strawberry', 'display_name': '草莓'},
            {'value': 'grape', 'display_name': '葡萄'},
            {'value': 'apple', 'display_name': '蘋果'},
            {'value': 'original', 'display_name': '原味'},
            {'value': 'blueberry', 'display_name': '藍莓'},
            {'value': 'peach', 'display_name': '水蜜桃'}
        ],
        'color': [
            {'value': 'black', 'display_name': '黑色', 'color_code': '#000000'},
            {'value': 'white', 'display_name': '白色', 'color_code': '#FFFFFF'},
            {'value': 'red', 'display_name': '紅色', 'color_code': '#FF0000'},
            {'value': 'blue', 'display_name': '藍色', 'color_code': '#0000FF'},
            {'value': 'green', 'display_name': '綠色', 'color_code': '#00FF00'},
            {'value': 'pink', 'display_name': '粉色', 'color_code': '#FFC0CB'},
            {'value': 'silver', 'display_name': '銀色', 'color_code': '#C0C0C0'}
        ],
        'size': [
            {'value': 'small', 'display_name': '小號'},
            {'value': 'medium', 'display_name': '中號'},
            {'value': 'large', 'display_name': '大號'}
        ],
        'strength': [
            {'value': 'light', 'display_name': '輕度'},
            {'value': 'medium', 'display_name': '中度'},
            {'value': 'strong', 'display_name': '重度'}
        ]
    }
    
    for type_name, values in default_values.items():
        variant_type = VariantType.query.filter_by(name=type_name).first()
        if variant_type:
            for value_data in values:
                existing = VariantValue.query.filter_by(
                    variant_type_id=variant_type.id,
                    value=value_data['value']
                ).first()
                if not existing:
                    variant_value = VariantValue(
                        variant_type_id=variant_type.id,
                        **value_data
                    )
                    db.session.add(variant_value)
    
    db.session.commit()

def create_sample_variants():
    """為現有產品創建示例變體"""
    products = Product.query.filter_by(is_active=True).all()
    
    # 示例變體配置
    sample_variants = [
        # 口味變體
        {
            'variant_type': 'flavor',
            'variants': [
                {'value': 'mint', 'name': '薄荷味', 'stock': 50},
                {'value': 'strawberry', 'name': '草莓味', 'stock': 30},
                {'value': 'grape', 'name': '葡萄味', 'stock': 25},
                {'value': 'original', 'name': '原味', 'stock': 40}
            ]
        },
        # 顏色變體
        {
            'variant_type': 'color',
            'variants': [
                {'value': 'black', 'name': '黑色', 'stock': 35},
                {'value': 'white', 'name': '白色', 'stock': 20},
                {'value': 'red', 'name': '紅色', 'stock': 15},
                {'value': 'blue', 'name': '藍色', 'stock': 25}
            ]
        }
    ]
    
    created_count = 0
    for product in products[:3]:  # 只為前3個產品創建變體
        print(f"  📦 為產品 '{product.name}' 創建變體...")
        
        # 根據產品類型選擇合適的變體
        if "主機" in product.name or "套裝" in product.name:
            # 主機類產品創建顏色變體
            variant_config = sample_variants[1]  # 顏色變體
        else:
            # 其他產品創建口味變體
            variant_config = sample_variants[0]  # 口味變體
        
        for variant_data in variant_config['variants']:
            # 檢查是否已存在
            existing = ProductVariant.query.filter_by(
                product_id=product.id,
                variant_type=variant_config['variant_type'],
                variant_value=variant_data['value']
            ).first()
            
            if not existing:
                # 生成SKU
                sku = f"{product.id}-{variant_data['value'][:3].upper()}-{created_count + 1:03d}"
                
                variant = ProductVariant(
                    product_id=product.id,
                    variant_name=variant_data['name'],
                    variant_type=variant_config['variant_type'],
                    variant_value=variant_data['value'],
                    stock_quantity=variant_data['stock'],
                    price_adjustment=0.0,  # 不調整價格
                    sku=sku,
                    is_active=True,
                    is_default=(variant_data['value'] == 'original' or variant_data['value'] == 'black'),
                    sort_order=created_count
                )
                
                db.session.add(variant)
                created_count += 1
                print(f"    ✅ 創建變體: {variant_data['name']} (庫存: {variant_data['stock']})")
    
    db.session.commit()
    print(f"  🎉 總共創建了 {created_count} 個產品變體")

def show_variant_summary():
    """顯示變體系統摘要"""
    with app.app_context():
        print("\n📊 變體系統摘要:")
        print("=" * 50)
        
        # 統計數據
        total_variants = ProductVariant.query.filter_by(is_active=True).count()
        total_stock = db.session.query(db.func.sum(ProductVariant.stock_quantity)).filter(
            ProductVariant.is_active == True
        ).scalar() or 0
        
        print(f"🎨 總變體數量: {total_variants}")
        print(f"📦 總變體庫存: {total_stock}")
        
        # 按類型統計
        type_stats = db.session.query(
            ProductVariant.variant_type,
            db.func.count(ProductVariant.id),
            db.func.sum(ProductVariant.stock_quantity)
        ).filter(ProductVariant.is_active == True).group_by(ProductVariant.variant_type).all()
        
        print(f"\n📋 按類型統計:")
        for variant_type, count, stock in type_stats:
            type_name = {
                'flavor': '口味',
                'color': '顏色', 
                'size': '尺寸',
                'strength': '濃度'
            }.get(variant_type, variant_type)
            print(f"  • {type_name}: {count}個變體, {stock or 0}總庫存")
        
        # 顯示產品變體
        print(f"\n📦 產品變體詳情:")
        products_with_variants = db.session.query(Product).join(ProductVariant).filter(
            ProductVariant.is_active == True
        ).distinct().all()
        
        for product in products_with_variants:
            variants = ProductVariant.query.filter_by(
                product_id=product.id, is_active=True
            ).all()
            print(f"\n  🎨 {product.name}:")
            for variant in variants:
                status = "⚠️ 低庫存" if variant.stock_quantity <= 10 else "✅ 充足"
                print(f"    • {variant.variant_name}: {variant.stock_quantity} ({status})")

if __name__ == '__main__':
    print("🚀 開始初始化產品變體系統...")
    init_variant_system()
    show_variant_summary()
    print("\n🎉 變體系統初始化完成！現在可以使用 Telegram 機器人管理變體庫存了。") 