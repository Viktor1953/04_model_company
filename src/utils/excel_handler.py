# src/utils/excel_handler.py
import pandas as pd
from src.controllers.customer_controller import CustomerController 
from src.controllers.product_controller import ProductController
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows


class ExcelHandler:
    def __init__(self):
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.default_file = self.output_dir / "tem_data.xlsx"

    # ====================== ЭКСПОРТ ======================

    def export_customers(self, customers_list: list, parent=None):
        """Экспорт клиентов в Excel с красивым форматированием"""
        if not customers_list:
            QMessageBox.information(parent, "Инфо", "Нет данных для экспорта")
            return False

        df = pd.DataFrame(customers_list, columns=["ID", "Компания", "Расстояние, км"])

        try:
            file_path = self._get_save_path("Клиенты", parent)
            if not file_path:
                return False

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Customers", index=False)

                # Красивое форматирование
                workbook = writer.book
                worksheet = writer.sheets["Customers"]

                # Заголовки
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="1f538d", end_color="1f538d", fill_type="solid")

                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center")

                # Автоподбор ширины
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            QMessageBox.information(parent, "Успех", f"Клиенты успешно экспортированы в:\n{file_path}")
            return True

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Ошибка экспорта клиентов:\n{str(e)}")
            return False

    def export_products(self, products_list: list, parent=None):
        """Экспорт изделий в Excel"""
        if not products_list:
            QMessageBox.information(parent, "Инфо", "Нет данных для экспорта")
            return False

        df = pd.DataFrame(products_list, columns=["ID", "Название", "Ед.изм.", "Цена", "Валюта"])

        try:
            file_path = self._get_save_path("Изделия", parent)
            if not file_path:
                return False

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Products", index=False)

                workbook = writer.book
                worksheet = writer.sheets["Products"]

                # Форматирование заголовков
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="1f538d", end_color="1f538d", fill_type="solid")

                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center")

                # Форматирование цены
                for row in worksheet.iter_rows(min_row=2, min_col=4, max_col=4):
                    for cell in row:
                        cell.number_format = '#,##0.00'

            QMessageBox.information(parent, "Успех", f"Изделия успешно экспортированы в:\n{file_path}")
            return True

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Ошибка экспорта изделий:\n{str(e)}")
            return False

    def _get_save_path(self, name: str, parent=None):
        """Диалог сохранения файла"""
        default_name = f"tem_{name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            f"Сохранить {name}",
            str(self.output_dir / default_name),
            "Excel Files (*.xlsx)"
        )
        return file_path if file_path else None

    # ====================== ИМПОРТ ======================

    def import_customers(self, parent=None):
        """Импорт клиентов из Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent, "Выберите файл с клиентами", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return False

        try:
            df = pd.read_excel(file_path)
            # Приводим названия колонок к ожидаемым
            df.columns = [col.strip() for col in df.columns]

            controller = CustomerController()  # будет импортировано позже
            success_count = 0

            for _, row in df.iterrows():
                try:
                    company = str(row.get("Компания", row.get("Customer", ""))).strip()
                    distance = float(row.get("Расстояние, км", row.get("Distance, km", 0)))
                    if company:
                        controller.create_customer(company, distance)
                        success_count += 1
                except:
                    continue

            QMessageBox.information(parent, "Импорт завершён", 
                                  f"Успешно импортировано {success_count} клиентов.")
            return True

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка импорта", f"Не удалось прочитать файл:\n{str(e)}")
            return False

    def import_products(self, parent=None):
        """Импорт изделий из Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent, "Выберите файл с изделиями", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return False

        try:
            df = pd.read_excel(file_path)
            df.columns = [col.strip() for col in df.columns]

            controller = ProductController()
            success_count = 0

            for _, row in df.iterrows():
                try:
                    name = str(row.get("Название", "")).strip()
                    uom = str(row.get("Ед.изм.", "pcs")).strip()
                    price = float(row.get("Цена", 0))
                    currency = str(row.get("Валюта", "RUB")).strip()

                    if name:
                        controller.create_product(name, uom, price, currency)
                        success_count += 1
                except:
                    continue

            QMessageBox.information(parent, "Импорт завершён", 
                                  f"Успешно импортировано {success_count} изделий.")
            return True

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка импорта", f"Не удалось прочитать файл:\n{str(e)}")
            return False
        
    