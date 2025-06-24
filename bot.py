# bot.py
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from datetime import datetime
import pandas as pd

from config import API_TOKEN, ADMIN_IDS
from models import (
    Base, engine, SessionLocal,
    Product, Option, CartItem, Order, OrderItem
)

# 初始化 DB
Base.metadata.create_all(engine)

# CallbackData
add_cb   = CallbackData('add',   'prod_id')
opt_cb   = CallbackData('opt',   'cartitem_id', 'opt_id')
finish_cb= CallbackData('finish','cartitem_id')

# FSM for admin and ordering
class AdminStates(StatesGroup):
    adding_product  = State()
    adding_option   = State()
    editing_product = State()

class OrderStates(StatesGroup):
    waiting_items   = State()

# 設定 Bot
bot = Bot(token=API_TOKEN)
dp  = Dispatcher(bot, storage=MemoryStorage())

# /start
@dp.message_handler(commands=['start'])
async def cmd_start(msg: types.Message):
    text = (
        "歡迎使用 TG 商店機器人！\n"
        "/browse - 瀏覽商品\n"
        "/cart - 查看購物車\n"
        "/checkout - 結帳\n"
        "/myorders - 我的訂單\n"
    )
    if msg.from_user.id in ADMIN_IDS:
        text += "/add_product - 新增商品 (Admin)\n"
        text += "/add_option - 新增附加項 (Admin)\n"
        text += "/allorders - 查看所有訂單 (Admin)\n"
        text += "/setstatus - 設定訂單狀態 (Admin)\n"
    await msg.answer(text)

# /browse: 列商品
@dp.message_handler(commands=['browse'])
async def cmd_browse(msg: types.Message):
    session = SessionLocal()
    prods = session.query(Product).all()
    kb = types.InlineKeyboardMarkup(row_width=2)
    for p in prods:
        kb.insert(types.InlineKeyboardButton(p.name, callback_data=add_cb.new(prod_id=p.id)))
    await msg.answer("請選擇商品：", reply_markup=kb)
    session.close()

# 加入購物車 - 選擇商品 a
@dp.callback_query_handler(add_cb.filter())
async def on_add_to_cart(cq: types.CallbackQuery, callback_data: dict):
    prod_id = int(callback_data['prod_id'])
    session = SessionLocal()
    # 建立臨時 CartItem
    ci = CartItem(user_id=cq.from_user.id, product_id=prod_id)
    session.add(ci)
    session.commit()
    # 列出可選附加項 b
    opts = session.query(Option).filter_by(product_id=prod_id).all()
    kb = types.InlineKeyboardMarkup(row_width=3)
    for o in opts:
        kb.insert(types.InlineKeyboardButton(
            f"{o.name}(+{o.price})", callback_data=opt_cb.new(cartitem_id=ci.id, opt_id=o.id)
        ))
    kb.add(types.InlineKeyboardButton("✅ 完成", callback_data=finish_cb.new(cartitem_id=ci.id)))
    prod = session.query(Product).get(prod_id)
    caption = f"{prod.name}\n單價：{prod.price}\n請選附加選項(多選)："
    await cq.message.answer_photo(prod.image_url, caption=caption, reply_markup=kb)
    session.close()
    await cq.answer()

# 切換附加項
@dp.callback_query_handler(opt_cb.filter())
async def on_toggle_opt(cq: types.CallbackQuery, callback_data: dict):
    ci_id  = int(callback_data['cartitem_id'])
    opt_id = int(callback_data['opt_id'])
    session = SessionLocal()
    ci = session.query(CartItem).get(ci_id)
    opt= session.query(Option).get(opt_id)
    if opt in ci.options:
        ci.options.remove(opt)
    else:
        ci.options.append(opt)
    session.commit()
    names = [o.name for o in ci.options]
    await cq.answer(f"目前選：{', '.join(names) or '無'}")
    session.close()

# 完成附加
@dp.callback_query_handler(finish_cb.filter())
async def on_finish(cq: types.CallbackQuery, callback_data: dict):
    ci_id = int(callback_data['cartitem_id'])
    session = SessionLocal()
    ci = session.query(CartItem).get(ci_id)
    base = ci.product.price
    extras = sum(o.price for o in ci.options)
    unit_price = base + extras
    session.commit()
    await cq.message.answer(
        f"✅ 已加入購物車：{ci.product.name}\n"
        f"附加：{', '.join(o.name for o in ci.options) or '無'}\n"
        f"單價：{unit_price}\n數量：{ci.quantity}"
    )
    session.close()
    await cq.answer()

# /cart
@dp.message_handler(commands=['cart'])
async def cmd_cart(msg: types.Message):
    session = SessionLocal()
    items = session.query(CartItem).filter_by(user_id=msg.from_user.id).all()
    if not items:
        await msg.answer("購物車是空的。")
    else:
        text = "購物車內容：\n"
        for ci in items:
            base = ci.product.price
            extras= sum(o.price for o in ci.options)
            unit_price = base+extras
            text += (
                f"{ci.id}. {ci.product.name} +{','.join(o.name for o in ci.options) or '無'} x{ci.quantity}"
                f" 單價 {unit_price}\n"
            )
        text += "輸入 /checkout 開始結帳。"
        await msg.answer(text)
    session.close()

# /checkout
@dp.message_handler(commands=['checkout'])
async def cmd_checkout(msg: types.Message):
    await msg.answer("請輸入 7-11 門市編號：")
    await OrderStates.waiting_items.set()

@dp.message_handler(state=OrderStates.waiting_items)
async def process_store(msg: types.Message, state: FSMContext):
    store = msg.text.strip()
    data = await state.get_data()
    session = SessionLocal()
    items = session.query(CartItem).filter_by(user_id=msg.from_user.id).all()
    if not items:
        await msg.answer("購物車為空，無法結帳。")
        await state.finish()
        session.close()
        return
    # 建訂單
    order_no = datetime.now().strftime("ORD%Y%d%m%H%M")
    order = Order(order_no=order_no, user_id=msg.from_user.id, store_code=store)
    session.add(order); session.commit()
    # order items
    for ci in items:
        base=ci.product.price; extras=sum(o.price for o in ci.options)
        unit_price=base+extras
        oi=OrderItem(order_id=order.id, product_id=ci.product_id,
                     quantity=ci.quantity, price=unit_price)
        oi.options = ci.options.copy()
        session.add(oi)
        session.delete(ci)
    session.commit()
    await msg.answer(f"✅ 訂單建立成功！訂單號：{order_no}")
    await state.finish()
    session.close()

# /myorders
@dp.message_handler(commands=['myorders'])
async def cmd_myorders(msg: types.Message):
    session = SessionLocal()
    orders = session.query(Order).filter_by(user_id=msg.from_user.id).order_by(Order.created_at.desc()).all()
    if not orders:
        await msg.answer("尚無任何訂單。")
    else:
        text="您的訂單：\n"
        for o in orders:
            text+=f"{o.order_no} | {o.status} | {o.created_at:%Y-%m-%d %H:%M}\n"
        await msg.answer(text)
    session.close()

# Admin: /allorders
@dp.message_handler(lambda msg: msg.text.startswith('/allorders'))
async def cmd_allorders(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    session = SessionLocal()
    orders = session.query(Order).order_by(Order.created_at.desc()).all()
    text="所有訂單：\n"
    for o in orders:
        text+=f"{o.order_no} | UID:{o.user_id} | {o.status}\n"
    await msg.answer(text)
    session.close()

# Admin: /setstatus ORD... 新狀態
@dp.message_handler(lambda msg: msg.text.startswith('/setstatus '))
async def cmd_setstatus(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    parts = msg.text.split(maxsplit=2)
    if len(parts)<3:
        return await msg.answer("用法：/setstatus <訂單號> <新狀態>")
    _, ono, status = parts
    session = SessionLocal()
    o = session.query(Order).filter_by(order_no=ono).first()
    if not o:
        await msg.answer("找不到此訂單號。")
    else:
        o.status = status; session.commit()
        await msg.answer(f"✅ 訂單 {ono} 狀態已設為 {status}")
        # 通知用戶
        await bot.send_message(o.user_id, f"您的訂單 {ono} 狀態：{status}")
    session.close()

if __name__ == '__main__':
    asyncio.run(dp.start_polling())