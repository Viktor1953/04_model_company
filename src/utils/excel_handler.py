# src/utils/excel_handler.py
import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox
from datetime import datetime

from src.controllers.customer_controller import CustomerController
from src.controllers.product_controller import ProductController
from src.controllers.supplier_controller import SupplierController
from src.controllers.product_component_controller import ProductComponentController


class ExcelHandler:
    def __init__(self):
        self.customer_controller = CustomerController()
        self.product_controller = ProductController()
        self.supplier_controller = SupplierController()
        self.component_controller = ProductComponentController()

    # ====================== CUSTOMERS ======================
    def export_customers(self, parent=None):
        customers = self.customer_controller.get_all_customers()
        if not customers:
            QMessageBox.warning(parent, "Экспорт", "Нет данных для экспорта клиентов.")
            return

        data = [{"ID": c.id, "Компания": c.company, "Расстояние км": c.distance_km} for c in customers]
        df = pd.DataFrame(data)

        filename, _ = QFileDialog.getSaveFileName(
            parent, "Сохранить клиентов", 
            f"customers_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", 
            "Excel Files (*.xlsx)"
        )
        if filename:
            try:
                df.to_excel(filename, index=False, sheet_name="Customers")
                QMessageBox.information(parent, "Успех", f"Клиенты успешно экспортированы в:\n{filename}")
            except Exception as e:
                QMessageBox.critical(parent, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def import_customers(self, parent=None):
        filename, _ = QFileDialog.getOpenFileName(parent, "Выберите файл клиентов", "", "Excel Files (*.xlsx)")
        if not filename:
            return False
        try:
            df = pd.read_excel(filename, sheet_name="Customers")
            imported = 0
            for _, row in df.iterrows():
                try:
                    self.customer_controller.create_customer(
                        company=str(row.get("Компания", "")),
                        distance_km=float(row.get("Расстояние км", 0))
                    )
                    imported += 1
                except:
                    continue
            QMessageBox.information(parent, "Импорт", f"Импортировано {imported} клиентов.")
            return True
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Не удалось импортировать клиентов:\n{str(e)}")
            return False

    # ====================== PRODUCTS ======================
    def export_products(self, parent=None):
        products = self.product_controller.get_all_products()
        if not products:
            QMessageBox.warning(parent, "Экспорт", "Нет данных для экспорта изделий.")
            return

        data = [{
            "ID": p.id,
            "Название": p.name,
            "Ед.изм.": p.uom,
            "Цена": p.unit_price,
            "Валюта": p.currency
        } for p in products]

        df = pd.DataFrame(data)
        filename, _ = QFileDialog.getSaveFileName(
            parent, "Сохранить изделия", 
            f"products_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", 
            "Excel Files (*.xlsx)"
        )
        if filename:
            df.to_excel(filename, index=False, sheet_name="Products")
            QMessageBox.information(parent, "Успех", f"Изделия успешно экспортированы.")

    def import_products(self, parent=None):
        filename, _ = QFileDialog.getOpenFileName(parent, "Выберите файл изделий", "", "Excel Files (*.xlsx)")
        if not filename:
            return False
        try:
            df = pd.read_excel(filename, sheet_name="Products")
            imported = 0
            for _, row in df.iterrows():
                try:
                    self.product_controller.create_product(
                        name=str(row.get("Название", "")),
                        uom=str(row.get("Ед.изм.", "pcs")),
                        unit_price=float(row.get("Цена", 0)),
                        currency=str(row.get("Валюта", "USD"))
                    )
                    imported += 1
                except:
                    continue
            QMessageBox.information(parent, "Импорт", f"Импортировано {imported} изделий.")
            return True
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Не удалось импортировать изделия:\n{str(e)}")
            return False

    # ====================== SUPPLIERS ======================
    def export_suppliers(self, parent=None):
        suppliers = self.supplier_controller.get_all_suppliers()
        if not suppliers:
            QMessageBox.warning(parent, "Экспорт", "Нет данных для экспорта поставщиков.")
            return

        data = [{
            "ID": s.id,
            "Компания": s.company_name,
            "Валюта": s.currency,
            "Расстояние км": s.distance_km,
            "Надёжность": s.reliability_score
        } for s in suppliers]

        df = pd.DataFrame(data)
        filename, _ = QFileDialog.getSaveFileName(
            parent, "Сохранить поставщиков", 
            f"suppliers_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", 
            "Excel Files (*.xlsx)"
        )
        if filename:
            df.to_excel(filename, index=False, sheet_name="Suppliers")
            QMessageBox.information(parent, "Успех", f"Поставщики успешно экспортированы.")

    def import_suppliers(self, parent=None):
        filename, _ = QFileDialog.getOpenFileName(parent, "Выберите файл поставщиков", "", "Excel Files (*.xlsx)")
        if not filename:
            return False
        try:
            df = pd.read_excel(filename, sheet_name="Suppliers")
            imported = 0
            for _, row in df.iterrows():
                try:
                    self.supplier_controller.create_supplier(
                        company_name=str(row.get("Компания", "")),
                        currency=str(row.get("Валюта", "USD")),
                        distance_km=float(row.get("Расстояние км", 100)),
                        reliability_score=float(row.get("Надёжность", 0.85))
                    )
                    imported += 1
                except:
                    continue
            QMessageBox.information(parent, "Импорт", f"Импортировано {imported} поставщиков.")
            return True
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Не удалось импортировать поставщиков:\n{str(e)}")
            return False

    # ====================== PRODUCT COMPONENTS ======================
    def export_product_components(self, parent=None):
        """Экспорт состава изделий с понятными колонками"""
        components = self.component_controller.get_all_components()
        if not components:
            QMessageBox.warning(parent, "Экспорт", "Нет данных для экспорта состава изделий.")
            return

        data = [{
            "ID Компонента": c.id,
            "ID Изделия": c.product_id,
            "Название Изделия": getattr(c, 'product_name', '') or c.product_id,
            "Название Компонента": c.component_name,
            "MCR/GU": c.mcr_gu,
            "Производственные потери %": c.manufacturing_losses_pct,
            "Неисправимый брак %": c.scrap_pct,
            "TMC/GU": c.tmc_gu,
            "Ед.изм.": c.uom,
            "Примечания": c.notes or ""
        } for c in components]

        df = pd.DataFrame(data)

        filename, _ = QFileDialog.getSaveFileName(
            parent,
            "Сохранить состав изделий",
            f"product_components_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            "Excel Files (*.xlsx)"
        )

        if filename:
            try:
                df.to_excel(filename, index=False, sheet_name="ProductComponents")
                QMessageBox.information(parent, "Успех", 
                                      f"Состав изделий успешно экспортирован в:\n{filename}")
            except Exception as e:
                QMessageBox.critical(parent, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def import_product_components(self, parent=None):
        """Импорт состава изделий из Excel"""
        filename, _ = QFileDialog.getOpenFileName(
            parent,
            "Выберите файл состава изделий",
            "",
            "Excel Files (*.xlsx)"
        )
        if not filename:
            return False

        try:
            df = pd.read_excel(filename, sheet_name="ProductComponents")
            
            required = ["ID Изделия", "Название Компонента", "MCR/GU"]
            missing = [col for col in required if col not in df.columns]
            if missing:
                QMessageBox.warning(parent, "Ошибка импорта", 
                                    f"Отсутствуют обязательные колонки: {missing}")
                return False

            imported = 0
            for _, row in df.iterrows():
                try:
                    self.component_controller.create_component(
                        product_id=str(row.get("ID Изделия", "")),
                        component_name=str(row.get("Название Компонента", "")),
                        mcr_gu=float(row.get("MCR/GU", 0)),
                        manufacturing_losses_pct=float(row.get("Производственные потери %", 0)),
                        scrap_pct=float(row.get("Неисправимый брак %", 0)),
                        uom=str(row.get("Ед.изм.", "pcs")),
                        notes=str(row.get("Примечания", "")) if pd.notna(row.get("Примечания")) else None
                    )
                    imported += 1
                except Exception as inner_e:
                    print(f"Пропущена строка: {inner_e}")
                    continue

            QMessageBox.information(parent, "Импорт", 
                                    f"Успешно импортировано {imported} компонентов в состав изделий.")
            return True

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка импорта", f"Не удалось прочитать файл:\n{str(e)}")
            return False