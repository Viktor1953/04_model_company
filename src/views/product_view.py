# src/views/product_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PySide6.QtCore import Qt

from src.controllers.product_controller import ProductController
# from src.views.product_dialog import ProductDialog   # раскомментируй, когда будет диалог


class ProductView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ProductController()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Панель кнопок
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Добавить изделие")
        self.btn_edit = QPushButton("Редактировать")      # ← кнопка есть
        self.btn_delete = QPushButton("Удалить")
        self.btn_clear = QPushButton("Очистить все изделия")
        self.btn_refresh = QPushButton("Обновить")

        self.btn_add.clicked.connect(self.add_product)
        self.btn_edit.clicked.connect(self.edit_product)      # ← теперь метод существует
        self.btn_delete.clicked.connect(self.delete_product)
        self.btn_clear.clicked.connect(self.clear_all_products)
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Ед.изм.", "Цена", "Валюта"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        products = self.controller.get_all_products()
        self.table.setRowCount(len(products))

        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(row, 1, QTableWidgetItem(p.name))
            self.table.setItem(row, 2, QTableWidgetItem(p.uom))
            self.table.setItem(row, 3, QTableWidgetItem(f"{p.unit_price:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(p.currency))

    def add_product(self):
        # Пока просто сообщение, потом подключишь диалог
        QMessageBox.information(self, "Добавление", "Функция добавления изделия будет доступна после создания диалога.")
        # dialog = ProductDialog(self)
        # if dialog.exec() == QDialog.Accepted:
        #     self.refresh_table()

    def edit_product(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите изделие для редактирования")
            return
        prod_id = self.table.item(row, 0).text()
        QMessageBox.information(self, "Редактирование", f"Редактирование изделия {prod_id} пока не реализовано.")

    def delete_product(self):
        row = self.table.currentRow()
        if row < 0:
            return
        prod_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удаление", 
                                     f"Удалить изделие {prod_id}?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.controller.delete_product(prod_id):
                self.refresh_table()

    def clear_all_products(self):
        reply = QMessageBox.question(self, "Очистка", 
                                     "Удалить ВСЕ изделия?\n\nЭто действие нельзя отменить!",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            products = self.controller.get_all_products()
            for p in products:
                self.controller.delete_product(p.id)
            QMessageBox.information(self, "Готово", "Все изделия удалены.")
            self.refresh_table()