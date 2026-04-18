# src/utils/excel_handler.py
import pandas as pd
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox
from openpyxl.styles import Font, PatternFill, Alignment

from src.controllers.customer_controller import CustomerController
from src.controllers.product_controller import ProductController
from src.controllers.customer_order_controller import CustomerOrderController
from src.controllers.customer_order_item_controller import CustomerOrderItemController


class ExcelHandler:
    def __init__(self):
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ====================== ЭКСПОРТ ЗАКАЗОВ (с двумя листами) ======================
    def export_customer_orders_full(self, parent=None):
        """Экспорт заказов с двумя листами: заголовки + детали"""
        try:
            order_controller = CustomerOrderController()
            item_controller = CustomerOrderItemController()

            orders = order_controller.get_all_orders()

            if not orders:
                QMessageBox.information(parent, "Инфо", "Нет заказов для экспорта")
                return False

            # Подготовка данных для заголовков
            orders_data = []
            items_data = []

            for order in orders:
                total_value = self._calculate_order_value(order.id, item_controller)

                orders_data.append({
                    "ID": order.id,
                    "Дата": order.order_date,
                    "ID Клиента": order.customer_id,
                    "Валюта": order.currency,
                    "Скидка %": order.discount_percent,
                    "Сумма заказа": total_value,
                    "Статус": order.status,
                    "Аванс %": order.advance_percent
                })

                # Детали заказа
                items = item_controller.get_items_by_order(order.id)
                for item in items:
                    total_item = item.qty * (item.product.unit_price if item.product else 0)
                    items_data.append({
                        "ID Заказа": order.id,
                        "ID Изделия": item.product_id,
                        "Название": item.product.name if item.product else "—",
                        "Кол-во": item.qty,
                        "Ед.изм.": item.product.uom if item.product else "—",
                        "Цена": item.product.unit_price if item.product else 0,
                        "Сумма позиции": total_item
                    })

            # Создаём Excel-файл с двумя листами
            file_path = self._get_save_path("Полные_Заказы", parent)
            if not file_path:
                return False

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Лист 1 — Заголовки заказов
                pd.DataFrame(orders_data).to_excel(writer, sheet_name="Customer_Orders", index=False)
                # Лист 2 — Позиции заказов
                pd.DataFrame(items_data).to_excel(writer, sheet_name="Order_Items", index=False)

                # Форматирование заголовков
                self._format_header(writer.sheets["Customer_Orders"])
                self._format_header(writer.sheets["Order_Items"])

            QMessageBox.information(parent, "Успех", 
                                  f"Заказы успешно экспортированы в файл:\n{file_path}\n\n"
                                  f"Листы: Customer_Orders и Order_Items")
            return True

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Ошибка экспорта заказов:\n{str(e)}")
            return False

    def _calculate_order_value(self, order_id: str, item_controller) -> float:
        items = item_controller.get_items_by_order(order_id)
        total = 0.0
        for item in items:
            total += item.qty * (item.product.unit_price if item.product else 0)
        return total

    # ====================== Вспомогательные методы ======================
    def _get_save_path(self, name: str, parent=None):
        default_name = f"tem_{name}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            f"Сохранить {name}",
            str(self.output_dir / default_name),
            "Excel Files (*.xlsx)"
        )
        return file_path if file_path else None

    def _format_header(self, worksheet):
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1f538d", end_color="1f538d", fill_type="solid")

        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

    # ====================== Старые методы (оставляем для совместимости) ======================
    def export_customers(self, customers_list: list, parent=None):
        # ... (оставляем как было)
        pass

    def export_products(self, products_list: list, parent=None):
        # ... (оставляем как было)
        pass

    def import_customers(self, parent=None):
        # ... (оставляем как было)
        pass

    def import_products(self, parent=None):
        # ... (оставляем как было)
        pass

    def import_customer_orders(self, parent=None):
        """Импорт заказов с созданием новых ID (чтобы избежать конфликта duplicate key)"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent, "Импорт заказов клиентов", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return False

        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            # Читаем листы
            if "Customer_Orders" in sheet_names:
                df_orders = pd.read_excel(excel_file, "Customer_Orders")
            else:
                df_orders = pd.read_excel(excel_file, sheet_name=0)

            if "Order_Items" in sheet_names:
                df_items = pd.read_excel(excel_file, "Order_Items")
            else:
                df_items = pd.DataFrame()

            df_orders.columns = [str(col).strip() for col in df_orders.columns]
            if not df_items.empty:
                df_items.columns = [str(col).strip() for col in df_items.columns]

            order_controller = CustomerOrderController()
            item_controller = CustomerOrderItemController()

            success_orders = 0
            success_items = 0
            order_id_mapping = {}   # Старый ID → Новый ID

            # 1. Импорт заголовков с генерацией новых ID
            for _, row in df_orders.iterrows():
                try:
                    customer_id = str(row.get("ID Клиента", row.get("Customer ID", ""))).strip()
                    if not customer_id:
                        continue

                    currency = str(row.get("Валюта", "USD")).strip()
                    discount = float(row.get("Скидка %", 0))
                    status = str(row.get("Статус", "Quotation")).strip()
                    advance = float(row.get("Аванс %", 0))

                    # Создаём новый заказ с новым ID
                    new_order_id = order_controller.create_order(
                        customer_id=customer_id,
                        currency=currency,
                        discount_percent=discount,
                        status=status,
                        advance_percent=advance
                    )

                    if new_order_id:
                        success_orders += 1
                        # Сохраняем соответствие старого ID → нового ID
                        old_order_id = str(row.get("ID", "")).strip()
                        if old_order_id:
                            order_id_mapping[old_order_id] = new_order_id

                        # 2. Импорт позиций для этого заказа
                        if not df_items.empty and old_order_id:
                            order_items = df_items[
                                df_items.get("ID Заказа", df_items.get("Order ID", "")) == old_order_id
                            ]
                            for _, item_row in order_items.iterrows():
                                try:
                                    product_id = str(item_row.get("ID Изделия", item_row.get("Product ID", ""))).strip()
                                    qty = float(item_row.get("Кол-во", item_row.get("Qty", 0)))
                                    if product_id and qty > 0:
                                        item_controller.add_item(new_order_id, product_id, qty)
                                        success_items += 1
                                except:
                                    continue
                except Exception as e:
                    print(f"Ошибка импорта заказа: {e}")
                    continue

            msg = f"Импорт завершён успешно!\n\n"
            msg += f"Создано новых заказов: {success_orders}\n"
            msg += f"Добавлено позиций изделий: {success_items}\n\n"
            msg += f"Старые ID заказов были заменены на новые."

            QMessageBox.information(parent, "Импорт завершён", msg)
            return True

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка импорта", f"Не удалось прочитать файл:\n{str(e)}")
            return False