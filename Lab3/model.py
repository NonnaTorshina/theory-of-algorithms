"""Модуль данных для трекера сна"""

# Содержит классы для работы с записями о сне и статистикой

from datetime import date
from custom_exceptions import InvalidDurationError, InvalidDateError, InvalidQualityError


# Класс, представляющий одну запись о сне
class SleepRecord:

    def __init__(self, sleep_date: date, duration_hours: float, quality: int, notes: str = ""):
        self.sleep_date = sleep_date
        self.duration_hours = duration_hours
        # для оценки качества сна от 1 до 10
        self.quality = quality
        self.notes = notes

        # Валидация данных при создании объекта
        self._validate()

        # Валидация данных записи, вызывает исключения при ошибках
    def _validate(self):

        # Проверка длительности сна
        if self.duration_hours <= 0:
            raise InvalidDurationError("Продолжительность сна должна быть больше 0 часов")
        if self.duration_hours > 24:
            raise InvalidDurationError("Продолжительность сна не может превышать 24 часа")

        # Проверка даты
        if self.sleep_date > date.today():
            raise InvalidDateError("Дата сна не может быть в будущем")

        # Проверка качетсва сна
        if not (1 <= self.quality <= 10):
            raise InvalidQualityError("Качество сна должно быть оценено от 1 до 10")

        # Возвращает данные записи в виде списка для отображения в табице
    def to_list(self):
        return [
            self.sleep_date.strftime("%Y-%m-%d"),
            f"{self.duration_hours:.1f}",
            str(self.quality),
            self.notes
        ]

    # Строковое представление записи для отладки
    def __str__(self):
        return f"SleepRecord{self.sleep_date}, {self.duration_hours}ч, качество сна: {self.quality}"


# Класс модель, управляющий коллекцией записей о сне
class SleepTrackerModel:

    def __init__(self):
        from database import DatabaseManager
        self.db = DatabaseManager()

    # Добавляет новую запись о сне в базу данных
    def add_record(self, record: SleepRecord):

        self.db.add_sleep_record(record)
    # Возвращает все записи из базы данных

    def get_all_records(self):
        return self.db.get_all_records()

    # Возвращает количество записей
    def get_records_count(self):
        return self.db.get_records_count()

    # Рассчитывает среднюю продолжительность сна за последние 7 дней
    def get_weekly_average(self):
        return self.db.get_weekly_average()

    # Возвращает последнюю добавленную запись или None
    def get_last_record(self):
        all_records = self.get_all_records()
        return all_records[0] if all_records else None

    # Очищает все записи (для тестирования)
    def clear_all_records(self):
        self.db.clear_all_records()
