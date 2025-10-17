"""Модуль данных для трекера сна"""

# Содержит классы для работы с записями о сне и статистикой

from datetime import date, timedelta
from custom_exceptions import InvalidDurationError, InvalidDateError, InvalidQualityError

# Класс, представляющий одну запись о сне
class SleepRecord:

    def __init__ (self, sleep_date: date, duration_hours: float, quality: int, notes: str = ""):
        self.sleep_date = sleep_date
        self.duration_hours = duration_hours
        self.quality = quality #для оценки качества сна от 1 до 10
        self.notes = notes

        self._validate() # Валидация данных при создании объекта

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


#Класс модель, управляющий коллекцией записей о сне
class SleepTrackerModel:

    def __init__(self):
        self.records = []

    # Добавляем новую запись о сне
    def add_record(self, record: SleepRecord):
        self.records.append(record)
        # Сортировка по дате (сверху будут новые)
        self.records.sort(key = lambda r: r.sleep_date, reverse=True)

    # Возвращает все записи
    def get_all_records(self):
        return self.records.copy() #для безопасности вовзвращаем копию

    # Возвращает количество записей
    def get_records_count(self):
        return len(self.records)

    # Рассчитывает среднюю продолжительность сна за послдение 7 дней
    def get_weekly_average(self):
        last_week = date.today() - timedelta(days=7)
        recent_records = [r for r in self.records if r.sleep_date >= last_week]

        if not recent_records:
            return 0.0

        total_duration = sum(r.duration_hours for r in recent_records)
        return total_duration / len(recent_records)


    # Возвращает последню добавленную запись или none
    def get_last_record(self):
        return self.records[0] if self.records else None

    # Очищает все записи (нужно для тестирования)
    def clear_all_records(self):
        self.records.clear()


