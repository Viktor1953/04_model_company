# src/views/customer_order_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QSplitter, QInputDialog
)
from PySide6.QtCore import Qt

from src.controllers.customer_order_controller import CustomerOrderController
from src.controllers.customer_order_item_controller import CustomerOrderItemController
from src.views.customer_order_dialog import CustomerOrderDialog
from src.views.customer_order_item_dialog import CustomerOrderItemDialog
from src.utils.excel_handler import ExcelHandler


class CustomerOrderView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = CustomerOrderController()
        self.item_controller = CustomerOrderItemController()
        self.excel_handler = ExcelHandler()
        self.current_order_id = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Панель кнопок
        btn_layout = QHBoxLayout()

        self.btn_add_order = QPushButton("Новый заказ")
        self.btn_add_item = QPushButton("Добавить изделие")
        self.btn_edit_order = QPushButton("Редактировать заказ")
        self.btn_delete_order = QPushButton("Удалить заказ")
        self.btn_delete_all = QPushButton("Удалить ВСЕ заказы")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_export = QPushButton("Экспорт в Excel")   # ← Вернули
        self.btn_import = QPushButton("Импорт из Excel")   # ← Вернули

        self.btn_add_order.clicked.connect(self.add_order)
        self.btn_add_item.clicked.connect(self.add_item_to_order)
        self.btn_edit_order.clicked.connect(self.edit_order)
        self.btn_delete_order.clicked.connect(self.delete_order)
        self.btn_delete_all.clicked.connect(self.delete_all_orders)
        self.btn_refresh.clicked.connect(self.refresh_all)
        self.btn_export.clicked.connect(self.export_to_excel)   # ← Подключили
        self.btn_import.clicked.connect(self.import_from_excel) # ← Подключили

        btn_layout.addWidget(self.btn_add_order)
        btn_layout.addWidget(self.btn_add_item)
        btn_layout.addWidget(self.btn_edit_order)
        btn_layout.addWidget(self.btn_delete_order)
        btn_layout.addWidget(self.btn_delete_all)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_import)

        main_layout.addLayout(btn_layout)

        # Splitter
        splitter = QSplitter(Qt.Vertical)

        self.order_table = QTableWidget()
        self.order_table.setColumnCount(8)
        self.order_table.setHorizontalHeaderLabels([
            "ID", "Дата", "Клиент", "Валюта", "Скидка %", 
            "Сумма заказа", "Статус", "Аванс %"
        ])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_table.itemSelectionChanged.connect(self.on_order_selected)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels([
            "ID", "ID Изделия", "Название", "Кол-во", "Цена", "Сумма"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.itemDoubleClicked.connect(self.edit_item)

        splitter.addWidget(self.order_table)
        splitter.addWidget(self.items_table)
        splitter.setSizes([380, 250])

        main_layout.addWidget(splitter)

        self.refresh_all()

    def refresh_all(self):
        self.refresh_order_table()
        self.items_table.setRowCount(0)
        self.current_order_id = None

    def refresh_order_table(self):
        orders = self.controller.get_all_orders()
        self.order_table.setRowCount(len(orders))

        for row, order in enumerate(orders):
            total_value = self.calculate_order_value(order.id)
            self.order_table.setItem(row, 0, QTableWidgetItem(str(order.id)))
            self.order_table.setItem(row, 1, QTableWidgetItem(str(order.order_date)))
            self.order_table.setItem(row, 2, QTableWidgetItem(str(order.customer_id)))
            self.order_table.setItem(row, 3, QTableWidgetItem(str(order.currency)))
            self.order_table.setItem(row, 4, QTableWidgetItem(f"{order.discount_percent:.1f}%"))
            self.order_table.setItem(row, 5, QTableWidgetItem(f"{total_value:.2f}"))
            self.order_table.setItem(row, 6, QTableWidgetItem(str(order.status)))
            self.order_table.setItem(row, 7, QTableWidgetItem(f"{order.advance_percent:.1f}%"))

    def calculate_order_value(self, order_id: str) -> float:
        items = self.item_controller.get_items_by_order(order_id)
        total = 0.0
        for item in items:
            total += item.qty * (item.product.unit_price if item.product else 0)
        return total

    def on_order_selected(self):
        row = self.order_table.currentRow()
        if row < 0:
            self.items_table.setRowCount(0)
            self.current_order_id = None
            return

        self.current_order_id = self.order_table.item(row, 0).text()
        self.refresh_items_table()

    def refresh_items_table(self):
        if not self.current_order_id:
            return

        items = self.item_controller.get_items_by_order(self.current_order_id)
        self.items_table.setRowCount(len(items))

        for row, item in enumerate(items):
            unit_price = item.product.unit_price if item.product else 0
            total = item.qty * unit_price

            self.items_table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item.product_id)))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item.product.name if item.product else "—")))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item.qty:.2f}"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{unit_price:.2f}"))
            self.items_table.setItem(row, 5, QTableWidgetItem(f"{total:.2f}"))

    def add_order(self):
        dialog = CustomerOrderDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_all()

    def add_item_to_order(self):
        if not self.current_order_id:
            QMessageBox.warning(self, "Внимание", "Сначала выберите заказ в верхней таблице")
            return

        dialog = CustomerOrderItemDialog(self, self.current_order_id)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_items_table()
            self.refresh_order_table()

    def edit_item(self):
        current_row = self.items_table.currentRow()
        if current_row < 0:
            return
        item_id = int(self.items_table.item(current_row, 0).text())

        qty, ok = QInputDialog.getDouble(self, "Изменить количество", "Новое количество:", 1.0, 0.01, 10000, 2)
        if ok and qty > 0:
            if self.item_controller.update_item(item_id, qty):
                self.refresh_items_table()
                self.refresh_order_table()

    def edit_order(self):
        row = self.order_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите заказ")
            return

        order_id = self.order_table.item(row, 0).text()
        order = self.controller.get_order_by_id(order_id)
        if order:
            dialog = CustomerOrderDialog(self, order)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_all()

    def delete_order(self):
        row = self.order_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите заказ")
            return

        order_id = self.order_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удаление", 
                                     f"Удалить заказ {order_id} и все его позиции?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.controller.delete_order(order_id):
                self.refresh_all()

    def delete_all_orders(self):
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            "Удалить ВСЕ заказы и все их позиции?\n\nЭто действие нельзя отменить!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            second_reply = QMessageBox.question(
                self, 
                "Финальное подтверждение", 
                "Вы уверены? Будут удалены все данные заказов.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if second_reply == QMessageBox.Yes:
                orders = self.controller.get_all_orders()
                deleted = 0
                for order in orders:
                    if self.controller.delete_order(order.id):
                        deleted += 1
                QMessageBox.information(self, "Удалено", f"Удалено {deleted} заказов.")
                self.refresh_all()

    def export_to_excel(self):
        self.excel_handler.export_customer_orders_full(self)

    def import_from_excel(self):
        if self.excel_handler.import_customer_orders(self):
            self.refresh_all()