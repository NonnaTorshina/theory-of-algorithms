from typing import Dict, Any
from .models import Book, Reader, Subscription
from .database import DatabaseManager
from datetime import datetime

class StatisticsService:
    #Расчет статистики читателя с рейтингом по каждой книге
    @staticmethod
    def calculate_reader_statistics(reader: Reader) -> Dict[str, Any]:

        stats = reader.get_reading_statistics()

        # Рейтинг по каждой книге в %
        book_ratings = []
        for book, pages_read in reader.books_in_progress.items():
            progress_percent = (pages_read / book.total_pages) * 100
            book_ratings.append({
                'book_name': book.name,
                'progress_percent': round(progress_percent, 1),
                'pages_read': pages_read,
                'total_pages': book.total_pages
            })

        # Общий рейтинг (средний по всем книгам)
        total_rating = 0
        if book_ratings:
            total_rating = sum(rating['progress_percent'] for rating in book_ratings) / len(book_ratings)

        return {
            'reader_name': reader.name,
            'total_books_read': stats['finished_books'],
            'books_in_progress': stats['in_progress_books'],
            'total_pages_read': stats['total_pages'],
            'book_ratings': book_ratings,  # Рейтинг по каждой книге
            'average_rating': round(total_rating, 1)  # Средний рейтинг
        }

    @staticmethod
    def calculate_subscription_statistics(subscription: Subscription) -> Dict[str, Any]:

        status = subscription.get_status_info()

        return {
            'reader_name': status['reader_name'],
            'is_active': status['is_active'],
            'days_remaining': status['days_remaining'],
            'end_date': status['end_date'],
            'subscription_status': 'Активен' if status['is_active'] else 'Неактивен'
        }


# Основной сервис библиотеки
class LibraryService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    #Загружает прогресс чтения читателя из БД
    def load_reader_data(self, reader: Reader):
        progress_data = self.db_manager.get_reading_progress(reader.reader_id)
        books = self.db_manager.get_all_books()

        # Очищаем текущий прогресс
        reader._books_in_progress.clear()

        for book in books:
            if book.entity_id in progress_data:
                pages_read = progress_data[book.entity_id]
                book.pages_read = pages_read
                reader.books_in_progress[book] = pages_read

    def get_complete_report(self, reader: Reader, subscription: Subscription) -> Dict[str, Any]:
        reader_stats = StatisticsService.calculate_reader_statistics(reader)
        subscription_stats = StatisticsService.calculate_subscription_statistics(subscription)

        # СОХРАНЯЕМ СТАТИСТИКУ В БД
        self.db_manager.save_statistics(reader.reader_id, reader_stats)

        report_data = {
            'reader_statistics': reader_stats,
            'subscription_statistics': subscription_stats,
            'report_date': datetime.now().strftime('%d.%m.%Y %H:%M')
        }

        # Сохраняем отчет в БД
        self.db_manager.save_report(reader.reader_id, report_data)

        return report_data
    #Сохраняет сессию чтения в БД и автоматически статистику
    def save_reading_session(self, reader: Reader, book: Book, pages: int):
        if reader.read_book(book, pages):
            self.db_manager.save_reading_progress(reader, book, pages)

            # Автоматически сохраняем статистику после чтения
            reader_stats = StatisticsService.calculate_reader_statistics(reader)
            self.db_manager.save_statistics(reader.reader_id, reader_stats)

            return True
        return False
