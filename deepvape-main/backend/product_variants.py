#!/usr/bin/env python3
"""
產品變體管理系統
支援口味、顏色等不同變體的獨立庫存管理
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# 使用現有的db實例
from app import db

class ProductVariant(db.Model):
    """產品變體模型 - 管理產品的不同口味、顏色等變體"""
    __tablename__ = 'product_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # 變體基本信息
    variant_name = db.Column(db.String(100), nullable=False)  # 變體名稱：如"薄荷口味"、"黑色"
    variant_type = db.Column(db.String(50), nullable=False)   # 變體類型：flavor, color, size
    variant_value = db.Column(db.String(100), nullable=False) # 變體值：mint, black, large
    
    # 庫存和價格
    stock_quantity = db.Column(db.Integer, default=0)         # 該變體的庫存
    price_adjustment = db.Column(db.Float, default=0.0)       # 價格調整（相對主產品）
    sku = db.Column(db.String(100), unique=True)              # 變體SKU
    
    # 變體屬性
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)         # 是否為預設變體
    sort_order = db.Column(db.Integer, default=0)             # 排序
    
    # 變體圖片和描述
    image_url = db.Column(db.String(255))                     # 變體專屬圖片
    description = db.Column(db.Text)                          # 變體描述
    
    # 時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯關係
    product = db.relationship('Product', back_populates='product_variants')
    
    def __repr__(self):
        return f'<ProductVariant {self.variant_name}>'
    
    @property
    def final_price(self):
        """計算最終價格（基礎價格 + 調整）"""
        base_price = self.product.price if self.product else 0
        return base_price + self.price_adjustment
    
    @property
    def is_low_stock(self, threshold=10):
        """檢查是否低庫存"""
        return self.stock_quantity <= threshold
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'variant_name': self.variant_name,
            'variant_type': self.variant_type,
            'variant_value': self.variant_value,
            'stock_quantity': self.stock_quantity,
            'price_adjustment': self.price_adjustment,
            'final_price': self.final_price,
            'sku': self.sku,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'sort_order': self.sort_order,
            'image_url': self.image_url,
            'description': self.description,
            'is_low_stock': self.is_low_stock,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'product_name': self.product.name if self.product else None
        }

class VariantType(db.Model):
    """變體類型管理"""
    __tablename__ = 'variant_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # flavor, color, size
    display_name = db.Column(db.String(100), nullable=False)      # 口味, 顏色, 尺寸
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'is_active': self.is_active,
            'sort_order': self.sort_order
        }

class VariantValue(db.Model):
    """變體值管理"""
    __tablename__ = 'variant_values'
    
    id = db.Column(db.Integer, primary_key=True)
    variant_type_id = db.Column(db.Integer, db.ForeignKey('variant_types.id'), nullable=False)
    value = db.Column(db.String(100), nullable=False)           # mint, black, large
    display_name = db.Column(db.String(100), nullable=False)    # 薄荷, 黑色, 大號
    color_code = db.Column(db.String(7))                        # 顏色代碼 #000000
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯關係
    variant_type = db.relationship('VariantType', backref=db.backref('values', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'variant_type_id': self.variant_type_id,
            'value': self.value,
            'display_name': self.display_name,
            'color_code': self.color_code,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'variant_type_name': self.variant_type.display_name if self.variant_type else None
        }

# 輔助函數
def get_product_total_stock(product_id):
    """獲取產品所有變體的總庫存"""
    total = db.session.query(db.func.sum(ProductVariant.stock_quantity)).filter(
        ProductVariant.product_id == product_id,
        ProductVariant.is_active == True
    ).scalar()
    return total or 0

def get_low_stock_variants(threshold=10):
    """獲取低庫存變體"""
    return ProductVariant.query.filter(
        ProductVariant.stock_quantity <= threshold,
        ProductVariant.is_active == True
    ).all()

def get_product_variants_by_type(product_id, variant_type):
    """獲取產品特定類型的變體"""
    return ProductVariant.query.filter(
        ProductVariant.product_id == product_id,
        ProductVariant.variant_type == variant_type,
        ProductVariant.is_active == True
    ).order_by(ProductVariant.sort_order).all()

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
    
    db.session.commit()

def create_default_variant_values():
    """創建預設變體值"""
    default_values = {
        'flavor': [
            {'value': 'mint', 'display_name': '薄荷'},
            {'value': 'strawberry', 'display_name': '草莓'},
            {'value': 'grape', 'display_name': '葡萄'},
            {'value': 'apple', 'display_name': '蘋果'},
            {'value': 'original', 'display_name': '原味'}
        ],
        'color': [
            {'value': 'black', 'display_name': '黑色', 'color_code': '#000000'},
            {'value': 'white', 'display_name': '白色', 'color_code': '#FFFFFF'},
            {'value': 'red', 'display_name': '紅色', 'color_code': '#FF0000'},
            {'value': 'blue', 'display_name': '藍色', 'color_code': '#0000FF'},
            {'value': 'green', 'display_name': '綠色', 'color_code': '#00FF00'}
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

def init_variant_system():
    """初始化變體系統"""
    # 創建表格
    db.create_all()
    
    # 創建預設數據
    create_default_variant_types()
    create_default_variant_values()
    
    print("✅ 產品變體系統初始化完成")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        init_variant_system() 