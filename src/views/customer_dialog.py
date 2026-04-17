# src/views/customer_dialog.py
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QLabel, QPushButton, 
    QHBoxLayout, QMessageBox
)

from src.controllers.customer_controller import CustomerController


class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.setWindowTitle("Новый клиент" if not customer else "Редактировать клиента")
        self.setMinimumWidth(420)
        self.customer = customer
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.id_label = QLabel("Автоматически")
        self.company_edit = QLineEdit()
        self.distance_edit = QLineEdit()

        layout.addRow("ID:", self.id_label)
        layout.addRow("Компания:", self.company_edit)
        layout.addRow("Расстояние (км):", self.distance_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        save_btn.clicked.connect(self.save)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        if self.customer:
            self.id_label.setText(self.customer.id)
            self.company_edit.setText(self.customer.company)
            self.distance_edit.setText(str(self.customer.distance_km))

    def save(self):
        company = self.company_edit.text().strip()
        try:
            distance = float(self.distance_edit.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Расстояние должно быть числом")
            return

        if not company:
            QMessageBox.warning(self, "Ошибка", "Введите название компании")
            return

        controller = CustomerController()

        if self.customer:
            success = controller.update_customer(self.customer.id, company, distance)
        else:
            success = controller.create_customer(company, distance)

        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить данные")