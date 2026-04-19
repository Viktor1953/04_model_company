# scripts/generate_products.py
"""
Генератор тестовых изделий с выбором базовой валюты
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.controllers.product_controller import ProductController

# Списки для генерации реалистичных названий изделий
product_nouns = [
    "Gear", "Shaft", "Bearing", "Valve", "Pump", "Motor", "Compressor", "Reducer",
    "Flange", "Bracket", "Housing", "Rotor", "Impeller", "Cylinder", "Piston",
    "Sprocket", "Chain", "Pulley", "Frame", "Chassis", "Nozzle", "Fitting",
    "Manifold", "Reservoir", "HeatExchanger", "Actuator", "Sensor", "Controller"
]

product_adjectives = [
    "Precision", "Heavy", "Industrial", "High", "Compact", "Robust", "Durable",
    "Alloy", "Hydraulic", "Pneumatic", "Electric", "Mechanical", "Rotary", "Linear",
    "Reinforced", "Custom", "Standard", "HeavyDuty", "Modular", "Sealed"
]

uom_list = ["pcs", "kg", "m", "sq.m", "cu.m", "lm", "l", "t", "set"]
currency_list = ["USD", "EUR", "RUB", "CNY", "JPY"]


def generate_product_name():
    """Генерирует название изделия"""
    return f"{random.choice(product_adjectives)} {random.choice(product_nouns)}"


def generate_products(count: int = 18):
    """Основная функция генерации изделий"""
    controller = ProductController()
    created = 0

    print("=== Генератор тестовых изделий ===\n")

    # Выбор базовой валюты
    base_currency = input("Введите базовую валюту (по умолчанию USD): ").strip().upper()
    if base_currency not in currency_list:
        base_currency = "USD"
        print(f"Базовая валюта установлена: {base_currency}")

    print(f"Базовая валюта: {base_currency}")
    print(f"Генерируем {count} изделий...\n")

    for i in range(count):
        name = generate_product_name()
        uom = random.choice(uom_list)
        
        # Цена: базовая валюта имеет "нормальный" диапазон, остальные — с разбросом
        if base_currency == "USD":
            unit_price = random.randint(200, 5000)
        else:
            unit_price = round(random.randint(200, 5000) * random.uniform(0.75, 1.35), 2)

        # По умолчанию все изделия создаются в базовой валюте
        currency = base_currency

        success = controller.create_product(name, uom, unit_price, currency)
        if success:
            created += 1
            print(f"✓ {name:<35} | {uom:<6} | {unit_price:8.2f} {currency}")

    print(f"\n✅ Генерация завершена. Создано изделий: {created}")


if __name__ == "__main__":
    try:
        count = int(input("Сколько изделий создать? (15-25): ") or 18)
        if 15 <= count <= 25:
            generate_products(count)
        else:
            print("Количество должно быть от 15 до 25.")
    except ValueError:
        print("Введите число.")
    
    input("\nНажмите Enter для завершения...")