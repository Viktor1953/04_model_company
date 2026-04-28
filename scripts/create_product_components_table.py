# scripts/create_product_components_table.py
"""
Принудительное создание таблицы product_components
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.database.engine import engine
from sqlalchemy import text


def create_product_components_table():
    print("🔧 Создаём таблицу product_components...")

    with engine.connect() as conn:
        # Удаляем таблицу, если она существует с ошибками
        conn.execute(text("DROP TABLE IF EXISTS product_components CASCADE;"))
        
        # Создаём таблицу
        conn.execute(text("""
            CREATE TABLE product_components (
                id VARCHAR PRIMARY KEY,
                product_id VARCHAR NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                component_name VARCHAR NOT NULL,
                mcr_gu FLOAT NOT NULL,
                manufacturing_losses_pct FLOAT NOT NULL DEFAULT 0.0,
                scrap_pct FLOAT NOT NULL DEFAULT 0.0,
                tmc_gu FLOAT NOT NULL,
                uom VARCHAR NOT NULL,
                notes TEXT
            );
        """))
        conn.commit()

    print("✅ Таблица product_components успешно создана!")
    print("   Колонки: id, product_id, component_name, mcr_gu, manufacturing_losses_pct, scrap_pct, tmc_gu, uom, notes")


if __name__ == "__main__":
    create_product_components_table()
    input("\nНажмите Enter для завершения...")