# scripts/generate_suppliers.py
"""
Генератор тестовых поставщиков (15–20 записей)
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.controllers.supplier_controller import SupplierController

company_types = [
    "Precision", "Industrial", "Heavy", "Advanced", "Global", "Elite", "Supreme", 
    "Prime", "Reliable", "Tech", "Metal", "Forge", "Casting", "Components", "Systems"
]

company_nouns = [
    "Engineering", "Mechanics", "Metals", "Components", "Solutions", "Industries", 
    "Manufacturing", "Fabrication", "Supplies", "Technologies", "Group", "Works", "Labs"
]

currencies = ["USD", "EUR", "RUB", "CNY", "JPY"]


def generate_company_name():
    return f"{random.choice(company_types)} {random.choice(company_nouns)}"


def generate_suppliers(count: int = 18):
    controller = SupplierController()
    created = 0

    print(f"Генерация {count} поставщиков...\n")

    for i in range(count):
        company_name = generate_company_name()
        currency = random.choice(currencies)
        distance_km = round(random.uniform(15, 500), 1)
        reliability = round(random.uniform(0.65, 0.98), 2)

        success = controller.create_supplier(
            company_name=company_name,
            currency=currency,
            distance_km=distance_km,
            reliability_score=reliability
        )

        if success:
            created += 1
            print(f"✓ {company_name:<35} | {currency:<4} | {distance_km:6.1f} км | Надёжность: {reliability:.2f}")

    print(f"\n✅ Создано поставщиков: {created}")


if __name__ == "__main__":
    count = int(input("Сколько поставщиков создать (15-25): ") or 18)
    generate_suppliers(count)
    input("\nНажмите Enter для завершения...")