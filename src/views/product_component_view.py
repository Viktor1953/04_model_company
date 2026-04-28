# src/views/product_component_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PySide6.QtCore import Qt

from src.controllers.product_component_controller import ProductComponentController
from src.views.product_component_dialog import ProductComponentDialog
from src.utils.excel_handler import ExcelHandler


class ProductComponentView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ProductComponentController()
        self.excel_handler = ExcelHandler()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Добавить компонент")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_clear = QPushButton("Очистить все компоненты")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_export = QPushButton("Экспорт в Excel")
        self.btn_import = QPushButton("Импорт из Excel")

        self.btn_add.clicked.connect(self.add_component)
        self.btn_edit.clicked.connect(self.edit_component)
        self.btn_delete.clicked.connect(self.delete_component)
        self.btn_clear.clicked.connect(self.clear_all_components)
        self.btn_refresh.clicked.connect(self.refresh_table)
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_import.clicked.connect(self.import_from_excel)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_import)

        main_layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Изделие", "Компонент", "MCR/GU", "Потери %", 
            "Брак %", "TMC/GU", "Ед.изм."
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        components = self.controller.get_all_components()
        self.table.setRowCount(len(components))

        for row, comp in enumerate(components):
            product_name = getattr(comp, 'product_name', None) or comp.product_id

            self.table.setItem(row, 0, QTableWidgetItem(str(comp.id)))
            self.table.setItem(row, 1, QTableWidgetItem(product_name))
            self.table.setItem(row, 2, QTableWidgetItem(comp.component_name))
            self.table.setItem(row, 3, QTableWidgetItem(f"{comp.mcr_gu:.3f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{comp.manufacturing_losses_pct:.1f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{comp.scrap_pct:.1f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{comp.tmc_gu:.3f}"))
            self.table.setItem(row, 7, QTableWidgetItem(comp.uom))

    def add_component(self):
        dialog = ProductComponentDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_table()

    def edit_component(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите компонент для редактирования")
            return

        component_id = self.table.item(row, 0).text()
        component = self.controller.get_component_by_id(component_id)

        if component:
            dialog = ProductComponentDialog(self, component)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_table()

    def delete_component(self):
        row = self.table.currentRow()
        if row < 0:
            return
        comp_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удаление", f"Удалить компонент {comp_id}?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.controller.delete_component(comp_id):
                self.refresh_table()

    def clear_all_components(self):
        reply = QMessageBox.question(self, "Очистка", 
                                     "Удалить ВСЕ компоненты?\n\nЭто действие нельзя отменить!",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.clear_all_components()
            QMessageBox.information(self, "Готово", "Все компоненты удалены.")
            self.refresh_table()

    def export_to_excel(self):
        self.excel_handler.export_product_components(self)

    def import_from_excel(self):
        if self.excel_handler.import_product_components(self):
            self.refresh_table()