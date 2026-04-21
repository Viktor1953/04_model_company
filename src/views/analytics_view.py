# src/views/analytics_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QTabWidget
)
from PySide6.QtCore import Qt
from datetime import date, timedelta
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.controllers.customer_order_controller import CustomerOrderController
from src.controllers.customer_order_item_controller import CustomerOrderItemController
from src.utils.exchange_rates import convert_to_base_currency


class AnalyticsView(QWidget):
    def __init__(self):
        super().__init__()
        self.order_controller = CustomerOrderController()
        self.item_controller = CustomerOrderItemController()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        title = QLabel("Аналитика заказов")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 8px;")
        main_layout.addWidget(title)

        # Кнопка обновления
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить аналитику")
        self.btn_refresh.clicked.connect(self.refresh_all)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        main_layout.addLayout(btn_layout)

        # Вкладки внутри аналитики
        self.inner_tabs = QTabWidget()
        main_layout.addWidget(self.inner_tabs)

        # Вкладка 1 — Сводка по периодам
        self.tab_summary = QWidget()
        self.inner_tabs.addTab(self.tab_summary, "Сводка по периодам")
        self._setup_summary_tab()

        # Вкладка 2 — Рейтинг клиентов
        self.tab_customers = QWidget()
        self.inner_tabs.addTab(self.tab_customers, "Рейтинг Клиентов")
        self._setup_customers_tab()

        # Вкладка 3 — Рейтинг изделий
        self.tab_products = QWidget()
        self.inner_tabs.addTab(self.tab_products, "Рейтинг Изделий")
        self._setup_products_tab()

        self.refresh_all()

    # ====================== Сводка по периодам ======================
    def _setup_summary_tab(self):
        layout = QVBoxLayout(self.tab_summary)

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(5)
        self.summary_table.setHorizontalHeaderLabels([
            "Период", "Заказов", "Сумма (USD)", "Средний чек", "% от общего"
        ])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.summary_table)

    # ====================== Рейтинг клиентов ======================
    def _setup_customers_tab(self):
        layout = QVBoxLayout(self.tab_customers)

        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels([
            "Клиент", "Заказов (Ordered)", "Сумма (USD)", "Изделий"
        ])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.customer_table)

    # ====================== Рейтинг изделий ======================
    def _setup_products_tab(self):
        layout = QVBoxLayout(self.tab_products)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(3)
        self.product_table.setHorizontalHeaderLabels([
            "Изделие", "Заказано шт.", "Сумма (USD)"
        ])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.product_table)

    def refresh_all(self):
        """Главная функция обновления"""
        orders = self.order_controller.get_all_orders()
        if not orders:
            return

        self._update_summary(orders)
        self._update_customer_rating(orders)
        self._update_product_rating(orders)

    def _update_summary(self, orders):
        period_data = self._calculate_period_data(orders)
        self.summary_table.setRowCount(0)
        grand_total = sum(d["total_usd"] for d in period_data.values())

        for period_name, data in period_data.items():
            if data["count"] == 0:
                continue
            avg_check = data["total_usd"] / data["count"]
            percent = (data["total_usd"] / grand_total * 100) if grand_total > 0 else 0

            row = self.summary_table.rowCount()
            self.summary_table.insertRow(row)
            self.summary_table.setItem(row, 0, QTableWidgetItem(period_name))
            self.summary_table.setItem(row, 1, QTableWidgetItem(str(data["count"])))
            self.summary_table.setItem(row, 2, QTableWidgetItem(f"{data['total_usd']:.2f}"))
            self.summary_table.setItem(row, 3, QTableWidgetItem(f"{avg_check:.2f}"))
            self.summary_table.setItem(row, 4, QTableWidgetItem(f"{percent:.1f}%"))

    def _calculate_period_data(self, orders):
        today = date.today()
        periods = {
            "Прошлый 3м": (today - timedelta(days=90), today),
            "Оперативный": (today, today + timedelta(days=90)),
            "Тактический": (today, today + timedelta(days=180)),
            "Стратегический": (today, today + timedelta(days=365))
        }

        result = defaultdict(lambda: {"count": 0, "total_usd": 0.0})

        for order in orders:
            if order.status != "Ordered":
                continue

            items = self.item_controller.get_items_by_order(order.id)
            order_usd = 0.0
            for item in items:
                if item.product:
                    base_price = convert_to_base_currency(item.product.unit_price, item.product.currency)
                    order_usd += item.qty * base_price

            order_date = order.order_date
            for p_name, (start, end) in periods.items():
                if start <= order_date <= end:
                    result[p_name]["count"] += 1
                    result[p_name]["total_usd"] += order_usd
                    break

        return result

    def _update_customer_rating(self, orders):
        customer_stats = defaultdict(lambda: {"orders": 0, "usd": 0.0, "items": 0})

        for order in orders:
            if order.status != "Ordered":
                continue
            items = self.item_controller.get_items_by_order(order.id)
            order_usd = sum(item.qty * convert_to_base_currency(item.product.unit_price, item.product.currency) 
                          for item in items if item.product)

            customer_stats[order.customer_id]["orders"] += 1
            customer_stats[order.customer_id]["usd"] += order_usd
            customer_stats[order.customer_id]["items"] += sum(item.qty for item in items)

        # Топ-8 клиентов
        top_customers = sorted(customer_stats.items(), key=lambda x: x[1]["usd"], reverse=True)[:8]

        self.customer_table.setRowCount(0)
        for cust_id, stats in top_customers:
            # Можно добавить имя клиента позже
            row = self.customer_table.rowCount()
            self.customer_table.insertRow(row)
            self.customer_table.setItem(row, 0, QTableWidgetItem(f"Клиент {cust_id}"))
            self.customer_table.setItem(row, 1, QTableWidgetItem(str(stats["orders"])))
            self.customer_table.setItem(row, 2, QTableWidgetItem(f"{stats['usd']:.2f}"))
            self.customer_table.setItem(row, 3, QTableWidgetItem(str(int(stats["items"]))))

    def _update_product_rating(self, orders):
        product_stats = defaultdict(lambda: {"qty": 0, "usd": 0.0, "name": ""})

        for order in orders:
            if order.status != "Ordered":
                continue
            items = self.item_controller.get_items_by_order(order.id)
            for item in items:
                if item.product:
                    base_price = convert_to_base_currency(item.product.unit_price, item.product.currency)
                    product_stats[item.product_id]["qty"] += item.qty
                    product_stats[item.product_id]["usd"] += item.qty * base_price
                    product_stats[item.product_id]["name"] = item.product.name

        # Топ-10 изделий
        top_products = sorted(product_stats.items(), key=lambda x: x[1]["qty"], reverse=True)[:10]

        self.product_table.setRowCount(0)
        for prod_id, stats in top_products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            self.product_table.setItem(row, 0, QTableWidgetItem(stats["name"]))
            self.product_table.setItem(row, 1, QTableWidgetItem(str(int(stats["qty"]))))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{stats['usd']:.2f}"))