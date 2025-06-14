#!/usr/bin/env python3
"""
Deepvape Telegram 管理機器人
提供產品價格、庫存和公告的遠端管理功能
"""

import os
import json
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from app import app, db, Product, Category, Announcement, Admin
from werkzeug.security import check_password_hash

# 配置
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_CHAT_IDS = os.environ.get('ADMIN_CHAT_IDS', '').split(',')  # 允許使用機器人的管理員ID

# 用戶會話狀態
user_sessions = {}

class AdminBot:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """設置命令處理器"""
        # 基本命令
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("login", self.login))
        self.app.add_handler(CommandHandler("logout", self.logout))
        self.app.add_handler(CommandHandler("status", self.status))
        
        # 管理命令
        self.app.add_handler(CommandHandler("products", self.list_products))
        self.app.add_handler(CommandHandler("announcements", self.list_announcements))
        self.app.add_handler(CommandHandler("stats", self.show_stats))
        
        # 回調處理
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # 文本消息處理
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """開始命令"""
        user_id = update.effective_user.id
        
        # 檢查是否已登入
        if user_id in user_sessions and user_sessions[user_id].get('logged_in'):
            await self.show_main_menu(update)
            return
        
        welcome_text = """
🎯 **Deepvape 管理機器人**

歡迎使用 Deepvape 後台管理機器人！

📋 **可用功能：**
• 產品價格管理
• 庫存數量管理  
• 網站公告管理
• 系統狀態查詢

⚠️ 只有授權的管理員才能使用此機器人。
        """
        
        # 創建登入按鈕
        keyboard = [
            [InlineKeyboardButton("🔐 管理員登入", callback_data="start_login")],
            [InlineKeyboardButton("📚 使用說明", callback_data="show_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_main_menu(self, update):
        """顯示主選單"""
        username = user_sessions.get(update.effective_user.id, {}).get('username', '管理員')
        
        menu_text = f"""
🎯 **Deepvape 管理中心**

歡迎回來，{username}！

請選擇您要執行的操作：
        """
        
        # 創建主選單按鈕
        keyboard = [
            [
                InlineKeyboardButton("📦 產品管理", callback_data="menu_products"),
                InlineKeyboardButton("📢 公告管理", callback_data="menu_announcements")
            ],
            [
                InlineKeyboardButton("📊 統計報告", callback_data="menu_stats"),
                InlineKeyboardButton("⚙️ 系統狀態", callback_data="menu_status")
            ],
            [
                InlineKeyboardButton("⚡ 快速操作", callback_data="menu_quick"),
                InlineKeyboardButton("📚 使用說明", callback_data="show_help")
            ],
            [
                InlineKeyboardButton("🔄 重新整理", callback_data="refresh_menu"),
                InlineKeyboardButton("👋 登出", callback_data="logout_confirm")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            # 如果是callback query
            await update.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """幫助命令"""
        help_text = """
📚 **Deepvape 管理機器人命令列表**

🔐 **認證命令：**
`/login` - 登入管理帳號
`/logout` - 登出當前會話

📊 **查詢命令：**
`/status` - 系統狀態
`/stats` - 統計數據
`/products` - 產品列表
`/announcements` - 公告列表

⚡ **快速操作：**
• 點擊產品可直接修改價格/庫存
• 點擊公告可直接編輯內容
• 支持批量價格調整

💡 **使用技巧：**
• 所有操作都有確認步驟
• 支持撤銷最近的操作
• 可以設定價格變動通知

需要幫助請聯繫系統管理員。
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """登入命令"""
        user_id = update.effective_user.id
        
        # 檢查是否已登入
        if user_id in user_sessions and user_sessions[user_id].get('logged_in'):
            await update.message.reply_text("✅ 您已經登入了！")
            return
        
        # 初始化會話
        user_sessions[user_id] = {'state': 'waiting_username'}
        
        await update.message.reply_text(
            "🔐 **管理員登入**\n\n請輸入您的用戶名：",
            parse_mode='Markdown'
        )
    
    async def logout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """登出命令"""
        user_id = update.effective_user.id
        
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        await update.message.reply_text("👋 已成功登出！")
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """系統狀態"""
        if not await self.check_auth(update):
            return
        
        with app.app_context():
            try:
                # 檢查數據庫連接
                total_products = Product.query.count()
                active_products = Product.query.filter_by(is_active=True).count()
                total_announcements = Announcement.query.count()
                active_announcements = Announcement.query.filter_by(is_active=True).count()
                
                status_text = f"""
🟢 **系統狀態：正常運行**

📊 **數據統計：**
• 總產品數：{total_products}
• 啟用產品：{active_products}
• 總公告數：{total_announcements}
• 活躍公告：{active_announcements}

⏰ **檢查時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🌐 **後台地址：** http://192.168.2.16:5001
                """
                
                await update.message.reply_text(status_text, parse_mode='Markdown')
                
            except Exception as e:
                await update.message.reply_text(f"❌ 系統錯誤：{str(e)}")
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """顯示詳細統計"""
        if not await self.check_auth(update):
            return
        
        with app.app_context():
            try:
                # 統計數據
                products = Product.query.all()
                categories = Category.query.all()
                announcements = Announcement.query.all()
                
                # 計算庫存統計
                total_stock = sum(p.stock_quantity for p in products)
                low_stock_products = [p for p in products if p.stock_quantity < 10]
                
                # 價格統計
                if products:
                    avg_price = sum(p.price for p in products) / len(products)
                    max_price = max(p.price for p in products)
                    min_price = min(p.price for p in products)
                else:
                    avg_price = max_price = min_price = 0
                
                stats_text = f"""
📊 **詳細統計報告**

🛍️ **產品統計：**
• 總產品數：{len(products)}
• 啟用產品：{len([p for p in products if p.is_active])}
• 產品分類：{len(categories)}
• 總庫存量：{total_stock}
• 低庫存產品：{len(low_stock_products)}

💰 **價格統計：**
• 平均價格：NT$ {avg_price:.0f}
• 最高價格：NT$ {max_price:.0f}
• 最低價格：NT$ {min_price:.0f}

📢 **公告統計：**
• 總公告數：{len(announcements)}
• 活躍公告：{len([a for a in announcements if a.is_active])}

⚠️ **需要注意：**
{f"• {len(low_stock_products)} 個產品庫存不足" if low_stock_products else "• 所有產品庫存充足"}
                """
                
                await update.message.reply_text(stats_text, parse_mode='Markdown')
                
                # 如果有低庫存產品，顯示詳情
                if low_stock_products:
                    low_stock_text = "🔴 **低庫存產品：**\n\n"
                    for product in low_stock_products[:5]:  # 只顯示前5個
                        low_stock_text += f"• {product.name}：{product.stock_quantity} 件\n"
                    
                    if len(low_stock_products) > 5:
                        low_stock_text += f"\n... 還有 {len(low_stock_products) - 5} 個產品"
                    
                    await update.message.reply_text(low_stock_text, parse_mode='Markdown')
                
            except Exception as e:
                await update.message.reply_text(f"❌ 獲取統計數據失敗：{str(e)}")
    
    async def list_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """列出產品"""
        if not await self.check_auth(update):
            return
        
        with app.app_context():
            try:
                products = Product.query.order_by(Product.name).all()
                
                if not products:
                    await update.message.reply_text("📦 目前沒有產品")
                    return
                
                # 創建產品列表按鈕
                keyboard = []
                for product in products[:20]:  # 限制顯示數量
                    status_icon = "✅" if product.is_active else "❌"
                    stock_icon = "🔴" if product.stock_quantity < 10 else "🟢"
                    
                    button_text = f"{status_icon}{stock_icon} {product.name} - NT${product.price:.0f} ({product.stock_quantity})"
                    keyboard.append([InlineKeyboardButton(
                        button_text, 
                        callback_data=f"product_{product.id}"
                    )])
                
                # 添加管理按鈕
                keyboard.append([
                    InlineKeyboardButton("📊 批量調價", callback_data="batch_price"),
                    InlineKeyboardButton("📦 批量補貨", callback_data="batch_stock")
                ])
                keyboard.append([
                    InlineKeyboardButton("🔙 返回主選單", callback_data="back_to_menu")
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                product_text = f"""
📦 **產品管理** ({len(products)} 個產品)

點擊產品可進行編輯：
✅❌ = 啟用/停用狀態
🟢🔴 = 庫存狀態 (🔴 < 10件)

格式：狀態 產品名 - 價格 (庫存)
                """
                
                await update.message.reply_text(
                    product_text, 
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
            except Exception as e:
                await update.message.reply_text(f"❌ 獲取產品列表失敗：{str(e)}")
    
    async def list_announcements(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """列出公告"""
        if not await self.check_auth(update):
            return
        
        with app.app_context():
            try:
                announcements = Announcement.query.order_by(
                    Announcement.priority.desc(), 
                    Announcement.created_at.desc()
                ).all()
                
                if not announcements:
                    keyboard = [
                        [
                            InlineKeyboardButton("➕ 新增公告", callback_data="new_announcement"),
                            InlineKeyboardButton("⚠️ 緊急公告", callback_data="urgent_announcement")
                        ],
                        [InlineKeyboardButton("🔙 返回主選單", callback_data="back_to_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        "📢 目前沒有公告",
                        reply_markup=reply_markup
                    )
                    return
                
                # 創建公告列表按鈕
                keyboard = []
                for announcement in announcements[:10]:  # 限制顯示數量
                    status_icon = "✅" if announcement.is_active else "❌"
                    priority_icon = "🔴" if announcement.priority == 3 else "🟡" if announcement.priority == 2 else "🟢"
                    
                    button_text = f"{status_icon}{priority_icon} {announcement.title[:20]}..."
                    keyboard.append([InlineKeyboardButton(
                        button_text, 
                        callback_data=f"announcement_{announcement.id}"
                    )])
                
                # 添加管理按鈕
                keyboard.append([
                    InlineKeyboardButton("➕ 新增公告", callback_data="new_announcement"),
                    InlineKeyboardButton("⚠️ 緊急公告", callback_data="urgent_announcement")
                ])
                keyboard.append([
                    InlineKeyboardButton("🔙 返回主選單", callback_data="back_to_menu")
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                announcement_text = f"""
📢 **公告管理** ({len(announcements)} 個公告)

點擊公告可進行編輯：
✅❌ = 啟用/停用狀態
🔴🟡🟢 = 優先級 (高/中/低)
                """
                
                await update.message.reply_text(
                    announcement_text, 
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
            except Exception as e:
                await update.message.reply_text(f"❌ 獲取公告列表失敗：{str(e)}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理回調查詢"""
        query = update.callback_query
        await query.answer()
        
        if not await self.check_auth(update):
            return
        
        data = query.data
        
        # 主選單項目
        if data == "start_login":
            await self.handle_start_login(query)
        elif data == "show_help":
            await self.handle_show_help(query)
        elif data == "menu_products":
            await self.handle_menu_products(query)
        elif data == "menu_announcements":
            await self.handle_menu_announcements(query)
        elif data == "menu_stats":
            await self.handle_menu_stats(query)
        elif data == "menu_status":
            await self.handle_menu_status(query)
        elif data == "menu_quick":
            await self.handle_menu_quick(query)
        elif data == "refresh_menu":
            await self.show_main_menu(query)
        elif data == "logout_confirm":
            await self.handle_logout_confirm(query)
        elif data == "back_to_menu":
            await self.show_main_menu(query)
        elif data == "confirm_logout":
            await self.handle_confirm_logout(query)
        elif data == "check_low_stock":
            await self.handle_check_low_stock(query)
        elif data == "urgent_announcement":
            await self.handle_urgent_announcement(query)
        
        # 產品和公告操作
        elif data.startswith("product_"):
            await self.handle_product_callback(query, data)
        elif data.startswith("announcement_"):
            await self.handle_announcement_callback(query, data)
        elif data.startswith("batch_"):
            await self.handle_batch_callback(query, data)
        elif data == "new_announcement":
            await self.handle_new_announcement(query)
        elif data.startswith("edit_price_"):
            await self.handle_edit_price_callback(query, data)
        elif data.startswith("edit_stock_"):
            await self.handle_edit_stock_callback(query, data)
        elif data.startswith("toggle_active_"):
            await self.handle_toggle_active_callback(query, data)
        elif data.startswith("edit_announcement_content_"):
            await self.handle_edit_announcement_content_callback(query, data)
        elif data.startswith("toggle_announcement_"):
            await self.handle_toggle_announcement_callback(query, data)
        elif data.startswith("delete_announcement_"):
            await self.handle_delete_announcement_callback(query, data)
        elif data == "back_to_products":
            await self.list_products_callback(query)
        elif data == "back_to_announcements":
            await self.list_announcements_callback(query)
    
    async def handle_product_callback(self, query, data):
        """處理產品回調"""
        product_id = int(data.split("_")[1])
        
        with app.app_context():
            try:
                product = Product.query.get(product_id)
                if not product:
                    await query.edit_message_text("❌ 產品不存在")
                    return
                
                # 創建產品操作按鈕
                keyboard = [
                    [
                        InlineKeyboardButton("💰 修改價格", callback_data=f"edit_price_{product_id}"),
                        InlineKeyboardButton("📦 修改庫存", callback_data=f"edit_stock_{product_id}")
                    ],
                    [
                        InlineKeyboardButton("✅ 啟用" if not product.is_active else "❌ 停用", 
                                           callback_data=f"toggle_active_{product_id}"),
                        InlineKeyboardButton("🏷️ 修改標籤", callback_data=f"edit_badge_{product_id}")
                    ],
                    [InlineKeyboardButton("🔙 返回列表", callback_data="back_to_products")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                product_text = f"""
📦 **產品詳情**

**名稱：** {product.name}
**價格：** NT$ {product.price:.0f}
**原價：** NT$ {product.original_price:.0f if product.original_price else product.price:.0f}
**庫存：** {product.stock_quantity} 件
**分類：** {product.category.name if product.category else '未分類'}
**狀態：** {'✅ 啟用' if product.is_active else '❌ 停用'}
**標籤：** {product.badge_text or '無'}
**描述：** {product.description[:100] if product.description else '無'}...

選擇要執行的操作：
                """
                
                await query.edit_message_text(
                    product_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
            except Exception as e:
                await query.edit_message_text(f"❌ 獲取產品詳情失敗：{str(e)}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理文本消息"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in user_sessions:
            await update.message.reply_text("請先使用 /login 命令登入")
            return
        
        session = user_sessions[user_id]
        state = session.get('state')
        
        if state == 'waiting_username':
            session['username'] = text
            session['state'] = 'waiting_password'
            await update.message.reply_text("🔑 請輸入密碼：")
            
        elif state == 'waiting_password':
            await self.verify_login(update, session['username'], text, user_id)
            
        elif state and state.startswith('edit_'):
            await self.handle_edit_input(update, state, text, user_id)
    
    async def handle_edit_input(self, update, state, text, user_id):
        """處理編輯輸入"""
        session = user_sessions[user_id]
        
        try:
            if state.startswith('edit_price_'):
                product_id = int(state.split('_')[2])
                new_price = float(text)
                
                with app.app_context():
                    product = Product.query.get(product_id)
                    if product:
                        old_price = product.price
                        product.price = new_price
                        product.updated_at = datetime.now()
                        db.session.commit()
                        
                        await update.message.reply_text(
                            f"✅ **價格更新成功！**\n\n"
                            f"產品：{product.name}\n"
                            f"原價格：NT$ {old_price:.0f}\n"
                            f"新價格：NT$ {new_price:.0f}\n"
                            f"變動：{((new_price - old_price) / old_price * 100):+.1f}%",
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text("❌ 產品不存在")
            
            elif state.startswith('edit_stock_'):
                product_id = int(state.split('_')[2])
                new_stock = int(text)
                
                with app.app_context():
                    product = Product.query.get(product_id)
                    if product:
                        old_stock = product.stock_quantity
                        product.stock_quantity = new_stock
                        product.updated_at = datetime.now()
                        db.session.commit()
                        
                        await update.message.reply_text(
                            f"✅ **庫存更新成功！**\n\n"
                            f"產品：{product.name}\n"
                            f"原庫存：{old_stock} 件\n"
                            f"新庫存：{new_stock} 件\n"
                            f"變動：{new_stock - old_stock:+d} 件",
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text("❌ 產品不存在")
            
            elif state.startswith('edit_announcement_'):
                announcement_id = int(state.split('_')[2])
                
                with app.app_context():
                    announcement = Announcement.query.get(announcement_id)
                    if announcement:
                        announcement.content = text
                        announcement.updated_at = datetime.now()
                        db.session.commit()
                        
                        await update.message.reply_text(
                            f"✅ **公告更新成功！**\n\n"
                            f"標題：{announcement.title}\n"
                            f"新內容：{text[:100]}...",
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text("❌ 公告不存在")
            
            elif state == 'new_announcement_title':
                session['new_announcement_title'] = text
                session['state'] = 'new_announcement_content'
                await update.message.reply_text("📝 請輸入公告內容：")
                return
            
            elif state == 'new_announcement_content':
                title = session.get('new_announcement_title')
                
                with app.app_context():
                    announcement = Announcement(
                        title=title,
                        content=text,
                        priority=2,  # 默認中等優先級
                        is_active=True
                    )
                    db.session.add(announcement)
                    db.session.commit()
                    
                    await update.message.reply_text(
                        f"✅ **公告創建成功！**\n\n"
                        f"標題：{title}\n"
                        f"內容：{text[:100]}...\n"
                        f"狀態：已啟用",
                        parse_mode='Markdown'
                    )
            
            elif state == 'urgent_announcement_title':
                session['urgent_announcement_title'] = text
                session['state'] = 'urgent_announcement_content'
                await update.message.reply_text("📝 請輸入緊急公告內容：")
                return
            
            elif state == 'urgent_announcement_content':
                title = session.get('urgent_announcement_title')
                
                with app.app_context():
                    announcement = Announcement(
                        title=title,
                        content=text,
                        priority=3,  # 高優先級
                        is_active=True
                    )
                    db.session.add(announcement)
                    db.session.commit()
                    
                    await update.message.reply_text(
                        f"⚠️ **緊急公告發布成功！**\n\n"
                        f"標題：{title}\n"
                        f"內容：{text[:100]}...\n"
                        f"優先級：🔴 高\n"
                        f"狀態：已啟用\n\n"
                        f"公告已在網站首頁顯示！",
                        parse_mode='Markdown'
                    )
            
            elif state == 'batch_price_input':
                percentage = float(text)
                
                with app.app_context():
                    products = Product.query.filter_by(is_active=True).all()
                    updated_count = 0
                    
                    for product in products:
                        old_price = product.price
                        product.price = old_price * (1 + percentage / 100)
                        product.updated_at = datetime.now()
                        updated_count += 1
                    
                    db.session.commit()
                    
                    await update.message.reply_text(
                        f"✅ **批量調價完成！**\n\n"
                        f"調整幅度：{percentage:+.1f}%\n"
                        f"更新產品：{updated_count} 個\n"
                        f"操作時間：{datetime.now().strftime('%H:%M:%S')}",
                        parse_mode='Markdown'
                    )
            
        except ValueError:
            await update.message.reply_text("❌ 輸入格式錯誤，請輸入有效的數字")
        except Exception as e:
            await update.message.reply_text(f"❌ 操作失敗：{str(e)}")
        
        # 清除會話狀態
        if user_id in user_sessions:
            user_sessions[user_id]['state'] = None
    
    async def handle_announcement_callback(self, query, data):
        """處理公告回調"""
        announcement_id = int(data.split("_")[1])
        
        with app.app_context():
            try:
                announcement = Announcement.query.get(announcement_id)
                if not announcement:
                    await query.edit_message_text("❌ 公告不存在")
                    return
                
                # 創建公告操作按鈕
                keyboard = [
                    [
                        InlineKeyboardButton("📝 編輯內容", callback_data=f"edit_announcement_content_{announcement_id}"),
                        InlineKeyboardButton("🏷️ 編輯標題", callback_data=f"edit_announcement_title_{announcement_id}")
                    ],
                    [
                        InlineKeyboardButton("✅ 啟用" if not announcement.is_active else "❌ 停用", 
                                           callback_data=f"toggle_announcement_{announcement_id}"),
                        InlineKeyboardButton("🔴 高優先級" if announcement.priority != 3 else "🟡 中優先級", 
                                           callback_data=f"toggle_priority_{announcement_id}")
                    ],
                    [InlineKeyboardButton("🗑️ 刪除公告", callback_data=f"delete_announcement_{announcement_id}")],
                    [InlineKeyboardButton("🔙 返回列表", callback_data="back_to_announcements")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                announcement_text = f"""
📢 **公告詳情**

**標題：** {announcement.title}
**內容：** {announcement.content[:200]}{'...' if len(announcement.content) > 200 else ''}
**狀態：** {'✅ 啟用' if announcement.is_active else '❌ 停用'}
**優先級：** {'🔴 高' if announcement.priority == 3 else '🟡 中' if announcement.priority == 2 else '🟢 低'}
**創建時間：** {announcement.created_at.strftime('%Y-%m-%d %H:%M')}
**更新時間：** {announcement.updated_at.strftime('%Y-%m-%d %H:%M') if announcement.updated_at else '未更新'}

選擇要執行的操作：
                """
                
                await query.edit_message_text(
                    announcement_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
            except Exception as e:
                await query.edit_message_text(f"❌ 獲取公告詳情失敗：{str(e)}")
    
    async def handle_batch_callback(self, query, data):
        """處理批量操作回調"""
        user_id = query.from_user.id
        
        if data == "batch_price":
            user_sessions[user_id]['state'] = 'batch_price_input'
            await query.edit_message_text(
                "📊 **批量調價**\n\n"
                "請輸入價格調整百分比：\n"
                "• 正數表示漲價（如：10 表示漲價10%）\n"
                "• 負數表示降價（如：-5 表示降價5%）\n\n"
                "範例：輸入 `15` 表示所有產品漲價15%",
                parse_mode='Markdown'
            )
        
        elif data == "batch_stock":
            with app.app_context():
                try:
                    low_stock_products = Product.query.filter(Product.stock_quantity < 10).all()
                    
                    if not low_stock_products:
                        await query.edit_message_text("✅ 所有產品庫存充足！")
                        return
                    
                    # 自動補貨到20件
                    updated_count = 0
                    for product in low_stock_products:
                        product.stock_quantity = 20
                        product.updated_at = datetime.now()
                        updated_count += 1
                    
                    db.session.commit()
                    
                    await query.edit_message_text(
                        f"✅ **批量補貨完成！**\n\n"
                        f"補貨產品：{updated_count} 個\n"
                        f"補貨至：20 件\n"
                        f"操作時間：{datetime.now().strftime('%H:%M:%S')}",
                        parse_mode='Markdown'
                    )
                    
                except Exception as e:
                    await query.edit_message_text(f"❌ 批量補貨失敗：{str(e)}")
    
    async def handle_new_announcement(self, query):
        """處理新增公告"""
        user_id = query.from_user.id
        user_sessions[user_id]['state'] = 'new_announcement_title'
        
        await query.edit_message_text(
            "📢 **新增公告**\n\n"
            "請輸入公告標題：",
            parse_mode='Markdown'
        )
    
    async def handle_edit_price_callback(self, query, data):
        """處理編輯價格回調"""
        product_id = int(data.split("_")[2])
        user_id = query.from_user.id
        user_sessions[user_id]['state'] = f'edit_price_{product_id}'
        
        with app.app_context():
            product = Product.query.get(product_id)
            if product:
                await query.edit_message_text(
                    f"💰 **修改價格**\n\n"
                    f"產品：{product.name}\n"
                    f"目前價格：NT$ {product.price:.0f}\n\n"
                    f"請輸入新價格（只需輸入數字）：",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ 產品不存在")
    
    async def handle_edit_stock_callback(self, query, data):
        """處理編輯庫存回調"""
        product_id = int(data.split("_")[2])
        user_id = query.from_user.id
        user_sessions[user_id]['state'] = f'edit_stock_{product_id}'
        
        with app.app_context():
            product = Product.query.get(product_id)
            if product:
                await query.edit_message_text(
                    f"📦 **修改庫存**\n\n"
                    f"產品：{product.name}\n"
                    f"目前庫存：{product.stock_quantity} 件\n\n"
                    f"請輸入新庫存數量（只需輸入數字）：",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ 產品不存在")
    
    async def handle_toggle_active_callback(self, query, data):
        """處理切換產品狀態回調"""
        product_id = int(data.split("_")[2])
        
        with app.app_context():
            try:
                product = Product.query.get(product_id)
                if product:
                    product.is_active = not product.is_active
                    product.updated_at = datetime.now()
                    db.session.commit()
                    
                    status = "啟用" if product.is_active else "停用"
                    await query.edit_message_text(
                        f"✅ **狀態更新成功！**\n\n"
                        f"產品：{product.name}\n"
                        f"新狀態：{status}\n"
                        f"更新時間：{datetime.now().strftime('%H:%M:%S')}",
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text("❌ 產品不存在")
            except Exception as e:
                await query.edit_message_text(f"❌ 更新失敗：{str(e)}")
    
    async def handle_edit_announcement_content_callback(self, query, data):
        """處理編輯公告內容回調"""
        announcement_id = int(data.split("_")[3])
        user_id = query.from_user.id
        user_sessions[user_id]['state'] = f'edit_announcement_{announcement_id}'
        
        with app.app_context():
            announcement = Announcement.query.get(announcement_id)
            if announcement:
                await query.edit_message_text(
                    f"📝 **編輯公告內容**\n\n"
                    f"標題：{announcement.title}\n"
                    f"目前內容：{announcement.content[:200]}...\n\n"
                    f"請輸入新的公告內容：",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ 公告不存在")
    
    async def handle_toggle_announcement_callback(self, query, data):
        """處理切換公告狀態回調"""
        announcement_id = int(data.split("_")[2])
        
        with app.app_context():
            try:
                announcement = Announcement.query.get(announcement_id)
                if announcement:
                    announcement.is_active = not announcement.is_active
                    announcement.updated_at = datetime.now()
                    db.session.commit()
                    
                    status = "啟用" if announcement.is_active else "停用"
                    await query.edit_message_text(
                        f"✅ **公告狀態更新成功！**\n\n"
                        f"標題：{announcement.title}\n"
                        f"新狀態：{status}\n"
                        f"更新時間：{datetime.now().strftime('%H:%M:%S')}",
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text("❌ 公告不存在")
            except Exception as e:
                await query.edit_message_text(f"❌ 更新失敗：{str(e)}")
    
    async def handle_delete_announcement_callback(self, query, data):
        """處理刪除公告回調"""
        announcement_id = int(data.split("_")[2])
        
        # 創建確認按鈕
        keyboard = [
            [
                InlineKeyboardButton("✅ 確認刪除", callback_data=f"confirm_delete_{announcement_id}"),
                InlineKeyboardButton("❌ 取消", callback_data="back_to_announcements")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        with app.app_context():
            announcement = Announcement.query.get(announcement_id)
            if announcement:
                await query.edit_message_text(
                    f"⚠️ **確認刪除公告**\n\n"
                    f"標題：{announcement.title}\n"
                    f"內容：{announcement.content[:100]}...\n\n"
                    f"**此操作無法撤銷！**",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ 公告不存在")
    
    async def list_products_callback(self, query):
        """返回產品列表回調"""
        # 模擬update對象
        class MockUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        mock_update = MockUpdate(query)
        await self.list_products(mock_update, None)
    
    async def list_announcements_callback(self, query):
        """返回公告列表回調"""
        # 模擬update對象
        class MockUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        mock_update = MockUpdate(query)
        await self.list_announcements(mock_update, None)
    
    async def handle_start_login(self, query):
        """處理開始登入"""
        user_id = query.from_user.id
        user_sessions[user_id] = {'state': 'waiting_username'}
        
        await query.edit_message_text(
            "🔐 **管理員登入**\n\n請輸入您的用戶名：",
            parse_mode='Markdown'
        )
    
    async def handle_show_help(self, query):
        """顯示使用說明"""
        help_text = """
📚 **Deepvape 管理機器人使用說明**

🎯 **主要功能**：
• **📦 產品管理** - 查看、修改產品價格和庫存
• **📢 公告管理** - 新增、編輯、刪除網站公告
• **📊 統計報告** - 查看詳細的營運數據
• **⚙️ 系統狀態** - 監控系統運行狀況

⚡ **快速操作技巧**：
• 點擊產品可直接修改價格/庫存
• 支援批量調價和補貨功能
• 可設定公告優先級和時效
• 即時同步所有數據變更

🔐 **安全機制**：
• 需要管理員帳號密碼驗證
• 重要操作都有確認步驟
• 支援多人同時使用
• 自動記錄操作時間

💡 **使用建議**：
• 定期查看統計報告了解營運狀況
• 設定低庫存警告避免斷貨
• 使用批量功能提高效率
• 重要公告設為高優先級

需要協助請聯繫技術支援團隊。
        """
        
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_menu_products(self, query):
        """處理產品管理選單"""
        if not await self.check_auth_query(query):
            return
        
        # 重用現有的產品列表功能
        await self.list_products_callback(query)
    
    async def handle_menu_announcements(self, query):
        """處理公告管理選單"""
        if not await self.check_auth_query(query):
            return
        
        # 重用現有的公告列表功能
        await self.list_announcements_callback(query)
    
    async def handle_menu_stats(self, query):
        """處理統計報告選單"""
        if not await self.check_auth_query(query):
            return
        
        # 重用現有的統計功能
        class MockUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        mock_update = MockUpdate(query)
        await self.show_stats(mock_update, None)
    
    async def handle_menu_status(self, query):
        """處理系統狀態選單"""
        if not await self.check_auth_query(query):
            return
        
        # 重用現有的狀態功能
        class MockUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        mock_update = MockUpdate(query)
        await self.status(mock_update, None)
    
    async def handle_menu_quick(self, query):
        """處理快速操作選單"""
        if not await self.check_auth_query(query):
            return
        
        quick_text = """
⚡ **快速操作中心**

選擇您要執行的快速操作：
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 批量調價", callback_data="batch_price"),
                InlineKeyboardButton("📦 批量補貨", callback_data="batch_stock")
            ],
            [
                InlineKeyboardButton("➕ 新增公告", callback_data="new_announcement"),
                InlineKeyboardButton("📈 查看統計", callback_data="menu_stats")
            ],
            [
                InlineKeyboardButton("🔍 低庫存產品", callback_data="check_low_stock"),
                InlineKeyboardButton("⚠️ 緊急公告", callback_data="urgent_announcement")
            ],
            [InlineKeyboardButton("🔙 返回主選單", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(quick_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_logout_confirm(self, query):
        """處理登出確認"""
        keyboard = [
            [
                InlineKeyboardButton("✅ 確認登出", callback_data="confirm_logout"),
                InlineKeyboardButton("❌ 取消", callback_data="back_to_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👋 **確認登出**\n\n您確定要登出嗎？",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def check_auth_query(self, query):
        """檢查查詢的用戶認證"""
        user_id = query.from_user.id
        
        if user_id not in user_sessions or not user_sessions[user_id].get('logged_in'):
            await query.edit_message_text(
                "🔐 請先登入！\n\n請使用主選單的登入功能。"
            )
            return False
        
        return True
    
    async def handle_confirm_logout(self, query):
        """處理確認登出"""
        user_id = query.from_user.id
        
        if user_id in user_sessions:
            username = user_sessions[user_id].get('username', '管理員')
            del user_sessions[user_id]
        else:
            username = '管理員'
        
        await query.edit_message_text(
            f"👋 **登出成功**\n\n再見，{username}！\n\n若要重新使用，請發送 /start"
        )
    
    async def handle_check_low_stock(self, query):
        """檢查低庫存產品"""
        if not await self.check_auth_query(query):
            return
        
        with app.app_context():
            try:
                low_stock_products = Product.query.filter(Product.stock_quantity < 10).all()
                
                if not low_stock_products:
                    text = """
✅ **庫存狀況良好**

所有產品庫存充足！
                    """
                    keyboard = [[InlineKeyboardButton("🔙 返回快速操作", callback_data="menu_quick")]]
                else:
                    text = f"""
🔴 **低庫存警告**

發現 {len(low_stock_products)} 個產品庫存不足：

"""
                    for product in low_stock_products[:10]:  # 最多顯示10個
                        text += f"• {product.name}：{product.stock_quantity} 件\n"
                    
                    if len(low_stock_products) > 10:
                        text += f"\n... 還有 {len(low_stock_products) - 10} 個產品需要補貨"
                    
                    keyboard = [
                        [InlineKeyboardButton("📦 立即補貨", callback_data="batch_stock")],
                        [InlineKeyboardButton("🔙 返回快速操作", callback_data="menu_quick")]
                    ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
                
            except Exception as e:
                await query.edit_message_text(f"❌ 檢查庫存失敗：{str(e)}")
    
    async def handle_urgent_announcement(self, query):
        """緊急公告快速入口"""
        if not await self.check_auth_query(query):
            return
        
        user_id = query.from_user.id
        user_sessions[user_id]['state'] = 'urgent_announcement_title'
        
        await query.edit_message_text(
            "⚠️ **緊急公告**\n\n請輸入緊急公告的標題：\n\n💡 此公告將設為最高優先級並立即啟用",
            parse_mode='Markdown'
        )
    
    async def verify_login(self, update, username, password, user_id):
        """驗證登入"""
        with app.app_context():
            try:
                admin = Admin.query.filter_by(username=username).first()
                
                if admin and check_password_hash(admin.password_hash, password):
                    user_sessions[user_id] = {
                        'logged_in': True,
                        'username': username,
                        'login_time': datetime.now()
                    }
                    
                    await update.message.reply_text(f"✅ 登入成功！歡迎，{username}！")
                    
                    # 顯示主選單
                    await self.show_main_menu(update)
                else:
                    if user_id in user_sessions:
                        del user_sessions[user_id]
                    await update.message.reply_text("❌ 用戶名或密碼錯誤！")
                    
            except Exception as e:
                await update.message.reply_text(f"❌ 登入失敗：{str(e)}")
    
    async def check_auth(self, update):
        """檢查用戶認證"""
        user_id = update.effective_user.id
        
        if user_id not in user_sessions or not user_sessions[user_id].get('logged_in'):
            await update.message.reply_text(
                "🔐 請先登入！\n\n使用 /login 命令進行登入。"
            )
            return False
        
        return True
    
    def run(self):
        """運行機器人"""
        print("🤖 Deepvape Telegram 管理機器人啟動中...")
        print(f"📱 機器人Token: {TELEGRAM_BOT_TOKEN[:10]}...")
        print("✅ 機器人已啟動，等待命令...")
        
        self.app.run_polling()

if __name__ == '__main__':
    if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ 請先設定 TELEGRAM_BOT_TOKEN 環境變數")
        print("💡 獲取方式：")
        print("1. 在 Telegram 中搜尋 @BotFather")
        print("2. 發送 /newbot 創建新機器人")
        print("3. 按照指示設定機器人名稱")
        print("4. 獲取 Token 並設定環境變數")
        print("\n範例：")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
    else:
        bot = AdminBot()
        bot.run() 