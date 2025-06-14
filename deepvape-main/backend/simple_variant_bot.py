#!/usr/bin/env python3
"""
簡化版變體管理機器人
專注於核心功能：價格管理（影響所有變體）和庫存管理（獨立變體）
"""

import os
import sys
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Product, Announcement, Admin, ProductVariant

# 配置日誌
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 用戶會話管理
user_sessions = {}

class SimpleVariantBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """設置命令處理器"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("login", self.login))
        self.application.add_handler(CommandHandler("logout", self.logout))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
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
                InlineKeyboardButton("📦 產品管理", callback_data="products"),
                InlineKeyboardButton("📢 公告管理", callback_data="announcements")
            ],
            [
                InlineKeyboardButton("📊 統計報告", callback_data="stats"),
                InlineKeyboardButton("👋 登出", callback_data="logout")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """開始命令"""
        user_id = update.effective_user.id
        
        if self.is_logged_in(user_id):
            await update.message.reply_text(
                "🎉 歡迎回來！",
                reply_markup=self.create_main_menu()
            )
        else:
            await update.message.reply_text(
                "👋 歡迎使用深煙電子煙管理機器人！\n\n"
                "請使用 /login 登入管理後台"
            )
    
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
        await update.message.reply_text("🔐 請輸入管理員帳號：")
    
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
            await update.message.reply_text("❌ 帳號或密碼錯誤！")
        
        # 處理價格和庫存輸入
        elif session['state'] and session['state'].startswith('edit_'):
            await self.handle_edit_input(update, session, text)
        
        else:
            await update.message.reply_text("💡 請使用按鈕操作")
    
    async def handle_edit_input(self, update, session, text):
        """處理編輯輸入"""
        try:
            if session['state'].startswith('edit_price_'):
                # 修改產品價格（影響所有變體）
                product_id = int(session['state'].split('_')[2])
                new_price = float(text)
                
                if new_price <= 0:
                    await update.message.reply_text("❌ 價格必須大於0！")
                    return
                
                with app.app_context():
                    product = Product.query.get(product_id)
                    if product:
                        old_price = product.price
                        product.price = new_price
                        db.session.commit()
                        
                        # 統計變體數量
                        variant_count = ProductVariant.query.filter_by(
                            product_id=product_id, is_active=True
                        ).count()
                        
                        await update.message.reply_text(
                            f"✅ 價格更新成功！\n"
                            f"📦 {product.name}\n"
                            f"💰 {old_price} → {new_price}\n"
                            f"🎨 影響 {variant_count} 個變體",
                            reply_markup=self.create_main_menu()
                        )
                        
                        session['state'] = None
                    else:
                        await update.message.reply_text("❌ 產品不存在！")
            
            elif session['state'].startswith('edit_variant_stock_'):
                # 修改變體庫存
                variant_id = int(session['state'].split('_')[3])
                new_stock = int(text)
                
                if new_stock < 0:
                    await update.message.reply_text("❌ 庫存不能為負數！")
                    return
                
                with app.app_context():
                    variant = ProductVariant.query.get(variant_id)
                    if variant:
                        old_stock = variant.stock_quantity
                        variant.stock_quantity = new_stock
                        db.session.commit()
                        
                        await update.message.reply_text(
                            f"✅ 變體庫存更新成功！\n"
                            f"🎨 {variant.variant_name}\n"
                            f"📦 {old_stock} → {new_stock}",
                            reply_markup=self.create_main_menu()
                        )
                        
                        session['state'] = None
                    else:
                        await update.message.reply_text("❌ 變體不存在！")
            
            elif session['state'].startswith('edit_product_stock_'):
                # 修改主產品庫存
                product_id = int(session['state'].split('_')[3])
                new_stock = int(text)
                
                if new_stock < 0:
                    await update.message.reply_text("❌ 庫存不能為負數！")
                    return
                
                with app.app_context():
                    product = Product.query.get(product_id)
                    if product:
                        old_stock = product.stock_quantity
                        product.stock_quantity = new_stock
                        db.session.commit()
                        
                        await update.message.reply_text(
                            f"✅ 主庫存更新成功！\n"
                            f"📦 {product.name}\n"
                            f"📦 {old_stock} → {new_stock}",
                            reply_markup=self.create_main_menu()
                        )
                        
                        session['state'] = None
                    else:
                        await update.message.reply_text("❌ 產品不存在！")
            
            elif session['state'].startswith('batch_stock_'):
                # 批量修改庫存
                product_id = int(session['state'].split('_')[2])
                new_stock = int(text)
                
                if new_stock < 0:
                    await update.message.reply_text("❌ 庫存不能為負數！")
                    return
                
                with app.app_context():
                    variants = ProductVariant.query.filter_by(
                        product_id=product_id, is_active=True
                    ).all()
                    
                    if variants:
                        for variant in variants:
                            variant.stock_quantity = new_stock
                        db.session.commit()
                        
                        product = Product.query.get(product_id)
                        await update.message.reply_text(
                            f"✅ 批量庫存更新成功！\n"
                            f"📦 {product.name}\n"
                            f"🎨 {len(variants)} 個變體都設為 {new_stock}",
                            reply_markup=self.create_main_menu()
                        )
                        
                        session['state'] = None
                    else:
                        await update.message.reply_text("❌ 沒有找到變體！")
                        
        except ValueError:
            await update.message.reply_text("❌ 請輸入有效的數字！")
        except Exception as e:
            await update.message.reply_text(f"❌ 操作失敗：{str(e)}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理按鈕回調"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # 檢查登入狀態
        if not self.is_logged_in(user_id) and query.data != 'logout':
            await query.edit_message_text("❌ 請先登入！使用 /login 命令")
            return
        
        if query.data == "products":
            await self.show_products(query)
        
        elif query.data == "announcements":
            await self.show_announcements(query)
        
        elif query.data == "stats":
            await self.show_stats(query)
        
        elif query.data == "logout":
            user_id = query.from_user.id
            if user_id in user_sessions:
                del user_sessions[user_id]
            await query.edit_message_text("👋 已成功登出！")
        
        elif query.data == "main_menu":
            await query.edit_message_text(
                "🏠 管理後台主選單",
                reply_markup=self.create_main_menu()
            )
        
        elif query.data.startswith("product_"):
            product_id = int(query.data.split("_")[1])
            await self.show_product_detail(query, product_id)
        
        elif query.data.startswith("edit_price_"):
            product_id = int(query.data.split("_")[2])
            await self.start_edit_price(query, product_id)
        
        elif query.data.startswith("edit_stock_"):
            product_id = int(query.data.split("_")[2])
            await self.show_stock_options(query, product_id)
        
        elif query.data.startswith("main_stock_"):
            product_id = int(query.data.split("_")[2])
            await self.start_edit_main_stock(query, product_id)
        
        elif query.data.startswith("variant_stock_"):
            variant_id = int(query.data.split("_")[2])
            await self.start_edit_variant_stock(query, variant_id)
        
        elif query.data.startswith("batch_stock_"):
            product_id = int(query.data.split("_")[2])
            await self.start_batch_stock(query, product_id)
        
        elif query.data.startswith("variants_"):
            product_id = int(query.data.split("_")[1])
            await self.show_variants(query, product_id)
    
    async def show_products(self, query):
        """顯示產品列表"""
        with app.app_context():
            products = Product.query.filter_by(is_active=True).all()
            
            if not products:
                await query.edit_message_text(
                    "📝 暫無產品",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 返回", callback_data="main_menu")
                    ]])
                )
                return
            
            text = "📦 產品列表：\n\n"
            keyboard = []
            
            for product in products:
                # 計算總庫存
                variants = ProductVariant.query.filter_by(
                    product_id=product.id, is_active=True
                ).all()
                variant_stock = sum(v.stock_quantity for v in variants)
                total_stock = product.stock_quantity + variant_stock
                
                text += f"📦 {product.name}\n"
                text += f"   💰 NT${product.price}\n"
                text += f"   📦 總庫存: {total_stock} (主:{product.stock_quantity}, 變體:{variant_stock})\n"
                text += f"   🎨 變體數: {len(variants)}\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"📝 {product.name}",
                    callback_data=f"product_{product.id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="main_menu")])
            
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
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 返回", callback_data="products")
                    ]])
                )
                return
            
            variants = ProductVariant.query.filter_by(
                product_id=product_id, is_active=True
            ).all()
            variant_stock = sum(v.stock_quantity for v in variants)
            
            text = f"📦 {product.name}\n\n"
            text += f"💰 價格: NT${product.price}\n"
            text += f"📦 主庫存: {product.stock_quantity}\n"
            text += f"🎨 變體數量: {len(variants)}\n"
            text += f"📦 變體總庫存: {variant_stock}\n"
            text += f"📊 總庫存: {product.stock_quantity + variant_stock}\n"
            
            keyboard = [
                [
                    InlineKeyboardButton("💰 修改價格", callback_data=f"edit_price_{product_id}"),
                    InlineKeyboardButton("📦 修改庫存", callback_data=f"edit_stock_{product_id}")
                ],
                [
                    InlineKeyboardButton("🎨 管理變體", callback_data=f"variants_{product_id}")
                ],
                [
                    InlineKeyboardButton("🔙 返回", callback_data="products")
                ]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def start_edit_price(self, query, product_id):
        """開始修改價格"""
        user_id = query.from_user.id
        session = self.get_user_session(user_id)
        session['state'] = f'edit_price_{product_id}'
        
        with app.app_context():
            product = Product.query.get(product_id)
            variant_count = ProductVariant.query.filter_by(
                product_id=product_id, is_active=True
            ).count()
            
            await query.edit_message_text(
                f"💰 修改 {product.name} 的價格\n\n"
                f"目前價格: NT${product.price}\n"
                f"⚠️ 注意：修改價格會影響所有 {variant_count} 個變體\n\n"
                f"請輸入新價格："
            )
    
    async def show_stock_options(self, query, product_id):
        """顯示庫存修改選項"""
        with app.app_context():
            product = Product.query.get(product_id)
            variants = ProductVariant.query.filter_by(
                product_id=product_id, is_active=True
            ).all()
            
            text = f"📦 {product.name} 庫存管理\n\n"
            text += f"主庫存: {product.stock_quantity}\n"
            text += f"變體數量: {len(variants)}\n\n"
            text += "請選擇要修改的庫存類型："
            
            keyboard = [
                [InlineKeyboardButton("📦 主庫存", callback_data=f"main_stock_{product_id}")],
                [InlineKeyboardButton("🎨 個別變體", callback_data=f"variants_{product_id}")],
                [InlineKeyboardButton("📊 批量設定變體", callback_data=f"batch_stock_{product_id}")],
                [InlineKeyboardButton("🔙 返回", callback_data=f"product_{product_id}")]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def start_edit_main_stock(self, query, product_id):
        """開始修改主庫存"""
        user_id = query.from_user.id
        session = self.get_user_session(user_id)
        session['state'] = f'edit_product_stock_{product_id}'
        
        with app.app_context():
            product = Product.query.get(product_id)
            await query.edit_message_text(
                f"📦 修改 {product.name} 的主庫存\n\n"
                f"目前主庫存: {product.stock_quantity}\n\n"
                f"請輸入新的主庫存數量："
            )
    
    async def start_batch_stock(self, query, product_id):
        """開始批量修改變體庫存"""
        user_id = query.from_user.id
        session = self.get_user_session(user_id)
        session['state'] = f'batch_stock_{product_id}'
        
        with app.app_context():
            product = Product.query.get(product_id)
            variant_count = ProductVariant.query.filter_by(
                product_id=product_id, is_active=True
            ).count()
            
            await query.edit_message_text(
                f"📊 批量設定 {product.name} 的變體庫存\n\n"
                f"變體數量: {variant_count}\n"
                f"⚠️ 注意：會將所有變體庫存設為相同數量\n\n"
                f"請輸入新的庫存數量："
            )
    
    async def show_variants(self, query, product_id):
        """顯示產品變體"""
        with app.app_context():
            product = Product.query.get(product_id)
            variants = ProductVariant.query.filter_by(
                product_id=product_id, is_active=True
            ).all()
            
            if not variants:
                await query.edit_message_text(
                    f"📦 {product.name} 暫無變體",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 返回", callback_data=f"product_{product_id}")
                    ]])
                )
                return
            
            text = f"🎨 {product.name} 的變體：\n\n"
            keyboard = []
            
            for variant in variants:
                stock_status = "⚠️" if variant.stock_quantity <= 10 else "✅"
                text += f"{stock_status} {variant.variant_name}\n"
                text += f"   📦 庫存: {variant.stock_quantity}\n"
                text += f"   💰 價格: NT${product.price + variant.price_adjustment}\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"📦 {variant.variant_name} ({variant.stock_quantity})",
                    callback_data=f"variant_stock_{variant.id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 返回", callback_data=f"edit_stock_{product_id}")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def start_edit_variant_stock(self, query, variant_id):
        """開始修改變體庫存"""
        user_id = query.from_user.id
        session = self.get_user_session(user_id)
        session['state'] = f'edit_variant_stock_{variant_id}'
        
        with app.app_context():
            variant = ProductVariant.query.get(variant_id)
            await query.edit_message_text(
                f"📦 修改 {variant.variant_name} 的庫存\n\n"
                f"目前庫存: {variant.stock_quantity}\n\n"
                f"請輸入新的庫存數量："
            )
    
    async def show_announcements(self, query):
        """顯示公告（簡化版）"""
        await query.edit_message_text(
            "📢 公告管理功能開發中...",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 返回", callback_data="main_menu")
            ]])
        )
    
    async def show_stats(self, query):
        """顯示統計"""
        with app.app_context():
            products = Product.query.all()
            variants = ProductVariant.query.filter_by(is_active=True).all()
            
            total_main_stock = sum(p.stock_quantity for p in products)
            total_variant_stock = sum(v.stock_quantity for v in variants)
            
            text = "📊 系統統計\n\n"
            text += f"📦 產品數量: {len(products)}\n"
            text += f"🎨 變體數量: {len(variants)}\n"
            text += f"📦 主庫存總量: {total_main_stock}\n"
            text += f"🎨 變體庫存總量: {total_variant_stock}\n"
            text += f"📊 總庫存: {total_main_stock + total_variant_stock}\n"
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 返回", callback_data="main_menu")
                ]])
            )
    
    def run(self):
        """運行機器人"""
        print("🤖 簡化版變體管理機器人啟動中...")
        self.application.run_polling()

def main():
    """主函數"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ 請設置環境變量 TELEGRAM_BOT_TOKEN")
        return
    
    print("🔧 初始化系統...")
    with app.app_context():
        try:
            db.create_all()
            print("✅ 數據庫初始化完成")
        except Exception as e:
            print(f"⚠️ 數據庫初始化警告: {e}")
    
    bot = SimpleVariantBot(token)
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 機器人已停止")
    except Exception as e:
        print(f"❌ 機器人運行錯誤: {e}")

if __name__ == '__main__':
    main() 