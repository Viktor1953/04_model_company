# src/views/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QPushButton, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt

from src.views.customer_view import CustomerView
from src.views.product_view import ProductView
from src.views.customer_order_view import CustomerOrderView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Технико-экономическая модель — Машиностроение SMB")
        self.resize(1280, 760)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Заголовок
        title = QLabel("Технико-экономическая модель")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 15px;")
        main_layout.addWidget(title)

        # Вкладки
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Создаём вкладки
        self.customer_tab = CustomerView()
        self.product_tab = ProductView()

        self.tabs.addTab(self.customer_tab, "Клиенты (Customers)")
        self.tabs.addTab(self.product_tab, "Изделия (Products)")
        self.order_tab = CustomerOrderView()
        self.tabs.addTab(self.order_tab, "Заказы Клиента")

        # Нижняя панель управления
        bottom_layout = QHBoxLayout()
        refresh_btn = QPushButton("Обновить все таблицы")
        refresh_btn.clicked.connect(self.refresh_all)
        bottom_layout.addWidget(refresh_btn)

        export_btn = QPushButton("Экспорт в Excel")
        export_btn.clicked.connect(self.export_to_excel)
        bottom_layout.addWidget(export_btn)

        main_layout.addLayout(bottom_layout)

    def refresh_all(self):
        self.customer_tab.refresh_table()
        self.product_tab.refresh_table()

    def export_to_excel(self):
        # Пока заглушка — позже подключим ExcelHandler
        print("Экспорт в Excel (будет реализовано)")