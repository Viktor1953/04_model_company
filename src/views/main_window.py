# src/views/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import Qt

from src.views.customer_view import CustomerView
from src.views.product_view import ProductView
from src.views.customer_order_view import CustomerOrderView
from src.views.analytics_view import AnalyticsView
from src.models.periods import create_period


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Технико-экономическая модель — Машиностроение SMB")
        self.resize(1450, 880)

        self.current_period = create_period("strategic")

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        # === Верхняя панель с выбором периода ===
        top_panel = QHBoxLayout()

        period_label = QLabel("Период анализа:")
        period_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Стратегический (12 месяцев)",
            "Тактический (6 месяцев)",
            "Оперативный (3 месяца)",
            "Прошлый период (3 месяца)"
        ])
        self.period_combo.setCurrentIndex(0)
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)

        refresh_btn = QPushButton("Обновить все данные")
        refresh_btn.clicked.connect(self.refresh_all)
        refresh_btn.setStyleSheet("padding: 6px 12px;")

        top_panel.addWidget(period_label)
        top_panel.addWidget(self.period_combo, stretch=1)
        top_panel.addStretch()
        top_panel.addWidget(refresh_btn)

        main_layout.addLayout(top_panel)

        # === Заголовок приложения ===
        title = QLabel("Технико-экономическая модель")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px; 
            font-weight: bold; 
            margin: 12px 0;
            color: #2c3e50;
        """)
        main_layout.addWidget(title)

        # === Вкладки ===
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { padding: 10px 20px; }")
        main_layout.addWidget(self.tabs)

        # Создаём вкладки
        self.customer_tab = CustomerView()
        self.product_tab = ProductView()
        self.order_tab = CustomerOrderView()
        self.analytics_tab = AnalyticsView()          # ← Новая вкладка

        self.tabs.addTab(self.customer_tab, "Клиенты")
        self.tabs.addTab(self.product_tab, "Изделия")
        self.tabs.addTab(self.order_tab, "Заказы Клиента")
        self.tabs.addTab(self.analytics_tab, "Аналитика")   # ← Добавлена

        # === Статусная строка ===
        self.status_label = QLabel(f"Текущий период: {self.current_period}")
        self.status_label.setStyleSheet("""
            color: #555; 
            padding: 8px; 
            background-color: #f8f9fa; 
            border-top: 1px solid #ddd;
        """)
        main_layout.addWidget(self.status_label)

    def on_period_changed(self, index: int):
        """Смена периода анализа"""
        period_map = ["strategic", "tactical", "operational", "past_3m"]
        self.current_period = create_period(period_map[index])
        self.status_label.setText(f"Текущий период: {self.current_period}")
        
        # Обновляем все вкладки при смене периода
        self.refresh_all()

    def refresh_all(self):
        """Обновление всех вкладок"""
        try:
            self.customer_tab.refresh_table()
            self.product_tab.refresh_table()
            self.order_tab.refresh_all()
            self.analytics_tab.refresh_all()        # ← Обновляем аналитику
        except Exception as e:
            print(f"Ошибка при обновлении данных: {e}")

    def get_current_period(self):
        """Возвращает текущий выбранный период"""
        return self.current_period