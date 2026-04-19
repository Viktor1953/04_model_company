# src/views/analytics_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox
)
from PySide6.QtCore import Qt
from datetime import date, timedelta   # ← Добавили timedelta

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import defaultdict

from src.controllers.customer_order_controller import CustomerOrderController
from src.utils.exchange_rates import convert_to_base_currency


class AnalyticsView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = CustomerOrderController()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Заголовок
        title = QLabel("Аналитика заказов")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title)

        # Кнопка обновления
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить аналитику")
        self.btn_refresh.clicked.connect(self.refresh_all)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        main_layout.addLayout(btn_layout)

        # Сводная таблица по периодам
        group_summary = QGroupBox("Сводка по периодам матрёшки")
        summary_layout = QVBoxLayout(group_summary)
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(5)
        self.summary_table.setHorizontalHeaderLabels([
            "Период", "Заказов", "Сумма (USD)", "Средний чек (USD)", "% от общего"
        ])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        summary_layout.addWidget(self.summary_table)
        main_layout.addWidget(group_summary)

        # Графики
        charts_layout = QHBoxLayout()

        # График динамики по времени
        self.figure_time = Figure(figsize=(9, 5))
        self.canvas_time = FigureCanvas(self.figure_time)
        charts_layout.addWidget(self.canvas_time)

        # График распределения по статусам
        self.figure_status = Figure(figsize=(6, 5))
        self.canvas_status = FigureCanvas(self.figure_status)
        charts_layout.addWidget(self.canvas_status)

        main_layout.addLayout(charts_layout)

        self.refresh_all()

    def refresh_all(self):
        """Полная перезагрузка аналитики"""
        orders = self.controller.get_all_orders()
        if not orders:
            print("Нет данных для аналитики")
            return

        period_data = self._group_orders_by_period(orders)
        self._fill_summary_table(period_data)
        self._plot_time_series(orders)
        self._plot_status_pie(orders)          # улучшенная версия

    def _group_orders_by_period(self, orders):
        """Группирует заказы по периодам матрёшки"""
        today = date.today()
        periods = {
            "Прошлый 3м": (today - timedelta(days=90), today),
            "Оперативный": (today, today + timedelta(days=90)),
            "Тактический": (today, today + timedelta(days=180)),
            "Стратегический": (today, today + timedelta(days=365))
        }

        result = defaultdict(lambda: {"count": 0, "total_usd": 0.0})

        for order in orders:
            order_date = order.order_date
            # Простой расчёт суммы заказа в USD (пока заглушка)
            order_value_usd = 1500.0   # TODO: позже сделаем реальный расчёт

            for period_name, (start, end) in periods.items():
                if start <= order_date <= end:
                    result[period_name]["count"] += 1
                    result[period_name]["total_usd"] += order_value_usd
                    break

        return result

    def _fill_summary_table(self, period_data):
        self.summary_table.setRowCount(0)
        grand_total = sum(data["total_usd"] for data in period_data.values())

        for period_name, data in period_data.items():
            if data["count"] == 0:
                continue
                
            avg_check = data["total_usd"] / data["count"] if data["count"] > 0 else 0
            percent = (data["total_usd"] / grand_total * 100) if grand_total > 0 else 0

            row = self.summary_table.rowCount()
            self.summary_table.insertRow(row)
            self.summary_table.setItem(row, 0, QTableWidgetItem(period_name))
            self.summary_table.setItem(row, 1, QTableWidgetItem(str(data["count"])))
            self.summary_table.setItem(row, 2, QTableWidgetItem(f"{data['total_usd']:.2f}"))
            self.summary_table.setItem(row, 3, QTableWidgetItem(f"{avg_check:.2f}"))
            self.summary_table.setItem(row, 4, QTableWidgetItem(f"{percent:.1f}%"))

    def _plot_time_series(self, orders):
        """График динамики заказов по времени"""
        self.figure_time.clear()
        ax = self.figure_time.add_subplot(111)

        # Группируем по датам (заглушка)
        dates = sorted(list(set(o.order_date for o in orders)))
        values = [len([o for o in orders if o.order_date == d]) * 1200 for d in dates]

        ax.plot(dates, values, 'b-o', linewidth=2, markersize=6)
        ax.set_title("Динамика количества заказов по датам")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Сумма заказов, USD")
        ax.grid(True, alpha=0.3)
        self.figure_time.autofmt_xdate()
        self.canvas_time.draw()

    def _plot_status_pie(self, orders):
        """Круговая диаграмма распределения по статусам"""
        self.figure_status.clear()
        ax = self.figure_status.add_subplot(111)

        status_count = {}
        for order in orders:
            status_count[order.status] = status_count.get(order.status, 0) + 1

        labels = list(status_count.keys())
        sizes = list(status_count.values())

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, shadow=True)
        ax.set_title("Распределение заказов по статусам")
        self.canvas_status.draw()