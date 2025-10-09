import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib_package.models import Reader, Book, Subscription
from lib_package.services import StatisticsService
from lib_package.utils import ReportGenerator


class TestReader:
    # Тест создания читателя с основными данными
    def test_reader_creation_basic(self):
        reader = Reader("Иван Иванов")  # Только имя, без ID

        assert reader.name == "Иван Иванов"
        assert reader.entity_id is None

    #Тест создания читателя с полным ФИО
    def test_reader_creation_full_name(self):
        reader = Reader("Петров Петр Петрович")

        assert reader.name == "Петров Петр Петрович"

    #Тест получения информации о читателе
    def test_reader_get_info(self):
        reader = Reader("Анна Сидорова")
        info = reader.get_info()

        assert "Читатель: Анна Сидорова" in info

    #Тест строкового представления
    def test_reader_string_representation(self):
        reader = Reader("Ольга Кузнецова")
        reader_str = str(reader)

        assert "Читатель" in reader_str
        assert "Ольга Кузнецова" in reader_str


class TestBook:
    #Тест создания книги
    def test_book_creation(self):
        book = Book("Преступление и наказание", "Ф.М. Достоевский", 672)

        assert book.name == "Преступление и наказание"
        assert book.author == "Ф.М. Достоевский"
        assert book.total_pages == 672

    # Тест книги с нулевым количеством страниц
    def test_book_with_zero_pages(self):
        book = Book("Тестовая книга", "Тестовый автор", 0)

        assert book.total_pages == 0
        assert book.name == "Тестовая книга"

    #Тест строкового представления книги
    def test_book_string_representation(self):
        book = Book("Мастер и Маргарита", "М.А. Булгаков", 480)
        book_str = str(book)

        assert "Книга" in book_str
        assert "Мастер и Маргарита" in book_str



class TestSubscription:
    #Тест создания подписки
    def test_subscription_creation(self):
        reader = Reader("Тестовый Читатель")
        subscription = Subscription(reader, 30)

        assert subscription.reader == reader
        assert subscription.days_remaining > 0


    #Тест проверки активной подписки
    def test_subscription_is_active(self):
        reader = Reader("Тестовый Читатель")
        subscription = Subscription(reader, 30)

        assert subscription.is_active == True

    #Тест получения информации о статусе
    def test_subscription_get_status_info(self):
        reader = Reader("Тестовый Читатель")
        subscription = Subscription(reader, 30)
        status = subscription.get_status_info()

        assert status['reader_name'] == "Тестовый Читатель"
        assert status['is_active'] == True


class TestStatisticsService:
    #Тест статистики для читателя без книг
    def test_calculate_reader_statistics_empty(self):
        reader = Reader("Иван Иванов")
        stats = StatisticsService.calculate_reader_statistics(reader)

        assert stats['reader_name'] == "Иван Иванов"
        assert stats['total_books_read'] == 0
        assert stats['books_in_progress'] == 0
        assert stats['total_pages_read'] == 0
        assert stats['average_rating'] == 0
        assert stats['book_ratings'] == []

    #Тест статистики для читателя с книгами
    def test_calculate_reader_statistics_with_books(self):
        reader = Reader("Петр Петров")
        book1 = Book("Книга 1", "Автор 1", 100)
        book2 = Book("Книга 2", "Автор 2", 200)

        # Добавляем книги в прогресс
        reader.books_in_progress[book1] = 50  # 50%
        reader.books_in_progress[book2] = 100  # 50%

        stats = StatisticsService.calculate_reader_statistics(reader)

        assert stats['reader_name'] == "Петр Петров"
        assert stats['books_in_progress'] == 2
        assert stats['total_pages_read'] == 150
        assert stats['average_rating'] == 50.0  # (50% + 50%) / 2
        assert len(stats['book_ratings']) == 2

    #Тест статистики с завершенной книгой
    def test_calculate_reader_statistics_finished_book(self):
        reader = Reader("Анна Сидорова")
        book = Book("Книга", "Автор", 100)

        # Книга прочитана полностью
        reader.books_in_progress[book] = 100

        stats = StatisticsService.calculate_reader_statistics(reader)

        assert stats['total_books_read'] == 0
        assert stats['books_in_progress'] == 1
        assert stats['book_ratings'][0]['progress_percent'] == 100.0

    #Тест статистики активной подписки
    def test_calculate_subscription_statistics_active(self):
        reader = Reader("Ольга Кузнецова")
        subscription = Subscription(reader, 30)

        stats = StatisticsService.calculate_subscription_statistics(subscription)

        assert stats['reader_name'] == "Ольга Кузнецова"
        assert stats['is_active'] == True
        assert stats['subscription_status'] == 'Активен'
        assert stats['days_remaining'] > 0
        assert 'end_date' in stats

    #Тест точного расчета прогресса
    def test_calculate_reader_statistics_progress_calculation(self):
        reader = Reader("Тестовый Читатель")
        book = Book("Тестовая книга", "Автор", 200)

        reader.books_in_progress[book] = 75  # 37.5%

        stats = StatisticsService.calculate_reader_statistics(reader)
        book_rating = stats['book_ratings'][0]

        assert book_rating['progress_percent'] == 37.5
        assert book_rating['pages_read'] == 75
        assert book_rating['total_pages'] == 200

class TestReportGenerator:
    # Создание DOCX файла
    def test_save_to_docx_creates_file(self):
        test_data = {
            'reader_statistics': {
                'reader_name': 'Тестовый Читатель',
                'total_books_read': 3,
                'books_in_progress': 1,
                'total_pages_read': 500,
                'average_rating': 80.0
            },
            'subscription_statistics': {
                'subscription_status': 'Активен',
                'days_remaining': 10,
                'end_date': '2024-12-31'
            }
        }

        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            filename = tmp_file.name

        try:
            ReportGenerator.save_to_docx(test_data, filename)
            assert os.path.exists(filename), "DOCX файл должен быть создан"
            assert os.path.getsize(filename) > 0, "DOCX файл не должен быть пустым"
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    #Создание XLSX файла
    def test_save_to_xlsx_creates_file(self):
        test_data = {
            'reader_statistics': {
                'reader_name': 'Тестовый Читатель',
                'total_books_read': 3,
                'books_in_progress': 1,
                'total_pages_read': 500,
                'average_rating': 80.0
            },
            'subscription_statistics': {
                'subscription_status': 'Активен',
                'days_remaining': 10,
                'end_date': '2024-12-31'
            }
        }

        # Вместо временного файла, проверяем создание файла с фиксированным именем
        filename = "Library_report.xlsx"

        try:
            # Удаляем файл если он уже существует
            if os.path.exists(filename):
                os.unlink(filename)

            ReportGenerator.save_to_xlsx(test_data, filename)
            assert os.path.exists(filename), "XLSX файл должен быть создан"
            assert os.path.getsize(filename) > 0, "XLSX файл не должен быть пустым"
        finally:
            # Очистка
            if os.path.exists(filename):
                os.unlink(filename)

    # Создание JSON файла
    def test_save_to_json_creates_file(self):
        test_data = {
            'reader_statistics': {
                'reader_name': 'Тестовый Читатель',
                'total_books_read': 3
            },
            'subscription_statistics': {
                'subscription_status': 'Активен'
            },
            'report_date': '2024-01-01'
        }

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            filename = tmp_file.name

        try:
            ReportGenerator.save_to_json(test_data, filename)
            assert os.path.exists(filename), "JSON файл должен быть создан"

            # Проверяем что JSON можно прочитать
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data, "Данные в JSON должны совпадать"

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    # Создание TXT файла
    def test_save_to_txt_creates_file(self):
        test_data = {
            'reader_statistics': {
                'reader_name': 'Тестовый Читатель',
                'total_books_read': 3,
                'books_in_progress': 1,
                'total_pages_read': 500,
                'average_rating': 80.0,
                'book_ratings': []
            },
            'subscription_statistics': {
                'subscription_status': 'Активен',
                'days_remaining': 10,
                'end_date': '2024-12-31'
            },
            'report_date': '2024-01-01'
        }

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            filename = tmp_file.name

        try:
            ReportGenerator.save_to_txt(test_data, filename)
            assert os.path.exists(filename), "TXT файл должен быть создан"
            assert os.path.getsize(filename) > 0, "TXT файл не должен быть пустым"

            # Проверяем что файл содержит основные заголовки
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'ОТЧЕТ ЭЛЕКТРОННОЙ БИБЛИОТЕКИ' in content
            assert 'СТАТИСТИКА ЧИТАТЕЛЯ:' in content

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

