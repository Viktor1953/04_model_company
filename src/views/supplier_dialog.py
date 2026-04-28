# src/views/supplier_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, 
    QComboBox, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt

from src.controllers.supplier_controller import SupplierController


class SupplierDialog(QDialog):
    def __init__(self, parent=None, supplier=None):
        super().__init__(parent)
        self.controller = SupplierController()
        self.supplier = supplier  # None = создание, объект = редактирование
        self.setWindowTitle("Новый поставщик" if not supplier else "Редактировать поставщика")
        self.setMinimumWidth(460)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(12)

        self.company_edit = QLineEdit()
        self.company_edit.setMinimumWidth(280)

        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "RUB", "CNY", "JPY"])

        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(15, 1000)
        self.distance_spin.setDecimals(1)
        self.distance_spin.setSuffix(" км")

        self.reliability_spin = QDoubleSpinBox()
        self.reliability_spin.setRange(0.5, 1.0)
        self.reliability_spin.setDecimals(2)
        self.reliability_spin.setSingleStep(0.05)

        form.addRow("Название компании:", self.company_edit)
        form.addRow("Основная валюта:", self.currency_combo)
        form.addRow("Расстояние:", self.distance_spin)
        form.addRow("Надёжность (0.5–1.0):", self.reliability_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Заполнение при редактировании
        if self.supplier:
            self.company_edit.setText(self.supplier.company_name)
            self.currency_combo.setCurrentText(self.supplier.currency)
            self.distance_spin.setValue(self.supplier.distance_km)
            self.reliability_spin.setValue(self.supplier.reliability_score)

    def save(self):
        company_name = self.company_edit.text().strip()
        if not company_name:
            QMessageBox.warning(self, "Ошибка", "Название компании обязательно!")
            return

        currency = self.currency_combo.currentText()
        distance_km = self.distance_spin.value()
        reliability = self.reliability_spin.value()

        try:
            if self.supplier:
                # Редактирование
                success = self.controller.update_supplier(
                    self.supplier.id,
                    company_name,
                    currency,
                    distance_km,
                    reliability
                )
                if success:
                    QMessageBox.information(self, "Успешно", "Поставщик обновлён!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить поставщика.")
            else:
                # Создание нового
                supplier_id = self.controller.create_supplier(
                    company_name=company_name,
                    currency=currency,
                    distance_km=distance_km,
                    reliability_score=reliability
                )
                QMessageBox.information(self, "Успешно", f"Поставщик создан!\nID: {supplier_id}")
                self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{str(e)}")