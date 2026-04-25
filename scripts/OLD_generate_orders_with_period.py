# scripts/generate_orders_with_period.py
"""
Генератор заказов с учётом матрёшки периодов
Запуск: python -m scripts.generate_orders_with_period
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
from src.models.periods import create_period, PeriodType


def generate_orders_with_period(period_type: str = "tactical",
                               orders_per_day_min: int = 0,
                               orders_per_day_max: int = 3,
                               status_distribution: dict = None):
    
    if status_distribution is None:
        status_distribution = {"Ordered": 0.6, "Quotation": 0.3, "In stock": 0.1}

    period = create_period(period_type)
    print(f"Генерация заказов в периоде: {period}")
    print(f"Распределение статусов: {status_distribution}\n")

    customer_ctrl = CustomerController()
    product_ctrl = ProductController()
    order_ctrl = CustomerOrderController()
    item_ctrl = CustomerOrderItemController()

    customers = customer_ctrl.get_all_customers()
    products = product_ctrl.get_all_products()

    if not customers or not products:
        print("❌ Ошибка: В базе должны быть клиенты и изделия.")
        return

    start_date, end_date = period.get_date_range()
    delta = end_date - start_date
    total_days = delta.days + 1

    total_orders = 0
    total_items = 0

    statuses = list(status_distribution.keys())
    weights = list(status_distribution.values())

    current_date = start_date
    while current_date <= end_date:
        num_orders_today = random.randint(orders_per_day_min, orders_per_day_max)

        for _ in range(num_orders_today):
            customer = random.choice(customers)

            currency = random.choice(["USD", "EUR", "RUB", "CNY", "JPY"])
            discount = round(random.uniform(0, 5), 1)
            status = random.choices(statuses, weights=weights, k=1)[0]
            advance_percent = round(random.uniform(5, 75), 1)
            advance_days = random.randint(1, 7)
            final_days = random.randint(1, 7)
            risk_days = random.randint(1, 15)

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

            if order_id:
                total_orders += 1

                # Добавляем от 1 до 10 позиций
                num_items = random.randint(1, 10)
                for _ in range(num_items):
                    product = random.choice(products)
                    qty = random.randint(5, 50)
                    item_ctrl.add_item(order_id, product.id, float(qty))
                    total_items += 1

                print(f"✓ {current_date} | {order_id} | {customer.company[:20]:<20} | "
                      f"{status:<10} | Скидка {discount:4.1f}% | {num_items} поз.")

        current_date += timedelta(days=1)

    print(f"\n🎉 Генерация завершена!")
    print(f"   Период: {period}")
    print(f"   Создано заказов: {total_orders}")
    print(f"   Создано позиций: {total_items}")


if __name__ == "__main__":
    print("=== Генератор заказов с матрёшкой периодов ===\n")

    print("Выберите уровень периода:")
    print("1. Стратегический (12 месяцев)")
    print("2. Тактический (6 месяцев)")
    print("3. Оперативный (3 месяца)")
    choice = input("Введите номер (1-3): ").strip()

    period_map = {"1": "strategic", "2": "tactical", "3": "operational"}
    period_type = period_map.get(choice, "tactical")

    # Настройка статусов
    print("\nНастройка распределения статусов (в %):")
    ordered = float(input("Ordered (%): ") or 60)
    quotation = float(input("Quotation (%): ") or 30)
    instock = float(input("In stock (%): ") or 10)

    total = ordered + quotation + instock
    status_distribution = {
        "Ordered": ordered / total,
        "Quotation": quotation / total,
        "In stock": instock / total
    }

    generate_orders_with_period(
        period_type=period_type,
        orders_per_day_min=0,
        orders_per_day_max=3,
        status_distribution=status_distribution
    )

    input("\nНажмите Enter для завершения...")