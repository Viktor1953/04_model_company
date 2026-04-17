# src/views/customer_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog   # ← Добавили QDialog
)
from PySide6.QtCore import Qt

from src.controllers.customer_controller import CustomerController
from src.utils.excel_handler import ExcelHandler
from src.views.customer_dialog import CustomerDialog   # ← Импорт диалога


class CustomerView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = CustomerController()
        self.excel_handler = ExcelHandler()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Панель кнопок
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Добавить клиента")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить таблицу")
        self.btn_export = QPushButton("Экспорт в Excel")
        self.btn_import = QPushButton("Импорт из Excel")

        self.btn_add.clicked.connect(self.add_customer)
        self.btn_edit.clicked.connect(self.edit_customer)
        self.btn_delete.clicked.connect(self.delete_customer)
        self.btn_refresh.clicked.connect(self.refresh_table)
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_import.clicked.connect(self.import_from_excel)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_import)

        layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Компания", "Расстояние, км"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        customers = self.controller.get_all_customers()
        self.table.setRowCount(len(customers))

        for row, customer in enumerate(customers):
            self.table.setItem(row, 0, QTableWidgetItem(str(customer.id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(customer.company)))
            self.table.setItem(row, 2, QTableWidgetItem(str(customer.distance_km)))

    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def edit_customer(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите клиента для редактирования")
            return

        customer_id = self.table.item(row, 0).text()
        customer = self.controller.get_by_id(customer_id)
        if customer:
            dialog = CustomerDialog(self, customer)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_table()

    def delete_customer(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите клиента для удаления")
            return

        customer_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Удалить клиента {customer_id}?", 
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.controller.delete_customer(customer_id):
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить клиента")

    def export_to_excel(self):
        data = []
        for row in range(self.table.rowCount()):
            row_data = [
                self.table.item(row, 0).text(),
                self.table.item(row, 1).text(),
                float(self.table.item(row, 2).text())
            ]
            data.append(row_data)
        self.excel_handler.export_customers(data, self)

    def import_from_excel(self):
        if self.excel_handler.import_customers(self):
            self.refresh_table()