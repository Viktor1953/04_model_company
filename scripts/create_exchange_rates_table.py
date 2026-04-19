# scripts/create_exchange_rates_table.py
"""
Принудительное создание таблицы exchange_rates
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.database.engine import engine
from sqlalchemy import text


def create_exchange_rates_table():
    print("Создаём таблицу exchange_rates...")

    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS exchange_rates (
                date DATE NOT NULL,
                currency VARCHAR NOT NULL,
                rate_to_usd FLOAT NOT NULL,
                PRIMARY KEY (date, currency)
            );
        """))
        conn.commit()

    print("✅ Таблица exchange_rates успешно создана (или уже существовала).")


if __name__ == "__main__":
    create_exchange_rates_table()
    input("\nНажмите Enter для завершения...")