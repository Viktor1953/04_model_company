# scripts/create_tables.py
"""
Принудительное создание всех таблиц через прямой SQL
Запуск: python -m scripts.create_tables
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.database.engine import engine
from sqlalchemy import text


def create_all_tables():
    print("🔨 Принудительное создание таблиц...")

    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS customer_order_items CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS customer_orders CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS products CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS customers CASCADE;"))

        # Создаём таблицы вручную
        conn.execute(text("""
            CREATE TABLE customers (
                id VARCHAR PRIMARY KEY,
                company VARCHAR NOT NULL,
                distance_km FLOAT NOT NULL
            );
        """))

        conn.execute(text("""
            CREATE TABLE products (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                uom VARCHAR NOT NULL,
                unit_price FLOAT NOT NULL,
                currency VARCHAR NOT NULL
            );
        """))

        conn.execute(text("""
            CREATE TABLE customer_orders (
                id VARCHAR PRIMARY KEY,
                order_date DATE NOT NULL,
                customer_id VARCHAR NOT NULL REFERENCES customers(id),
                currency VARCHAR NOT NULL,
                discount_percent FLOAT DEFAULT 0,
                status VARCHAR DEFAULT 'Quotation',
                advance_percent FLOAT DEFAULT 0,
                advance_deadline_days INTEGER DEFAULT 14,
                final_payment_days INTEGER DEFAULT 30,
                risk_late_payment_days INTEGER DEFAULT 7
            );
        """))

        conn.execute(text("""
            CREATE TABLE customer_order_items (
                id SERIAL PRIMARY KEY,
                order_id VARCHAR NOT NULL REFERENCES customer_orders(id) ON DELETE CASCADE,
                product_id VARCHAR NOT NULL REFERENCES products(id),
                qty FLOAT NOT NULL
            );
        """))

        conn.commit()

    print("✅ Все таблицы успешно созданы вручную!")


if __name__ == "__main__":
    create_all_tables()
    input("\nНажмите Enter для завершения...")