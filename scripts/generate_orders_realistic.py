# scripts/generate_orders_realistic.py
"""
Реалистичный генератор заказов с Парето, логнормальным и сезонными эффектами
"""

import random
import numpy as np
from datetime import date, timedelta
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.controllers.customer_controller import CustomerController
from src.controllers.product_controller import ProductController
from src.controllers.customer_order_controller import CustomerOrderController
from src.controllers.customer_order_item_controller import CustomerOrderItemController
from src.models.periods import create_period
from src.utils.exchange_rates import fetch_exchange_rates


def pareto_weights(values, alpha=1.05):
    """Парето-распределение весов"""
    ranks = np.argsort(values)[::-1]
    weights = 1.0 / (ranks + 1) ** alpha
    weights /= weights.sum()
    return weights


def generate_realistic_orders():
    print("=== РЕАЛИСТИЧНЫЙ ГЕНЕРАТОР ЗАКАЗОВ ===\n")

    fetch_exchange_rates()

    customer_ctrl = CustomerController()
    product_ctrl = ProductController()
    order_ctrl = CustomerOrderController()
    item_ctrl = CustomerOrderItemController()

    customers = customer_ctrl.get_all_customers()
    products = product_ctrl.get_all_products()

    if not customers or not products:
        print("❌ Ошибка: Нет клиентов или изделий в базе.")
        return

    # ==================== Настройки ====================
    alpha = float(input("Параметр Парето (alpha) для клиентов [по умолчанию 1.05]: ") or 1.05)

    # ЭТАП 1: Прошлый период (3 месяца)
    print("\nЭТАП 1 → Прошлый период (3 месяца)")
    avg_orders_past = int(input("Среднее кол-во заказов в день: ") or 2)
    orders, items = generate_in_period(
        period_type="past_3m",
        avg_orders_per_day=avg_orders_past,
        alpha=alpha,
        customers=customers,
        products=products,
        order_ctrl=order_ctrl,
        item_ctrl=item_ctrl,
        is_past=True
    )

    # ЭТАП 2: Оперативный
    print("\nЭТАП 2 → Оперативный период (3 месяца)")
    avg_orders_op = int(input("Среднее кол-во заказов в день: ") or 2)
    ordered_pct = float(input("Ordered (%): ") or 60)
    quot_pct = float(input("Quotation (%): ") or 30)
    instock_pct = float(input("In stock (%): ") or 10)

    generate_in_period(
        period_type="operational",
        avg_orders_per_day=avg_orders_op,
        alpha=alpha,
        customers=customers,
        products=products,
        order_ctrl=order_ctrl,
        item_ctrl=item_ctrl,
        status_dist={"Ordered": ordered_pct/100, "Quotation": quot_pct/100, "In stock": instock_pct/100}
    )

    # ЭТАП 3: Тактический
    print("\nЭТАП 3 → Тактический период (3 месяца)")
    avg_orders_tac = int(input("Среднее кол-во заказов в день: ") or 2)
    ordered_pct = float(input("Ordered (%): ") or 65)
    quot_pct = float(input("Quotation (%): ") or 25)
    instock_pct = float(input("In stock (%): ") or 10)

    generate_in_period(
        period_type="tactical",
        avg_orders_per_day=avg_orders_tac,
        alpha=alpha,
        customers=customers,
        products=products,
        order_ctrl=order_ctrl,
        item_ctrl=item_ctrl,
        status_dist={"Ordered": ordered_pct/100, "Quotation": quot_pct/100, "In stock": instock_pct/100}
    )

    # ЭТАП 4: Стратегический
    print("\nЭТАП 4 → Стратегический период (6 месяцев)")
    avg_orders_str = int(input("Среднее кол-во заказов в день: ") or 1)
    ordered_pct = float(input("Ordered (%): ") or 70)
    quot_pct = float(input("Quotation (%): ") or 20)
    instock_pct = float(input("In stock (%): ") or 10)

    generate_in_period(
        period_type="strategic",
        avg_orders_per_day=avg_orders_str,
        alpha=alpha,
        customers=customers,
        products=products,
        order_ctrl=order_ctrl,
        item_ctrl=item_ctrl,
        status_dist={"Ordered": ordered_pct/100, "Quotation": quot_pct/100, "In stock": instock_pct/100}
    )

    print("\nГенерация завершена.")


def generate_in_period(period_type, avg_orders_per_day, alpha, customers, products,
                       order_ctrl, item_ctrl, status_dist=None, is_past=False):
    
    period = create_period(period_type)
    start_date, end_date = period.get_date_range()

    print(f"→ Генерация {period.get_level_name()} | {start_date} — {end_date}")

    if status_dist is None:
        status_dist = {"Ordered": 1.0}

    statuses = list(status_dist.keys())
    weights = list(status_dist.values())

    # Парето-веса клиентов
    customer_weights = pareto_weights([1.0] * len(customers), alpha)

    total_orders = 0
    total_items = 0
    current_date = start_date

    while current_date <= end_date:
        # Сезонные и дневные коэффициенты
        month = current_date.month
        is_weekend = current_date.weekday() >= 5
        is_end_of_month = current_date.day >= 25

        multiplier = 1.0
        if is_weekend:
            multiplier *= 0.33          # в 3 раза меньше
        if is_end_of_month:
            multiplier *= 1.5           # пик в конце месяца
        if month in [11, 12]:
            multiplier *= 1.2           # ноябрь-декабрь
        if 5 <= month <= 9:
            multiplier *= 1.2           # май-сентябрь

        orders_today = max(0, int(avg_orders_per_day * multiplier + random.choice([-1, 0, 1])))

        for _ in range(orders_today):
            # Выбор клиента по Парето
            customer_idx = np.random.choice(len(customers), p=customer_weights)
            customer = customers[customer_idx]

            if is_past:
                status = "Ordered"
                discount = 0.0
                advance = 0.0
                currency = "USD"
            else:
                status = random.choices(statuses, weights=weights, k=1)[0]
                discount = round(random.uniform(0, 5), 1)
                advance = round(random.uniform(5, 75), 1)
                currency = random.choice(["USD", "EUR", "RUB", "CNY", "JPY"])

            order_id = order_ctrl.create_order(
                customer_id=customer.id,
                currency=currency,
                discount_percent=discount,
                status=status,
                advance_percent=advance,
                advance_deadline_days=random.randint(1, 7),
                final_payment_days=random.randint(1, 7),
                risk_late_payment_days=random.randint(1, 15),
                order_date=current_date
            )

            if order_id:
                total_orders += 1

                # Логнормальное распределение количества изделий в заказе
                num_items = max(1, int(np.random.lognormal(mean=1.8, sigma=0.7)))

                for _ in range(num_items):
                    product = random.choice(products)
                    # Логнормальное количество штук
                    qty = max(1, int(np.random.lognormal(mean=2.2, sigma=0.9)))
                    item_ctrl.add_item(order_id, product.id, float(qty))
                    total_items += 1

                print(f"  ✓ {current_date} | {order_id} | {customer.company[:20]:<20} | "
                      f"{status:<10} | {num_items} поз. | {currency}")

        current_date += timedelta(days=1)

    print(f"   Завершено: {total_orders} заказов, {total_items} позиций")
    return total_orders, total_items


if __name__ == "__main__":
    generate_realistic_orders()
    input("\nНажмите Enter для завершения...")