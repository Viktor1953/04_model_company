# scripts/generate_orders.py
"""
Генератор тестовых заказов с гибкой настройкой статусов и округлением
Запуск: python -m scripts.generate_orders
"""

import random
from datetime import date, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.controllers.customer_controller import CustomerController
from src.controllers.product_controller import ProductController
from src.controllers.customer_order_controller import CustomerOrderController
from src.controllers.customer_order_item_controller import CustomerOrderItemController


def generate_orders(num_days=30, 
                   orders_per_day_min=0, 
                   orders_per_day_max=3,
                   status_distribution=None):
    
    if status_distribution is None:
        status_distribution = {"Ordered": 0.6, "Quotation": 0.3, "In stock": 0.1}

    print(f"🚀 Генерация заказов за {num_days} дней...")
    print(f"Распределение статусов: {status_distribution}\n")

    customer_ctrl = CustomerController()
    product_ctrl = ProductController()
    order_ctrl = CustomerOrderController()
    item_ctrl = CustomerOrderItemController()

    customers = customer_ctrl.get_all_customers()
    products = product_ctrl.get_all_products()

    if not customers or not products:
        print("❌ Ошибка: Необходимо наличие клиентов и изделий в базе.")
        return

    start_date = date.today() - timedelta(days=num_days - 1)
    total_orders = 0
    total_items = 0

    statuses = list(status_distribution.keys())
    weights = list(status_distribution.values())

    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        num_orders_today = random.randint(orders_per_day_min, orders_per_day_max)

        for _ in range(num_orders_today):
            customer = random.choice(customers)

            # Параметры заказа
            currency = random.choice(["USD", "EUR", "RUB", "CNY", "JPY"])
            discount = round(random.uniform(0, 5), 1)           # 0.0 - 5.0 с одним знаком
            status = random.choices(statuses, weights=weights, k=1)[0]
            advance_percent = round(random.uniform(5, 75), 1)   # тоже с одним знаком
            advance_days = random.randint(1, 7)
            final_days = random.randint(1, 7)
            risk_days = random.randint(1, 15)

            # Создаём заказ
            order_id = order_ctrl.create_order(
                customer_id=customer.id,
                currency=currency,
                discount_percent=discount,
                status=status,
                advance_percent=advance_percent,
                advance_deadline_days=advance_days,
                final_payment_days=final_days,
                risk_late_payment_days=risk_days,
                order_date=current_date
            )

            if not order_id:
                continue

            total_orders += 1

            # Добавляем позиции (1–10)
            num_items = random.randint(1, 10)
            for _ in range(num_items):
                product = random.choice(products)
                qty = random.randint(5, 50)
                item_ctrl.add_item(order_id, product.id, float(qty))
                total_items += 1

            print(f"✓ {current_date.strftime('%Y-%m-%d')} | {order_id} | {customer.company[:25]:<25} | "
                  f"{status:<10} | Скидка {discount:4.1f}% | Аванс {advance_percent:4.1f}% | {num_items} поз.")

    print(f"\n🎉 Генерация завершена!")
    print(f"   Создано заказов: {total_orders}")
    print(f"   Создано позиций: {total_items}")


if __name__ == "__main__":
    print("=== Генератор тестовых заказов ===\n")

    # Выбор периода
    print("Выберите период генерации:")
    print("1. 30 дней")
    print("2. 90 дней")
    period_choice = input("Введите 1 или 2: ").strip()

    num_days = 30 if period_choice == "1" else 90

    # Настройка распределения статусов
    print("\nНастройка распределения статусов заказов:")
    print("Введите доли (в процентах, сумма должна быть 100):")

    ordered_pct = float(input("Ordered (%): ") or 60)
    quotation_pct = float(input("Quotation (%): ") or 30)
    instock_pct = float(input("In stock (%): ") or 10)

    # Нормализация
    total_pct = ordered_pct + quotation_pct + instock_pct
    status_distribution = {
        "Ordered": ordered_pct / total_pct,
        "Quotation": quotation_pct / total_pct,
        "In stock": instock_pct / total_pct
    }

    print(f"\nЗапуск генерации за {num_days} дней с распределением статусов:")
    print(f"   Ordered: {ordered_pct:.1f}%")
    print(f"   Quotation: {quotation_pct:.1f}%")
    print(f"   In stock: {instock_pct:.1f}%")

    generate_orders(
        num_days=num_days,
        orders_per_day_min=0,
        orders_per_day_max=3,
        status_distribution=status_distribution
    )

    input("\nНажмите Enter для завершения...")