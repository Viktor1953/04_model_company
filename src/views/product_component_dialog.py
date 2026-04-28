# src/views/product_component_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, 
    QComboBox, QDialogButtonBox, QMessageBox, QLabel
)
from PySide6.QtCore import Qt

from src.controllers.product_component_controller import ProductComponentController
from src.controllers.product_controller import ProductController


class ProductComponentDialog(QDialog):
    def __init__(self, parent=None, component=None):
        super().__init__(parent)
        self.controller = ProductComponentController()
        self.product_controller = ProductController()
        self.component = component  # None = создание, объект = редактирование
        self.setWindowTitle("Новый компонент" if not component else "Редактировать компонент")
        self.setMinimumWidth(520)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(12)

        self.product_combo = QComboBox()
        products = self.product_controller.get_all_products()
        for p in products:
            self.product_combo.addItem(f"{p.name} ({p.id})", p.id)

        self.component_name_edit = QLineEdit()

        self.mcr_spin = QDoubleSpinBox()
        self.mcr_spin.setRange(0.001, 10000)
        self.mcr_spin.setDecimals(4)

        self.losses_spin = QDoubleSpinBox()
        self.losses_spin.setRange(0, 100)
        self.losses_spin.setDecimals(2)
        self.losses_spin.setSuffix(" %")

        self.scrap_spin = QDoubleSpinBox()
        self.scrap_spin.setRange(0, 50)
        self.scrap_spin.setDecimals(2)
        self.scrap_spin.setSuffix(" %")

        self.uom_combo = QComboBox()
        self.uom_combo.addItems(["pcs", "kg", "m", "sq.m", "cu.m", "lm", "l", "t", "set"])

        self.notes_edit = QLineEdit()

        self.tmc_label = QLabel("0.0000")

        form.addRow("Изделие:", self.product_combo)
        form.addRow("Название компонента:", self.component_name_edit)
        form.addRow("MCR/GU:", self.mcr_spin)
        form.addRow("Производственные потери %:", self.losses_spin)
        form.addRow("Неисправимый брак %:", self.scrap_spin)
        form.addRow("Ед. измерения:", self.uom_combo)
        form.addRow("TMC/GU (итого):", self.tmc_label)
        form.addRow("Примечания:", self.notes_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Автопересчёт TMC/GU
        self.mcr_spin.valueChanged.connect(self.calculate_tmc)
        self.losses_spin.valueChanged.connect(self.calculate_tmc)
        self.scrap_spin.valueChanged.connect(self.calculate_tmc)

        # Заполнение при редактировании
        if self.component:
            self.product_combo.setEnabled(False)   # нельзя менять изделие
            current_text = f"{getattr(self.component, 'product_name', '') or ''} ({self.component.product_id})"
            index = self.product_combo.findText(current_text)
            if index >= 0:
                self.product_combo.setCurrentIndex(index)

            self.component_name_edit.setText(self.component.component_name)
            self.mcr_spin.setValue(self.component.mcr_gu)
            self.losses_spin.setValue(self.component.manufacturing_losses_pct)
            self.scrap_spin.setValue(self.component.scrap_pct)
            self.uom_combo.setCurrentText(self.component.uom)
            self.notes_edit.setText(self.component.notes or "")

    def calculate_tmc(self):
        mcr = self.mcr_spin.value()
        losses = self.losses_spin.value() / 100
        scrap = self.scrap_spin.value() / 100
        tmc = mcr * (1 + losses + scrap)
        self.tmc_label.setText(f"{tmc:.4f}")

    def save(self):
        product_id = self.product_combo.currentData()
        component_name = self.component_name_edit.text().strip()

        if not product_id or not component_name:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля!")
            return

        try:
            if self.component:
                # === РЕДАКТИРОВАНИЕ ===
                success = self.controller.update_component(
                    component_id=self.component.id,
                    component_name=component_name,
                    mcr_gu=self.mcr_spin.value(),
                    manufacturing_losses_pct=self.losses_spin.value(),
                    scrap_pct=self.scrap_spin.value(),
                    uom=self.uom_combo.currentText(),
                    notes=self.notes_edit.text().strip() or None
                )
                if success:
                    QMessageBox.information(self, "Успех", "Компонент успешно обновлён!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить компонент.")
            else:
                # === СОЗДАНИЕ ===
                self.controller.create_component(
                    product_id=product_id,
                    component_name=component_name,
                    mcr_gu=self.mcr_spin.value(),
                    manufacturing_losses_pct=self.losses_spin.value(),
                    scrap_pct=self.scrap_spin.value(),
                    uom=self.uom_combo.currentText(),
                    notes=self.notes_edit.text().strip() or None
                )
                QMessageBox.information(self, "Успех", "Компонент успешно добавлен!")
                self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить компонент:\n{str(e)}")