# src/views/customer_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PySide6.QtCore import Qt

from src.controllers.customer_controller import CustomerController
from src.views.customer_dialog import CustomerDialog   # предполагаем, что диалог уже есть


class CustomerView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = CustomerController()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Панель кнопок
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Добавить клиента")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить выбранного")
        self.btn_clear = QPushButton("Очистить всех клиентов")   # ← Новая кнопка
        self.btn_refresh = QPushButton("Обновить")

        self.btn_add.clicked.connect(self.add_customer)
        self.btn_edit.clicked.connect(self.edit_customer)
        self.btn_delete.clicked.connect(self.delete_customer)
        self.btn_clear.clicked.connect(self.clear_all_customers)   # ← Подключение
        self.btn_refresh.clicked.connect(self.refresh_table)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)

        main_layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Клиент", "Расстояние, км"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        customers = self.controller.get_all_customers()
        self.table.setRowCount(len(customers))

        for row, cust in enumerate(customers):
            self.table.setItem(row, 0, QTableWidgetItem(str(cust.id)))
            self.table.setItem(row, 1, QTableWidgetItem(cust.company))
            self.table.setItem(row, 2, QTableWidgetItem(f"{cust.distance_km:.1f}"))

    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def edit_customer(self):
        row = self.table.currentRow()
        if row < 0:
            return
        customer_id = self.table.item(row, 0).text()
        # Здесь можно добавить редактирование (пока пропускаем для краткости)

    def delete_customer(self):
        row = self.table.currentRow()
        if row < 0:
            return
        customer_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удаление", f"Удалить клиента {customer_id}?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.delete_customer(customer_id)
            self.refresh_table()

    def clear_all_customers(self):
        reply = QMessageBox.question(self, "Очистка таблицы", 
                                     "Удалить ВСЕХ клиентов?\n\nЭто действие нельзя отменить!",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            customers = self.controller.get_all_customers()
            for cust in customers:
                self.controller.delete_customer(cust.id)
            QMessageBox.information(self, "Готово", "Все клиенты удалены.")
            self.refresh_table()