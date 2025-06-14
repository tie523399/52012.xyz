from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import uuid
from config import config

# 創建應用工廠函數
def create_app(config_name=None):
    app = Flask(__name__)
    
    # 從環境變量獲取配置，默認為 development
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化擴展
    db.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    
    return app

# 初始化擴展
db = SQLAlchemy()

# 創建應用實例
app = create_app()

# 數據庫模型
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)  # 1=低, 2=中, 3=高
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)  # 原價
    stock_quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    
    # 產品圖片
    main_image = db.Column(db.String(255))
    images = db.Column(db.Text)  # JSON 格式存儲多張圖片
    
    # 產品屬性
    specifications = db.Column(db.Text)  # JSON 格式存儲規格
    variants = db.Column(db.Text)  # JSON 格式存儲變體（顏色、口味等）
    
    # 狀態和標籤
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    badge_type = db.Column(db.String(50))  # hot, new, safe, etc.
    badge_text = db.Column(db.String(100))
    
    # SEO
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    
    # 時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 變體關係將在後面定義
    
    def get_stock_status(self):
        """獲取庫存狀態"""
        # 計算總庫存（主庫存 + 所有變體庫存）
        total_stock = self.stock_quantity
        if hasattr(self, 'product_variants'):
            variant_stock = sum(v.stock_quantity for v in self.product_variants if v.is_active)
            total_stock += variant_stock
        
        if total_stock == 0:
            return {'status': 'out_of_stock', 'text': '產品缺貨', 'class': 'out-of-stock'}
        elif total_stock < 5:
            return {'status': 'critical_low', 'text': '庫存緊張', 'class': 'critical-low'}
        elif total_stock < 10:
            return {'status': 'low_stock', 'text': '庫存不足', 'class': 'low-stock'}
        else:
            return {'status': 'in_stock', 'text': '現貨供應', 'class': 'in-stock'}
    
    def get_total_stock(self):
        """獲取總庫存數量"""
        total_stock = self.stock_quantity
        if hasattr(self, 'product_variants'):
            variant_stock = sum(v.stock_quantity for v in self.product_variants if v.is_active)
            total_stock += variant_stock
        return total_stock

    def to_dict(self):
        # 獲取變體信息
        variants_data = []
        if hasattr(self, 'product_variants'):
            variants_data = [v.to_dict() for v in self.product_variants if v.is_active]
        
        stock_status = self.get_stock_status()
        total_stock = self.get_total_stock()
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'original_price': self.original_price,
            'stock_quantity': self.stock_quantity,
            'total_stock': total_stock,
            'stock_status': stock_status,
            'category': self.category.name if self.category else None,
            'category_id': self.category_id,
            'main_image': self.main_image,
            'images': json.loads(self.images) if self.images else [],
            'specifications': json.loads(self.specifications) if self.specifications else {},
            'variants': json.loads(self.variants) if self.variants else [],
            'product_variants': variants_data,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'badge_type': self.badge_type,
            'badge_text': self.badge_text,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

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
    product = db.relationship('Product', backref=db.backref('product_variants', lazy=True, cascade='all, delete-orphan'))
    
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

# 登入檢查裝飾器
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# 路由
@app.route('/')
def index():
    return redirect(url_for('admin_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('登入成功！', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('用戶名或密碼錯誤！', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

@app.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # 獲取當前管理員
        admin = Admin.query.get(session['admin_id'])
        
        # 驗證當前密碼
        if not check_password_hash(admin.password_hash, current_password):
            flash('當前密碼錯誤！', 'error')
            return render_template('admin/change_password.html')
        
        # 驗證新密碼
        if len(new_password) < 6:
            flash('新密碼長度至少需要6個字符！', 'error')
            return render_template('admin/change_password.html')
        
        if new_password != confirm_password:
            flash('新密碼與確認密碼不一致！', 'error')
            return render_template('admin/change_password.html')
        
        # 更新密碼
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('密碼更改成功！請重新登入。', 'success')
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('admin/change_password.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    # 統計數據
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    total_categories = Category.query.count()
    active_announcements = Announcement.query.filter_by(is_active=True).count()
    
    stats = {
        'total_products': total_products,
        'active_products': active_products,
        'total_categories': total_categories,
        'active_announcements': active_announcements
    }
    
    return render_template('admin/dashboard.html', stats=stats)

# 公告管理
@app.route('/admin/announcements')
@login_required
def announcements():
    announcements = Announcement.query.order_by(Announcement.priority.desc(), Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)

@app.route('/admin/announcements/create', methods=['GET', 'POST'])
@login_required
def create_announcement():
    if request.method == 'POST':
        # 檢查公告數量，最多3條
        announcement_count = Announcement.query.filter_by(is_active=True).count()
        if announcement_count >= 3:
            # 刪除最舊的公告
            oldest_announcement = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.asc()).first()
            if oldest_announcement:
                db.session.delete(oldest_announcement)
                flash('已刪除最舊的公告以維持最多3條公告的限制。', 'info')
        
        announcement = Announcement(
            title=request.form['title'],
            content=request.form['content'],
            priority=int(request.form['priority']),
            is_active=bool(request.form.get('is_active')),
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M') if request.form['start_date'] else datetime.utcnow(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M') if request.form['end_date'] else None
        )
        db.session.add(announcement)
        db.session.commit()
        flash('公告創建成功！', 'success')
        return redirect(url_for('announcements'))
    
    return render_template('admin/announcement_form.html')

@app.route('/admin/announcements/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    
    if request.method == 'POST':
        announcement.title = request.form['title']
        announcement.content = request.form['content']
        announcement.priority = int(request.form['priority'])
        announcement.is_active = bool(request.form.get('is_active'))
        announcement.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M') if request.form['start_date'] else datetime.utcnow()
        announcement.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M') if request.form['end_date'] else None
        announcement.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('公告更新成功！', 'success')
        return redirect(url_for('announcements'))
    
    return render_template('admin/announcement_form.html', announcement=announcement)

@app.route('/admin/announcements/<int:id>/delete', methods=['POST'])
@login_required
def delete_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    db.session.delete(announcement)
    db.session.commit()
    flash('公告刪除成功！', 'success')
    return redirect(url_for('announcements'))

# 產品管理
@app.route('/admin/products')
@login_required
def products():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    
    query = Product.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.order_by(Product.updated_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('admin/products.html', products=products, categories=categories, 
                         current_category=category_id, search=search)

@app.route('/admin/products/create', methods=['GET', 'POST'])
@login_required
def create_product():
    if request.method == 'POST':
        # 處理圖片上傳
        main_image = None
        if 'main_image' in request.files:
            file = request.files['main_image']
            if file and file.filename:
                filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'products', filename))
                main_image = f"products/{filename}"
        
        # 處理規格和變體
        specifications = {}
        variants = []
        
        # 從表單中提取規格
        for key, value in request.form.items():
            if key.startswith('spec_'):
                spec_name = key.replace('spec_', '')
                specifications[spec_name] = value
        
        # 從表單中提取變體
        variant_names = request.form.getlist('variant_name[]')
        variant_values = request.form.getlist('variant_value[]')
        for name, value in zip(variant_names, variant_values):
            if name and value:
                variants.append({'name': name, 'value': value})
        
        product = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            original_price=float(request.form['original_price']) if request.form['original_price'] else None,
            stock_quantity=int(request.form['stock_quantity']),
            category_id=int(request.form['category_id']),
            main_image=main_image,
            specifications=json.dumps(specifications, ensure_ascii=False),
            variants=json.dumps(variants, ensure_ascii=False),
            is_active=bool(request.form.get('is_active')),
            is_featured=bool(request.form.get('is_featured')),
            badge_type=request.form['badge_type'] if request.form['badge_type'] else None,
            badge_text=request.form['badge_text'] if request.form['badge_text'] else None,
            meta_title=request.form['meta_title'],
            meta_description=request.form['meta_description']
        )
        
        db.session.add(product)
        db.session.commit()
        flash('產品創建成功！', 'success')
        return redirect(url_for('products'))
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('admin/product_form.html', categories=categories)

@app.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        # 處理圖片上傳
        if 'main_image' in request.files:
            file = request.files['main_image']
            if file and file.filename:
                filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'products', filename))
                product.main_image = f"products/{filename}"
        
        # 處理規格和變體
        specifications = {}
        variants = []
        
        # 從表單中提取規格
        for key, value in request.form.items():
            if key.startswith('spec_'):
                spec_name = key.replace('spec_', '')
                specifications[spec_name] = value
        
        # 從表單中提取變體
        variant_names = request.form.getlist('variant_name[]')
        variant_values = request.form.getlist('variant_value[]')
        for name, value in zip(variant_names, variant_values):
            if name and value:
                variants.append({'name': name, 'value': value})
        
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.original_price = float(request.form['original_price']) if request.form['original_price'] else None
        product.stock_quantity = int(request.form['stock_quantity'])
        product.category_id = int(request.form['category_id'])
        product.specifications = json.dumps(specifications, ensure_ascii=False)
        product.variants = json.dumps(variants, ensure_ascii=False)
        product.is_active = bool(request.form.get('is_active'))
        product.is_featured = bool(request.form.get('is_featured'))
        product.badge_type = request.form['badge_type'] if request.form['badge_type'] else None
        product.badge_text = request.form['badge_text'] if request.form['badge_text'] else None
        product.meta_title = request.form['meta_title']
        product.meta_description = request.form['meta_description']
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('產品更新成功！', 'success')
        return redirect(url_for('products'))
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('admin/product_form.html', product=product, categories=categories)

@app.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('產品刪除成功！', 'success')
    return redirect(url_for('products'))

# 批量操作
@app.route('/admin/products/batch', methods=['POST'])
@login_required
def batch_products():
    action = request.form['action']
    product_ids = request.form.getlist('product_ids')
    
    if not product_ids:
        flash('請選擇要操作的產品！', 'error')
        return redirect(url_for('products'))
    
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    
    if action == 'delete':
        for product in products:
            db.session.delete(product)
        flash(f'成功刪除 {len(products)} 個產品！', 'success')
    
    elif action == 'activate':
        for product in products:
            product.is_active = True
        flash(f'成功啟用 {len(products)} 個產品！', 'success')
    
    elif action == 'deactivate':
        for product in products:
            product.is_active = False
        flash(f'成功停用 {len(products)} 個產品！', 'success')
    
    elif action == 'update_price':
        price_change = float(request.form['price_change'])
        change_type = request.form['change_type']
        
        for product in products:
            if change_type == 'percentage':
                product.price = product.price * (1 + price_change / 100)
            else:  # fixed amount
                product.price = product.price + price_change
            
            if product.price < 0:
                product.price = 0
        
        flash(f'成功更新 {len(products)} 個產品的價格！', 'success')
    
    elif action == 'update_stock':
        stock_change = int(request.form['stock_change'])
        change_type = request.form['change_type']
        
        for product in products:
            if change_type == 'set':
                product.stock_quantity = stock_change
            else:  # add
                product.stock_quantity = product.stock_quantity + stock_change
            
            if product.stock_quantity < 0:
                product.stock_quantity = 0
        
        flash(f'成功更新 {len(products)} 個產品的庫存！', 'success')
    
    elif action == 'update_badge':
        badge_type = request.form['badge_type']
        badge_text = request.form['badge_text']
        
        for product in products:
            product.badge_type = badge_type if badge_type else None
            product.badge_text = badge_text if badge_text else None
        
        flash(f'成功更新 {len(products)} 個產品的標籤！', 'success')
    
    db.session.commit()
    return redirect(url_for('products'))

# API 路由
@app.route('/api/announcements')
def api_announcements():
    now = datetime.utcnow()
    announcements = Announcement.query.filter(
        Announcement.is_active == True,
        Announcement.start_date <= now,
        db.or_(Announcement.end_date.is_(None), Announcement.end_date >= now)
    ).order_by(Announcement.priority.desc()).all()
    
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'content': a.content,
        'priority': a.priority
    } for a in announcements])

@app.route('/api/products')
def api_products():
    category = request.args.get('category')
    featured = request.args.get('featured', type=bool)
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        category_obj = Category.query.filter_by(slug=category).first()
        if category_obj:
            query = query.filter_by(category_id=category_obj.id)
    
    if featured:
        query = query.filter_by(is_featured=True)
    
    products = query.all()
    
    return jsonify([product.to_dict() for product in products])

@app.route('/api/products/<int:id>')
def api_product_detail(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_dict())

# 健康檢查路由
@app.route('/health')
def health_check():
    """健康檢查端點"""
    try:
        # 檢查數據庫連接
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# 初始化數據庫
def init_db():
    """初始化數據庫"""
    with app.app_context():
        db.create_all()
        
        # 創建默認管理員帳號
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin1122@@$$')
        
        admin = Admin.query.filter_by(username=admin_username).first()
        if not admin:
            admin = Admin(
                username=admin_username,
                password_hash=generate_password_hash(admin_password)
            )
            db.session.add(admin)
            print(f"已創建默認管理員帳號: {admin_username}")
        
        # 創建默認分類
        if not Category.query.first():
            categories = [
                {'name': '主機系列', 'slug': 'hosts', 'description': '頂級品質，極致體驗'},
                {'name': '煙彈系列', 'slug': 'pods', 'description': '多種口味，滿足不同需求'},
                {'name': '拋棄式系列', 'slug': 'disposable', 'description': '便攜方便，即開即用'}
            ]
            
            for cat_data in categories:
                category = Category(**cat_data)
                db.session.add(category)
            print("已創建默認產品分類")
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000) 