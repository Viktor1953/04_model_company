# scripts/generate_products.py
"""
Генератор тестовых изделий (Products)
Запуск: python -m scripts.generate_products
"""

import random
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.controllers.product_controller import ProductController

# Список типичных названий продукции машиностроительных SMB компаний
product_nouns = [
    "Gear", "Shaft", "Bearing", "Valve", "Pump", "Motor", "Compressor", "Reducer",
    "Coupler", "Flange", "Bracket", "Housing", "Casing", "Rotor", "Stator", "Impeller",
    "Cylinder", "Piston", "Crankshaft", "Camshaft", "Sprocket", "Chain", "Belt", "Pulley",
    "Frame", "Chassis", "Arm", "Lever", "Hinge", "Lock", "Clamp", "Fixture", "Adapter",
    "Nozzle", "Fitting", "Connector", "Manifold", "Reservoir", "Tank", "HeatExchanger"
]

product_adjectives = [
    "Precision", "Heavy", "Industrial", "High", "Compact", "Robust", "Durable", "Stainless",
    "Alloy", "Hydraulic", "Pneumatic", "Electric", "Mechanical", "Rotary", "Linear", "Adjustable",
    "Reinforced", "Custom", "Standard", "HeavyDuty", "Lightweight", "Modular", "Sealed", "Coated"
]

uom_list = ["pcs", "kg", "m", "sq.m", "cu.m", "lm", "l", "t", "set"]
currency_list = ["USD", "EUR", "RUB", "CNY", "JPY"]


def generate_product_name():
    """Генерирует реалистичное название изделия"""
    adj = random.choice(product_adjectives)
    noun = random.choice(product_nouns)
    return f"{adj} {noun}"


def generate_products(count: int = 18, default_uom=True, default_currency=True):
    """Генерирует указанное количество изделий"""
    controller = ProductController()
    created = 0

    print(f"Начинаем генерацию {count} изделий...\n")

    for i in range(count):
        name = generate_product_name()
        
        # Единица измерения
        if default_uom:
            uom = "pcs"
        else:
            uom = random.choice(uom_list)
        
        # Цена
        unit_price = random.randint(200, 5000)
        
        # Валюта
        if default_currency:
            currency = "USD"
        else:
            currency = random.choice(currency_list)

        success = controller.create_product(name, uom, float(unit_price), currency)
        
        if success:
            created += 1
            print(f"✓ Создано: {name} | {uom} | {unit_price} {currency}")
        else:
            print(f"✗ Ошибка при создании изделия: {name}")

    print(f"\nГенерация завершена. Успешно создано: {created} изделий")


if __name__ == "__main__":
    print("=== Генератор тестовых изделий (Products) ===\n")
    
    while True:
        try:
            choice = input("Сколько изделий создать? (15-20, или 'q' для выхода): ").strip()
            if choice.lower() == 'q':
                break
                
            count = int(choice)
            if 15 <= count <= 20:
                print("\nВарианты генерации:")
                print("1. По умолчанию: UoM = pcs, Currency = USD")
                print("2. Случайный выбор UoM и Currency")
                
                mode = input("Выберите режим (1 или 2): ").strip()
                
                default_uom = mode != "2"
                default_currency = mode != "2"
                
                generate_products(count, default_uom, default_currency)
                break
            else:
                print("Пожалуйста, введите число от 15 до 20.")
        except ValueError:
            print("Введите число или 'q' для выхода.")

    input("\nНажмите Enter для завершения...")