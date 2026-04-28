# src/views/supplier_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PySide6.QtCore import Qt

from src.controllers.supplier_controller import SupplierController
from src.views.supplier_dialog import SupplierDialog
from src.utils.excel_handler import ExcelHandler


class SupplierView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = SupplierController()
        self.excel_handler = ExcelHandler()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Добавить поставщика")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_clear = QPushButton("Очистить всех поставщиков")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_export = QPushButton("Экспорт в Excel")
        self.btn_import = QPushButton("Импорт из Excel")

        self.btn_add.clicked.connect(self.add_supplier)
        self.btn_edit.clicked.connect(self.edit_supplier)
        self.btn_delete.clicked.connect(self.delete_supplier)
        self.btn_clear.clicked.connect(self.clear_all_suppliers)
        self.btn_refresh.clicked.connect(self.refresh_table)
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_import.clicked.connect(self.import_from_excel)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_import)

        main_layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Компания", "Валюта", "Расстояние (км)", "Надёжность"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        suppliers = self.controller.get_all_suppliers()
        self.table.setRowCount(len(suppliers))

        for row, s in enumerate(suppliers):
            self.table.setItem(row, 0, QTableWidgetItem(str(s.id)))
            self.table.setItem(row, 1, QTableWidgetItem(s.company_name))
            self.table.setItem(row, 2, QTableWidgetItem(s.currency))
            self.table.setItem(row, 3, QTableWidgetItem(f"{s.distance_km:.1f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{s.reliability_score:.2f}"))

    def add_supplier(self):
        dialog = SupplierDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def edit_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите поставщика для редактирования")
            return

        supplier_id = self.table.item(row, 0).text()
        supplier = self.controller.get_supplier_by_id(supplier_id)   # нужно добавить этот метод

        if supplier:
            dialog = SupplierDialog(self, supplier)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_table()

    def delete_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            return
        supplier_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удаление", f"Удалить поставщика {supplier_id}?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.controller.delete_supplier(supplier_id):
                self.refresh_table()

    def clear_all_suppliers(self):
        reply = QMessageBox.question(self, "Очистка", 
                                     "Удалить ВСЕХ поставщиков?\n\nЭто действие нельзя отменить!",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.clear_all_suppliers()
            QMessageBox.information(self, "Готово", "Все поставщики удалены.")
            self.refresh_table()

    def export_to_excel(self):
        self.excel_handler.export_suppliers(self)

    def import_from_excel(self):
        if self.excel_handler.import_suppliers(self):
            self.refresh_table()