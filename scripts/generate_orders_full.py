# scripts/generate_orders_full.py
"""
Генератор заказов по матрёшке с автоматическим пересчётом валют в USD
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
from src.models.periods import create_period
from src.utils.exchange_rates import convert_to_base_currency, fetch_exchange_rates


def generate_orders_in_period(period_type: str,
                              avg_orders_per_day: int,
                              status_distribution: dict,
                              is_past: bool = False):
    
    period = create_period(period_type)
    start_date, end_date = period.get_date_range()

    print(f"\n{'='*85}")
    print(f"ЭТАП: {period.get_level_name()}")
    print(f"Период: {start_date} — {end_date}")
    print(f"Среднее заказов в день: {avg_orders_per_day} (±1)")
    print(f"Распределение статусов: {status_distribution}")
    print(f"{'='*85}")

    # Обновляем курсы валют перед генерацией
    fetch_exchange_rates()

    customer_ctrl = CustomerController()
    product_ctrl = ProductController()
    order_ctrl = CustomerOrderController()
    item_ctrl = CustomerOrderItemController()

    customers = customer_ctrl.get_all_customers()
    products = product_ctrl.get_all_products()

    if not customers or not products:
        print("❌ Ошибка: В базе должны быть клиенты и изделия.")
        return 0, 0

    total_orders = 0
    total_items = 0
    current_date = start_date

    statuses = list(status_distribution.keys())
    weights = list(status_distribution.values())

    while current_date <= end_date:
        variation = random.choice([-1, 0, 1])
        orders_today = max(0, avg_orders_per_day + variation)

        for _ in range(orders_today):
            customer = random.choice(customers)

            if is_past:
                status = "Ordered"
                discount = 0.0
                advance_percent = 0.0
                currency = "USD"
            else:
                status = random.choices(statuses, weights=weights, k=1)[0]
                discount = round(random.uniform(0, 5), 1)
                advance_percent = round(random.uniform(5, 75), 1)
                currency = random.choice(["USD", "EUR", "RUB", "CNY", "JPY"])

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

                num_items = random.randint(1, 10)
                order_total_usd = 0.0

                for _ in range(num_items):
                    product = random.choice(products)
                    qty = random.randint(5, 50)

                    # Пересчёт цены продукта в базовую валюту (USD)
                    base_price = convert_to_base_currency(product.unit_price, product.currency)
                    item_total_usd = qty * base_price
                    order_total_usd += item_total_usd

                    item_ctrl.add_item(order_id, product.id, float(qty))

                total_items += num_items

                # Красивый вывод с пересчётом
                currency_info = f"{currency}"
                if currency != "USD":
                    currency_info += f" → {order_total_usd:.2f} USD"

                print(f"  ✓ {current_date} | {order_id} | {customer.company[:22]:<22} | "
                      f"{status:<10} | Скидка {discount:4.1f}% | {currency_info} | {num_items} поз.")

        current_date += timedelta(days=1)

    print(f"✓ Период завершён → Заказов: {total_orders} | Позиций: {total_items}\n")
    return total_orders, total_items


if __name__ == "__main__":
    print("=== ГЕНЕРАТОР ЗАКАЗОВ ПО МАТРЁШКЕ С ПЕРЕСЧЁТОМ ВАЛЮТ ===\n")

    total_orders = 0
    total_items = 0

    # ЭТАП 1: Прошлый период (3 месяца)
    print("ЭТАП 1 → Прошлый период (3 месяца) — все заказы Ordered")
    avg_orders = int(input("Среднее количество заказов в день (0–5): ") or 2)
    orders, items = generate_orders_in_period(
        period_type="past_3m",
        avg_orders_per_day=avg_orders,
        status_distribution={"Ordered": 1.0},
        is_past=True
    )
    total_orders += orders
    total_items += items

    # ЭТАП 2: Оперативный период (3 месяца)
    print("\nЭТАП 2 → Оперативный период (3 месяца)")
    avg_orders = int(input("Среднее количество заказов в день (0–5): ") or 2)
    ordered = float(input("  Ordered (%): ") or 60)
    quotation = float(input("  Quotation (%): ") or 30)
    instock = float(input("  In stock (%): ") or 10)
    total_pct = ordered + quotation + instock

    orders, items = generate_orders_in_period(
        period_type="operational",
        avg_orders_per_day=avg_orders,
        status_distribution={
            "Ordered": ordered / total_pct,
            "Quotation": quotation / total_pct,
            "In stock": instock / total_pct
        }
    )
    total_orders += orders
    total_items += items

    # ЭТАП 3: Тактический период (3 месяца)
    print("\nЭТАП 3 → Тактический период (3 месяца)")
    avg_orders = int(input("Среднее количество заказов в день (0–5): ") or 2)
    ordered = float(input("  Ordered (%): ") or 65)
    quotation = float(input("  Quotation (%): ") or 25)
    instock = float(input("  In stock (%): ") or 10)
    total_pct = ordered + quotation + instock

    orders, items = generate_orders_in_period(
        period_type="tactical",
        avg_orders_per_day=avg_orders,
        status_distribution={
            "Ordered": ordered / total_pct,
            "Quotation": quotation / total_pct,
            "In stock": instock / total_pct
        }
    )
    total_orders += orders
    total_items += items

    # ЭТАП 4: Стратегический период (6 месяцев)
    print("\nЭТАП 4 → Стратегический период (6 месяцев)")
    avg_orders = int(input("Среднее количество заказов в день (0–5): ") or 1)
    ordered = float(input("  Ordered (%): ") or 70)
    quotation = float(input("  Quotation (%): ") or 20)
    instock = float(input("  In stock (%): ") or 10)
    total_pct = ordered + quotation + instock

    orders, items = generate_orders_in_period(
        period_type="strategic",
        avg_orders_per_day=avg_orders,
        status_distribution={
            "Ordered": ordered / total_pct,
            "Quotation": quotation / total_pct,
            "In stock": instock / total_pct
        }
    )
    total_orders += orders
    total_items += items

    print(f"\n{'═'*90}")
    print("ГЕНЕРАЦИЯ ЗАВЕРШЕНА")
    print(f"Всего создано заказов: {total_orders}")
    print(f"Всего создано позиций изделий: {total_items}")
    print(f"{'═'*90}")

    input("\nНажмите Enter для завершения...")