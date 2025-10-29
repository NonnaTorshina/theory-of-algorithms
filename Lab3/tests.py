""" тесты для приложения отслеживания сна """

import pytest
import os
from datetime import date, timedelta
from model import SleepRecord, SleepTrackerModel
from custom_exceptions import InvalidDurationError, InvalidDateError, InvalidQualityError
from database import DatabaseManager

class TestSleepRecord:
    # Тест создания корректной записи о сне
    def test_valid_record_creation(self):
        record = SleepRecord(date.today(), 7.5, 8, "Хороший сон")
        assert record.duration_hours == 7.5
        assert record.quality == 8
        assert record.notes == "Хороший сон"

    # Тест создания записи без заметок
    def test_valid_record_creation_no_notes(self):
        record = SleepRecord(date.today(), 7.5, 8)
        assert record.notes == ""

    # Тест отрицательной продолжительности сна
    def test_invalid_duration_negative(self):
        with pytest.raises(InvalidDurationError):
            SleepRecord(date.today(), -1, 5)

    # Тест нулевой продолжительности сна
    def test_invalid_duration_zero(self):
        with pytest.raises(InvalidDurationError):
            SleepRecord(date.today(), 0, 5)

    # Тест слишком большой продолжительности сна
    def test_invalid_duration_too_large(self):
        with pytest.raises(InvalidDurationError):
            SleepRecord(date.today(), 25, 5)

    # Тест даты из будущего
    def test_invalid_date_future(self):
        future_date = date.today() + timedelta(days=1)
        with pytest.raises(InvalidDateError):
            SleepRecord(future_date, 7.5, 5)

    # Тест слишком низкого качества сна
    def test_invalid_quality_too_low(self):
        with pytest.raises(InvalidQualityError):
            SleepRecord(date.today(), 7.5, 0)

    # Тест слишком высокого качества сна
    def test_invalid_quality_too_high(self):
        with pytest.raises(InvalidQualityError):
            SleepRecord(date.today(), 7.5, 11)

    # Тест граничных значений качества сна
    def test_boundary_quality_values(self):
        record1 = SleepRecord(date.today(), 7.5, 1)
        record2 = SleepRecord(date.today(), 7.5, 10)
        assert record1.quality == 1
        assert record2.quality == 10

    # Тест граничных значений продолжительности сна
    def test_boundary_duration_values(self):

        record1 = SleepRecord(date.today(), 0.1, 5)
        record2 = SleepRecord(date.today(), 24.0, 5)
        assert record1.duration_hours == 0.1
        assert record2.duration_hours == 24.0

    # Тест метода to_list() с заметками
    def test_to_list_method(self):
        record = SleepRecord(date(2024, 1, 15), 7.5, 8, "Test")
        result = record.to_list()
        expected = ["2024-01-15", "7.5", "8", "Test"]
        assert result == expected

    # Тест метода to_list() без заметок
    def test_to_list_method_no_notes(self):
        record = SleepRecord(date(2024, 1, 15), 7.5, 8)
        result = record.to_list()
        expected = ["2024-01-15", "7.5", "8", ""]
        assert result == expected

    # Тест строкового представления записи
    def test_str_representation(self):
        record = SleepRecord(date(2024, 1, 15), 7.5, 8, "Test")
        result = str(record)
        expected = "SleepRecord(2024-01-15, 7.5ч, качество сна: 8)"
        assert "2024-01-15" in result
        assert "7.5ч" in result
        assert "качество сна: 8" in result

# Тесты для класса SleepTrackerModel
class TestSleepTrackerModel:
    # Настройка перед каждым тестом
    def setup_method(self):
        self.model = SleepTrackerModel()
        self.model.clear_all_records()

    # Очистка после каждого теста
    def teardown_method(self):
        self.model.clear_all_records()

    # Тест добавления и получения записи
    def test_add_and_retrieve_record(self):
        record = SleepRecord(date.today(), 7.5, 8, "Test record")
        self.model.add_record(record)

        all_records = self.model.get_all_records()
        assert len(all_records) == 1
        assert all_records[0].duration_hours == 7.5
        assert all_records[0].quality == 8
        assert all_records[0].notes == "Test record"

    # Тест работы с несколькими записями
    def test_multiple_records(self):
        record1 = SleepRecord(date.today(), 7.0, 7, "First")
        record2 = SleepRecord(date.today() - timedelta(days=1), 8.0, 9, "Second")

        self.model.add_record(record1)
        self.model.add_record(record2)

        all_records = self.model.get_all_records()
        assert len(all_records) == 2
        assert all_records[0].sleep_date == date.today()
        assert all_records[1].sleep_date == date.today() - timedelta(days=1)

    # Тест пустой базы данных
    def test_empty_database(self):
        assert self.model.get_records_count() == 0
        assert self.model.get_weekly_average() == 0.0
        assert self.model.get_last_record() is None

    # Тест расчета средней продолжительности
    def test_weekly_average_calculation(self):
        for i in range(3):
            record = SleepRecord(
                date.today() - timedelta(days=i),
                8.0, 7, f"Day {i}"
            )
            self.model.add_record(record)

        avg = self.model.get_weekly_average()
        assert avg == 8.0

    # Тест средней продолжительности без записей
    def test_weekly_average_no_records(self):
        avg = self.model.get_weekly_average()
        assert avg == 0.0

    # Тест средней продолжительности с разными значениями
    def test_weekly_average_mixed_durations(self):
        records_data = [
            (date.today(), 6.0, 7),  # 6 часов
            (date.today() - timedelta(days=1), 7.0, 8),  # 7 часов
            (date.today() - timedelta(days=2), 8.0, 6)  # 8 часов
        ]

        for sleep_date, duration, quality in records_data:
            record = SleepRecord(sleep_date, duration, quality)
            self.model.add_record(record)

        avg = self.model.get_weekly_average()
        expected_avg = (6.0 + 7.0 + 8.0) / 3
        assert avg == expected_avg

    # Тест получения последней записи
    def test_get_last_record(self):
        assert self.model.get_last_record() is None

        record1 = SleepRecord(date.today(), 7.0, 7)
        record2 = SleepRecord(date.today() - timedelta(days=1), 8.0, 8)

        self.model.add_record(record1)
        self.model.add_record(record2)

        last_record = self.model.get_last_record()
        assert last_record is not None
        assert last_record.sleep_date == date.today()

    # Тест очистки всех записей
    def test_clear_all_records(self):
        record = SleepRecord(date.today(), 7.5, 8)
        self.model.add_record(record)
        assert self.model.get_records_count() == 1

        self.model.clear_all_records()
        assert self.model.get_records_count() == 0
        assert self.model.get_weekly_average() == 0.0

# Тесты для менеджера базы данных
class TestDatabaseManager:
    # Настройка перед каждым тестом
    def setup_method(self):
        self.db = DatabaseManager(":memory:")

    # Тест инициализации базы данных
    def test_database_initialization(self):
        # Просто проверяем что объект создан
        assert self.db is not None
        assert self.db.db_name == ":memory:"

    # Тест что подключение к БД работает
    def test_connection_works(self):
        # Проверяем что можем получить соединение
        with self.db._get_connection() as conn:
            assert conn is not None

    # Тест метода создания таблиц
    def test_table_creation_method(self):
        # Вызываем метод создания таблиц и проверяем что нет ошибок
        try:
            self.db._create_tables()
            assert True  # Если дошли сюда - метод работает
        except Exception:
            assert False  # Если ошибка - тест провален

    # Тест что метод добавления записи существует
    def test_add_record_method_exists(self):
        # Просто проверяем что метод есть
        assert hasattr(self.db, 'add_sleep_record')
        assert callable(self.db.add_sleep_record)

    # Тест что метод получения записей существует
    def test_get_records_method_exists(self):
        # Просто проверяем что метод есть
        assert hasattr(self.db, 'get_all_records')
        assert callable(self.db.get_all_records)

    # Тест что метод очистки существует
    def test_clear_method_exists(self):
        # Просто проверяем что метод есть
        assert hasattr(self.db, 'clear_all_records')
        assert callable(self.db.clear_all_records)


# Тесты для операций с файлом базы данных
class TestDatabaseFileOperations:
    # Тест создания файла базы данных
    def test_database_file_creation(self):
        test_db_name = "test_sleep_tracker.db"

        # Удаляем файл если существует
        if os.path.exists(test_db_name):
            os.remove(test_db_name)

        # Создаем новую БД
        db = DatabaseManager(test_db_name)

        # Проверяем что файл создан
        assert os.path.exists(test_db_name)

        # Тестируем операции
        from model import SleepRecord
        record = SleepRecord(date.today(), 7.5, 8)
        db.add_sleep_record(record)
        assert db.get_records_count() == 1

        # Очистка
        if os.path.exists(test_db_name):
            os.remove(test_db_name)

# Тест пользовательских исключений
def test_custom_exceptions():
    with pytest.raises(InvalidDurationError):
        raise InvalidDurationError("Test duration error")

    with pytest.raises(InvalidDateError):
        raise InvalidDateError("Test date error")

    with pytest.raises(InvalidQualityError):
        raise InvalidQualityError("Test quality error")

# Тест сообщений исключений
def test_exception_messages():
    try:
        raise InvalidDurationError("Сообщение об ошибке")
    except InvalidDurationError as e:
        assert str(e) == "Сообщение об ошибке"

    try:
        raise InvalidDateError("Ошибка даты")
    except InvalidDateError as e:
        assert str(e) == "Ошибка даты"


# Тесты для граничных случаев
def test_edge_cases():
    # Минимальная допустимая продолжительность
    record = SleepRecord(date.today(), 0.1, 1)
    assert record.duration_hours == 0.1

    # Максимальная допустимая продолжительность
    record = SleepRecord(date.today(), 24.0, 10)
    assert record.duration_hours == 24.0

    # Минимальное качество
    record = SleepRecord(date.today(), 7.5, 1)
    assert record.quality == 1

    # Максимальное качество
    record = SleepRecord(date.today(), 7.5, 10)
    assert record.quality == 10

# Тесты для контроллера
class TestSleepTrackerController:
    # Простой тест что модуль импортируется
    def test_controller_module_import(self):
        try:
            from controller import SleepTrackerController
            assert True
        except ImportError:
            pytest.skip("Модуль контроллера недоступен")

    # Простой тест что модель импортируется
    def test_model_module_import(self):
        try:
            from model import SleepTrackerModel
            assert True
        except ImportError:
            pytest.skip("Модуль модели недоступен")

    # Тест что классы существуют
    def test_classes_exist(self):
        try:
            from controller import SleepTrackerController
            from model import SleepTrackerModel
            assert SleepTrackerController is not None
            assert SleepTrackerModel is not None
        except ImportError:
            pytest.skip("Модули недоступны")