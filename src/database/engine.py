# src/database/engine.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tem_machinery")
DB_USER = os.getenv("DB_USER", "viktorskoromnik")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

if DB_PASSWORD:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session():
    """Возвращает новую сессию"""
    return SessionLocal()


def init_db(drop_all=False):
    """Инициализация базы данных"""
    # Явно импортируем ВСЕ модели перед созданием таблиц
    from src.database.models import (
        Customer,
        Product,
        CustomerOrder,
        CustomerOrderItem
    )

    if drop_all:
        print("⚠️  Удаляем все существующие таблицы...")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
    
    print("✅ База данных успешно инициализирована.")
    print("   Таблицы: customers, products, customer_orders, customer_order_items")


if __name__ == "__main__":
    choice = input("Пересоздать все таблицы? (y/n): ").strip().lower()
    init_db(drop_all=(choice == 'y'))