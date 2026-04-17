# src/views/customer_order_dialog.py
from datetime import date
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QLabel, QPushButton, 
    QHBoxLayout, QMessageBox, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import QDate, Qt

from src.controllers.customer_order_controller import CustomerOrderController
from src.controllers.customer_controller import CustomerController


class CustomerOrderDialog(QDialog):
    def __init__(self, parent=None, order=None):
        super().__init__(parent)
        self.setWindowTitle("Новый заказ клиента" if not order else "Редактировать заказ")
        self.setMinimumWidth(580)
        self.order = order
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setSpacing(12)

        # Поля формы
        self.order_id_label = QLabel("Автоматически")
        self.date_edit = QDateEdit()
        self.customer_combo = QComboBox()
        self.currency_combo = QComboBox()
        self.discount_spin = QDoubleSpinBox()
        self.status_combo = QComboBox()
        self.advance_spin = QDoubleSpinBox()
        self.advance_days = QSpinBox()
        self.final_days = QSpinBox()
        self.risk_days = QSpinBox()

        # Настройка виджетов
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")

        self.currency_combo.addItems(["USD", "EUR", "RUB", "CNY", "JPY"])
        self.status_combo.addItems(["Quotation", "Ordered", "In stock"])

        self.discount_spin.setRange(0, 50)
        self.discount_spin.setValue(0)
        self.discount_spin.setSuffix(" %")

        self.advance_spin.setRange(0, 100)
        self.advance_spin.setValue(30)
        self.advance_spin.setSuffix(" %")

        self.advance_days.setRange(1, 90)
        self.advance_days.setValue(14)
        self.final_days.setRange(1, 180)
        self.final_days.setValue(30)
        self.risk_days.setRange(0, 60)
        self.risk_days.setValue(7)

        # Загружаем клиентов
        self.load_customers()

        # Размещаем поля
        layout.addRow("Номер заказа:", self.order_id_label)
        layout.addRow("Дата заказа:", self.date_edit)
        layout.addRow("Клиент:", self.customer_combo)
        layout.addRow("Валюта:", self.currency_combo)
        layout.addRow("Скидка (%):", self.discount_spin)
        layout.addRow("Статус заказа:", self.status_combo)
        layout.addRow("Аванс (%):", self.advance_spin)
        layout.addRow("Срок аванса (дней):", self.advance_days)
        layout.addRow("Срок окончательной оплаты (дней):", self.final_days)
        layout.addRow("Риск просрочки (дней):", self.risk_days)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить заказ")
        btn_cancel = QPushButton("Отмена")

        self.btn_save.clicked.connect(self.save)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addRow(btn_layout)

        # Если редактируем существующий заказ
        if self.order:
            self.order_id_label.setText(self.order.id)
            self.date_edit.setDate(QDate(self.order.order_date))
            # Выбираем текущего клиента
            index = self.customer_combo.findData(self.order.customer_id)
            if index >= 0:
                self.customer_combo.setCurrentIndex(index)
            self.currency_combo.setCurrentText(self.order.currency or "USD")
            self.discount_spin.setValue(self.order.discount_percent or 0)
            self.status_combo.setCurrentText(self.order.status or "Quotation")
            self.advance_spin.setValue(self.order.advance_percent or 0)
            self.advance_days.setValue(self.order.advance_deadline_days or 14)
            self.final_days.setValue(self.order.final_payment_days or 30)
            self.risk_days.setValue(self.order.risk_late_payment_days or 7)

    def load_customers(self):
        """Загружает список клиентов в комбобокс"""
        controller = CustomerController()
        customers = controller.get_all_customers()
        self.customer_combo.clear()
        for customer in customers:
            display_text = f"{customer.id} — {customer.company}"
            self.customer_combo.addItem(display_text, customer.id)

    def save(self):
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите клиента")
            return

        controller = CustomerOrderController()

        try:
            if self.order:
                # Редактирование
                success = controller.update_order(
                    self.order.id,
                    customer_id=customer_id,
                    currency=self.currency_combo.currentText(),
                    discount_percent=self.discount_spin.value(),
                    status=self.status_combo.currentText(),
                    advance_percent=self.advance_spin.value(),
                    advance_deadline_days=self.advance_days.value(),
                    final_payment_days=self.final_days.value(),
                    risk_late_payment_days=self.risk_days.value(),
                    order_date=self.date_edit.date().toPython()
                )
            else:
                # Создание нового заказа
                success = controller.create_order(
                    customer_id=customer_id,
                    currency=self.currency_combo.currentText(),
                    discount_percent=self.discount_spin.value(),
                    status=self.status_combo.currentText(),
                    advance_percent=self.advance_spin.value(),
                    advance_deadline_days=self.advance_days.value(),
                    final_payment_days=self.final_days.value(),
                    risk_late_payment_days=self.risk_days.value(),
                    order_date=self.date_edit.date().toPython()
                )

            if success:
                QMessageBox.information(self, "Успех", "Заказ успешно сохранён!")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить заказ")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при сохранении:\n{str(e)}")