# scripts/fix_product_components_table.py
"""
Исправление таблицы product_components — добавление поля product_name
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.database.engine import engine
from sqlalchemy import text


def fix_product_components_table():
    print("🔧 Исправляем таблицу product_components...")

    with engine.connect() as conn:
        # Добавляем колонку product_name, если её нет
        conn.execute(text("""
            ALTER TABLE product_components 
            ADD COLUMN IF NOT EXISTS product_name VARCHAR;
        """))
        conn.commit()

    print("✅ Поле product_name успешно добавлено в таблицу product_components!")
    print("   Теперь можно использовать product_name для отображения названия изделия.")


if __name__ == "__main__":
    fix_product_components_table()
    input("\nНажмите Enter для завершения...")