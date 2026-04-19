# src/utils/exchange_rates.py
import requests
from datetime import datetime, date
from src.database.engine import get_session
from sqlalchemy import Column, String, Float, Date, text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    date = Column(Date, primary_key=True)
    currency = Column(String, primary_key=True)   # например "EUR", "RUB"
    rate_to_usd = Column(Float, nullable=False)   # сколько единиц валюты за 1 USD


def fetch_exchange_rates():
    """Получает актуальные курсы валют к USD"""
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        rates = data.get("rates", {})
        today = date.today()

        print(f"✅ Курсы валют получены на {today} (базовая валюта: USD)")

        with get_session() as session:
            # Сохраняем курсы в базу
            for currency, rate in rates.items():
                if currency in ["USD", "EUR", "RUB", "CNY", "JPY"]:
                    # Удаляем старые записи за сегодня
                    session.execute(text("DELETE FROM exchange_rates WHERE date = :date AND currency = :currency"),
                                  {"date": today, "currency": currency})
                    
                    rate_obj = ExchangeRate(date=today, currency=currency, rate_to_usd=rate)
                    session.add(rate_obj)
            
            session.commit()

        print("✅ Курсы валют успешно сохранены в базу.")
        return True

    except Exception as e:
        print(f"❌ Ошибка получения курсов валют: {e}")
        return False


def get_exchange_rate(currency: str, target_date: date = None) -> float:
    """Возвращает курс указанной валюты к USD"""
    if target_date is None:
        target_date = date.today()

    with get_session() as session:
        rate = session.query(ExchangeRate)\
            .filter(ExchangeRate.currency == currency, ExchangeRate.date == target_date)\
            .first()

        if rate:
            return rate.rate_to_usd
        else:
            # Если нет данных на дату — берём самый свежий
            latest = session.query(ExchangeRate)\
                .filter(ExchangeRate.currency == currency)\
                .order_by(ExchangeRate.date.desc())\
                .first()
            return latest.rate_to_usd if latest else 1.0


def convert_to_base_currency(amount: float, currency: str, target_date: date = None) -> float:
    """Пересчитывает сумму из любой валюты в базовую (USD)"""
    if currency.upper() == "USD":
        return round(amount, 2)

    rate = get_exchange_rate(currency.upper(), target_date)
    if rate and rate > 0:
        return round(amount / rate, 2)
    return round(amount, 2)  # fallback


# Для быстрого тестирования
if __name__ == "__main__":
    print("Получаем актуальные курсы валют...")
    fetch_exchange_rates()

    # Пример использования
    print(f"EUR к USD: {get_exchange_rate('EUR'):.4f}")
    print(f"100 EUR = {convert_to_base_currency(100, 'EUR'):.2f} USD")