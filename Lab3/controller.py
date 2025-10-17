"""Контроллер - связывает модель и представление"""

from datetime import date
from model import SleepRecord, SleepTrackerModel
from view import MainWindow
from custom_exceptions import SleepTrackerError

class SleepTrackerController:

    def __init__(self, model: SleepTrackerModel, view: MainWindow):
        self.model = model
        self.view = view
        self._connect_signals()

        self.update_view()

    def _connect_signals(self):
        self.view.add_button.clicked.connect(self.add_new_record)

    def add_new_record(self):
        try:
            input_data = self.view.get_input_data()

            if not input_data['duration'] or not input_data['quality']:
                raise ValueError("Поля [продолжительность] и [качество] обязательны для заполнения")

            sleep_date = input_data['date']
            duration_hours = float(input_data['duration'])
            quality = int(input_data['quality'])
            notes = input_data['notes']

            new_record = SleepRecord(sleep_date, duration_hours, quality, notes)

            self.model.add_record(new_record)

            self.update_view()

            self.view.clear_inputs()

            self.view.update_status(f" Запись за {sleep_date} успешно добавлена")

        except ValueError as e:

            error_message = self._parse_value_error(str(e))
            self.view.show_error(error_message)
            self.view.update_status("Ошибка при добавлении записи")

        except SleepTrackerError as e:

            self.view.show_error("Ошибка данных:", e)
            self.view.update_status("Ошибка при добавлении записи")

    def _parse_value_error(self, error_str):

        if "could not convert string to float" in error_str:
            return "Ошибка: Продолжительность должна быть числом (например: 7.5)"
        elif "invalid literal for int()" in error_str:
            return "Ошибка: Качество сна должно быть целым числом от 1 до 10"
        else:
            return f"Ошибка ввода: {error_str}"

    def update_view(self):
        all_records = self.model.get_all_records()

        self.view.update_table(all_records)

        self.view.update_chart(all_records)

        self._update_status_bar()

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
