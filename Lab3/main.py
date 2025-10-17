"""Главный файл приложения - точка входа в программу"""

import sys
from PySide6.QtWidgets import QApplication
from model import SleepTrackerModel
from view import MainWindow
from controller import SleepTrackerController

def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        print("Запуск приложения для отслеживания сна")

        model = SleepTrackerModel()
        view = MainWindow()
        controller = SleepTrackerController(model, view)

        print("Модель, представление и контроллер созданы успещно.")

        view.show()
        print("Графический интерфейс запущен")

        print("Запуск главной функции приложения")
        return_code = app.exec()

        print(f"Приложение завершено с кодом: {return_code}")
        return return_code
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}")
        return 1

if __name__ == "__main__":
    print("=" * 50)
    print("Трекер сна")
    print("=" * 50)

    sys.exit(main())