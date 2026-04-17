# scripts/generate_customers.py
"""
Генератор тестовых клиентов для демонстрации и отладки
Запуск: python -m scripts.generate_customers
"""

import random
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.controllers.customer_controller import CustomerController

# Список существительных, отражающих специфику клиентов машиностроительных компаний
company_nouns = [
    "Steel", "Forge", "Metal", "Precision", "Heavy", "Industrial", "Mining", "Construction",
    "Transport", "Logistics", "Agro", "Farm", "Oil", "Gas", "Chemical", "Power", "Energy",
    "Auto", "Truck", "Rail", "Marine", "Aero", "Defense", "Machinery", "Equipment", "Plant",
    "Foundry", "Fabrication", "Assembly", "Welding", "Cutting", "Press", "Hydraulic", "Pneumatic"
]

company_adjectives = [
    "Global", "National", "Regional", "Premier", "Advanced", "Modern", "Elite", "Pro",
    "Master", "Expert", "Supreme", "Prime", "First", "Leading", "Top", "Golden", "Silver",
    "Dynamic", "Innovative", "Reliable", "Strong", "Powerful", "Rapid", "Swift", "Secure"
]

def generate_company_name():
    """Генерирует реалистичное название компании"""
    adj = random.choice(company_adjectives)
    noun = random.choice(company_nouns)
    suffix = random.choice(["Corp", "Inc", "Ltd", "Group", "LLC", "Industries", "Engineering", "Works"])
    return f"{adj} {noun} {suffix}"


def generate_customers(count: int = 22):
    """Генерирует указанное количество клиентов"""
    controller = CustomerController()
    created = 0

    print(f"Начинаем генерацию {count} клиентов...\n")

    for i in range(count):
        company = generate_company_name()
        distance = random.randint(10, 200)

        success = controller.create_customer(company, float(distance))
        if success:
            created += 1
            print(f"✓ Создан: {company} | {distance} км")
        else:
            print(f"✗ Ошибка при создании клиента {company}")

    print(f"\nГенерация завершена. Успешно создано: {created} клиентов")


if __name__ == "__main__":
    print("=== Генератор тестовых клиентов ===\n")
    
    while True:
        try:
            choice = input("Сколько клиентов создать? (20-25, или 'q' для выхода): ").strip()
            if choice.lower() == 'q':
                break
            count = int(choice)
            if 20 <= count <= 25:
                generate_customers(count)
                break
            else:
                print("Пожалуйста, введите число от 20 до 25.")
        except ValueError:
            print("Введите число или 'q' для выхода.")

    input("\nНажмите Enter для завершения...")