# src/views/product_dialog.py
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QLabel, QPushButton, 
    QHBoxLayout, QMessageBox, QComboBox, QDoubleSpinBox
)

from src.controllers.product_controller import ProductController


class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("Новое изделие" if not product else "Редактировать изделие")
        self.setMinimumWidth(480)
        self.product = product
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.id_label = QLabel("Автоматически")
        self.name_edit = QLineEdit()
        self.uom_combo = QComboBox()
        self.price_spin = QDoubleSpinBox()
        self.currency_combo = QComboBox()

        self.uom_combo.addItems(["pcs", "kg", "m", "sq.m", "cu.m", "lm", "l", "t", "set"])
        self.currency_combo.addItems(["RUB", "USD", "EUR", "CNY", "JPY"])

        self.price_spin.setRange(0, 10000000)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" ")

        layout.addRow("ID:", self.id_label)
        layout.addRow("Название:", self.name_edit)
        layout.addRow("Ед. измерения:", self.uom_combo)
        layout.addRow("Цена:", self.price_spin)
        layout.addRow("Валюта:", self.currency_combo)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        save_btn.clicked.connect(self.save)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        if self.product:
            self.id_label.setText(self.product.id)
            self.name_edit.setText(self.product.name)
            self.uom_combo.setCurrentText(self.product.uom)
            self.price_spin.setValue(self.product.unit_price)
            self.currency_combo.setCurrentText(self.product.currency)

    def save(self):
        name = self.name_edit.text().strip()
        uom = self.uom_combo.currentText()
        price = self.price_spin.value()
        currency = self.currency_combo.currentText()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название изделия")
            return

        controller = ProductController()

        if self.product:
            success = controller.update_product(self.product.id, name, uom, price, currency)
        else:
            success = controller.create_product(name, uom, price, currency)

        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изделие")