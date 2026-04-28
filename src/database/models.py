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

    # Связь с заказами — с каскадным удалением
    customer_orders = relationship(
        "CustomerOrder", 
        back_populates="customer", 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Customer {self.id} - {self.company}>"


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    uom = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)

    # Каскадное удаление позиций заказов при удалении изделия
    order_items = relationship(
        "CustomerOrderItem", 
        back_populates="product", 
        cascade="all, delete-orphan"   # ← Добавили это
    )

    def __repr__(self):
        return f"<Product {self.id} - {self.name}>"
    
        # Состав изделия (компоненты)
    components = relationship(
        "ProductComponent", 
        back_populates="product", 
        cascade="all, delete-orphan"
    )

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
    items = relationship(
        "CustomerOrderItem", 
        back_populates="order", 
        cascade="all, delete-orphan"
    )


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

# === Добавь этот блок в самый конец файла src/database/models.py ===

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(String, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    reliability_score = Column(Float, nullable=False, default=0.85)

    def __repr__(self):
        return f"<Supplier {self.id} - {self.company_name}>"
    
    # Добавь в самый конец src/database/models.py

# === Добавь в самый конец src/database/models.py ===

# === Добавь в самый конец файла src/database/models.py ===

class ProductComponent(Base):
    __tablename__ = "product_components"

    id = Column(String, primary_key=True, index=True)

    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    product = relationship("Product", back_populates="components")

    # Добавляем поле product_name для удобства отображения
    product_name = Column(String, nullable=True)

    component_name = Column(String, nullable=False)
    mcr_gu = Column(Float, nullable=False)
    manufacturing_losses_pct = Column(Float, nullable=False, default=0.0)
    scrap_pct = Column(Float, nullable=False, default=0.0)
    tmc_gu = Column(Float, nullable=False)

    uom = Column(String, nullable=False)
    notes = Column(String, nullable=True)

    def __repr__(self):
        return f"<ProductComponent {self.id} - {self.component_name}>"
    
# === Добавь в самый конец src/database/models.py ===

class SupplierOrder(Base):
    __tablename__ = "supplier_orders"

    id = Column(String, primary_key=True, index=True)                    # spo-1, spo-2...
    order_date = Column(Date, nullable=False)

    supplier_id = Column(String, ForeignKey("suppliers.id"), nullable=False)
    supplier = relationship("Supplier")

    currency = Column(String, nullable=False)
    discount_percent = Column(Float, default=0.0)
    order_value = Column(Float, default=0.0)                             # рассчитывается
    status = Column(String, default="Ordered")                           # Ordered, In stock

    delivery_timeline_days = Column(Integer, nullable=False)
    advance_percent = Column(Float, default=0.0)
    advance_deadline_days = Column(Integer, nullable=False)
    dnf_days = Column(Integer, nullable=False)                           # Delivery Non-Fulfillment risk
    supplier_reliability = Column(Float, nullable=False)

    # Связь с позициями
    items = relationship("SupplierOrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SupplierOrder {self.id}>"


class SupplierOrderItem(Base):
    __tablename__ = "supplier_order_items"

    id = Column(String, primary_key=True, index=True)

    supplier_order_id = Column(String, ForeignKey("supplier_orders.id"), nullable=False)
    order = relationship("SupplierOrder", back_populates="items")

    component_id = Column(String, ForeignKey("product_components.id"), nullable=False)
    component = relationship("ProductComponent")

    qty = Column(Float, nullable=False)
    ule_percent = Column(Float, default=0.0)          # Unavoidable Leftovers and Excess
    total_qty = Column(Float, nullable=False)         # qty + ule
    uom = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)        # total_qty * unit_price

    def __repr__(self):
        return f"<SupplierOrderItem {self.id}>"