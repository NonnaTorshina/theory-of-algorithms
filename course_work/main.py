import sys
import os

# Добавление корневой директории проекта в путь поиска модулей Python
# Это необходимо для корректного импорта модулей из папок controllers, models, views, utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from controllers.main_controller import MainController

# Основная функция запуска приложения
def main():
    # Создание экземпляра QApplication - обязательный компонент любого PySide6 приложения
    # sys.argv передает аргументы командной строки в приложение
    app = QApplication(sys.argv)

    # Создание главного контроллера приложения
    # Контроллер управляет всей логикой приложения и связывает Model и View
    controller = MainController()

    # Запуск основного цикла приложения
    controller.run()

    # Запуск основного цикла обработки событий Qt
    # app.exec() возвращает код завершения приложения
    # sys.exit() гарантирует корректное завершение процесса
    sys.exit(app.exec())


# Точка входа в приложение
# Код выполняется только при прямом запуске этого файла
if __name__ == "__main__":
    main()