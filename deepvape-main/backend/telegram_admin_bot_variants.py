#!/usr/bin/env python3
"""
深煙電子煙 - Telegram 管理機器人 (變體管理版)
支援產品變體（口味、顏色）的獨立庫存管理
"""

import os
import sys
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Product, Announcement, Admin, ProductVariant, VariantType, VariantValue

# 配置日誌
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 用戶會話管理
user_sessions = {}

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

class VariantAdminBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """設置命令處理器"""
        # 命令處理器
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("login", self.login))
        self.application.add_handler(CommandHandler("logout", self.logout))
        
        # 回調處理器
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # 消息處理器
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def get_user_session(self, user_id):
        """獲取用戶會話"""
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                'logged_in': False,
                'username': None,
                'state': None,
                'data': {}
            }
        return user_sessions[user_id]
    
    def is_logged_in(self, user_id):
        """檢查用戶是否已登入"""
        session = self.get_user_session(user_id)
        return session.get('logged_in', False)
    
    def create_main_menu(self):
        """創建主選單"""
        keyboard = [
            [
                InlineKeyboardButton("📦 產品管理", callback_data="products_menu"),
                InlineKeyboardButton("🎨 變體管理", callback_data="variants_menu")
            ],
            [
                InlineKeyboardButton("📢 公告管理", callback_data="announcements_menu"),
                InlineKeyboardButton("📊 統計報告", callback_data="stats_menu")
            ],
            [
                InlineKeyboardButton("⚡ 快速操作", callback_data="quick_menu"),
                InlineKeyboardButton("⚙️ 系統狀態", callback_data="system_status")
            ],
            [
                InlineKeyboardButton("🔄 重新整理", callback_data="refresh_main"),
                InlineKeyboardButton("👋 登出", callback_data="logout")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_variants_menu(self):
        """創建變體管理選單"""
        keyboard = [
            [
                InlineKeyboardButton("📋 查看所有變體", callback_data="view_all_variants"),
                InlineKeyboardButton("➕ 新增變體", callback_data="add_variant")
            ],
            [
                InlineKeyboardButton("🔍 按產品查看", callback_data="variants_by_product"),
                InlineKeyboardButton("🎯 按類型查看", callback_data="variants_by_type")
            ],
            [
                InlineKeyboardButton("⚠️ 低庫存變體", callback_data="low_stock_variants"),
                InlineKeyboardButton("📊 變體統計", callback_data="variant_stats")
            ],
            [
                InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_back_button(self, callback_data="main_menu"):
        """創建返回按鈕"""
        keyboard = [[InlineKeyboardButton("🔙 返回", callback_data=callback_data)]]
        return InlineKeyboardMarkup(keyboard)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """開始命令"""
        user_id = update.effective_user.id
        
        if self.is_logged_in(user_id):
            await update.message.reply_text(
                "🎉 歡迎回來！您已經登入了。",
                reply_markup=self.create_main_menu()
            )
        else:
            await update.message.reply_text(
                "👋 歡迎使用深煙電子煙管理機器人 (變體管理版)！\n\n"
                "🔐 請先登入以使用管理功能：\n"
                "/login - 登入管理後台\n"
                "/help - 查看幫助信息"
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """幫助命令"""
        help_text = """
🤖 深煙電子煙管理機器人 (變體管理版)

📋 主要功能：
• 📦 產品管理 - 查看、編輯產品信息
• 🎨 變體管理 - 管理產品口味、顏色等變體
• 📢 公告管理 - 發佈和管理系統公告
• 📊 統計報告 - 查看庫存和銷售統計
• ⚡ 快速操作 - 批量調價、補貨等

🎯 變體功能：
• 口味管理 - 薄荷、草莓、葡萄等
• 顏色管理 - 黑色、白色、紅色等
• 獨立庫存 - 每個變體獨立管理庫存
• 價格調整 - 變體可設定價格差異

🔧 快捷命令：
/start - 開始使用
/login - 登入系統
/logout - 登出系統
/help - 顯示此幫助

💡 使用按鈕操作，無需記憶複雜命令！
"""
        await update.message.reply_text(help_text)
    
    async def login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """登入命令"""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        if session['logged_in']:
            await update.message.reply_text(
                "✅ 您已經登入了！",
                reply_markup=self.create_main_menu()
            )
            return
        
        session['state'] = 'waiting_username'
        await update.message.reply_text(
            "🔐 請輸入管理員帳號：",
            reply_markup=self.create_back_button("cancel_login")
        )
    
    async def logout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """登出命令"""
        user_id = update.effective_user.id
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        await update.message.reply_text("👋 已成功登出！")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理文字消息"""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        text = update.message.text
        
        if session['state'] == 'waiting_username':
            session['data']['username'] = text
            session['state'] = 'waiting_password'
            await update.message.reply_text("🔑 請輸入密碼：")
            
        elif session['state'] == 'waiting_password':
            username = session['data'].get('username')
            password = text
            
            # 驗證登入
            with app.app_context():
                admin = Admin.query.filter_by(username=username).first()
                if admin and admin.password_hash:
                    from werkzeug.security import check_password_hash
                    if check_password_hash(admin.password_hash, password):
                        session['logged_in'] = True
                        session['username'] = username
                        session['state'] = None
                        session['data'] = {}
                        
                        await update.message.reply_text(
                            f"✅ 登入成功！歡迎 {username}",
                            reply_markup=self.create_main_menu()
                        )
                        return
            
            # 登入失敗
            session['state'] = None
            session['data'] = {}
            await update.message.reply_text("❌ 帳號或密碼錯誤！請重新嘗試。")
        
        # 處理其他狀態的消息
        elif session['state'] and session['state'].startswith('edit_variant_'):
            await self.handle_variant_input(update, context)
        
        else:
            await update.message.reply_text(
                "💡 請使用按鈕操作或輸入 /help 查看可用命令。"
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理按鈕回調"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # 檢查登入狀態（除了登入相關操作）
        if not self.is_logged_in(user_id) and not query.data.startswith(('cancel_login', 'help')):
            await query.edit_message_text("❌ 請先登入！使用 /login 命令")
            return
        
        # 主選單操作
        if query.data == "main_menu":
            await query.edit_message_text(
                "🏠 管理後台主選單",
                reply_markup=self.create_main_menu()
            )
        
        elif query.data == "variants_menu":
            await query.edit_message_text(
                "🎨 產品變體管理選單",
                reply_markup=self.create_variants_menu()
            )
        
        elif query.data == "view_all_variants":
            await self.show_all_variants(query)
        
        elif query.data == "variants_by_product":
            await self.show_products_for_variants(query)
        
        elif query.data.startswith("product_variants_"):
            product_id = int(query.data.split("_")[2])
            await self.show_product_variants(query, product_id)
        
        elif query.data == "low_stock_variants":
            await self.show_low_stock_variants(query)
        
        elif query.data == "variant_stats":
            await self.show_variant_stats(query)
        
        elif query.data.startswith("edit_variant_"):
            variant_id = int(query.data.split("_")[2])
            await self.show_variant_edit_menu(query, variant_id)
        
        elif query.data.startswith("edit_variant_stock_"):
            variant_id = int(query.data.split("_")[3])
            await self.start_edit_variant_stock(query, variant_id)
        
        # 產品管理功能
        elif query.data == "products_menu":
            await self.show_products_menu(query)
        
        elif query.data == "view_products":
            await self.show_products_list(query)
        
        elif query.data.startswith("product_detail_"):
            product_id = int(query.data.split("_")[2])
            await self.show_product_detail(query, product_id)
        
        elif query.data.startswith("edit_product_price_"):
            product_id = int(query.data.split("_")[3])
            await self.start_edit_product_price(query, product_id)
        
        elif query.data.startswith("edit_product_stock_"):
            product_id = int(query.data.split("_")[3])
            await self.start_edit_product_stock(query, product_id)
        
        # 公告管理功能
        elif query.data == "announcements_menu":
            await self.show_announcements_menu(query)
        
        elif query.data == "view_announcements":
            await self.show_announcements_list(query)
        
        elif query.data == "add_announcement":
            await self.start_add_announcement(query)
        
        elif query.data.startswith("announcement_detail_"):
            announcement_id = int(query.data.split("_")[2])
            await self.show_announcement_detail(query, announcement_id)
        
        # 統計報告功能
        elif query.data == "stats_menu":
            await self.show_stats_report(query)
        
        # 系統狀態功能
        elif query.data == "system_status":
            await self.show_system_status(query)
        
        # 快速操作功能
        elif query.data == "quick_menu":
            await self.show_quick_operations(query)
        
        elif query.data == "batch_price_update":
            await self.start_batch_price_update(query)
        
        elif query.data == "batch_stock_update":
            await self.start_batch_stock_update(query)
        
        elif query.data == "refresh_main":
            await query.edit_message_text(
                "🔄 已重新整理",
                reply_markup=self.create_main_menu()
            )
        
        elif query.data == "logout":
            user_id = query.from_user.id
            if user_id in user_sessions:
                del user_sessions[user_id]
            await query.edit_message_text("👋 已成功登出！")
    
    async def show_all_variants(self, query):
        """顯示所有變體"""
        with app.app_context():
            variants = ProductVariant.query.join(Product).filter(ProductVariant.is_active == True).all()
            
            if not variants:
                await query.edit_message_text(
                    "📝 暫無產品變體\n\n💡 需要先為產品創建變體才能管理庫存",
                    reply_markup=self.create_back_button("variants_menu")
                )
                return
            
            text = "📋 所有產品變體：\n\n"
            for variant in variants[:20]:  # 限制顯示數量
                stock_status = "⚠️ 低庫存" if variant.is_low_stock else "✅ 充足"
                text += f"🎨 {variant.product.name} - {variant.variant_name}\n"
                text += f"   📦 庫存: {variant.stock_quantity} ({stock_status})\n"
                text += f"   💰 價格: NT${variant.final_price}\n"
                text += f"   🏷️ 類型: {variant.variant_type}\n\n"
            
            if len(variants) > 20:
                text += f"... 還有 {len(variants) - 20} 個變體"
            
            # 添加編輯按鈕
            keyboard = []
            for variant in variants[:10]:  # 只顯示前10個的編輯按鈕
                keyboard.append([InlineKeyboardButton(
                    f"✏️ {variant.variant_name}",
                    callback_data=f"edit_variant_{variant.id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="variants_menu")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def show_products_for_variants(self, query):
        """顯示有變體的產品列表"""
        with app.app_context():
            # 先嘗試找有變體的產品
            products_with_variants = db.session.query(Product).join(ProductVariant).filter(
                ProductVariant.is_active == True
            ).distinct().all()
            
            # 如果沒有變體，顯示所有產品讓用戶選擇
            if not products_with_variants:
                all_products = Product.query.filter_by(is_active=True).all()
                if not all_products:
                    await query.edit_message_text(
                        "📝 暫無可用產品",
                        reply_markup=self.create_back_button("variants_menu")
                    )
                    return
                
                text = "💡 暫無產品變體，選擇產品查看詳情：\n\n"
                keyboard = []
                for product in all_products:
                    keyboard.append([InlineKeyboardButton(
                        f"{product.name} (主庫存: {product.stock_quantity})",
                        callback_data=f"product_variants_{product.id}"
                    )])
                
                keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="variants_menu")])
                
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            # 顯示有變體的產品
            keyboard = []
            for product in products_with_variants:
                variant_count = ProductVariant.query.filter_by(
                    product_id=product.id, is_active=True
                ).count()
                button_text = f"{product.name} ({variant_count}個變體)"
                keyboard.append([InlineKeyboardButton(
                    button_text, 
                    callback_data=f"product_variants_{product.id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="variants_menu")])
            
            await query.edit_message_text(
                "🎯 選擇產品查看變體：",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def show_product_variants(self, query, product_id):
        """顯示指定產品的變體"""
        with app.app_context():
            product = Product.query.get(product_id)
            if not product:
                await query.edit_message_text(
                    "❌ 產品不存在",
                    reply_markup=self.create_back_button("variants_menu")
                )
                return
            
            variants = ProductVariant.query.filter_by(
                product_id=product_id, is_active=True
            ).all()
            
            if not variants:
                text = f"📦 {product.name}\n\n"
                text += f"💰 基礎價格: NT${product.price}\n"
                text += f"📦 主庫存: {product.stock_quantity}\n"
                text += f"📝 暫無變體\n\n"
                text += "💡 提示：可以為此產品添加不同口味或顏色的變體"
                
                await query.edit_message_text(
                    text,
                    reply_markup=self.create_back_button("variants_by_product")
                )
                return
            
            text = f"🎨 {product.name} 的變體：\n\n"
            keyboard = []
            
            for variant in variants:
                stock_status = "⚠️" if variant.is_low_stock else "✅"
                text += f"{stock_status} {variant.variant_name}\n"
                text += f"   📦 庫存: {variant.stock_quantity}\n"
                text += f"   💰 價格: NT${variant.final_price}\n"
                text += f"   🏷️ SKU: {variant.sku or 'N/A'}\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"✏️ 編輯 {variant.variant_name}",
                    callback_data=f"edit_variant_{variant.id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="variants_by_product")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def show_variant_edit_menu(self, query, variant_id):
        """顯示變體編輯選單"""
        with app.app_context():
            variant = ProductVariant.query.get(variant_id)
            if not variant:
                await query.edit_message_text(
                    "❌ 變體不存在",
                    reply_markup=self.create_back_button("variants_menu")
                )
                return
            
            text = f"✏️ 編輯變體: {variant.variant_name}\n\n"
            text += f"📦 當前庫存: {variant.stock_quantity}\n"
            text += f"💰 價格調整: NT${variant.price_adjustment}\n"
            text += f"💵 最終價格: NT${variant.final_price}\n"
            text += f"🏷️ SKU: {variant.sku or 'N/A'}\n"
            text += f"🎯 類型: {variant.variant_type}\n"
            
            keyboard = [
                [
                    InlineKeyboardButton("📦 修改庫存", callback_data=f"edit_variant_stock_{variant_id}"),
                    InlineKeyboardButton("💰 修改價格", callback_data=f"edit_variant_price_{variant_id}")
                ],
                [
                    InlineKeyboardButton("🔙 返回", callback_data=f"product_variants_{variant.product_id}")
                ]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def show_low_stock_variants(self, query):
        """顯示低庫存變體"""
        with app.app_context():
            low_stock_variants = get_low_stock_variants(threshold=10)
            
            if not low_stock_variants:
                await query.edit_message_text(
                    "✅ 所有變體庫存充足！",
                    reply_markup=self.create_back_button("variants_menu")
                )
                return
            
            text = "⚠️ 低庫存變體警告：\n\n"
            keyboard = []
            
            for variant in low_stock_variants:
                text += f"🚨 {variant.product.name} - {variant.variant_name}\n"
                text += f"   📦 剩餘: {variant.stock_quantity}\n"
                text += f"   🏷️ 類型: {variant.variant_type}\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"📦 補貨 {variant.variant_name}",
                    callback_data=f"edit_variant_stock_{variant.id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="variants_menu")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def show_variant_stats(self, query):
        """顯示變體統計"""
        with app.app_context():
            total_variants = ProductVariant.query.filter_by(is_active=True).count()
            total_stock = db.session.query(db.func.sum(ProductVariant.stock_quantity)).filter(
                ProductVariant.is_active == True
            ).scalar() or 0
            
            low_stock_count = len(get_low_stock_variants(threshold=10))
            
            # 按類型統計
            type_stats = db.session.query(
                ProductVariant.variant_type,
                db.func.count(ProductVariant.id),
                db.func.sum(ProductVariant.stock_quantity)
            ).filter(ProductVariant.is_active == True).group_by(ProductVariant.variant_type).all()
            
            text = "📊 變體統計報告：\n\n"
            text += f"🎨 總變體數量: {total_variants}\n"
            text += f"📦 總庫存量: {total_stock}\n"
            text += f"⚠️ 低庫存變體: {low_stock_count}\n\n"
            
            if type_stats:
                text += "📋 按類型統計：\n"
                for variant_type, count, stock in type_stats:
                    type_name = {
                        'flavor': '口味',
                        'color': '顏色', 
                        'size': '尺寸',
                        'strength': '濃度'
                    }.get(variant_type, variant_type)
                    text += f"• {type_name}: {count}個變體, {stock or 0}總庫存\n"
            else:
                text += "💡 暫無變體數據"
            
            await query.edit_message_text(
                text,
                reply_markup=self.create_back_button("variants_menu")
            )
    
    async def start_edit_variant_stock(self, query, variant_id):
        """開始編輯變體庫存"""
        user_id = query.from_user.id
        session = self.get_user_session(user_id)
        
        session['state'] = f'edit_variant_stock_{variant_id}'
        
        with app.app_context():
            variant = ProductVariant.query.get(variant_id)
            if variant:
                await query.edit_message_text(
                    f"📦 請輸入 {variant.variant_name} 的新庫存數量：\n"
                    f"目前庫存: {variant.stock_quantity}",
                    reply_markup=self.create_back_button("variants_menu")
                )
            else:
                await query.edit_message_text(
                    "❌ 變體不存在",
                    reply_markup=self.create_back_button("variants_menu")
                )
    
    async def handle_variant_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理變體輸入"""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        text = update.message.text
        
        if session['state'].startswith('edit_variant_stock_'):
            variant_id = int(session['state'].split('_')[3])
            
            try:
                new_stock = int(text)
                if new_stock < 0:
                    await update.message.reply_text("❌ 庫存數量不能為負數！")
                    return
                
                with app.app_context():
                    variant = ProductVariant.query.get(variant_id)
                    if variant:
                        old_stock = variant.stock_quantity
                        variant.stock_quantity = new_stock
                        db.session.commit()
                        
                        await update.message.reply_text(
                            f"✅ 庫存更新成功！\n"
                            f"📦 {variant.variant_name}\n"
                            f"🔄 {old_stock} → {new_stock}",
                            reply_markup=self.create_main_menu()
                        )
                        
                        session['state'] = None
                    else:
                        await update.message.reply_text("❌ 變體不存在！")
                        
            except ValueError:
                await update.message.reply_text("❌ 請輸入有效的數字！")
    
    # === 產品管理功能 ===
    async def show_products_menu(self, query):
        """顯示產品管理選單"""
        keyboard = [
            [
                InlineKeyboardButton("📋 查看產品列表", callback_data="view_products"),
                InlineKeyboardButton("🔍 搜尋產品", callback_data="search_products")
            ],
            [
                InlineKeyboardButton("📊 產品統計", callback_data="product_stats"),
                InlineKeyboardButton("⚠️ 低庫存產品", callback_data="low_stock_products")
            ],
            [
                InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")
            ]
        ]
        
        await query.edit_message_text(
            "📦 產品管理選單",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def show_products_list(self, query):
        """顯示產品列表"""
        with app.app_context():
            products = Product.query.filter_by(is_active=True).all()
            
            if not products:
                await query.edit_message_text(
                    "📝 暫無產品",
                    reply_markup=self.create_back_button("products_menu")
                )
                return
            
            text = "📦 產品列表：\n\n"
            keyboard = []
            
            for product in products[:15]:  # 限制顯示數量
                # 計算變體總庫存
                variant_stock = get_product_total_stock(product.id)
                total_stock = product.stock_quantity + variant_stock
                
                stock_status = "⚠️" if total_stock <= 10 else "✅"
                text += f"{stock_status} {product.name}\n"
                text += f"   💰 價格: NT${product.price}\n"
                text += f"   📦 庫存: {total_stock} (主: {product.stock_quantity}, 變體: {variant_stock})\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"📝 {product.name}",
                    callback_data=f"product_detail_{product.id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="products_menu")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def show_product_detail(self, query, product_id):
        """顯示產品詳情"""
        with app.app_context():
            product = Product.query.get(product_id)
            if not product:
                await query.edit_message_text(
                    "❌ 產品不存在",
                    reply_markup=self.create_back_button("products_menu")
                )
                return
            
            variant_count = ProductVariant.query.filter_by(
                product_id=product_id, is_active=True
            ).count()
            variant_stock = get_product_total_stock(product_id)
            
            text = f"📦 {product.name}\n\n"
            text += f"💰 價格: NT${product.price}\n"
            text += f"📦 主庫存: {product.stock_quantity}\n"
            text += f"🎨 變體數量: {variant_count}\n"
            text += f"📦 變體庫存: {variant_stock}\n"
            text += f"📊 總庫存: {product.stock_quantity + variant_stock}\n"
            text += f"🏷️ 分類: {product.category.name if product.category else 'N/A'}\n"
            text += f"📝 狀態: {'啟用' if product.is_active else '停用'}\n"
            
            keyboard = [
                [
                    InlineKeyboardButton("💰 修改價格", callback_data=f"edit_product_price_{product_id}"),
                    InlineKeyboardButton("📦 修改庫存", callback_data=f"edit_product_stock_{product_id}")
                ],
                [
                    InlineKeyboardButton("🎨 管理變體", callback_data=f"product_variants_{product_id}"),
                    InlineKeyboardButton("🔄 切換狀態", callback_data=f"toggle_product_{product_id}")
                ],
                [
                    InlineKeyboardButton("🔙 返回", callback_data="view_products")
                ]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    # === 公告管理功能 ===
    async def show_announcements_menu(self, query):
        """顯示公告管理選單"""
        keyboard = [
            [
                InlineKeyboardButton("📋 查看公告", callback_data="view_announcements"),
                InlineKeyboardButton("➕ 新增公告", callback_data="add_announcement")
            ],
            [
                InlineKeyboardButton("⚠️ 緊急公告", callback_data="urgent_announcement"),
                InlineKeyboardButton("📊 公告統計", callback_data="announcement_stats")
            ],
            [
                InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")
            ]
        ]
        
        await query.edit_message_text(
            "📢 公告管理選單",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def show_announcements_list(self, query):
        """顯示公告列表"""
        with app.app_context():
            announcements = Announcement.query.order_by(
                Announcement.priority.desc(), 
                Announcement.created_at.desc()
            ).all()
            
            if not announcements:
                await query.edit_message_text(
                    "📝 暫無公告",
                    reply_markup=self.create_back_button("announcements_menu")
                )
                return
            
            text = "📢 公告列表：\n\n"
            keyboard = []
            
            for announcement in announcements[:10]:
                priority_icon = {1: "🔵", 2: "🟡", 3: "🔴"}.get(announcement.priority, "⚫")
                status_icon = "✅" if announcement.is_active else "❌"
                
                text += f"{priority_icon} {status_icon} {announcement.title}\n"
                text += f"   📅 {announcement.created_at.strftime('%m-%d %H:%M')}\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"📝 {announcement.title[:20]}...",
                    callback_data=f"announcement_detail_{announcement.id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="announcements_menu")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    # === 統計報告功能 ===
    async def show_stats_report(self, query):
        """顯示統計報告"""
        with app.app_context():
            # 產品統計
            total_products = Product.query.count()
            active_products = Product.query.filter_by(is_active=True).count()
            
            # 庫存統計
            products = Product.query.all()
            total_main_stock = sum(p.stock_quantity for p in products)
            
            total_variant_stock = db.session.query(db.func.sum(ProductVariant.stock_quantity)).filter(
                ProductVariant.is_active == True
            ).scalar() or 0
            
            # 變體統計
            total_variants = ProductVariant.query.filter_by(is_active=True).count()
            low_stock_variants = len(get_low_stock_variants(threshold=10))
            
            # 公告統計
            total_announcements = Announcement.query.count()
            active_announcements = Announcement.query.filter_by(is_active=True).count()
            
            text = "📊 系統統計報告\n\n"
            text += f"📦 產品統計：\n"
            text += f"  • 總產品數: {total_products}\n"
            text += f"  • 啟用產品: {active_products}\n"
            text += f"  • 主庫存總量: {total_main_stock}\n\n"
            
            text += f"🎨 變體統計：\n"
            text += f"  • 總變體數: {total_variants}\n"
            text += f"  • 變體庫存: {total_variant_stock}\n"
            text += f"  • 低庫存變體: {low_stock_variants}\n\n"
            
            text += f"📢 公告統計：\n"
            text += f"  • 總公告數: {total_announcements}\n"
            text += f"  • 活躍公告: {active_announcements}\n\n"
            
            text += f"📊 總庫存量: {total_main_stock + total_variant_stock}\n"
            
            await query.edit_message_text(
                text,
                reply_markup=self.create_back_button("main_menu")
            )
    
    # === 系統狀態功能 ===
    async def show_system_status(self, query):
        """顯示系統狀態"""
        with app.app_context():
            try:
                # 檢查數據庫連接
                total_products = Product.query.count()
                
                text = "⚙️ 系統狀態檢查\n\n"
                text += f"🟢 數據庫連接: 正常\n"
                text += f"🟢 產品數據: {total_products} 個產品\n"
                text += f"🟢 變體系統: 運行正常\n"
                text += f"🟢 機器人狀態: 在線\n"
                text += f"⏰ 檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                
            except Exception as e:
                text = "⚙️ 系統狀態檢查\n\n"
                text += f"🔴 系統錯誤: {str(e)}\n"
            
            await query.edit_message_text(
                text,
                reply_markup=self.create_back_button("main_menu")
            )
    
    # === 快速操作功能 ===
    async def show_quick_operations(self, query):
        """顯示快速操作選單"""
        keyboard = [
            [
                InlineKeyboardButton("📊 批量調價", callback_data="batch_price_update"),
                InlineKeyboardButton("📦 批量補貨", callback_data="batch_stock_update")
            ],
            [
                InlineKeyboardButton("⚠️ 低庫存檢查", callback_data="low_stock_variants"),
                InlineKeyboardButton("🚨 緊急公告", callback_data="urgent_announcement")
            ],
            [
                InlineKeyboardButton("📈 今日統計", callback_data="stats_menu"),
                InlineKeyboardButton("🔄 系統檢查", callback_data="system_status")
            ],
            [
                InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")
            ]
        ]
        
        await query.edit_message_text(
            "⚡ 快速操作中心",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    def run(self):
        """運行機器人"""
        print("🤖 Telegram 變體管理機器人啟動中...")
        self.application.run_polling()

def main():
    """主函數"""
    # 獲取 Bot Token
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ 請設置環境變量 TELEGRAM_BOT_TOKEN")
        return
    
    # 初始化變體系統
    print("🔧 初始化變體系統...")
    with app.app_context():
        try:
            init_variant_system()
            print("✅ 變體系統初始化完成")
        except Exception as e:
            print(f"⚠️  變體系統初始化警告: {e}")
    
    # 啟動機器人
    bot = VariantAdminBot(token)
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 機器人已停止")
    except Exception as e:
        print(f"❌ 機器人運行錯誤: {e}")

if __name__ == '__main__':
    main() 