# src/views/customer_order_item_dialog.py
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QPushButton, 
    QHBoxLayout, QMessageBox, QLabel
)
from PySide6.QtCore import Qt

from src.controllers.product_controller import ProductController
from src.controllers.customer_order_item_controller import CustomerOrderItemController


class CustomerOrderItemDialog(QDialog):
    def __init__(self, parent=None, order_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить изделие в заказ")
        self.setMinimumWidth(520)
        self.order_id = order_id
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setLabelAlignment(Qt.AlignRight)

        self.product_combo = QComboBox()
        self.qty_spin = QDoubleSpinBox()

        self.qty_spin.setRange(0.01, 10000)
        self.qty_spin.setDecimals(2)
        self.qty_spin.setValue(1.0)

        self.load_products()

        layout.addRow("Изделие:", self.product_combo)
        layout.addRow("Количество:", self.qty_spin)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Добавить в заказ")
        cancel_btn = QPushButton("Отмена")

        save_btn.clicked.connect(self.save)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_products(self):
        controller = ProductController()
        products = controller.get_all_products()
        self.product_combo.clear()
        for p in products:
            display = f"{p.id} — {p.name} ({p.uom}) — {p.unit_price:.2f} {p.currency}"
            self.product_combo.addItem(display, p.id)

    def save(self):
        product_id = self.product_combo.currentData()
        qty = self.qty_spin.value()

        if not product_id:
            QMessageBox.warning(self, "Ошибка", "Выберите изделие")
            return
        if qty <= 0:
            QMessageBox.warning(self, "Ошибка", "Количество должно быть больше 0")
            return

        controller = CustomerOrderItemController()
        if controller.add_item(self.order_id, product_id, qty):
            QMessageBox.information(self, "Успех", "Изделие добавлено в заказ")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить изделие")