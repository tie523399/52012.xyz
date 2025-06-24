# models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Float,
    Boolean, ForeignKey, Table, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config import DATABASE_URL

Base = declarative_base()

# 關聯表：CartItem ↔ Option, OrderItem ↔ Option
cartitem_option = Table(
    'cartitem_option', Base.metadata,
    Column('cartitem_id', ForeignKey('cart_items.id'), primary_key=True),
    Column('option_id', ForeignKey('options.id'),   primary_key=True)
)

class Product(Base):
    __tablename__ = 'products'
    id         = Column(Integer, primary_key=True)
    name       = Column(String, nullable=False)
    price      = Column(Float, nullable=False)    # 本體價格 (a)
    image_url  = Column(String, nullable=True)
    category   = Column(String, nullable=True)
    options    = relationship("Option", back_populates="product")

class Option(Base):
    __tablename__ = 'options'
    id         = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    name       = Column(String, nullable=False)
    price      = Column(Float, nullable=False)    # 附加選項價格 (b)
    product    = relationship("Product", back_populates="options")

class CartItem(Base):
    __tablename__ = 'cart_items'
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity   = Column(Integer, default=1)
    options    = relationship("Option", secondary=cartitem_option)

class Order(Base):
    __tablename__ = 'orders'
    id         = Column(Integer, primary_key=True)
    order_no   = Column(String, unique=True, nullable=False)
    user_id    = Column(Integer, nullable=False)
    store_code = Column(String, nullable=True)
    cod        = Column(Boolean, default=True)
    status     = Column(String, default='新訂單')
    created_at = Column(DateTime, default=datetime.now)
    items      = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'
    id         = Column(Integer, primary_key=True)
    order_id   = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity   = Column(Integer, default=1)
    price      = Column(Float, nullable=False)  # 計算後單價 = a + sum(b_i)
    options    = relationship("Option", secondary=cartitem_option)
    order      = relationship("Order", back_populates="items")

# 建立 Engine 與 Session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)