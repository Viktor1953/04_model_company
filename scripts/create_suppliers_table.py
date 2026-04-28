# scripts/create_suppliers_table.py
"""
Принудительное создание таблицы suppliers
"""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.database.engine import engine
from sqlalchemy import text, Column, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def create_suppliers_table():
    print("🔧 Создаём таблицу suppliers...")

    with engine.connect() as conn:
        # Удаляем таблицу, если она существует с ошибками
        conn.execute(text("DROP TABLE IF EXISTS suppliers CASCADE;"))
        
        # Создаём таблицу заново
        conn.execute(text("""
            CREATE TABLE suppliers (
                id VARCHAR PRIMARY KEY,
                company_name VARCHAR NOT NULL,
                currency VARCHAR NOT NULL,
                distance_km FLOAT NOT NULL,
                reliability_score FLOAT NOT NULL DEFAULT 0.85
            );
        """))
        conn.commit()

    print("✅ Таблица suppliers успешно создана!")
    print("   Колонки: id, company_name, currency, distance_km, reliability_score")


if __name__ == "__main__":
    create_suppliers_table()
    input("\nНажмите Enter для завершения...")