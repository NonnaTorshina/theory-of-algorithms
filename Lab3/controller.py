"""Контроллер - связывает модель и представление"""

from datetime import date
from model import SleepRecord, SleepTrackerModel
from view import MainWindow
from custom_exceptions import SleepTrackerError

class SleepTrackerController:

    def __init__(self, model: SleepTrackerModel, view: MainWindow):
        self.model = model
        self.view = view
        # Подключаем обработчики событий (сигналы к слотам)
        self._connect_signals()

        self.update_view() # Загружаем начальные данные в представление

    # Подключает сигналы от виджетов к методам-обработчикам
    def _connect_signals(self):
        self.view.add_button.clicked.connect(self.add_new_record)

    # Обрабатывает добавление новой записи о сне
    def add_new_record(self):
        try:
            input_data = self.view.get_input_data()  # Получаем данные из полей ввода

            # Проверяем, что обязательные поля заполнены
            if not input_data['duration'] or not input_data['quality']:
                raise ValueError("Поля [продолжительность] и [качество] обязательны для заполнения")

            # Преобразуем и валидируем ввод
            sleep_date = input_data['date']
            duration_hours = float(input_data['duration'])
            quality = int(input_data['quality'])
            notes = input_data['notes']
            # Создаем новую запись (внутри происходит валидация)
            new_record = SleepRecord(sleep_date, duration_hours, quality, notes)
            # Добавляем запись в модель
            self.model.add_record(new_record)
            # Обновляем представление (таблицу, график, статус)
            self.update_view()
            # Очищаем поля ввода
            self.view.clear_inputs()
            # Логируем успешное добавление
            self.view.update_status(f" Запись за {sleep_date} успешно добавлена")

        except ValueError as e:
            # Обрабатываем ошибки преобразования типов
            error_message = self._parse_value_error(str(e))
            self.view.show_error(error_message)
            self.view.update_status("Ошибка при добавлении записи")

        except SleepTrackerError as e: # Обрабатываем пользовательские исключения

            self.view.show_error("Ошибка данных:", e)
            self.view.update_status("Ошибка при добавлении записи")

    #  Анализирует ValueError и возвращает понятное сообщение
    def _parse_value_error(self, error_str):

        if "could not convert string to float" in error_str:
            return "Ошибка: Продолжительность должна быть числом (например: 7.5)"
        elif "invalid literal for int()" in error_str:
            return "Ошибка: Качество сна должно быть целым числом от 1 до 10"
        else:
            return f"Ошибка ввода: {error_str}"

    # Полностью обновляет данные в представлении
    def update_view(self):
        all_records = self.model.get_all_records() # Получаем все записи из модели

        self.view.update_table(all_records)  # Обновляем таблицу

        self.view.update_chart(all_records) # Обновляем график

        self._update_status_bar() # Обновляем статус бар со статистикой

    # Обновляет статус бар с текущей статистикой
    def _update_status_bar(self):
        all_records = self.model.get_all_records()
        avg_sleep = self.model.get_weekly_average()
        total_records = len(all_records)

        if total_records == 0:
            status_message = "Записей ещё нет. Добавьте первую запись о сне"
        else:
            status_message = f"Записей в дневнике: {total_records}"
            if avg_sleep > 0:
                status_message += f" | Средняя продолжительность сна за неделю: {avg_sleep:.1f} ч."

        self.view.update_status(status_message)
