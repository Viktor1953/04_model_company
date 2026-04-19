# src/database/models.py
from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import date

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    company = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    uom = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)


class CustomerOrder(Base):
    __tablename__ = "customer_orders"

    id = Column(String, primary_key=True, index=True)                    # or-1, or-2 ...
    order_date = Column(Date, default=date.today, nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    currency = Column(String, nullable=False)
    discount_percent = Column(Float, default=0.0)
    status = Column(String, default="Quotation")                         # Ordered, Quotation, In stock
    advance_percent = Column(Float, default=0.0)
    advance_deadline_days = Column(Integer, default=14)
    final_payment_days = Column(Integer, default=30)
    risk_late_payment_days = Column(Integer, default=7)

    # Связи
    customer = relationship("Customer")
    items = relationship("CustomerOrderItem", back_populates="order", cascade="all, delete-orphan")


class CustomerOrderItem(Base):
    __tablename__ = "customer_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, ForeignKey("customer_orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    qty = Column(Float, nullable=False)

    # Связи
    order = relationship("CustomerOrder", back_populates="items")
    product = relationship("Product")

    # Добавьте в конец файла src/database/models.py

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    date = Column(Date, primary_key=True)
    currency = Column(String, primary_key=True)   # "EUR", "RUB" и т.д.
    rate_to_usd = Column(Float, nullable=False)   # сколько единиц валюты за 1 USD