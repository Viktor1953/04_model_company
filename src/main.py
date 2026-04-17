# src/main.py
import sys
from PySide6.QtWidgets import QApplication

# Сначала полностью инициализируем базу
from src.database.engine import init_db

print("Инициализация базы данных...")
init_db(drop_all=False)   # Измените на True, если хотите каждый раз очищать данные

# Теперь импортируем GUI
from src.views.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())