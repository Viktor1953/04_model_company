# scripts/generate_product_components.py
"""
Генератор состава изделий (ProductComponents)
Заполняет компоненты для существующих изделий
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.controllers.product_controller import ProductController
from src.controllers.product_component_controller import ProductComponentController


def generate_product_components():
    print("=== ГЕНЕРАТОР СОСТАВА ИЗДЕЛИЙ ===\n")

    product_ctrl = ProductController()
    component_ctrl = ProductComponentController()

    products = product_ctrl.get_all_products()
    if not products:
        print("❌ Ошибка: Нет изделий в базе. Сначала создайте изделия.")
        return

    print(f"Найдено изделий: {len(products)}\n")

    total_created = 0

    for product in products:
        # Для каждого изделия создаём от 3 до 8 компонентов
        num_components = random.randint(3, 8)
        print(f"→ Изделие {product.name} ({product.id}) — добавляем {num_components} компонентов")

        for i in range(num_components):
            component_name = random.choice([
                "Steel Body", "Aluminum Housing", "Copper Winding", "Bearing Set", 
                "Gear Assembly", "Shaft", "Seals", "Bolts Kit", "Electrical Connector",
                "Rubber Gasket", "Precision Spring", "Hydraulic Valve", "Sensor Unit"
            ])

            mcr_gu = round(random.uniform(0.5, 25.0), 3)
            losses = round(random.uniform(0.5, 8.0), 1)
            scrap = round(random.uniform(0.2, 3.0), 1)
            uom = random.choice(["pcs", "kg", "m", "set"])

            notes = random.choice(["Critical", "Standard", "Consumable", ""]) if random.random() > 0.6 else None

            try:
                component_ctrl.create_component(
                    product_id=product.id,
                    component_name=component_name,
                    mcr_gu=mcr_gu,
                    manufacturing_losses_pct=losses,
                    scrap_pct=scrap,
                    uom=uom,
                    notes=notes
                )
                total_created += 1
                print(f"   ✓ {component_name} | MCR: {mcr_gu} | TMC: {mcr_gu*(1+losses/100+scrap/100):.3f} {uom}")
            except Exception as e:
                print(f"   ✗ Ошибка при создании компонента: {e}")

    print(f"\n✅ Генерация завершена. Создано компонентов: {total_created}")


if __name__ == "__main__":
    generate_product_components()
    input("\nНажмите Enter для завершения...")