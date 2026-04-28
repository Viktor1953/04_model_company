# src/utils/id_generator.py
from sqlalchemy import text
from src.database.engine import get_session

def generate_customer_id() -> str:
    with get_session() as db:
        try:
            result = db.execute(text("""
                SELECT COALESCE(MAX(CAST(SPLIT_PART(id, '-', 2) AS INTEGER)), 0) 
                FROM customers
            """))
            max_num = result.scalar() or 0
            return f"cl-{max_num + 1}"
        except Exception:
            return "cl-1"

def generate_product_id() -> str:
    with get_session() as db:
        try:
            result = db.execute(text("""
                SELECT COALESCE(MAX(CAST(SPLIT_PART(id, '-', 2) AS INTEGER)), 0) 
                FROM products
            """))
            max_num = result.scalar() or 0
            return f"pr-{max_num + 1}"
        except Exception:
            return "pr-1"
        
def generate_supplier_id():
    """Генерирует ID поставщика: sup-1, sup-2, ..."""
    with get_session() as db:
        try:
            result = db.execute(text("SELECT MAX(CAST(SPLIT_PART(id, '-', 2) AS INTEGER)) FROM suppliers")).scalar()
            max_num = result if result is not None else 0
            return f"sup-{max_num + 1}"
        except:
            return "sup-1"

def generate_order_id() -> str:
    """Генерирует ID заказа: or-1, or-2, or-3 ..."""
    with get_session() as db:
        try:
            result = db.execute(text("""
                SELECT COALESCE(MAX(CAST(SPLIT_PART(id, '-', 2) AS INTEGER)), 0) 
                FROM customer_orders
            """))
            max_num = result.scalar() or 0
            return f"or-{max_num + 1}"
        except Exception:
            return "or-1"
        
def generate_product_component_id():
    """Генерирует ID компонента: mat-1, mat-2, ..."""
    with get_session() as db:
        try:
            result = db.execute(text("SELECT MAX(CAST(SPLIT_PART(id, '-', 2) AS INTEGER)) FROM product_components")).scalar()
            max_num = result if result is not None else 0
            return f"mat-{max_num + 1}"
        except:
            return "mat-1"