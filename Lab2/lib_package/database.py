import sqlite3
from typing import List, Dict, Any
from datetime import datetime
from .models import Book, Reader, Subscription

#Сервис для работы с базой данных
class DatabaseManager:
    def __init__(self, db_path: str = "library.db"):
        self.db_path = db_path
        self.init_database()
    # Инициализируем таблицы базы данных
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Таблица книг
            cursor.execute(
                ''' CREATE TABLE IF NOT EXISTS books (
                    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    total_pages INTEGER NOT NULL,
                    pages_read INTEGER DEFAULT 0
                ) '''
            )

            #Таблица читателей
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS readers (
                               reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
                               name TEXT NOT NULL
                           )
                       ''')

            #Таблица абонементов
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS subscriptions (
                                subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                reader_id INTEGER NOT NULL,
                                start_date TEXT NOT NULL,
                                duration_days INTEGER NOT NULL,
                                FOREIGN KEY (reader_id) REFERENCES readers (reader_id)
                            )
                        ''')
            #Таблица для связи читателей и книг 9чтиение)
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS reading_progress (
                                progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                reader_id INTEGER NOT NULL,
                                book_id INTEGER NOT NULL,
                                pages_read INTEGER NOT NULL,
                                FOREIGN KEY (reader_id) REFERENCES readers (reader_id),
                                FOREIGN KEY (book_id) REFERENCES books (book_id)
                            )
                        ''')
            # Таблица для хранения отчетов
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS reports (
                                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                reader_id INTEGER NOT NULL,
                                report_date TEXT NOT NULL,
                                report_data TEXT NOT NULL,
                                FOREIGN KEY (reader_id) REFERENCES readers (reader_id)
                            )
                        ''')
            #Таблица для статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reader_id INTEGER NOT NULL,
                    calculation_date TEXT NOT NULL,
                    total_books_read INTEGER,
                    books_in_progress INTEGER,
                    total_pages_read INTEGER,
                    average_rating REAL,
                    FOREIGN KEY (reader_id) REFERENCES readers (reader_id)
                )
            ''')
            conn.commit()

    #Методы для работы с книгами
    def save_book(self, book: Book) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # ПРОВЕРЯЕМ, есть ли уже такая книга
            cursor.execute('SELECT book_id FROM books WHERE title=? AND author=?',
                           (book.name, book.author))
            existing = cursor.fetchone()

            if existing:
                # Книга уже есть - возвращаем существующий ID
                return existing[0]
            elif book.entity_id:
                # Обновляем существующую книгу
                cursor.execute('''
                    UPDATE books SET title=?, author=?, total_pages=?, pages_read=?
                    WHERE book_id=?
                ''', (book.name, book.author, book.total_pages, book.pages_read, book.entity_id))
                book_id = book.entity_id
            else:
                # Создаем новую книгу
                cursor.execute('''
                    INSERT INTO books (title, author, total_pages, pages_read)
                    VALUES (?, ?, ?, ?)
                ''', (book.name, book.author, book.total_pages, book.pages_read))
                book_id = cursor.lastrowid

            conn.commit()
            return book_id

    def get_all_books(self) -> List[Book]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books')
            books_data = cursor.fetchall()

            books = []
            for book_data in books_data:
                book_dict = {
                    'book_id': book_data[0],
                    'title': book_data[1],
                    'author': book_data[2],
                    'total_pages': book_data[3],
                    'pages_read': book_data[4]
                }
                books.append(Book.from_dict(book_dict))
            return books

    # Методы для работы с читателями
    def save_reader(self, reader: Reader) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if reader.entity_id:
                cursor.execute('UPDATE readers SET name=? WHERE reader_id=?',
                               (reader.name, reader.entity_id))
                reader_id = reader.entity_id
            else:
                cursor.execute('INSERT INTO readers (name) VALUES (?)', (reader.name,))
                reader_id = cursor.lastrowid
            conn.commit()
            return reader_id

    def get_reader(self, reader_id: int) -> [Reader]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM readers WHERE reader_id=?', (reader_id,))
            reader_data = cursor.fetchone()

            if reader_data:
                reader_dict = {
                    'reader_id': reader_data[0],
                    'name': reader_data[1]
                }
                return Reader.from_dict(reader_dict)
            return None

    # Методы для работы с абонементами
    def save_subscription(self, subscription: Subscription) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            reader_id = self.save_reader(subscription.reader)

            if subscription.entity_id:
                cursor.execute('''
                    UPDATE subscriptions SET reader_id=?, start_date=?, duration_days=?
                    WHERE subscription_id=?
                ''', (reader_id, subscription.start_date.isoformat(),
                      subscription._duration_days, subscription.entity_id))
                subscription_id = subscription.entity_id
            else:
                cursor.execute('''
                    INSERT INTO subscriptions (reader_id, start_date, duration_days)
                    VALUES (?, ?, ?)
                ''', (reader_id, subscription.start_date.isoformat(),
                      subscription._duration_days))
                subscription_id = cursor.lastrowid
            conn.commit()
            return subscription_id

    def get_subscription(self, reader_id: int) -> [Subscription]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM subscriptions WHERE reader_id=?', (reader_id,))
            subscription_data = cursor.fetchone()

            if subscription_data:
                reader = self.get_reader(reader_id)

                if reader is None:
                    return None
                subscription_dict = {
                    'subscription_id': subscription_data[0],
                    'reader_id': subscription_data[1],
                    'start_date': subscription_data[2],
                    'duration_days': subscription_data[3]
                }
                return Subscription.from_dict(subscription_dict, reader)

    # Для сохранения расчетов (статистики)
    def save_statistics(self, reader_id: int, stats_data: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO statistics 
                (reader_id, calculation_date, total_books_read, books_in_progress, total_pages_read, average_rating)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                reader_id,
                datetime.now().isoformat(),
                stats_data.get('total_books_read', 0),
                stats_data.get('books_in_progress', 0),
                stats_data.get('total_pages_read', 0),
                stats_data.get('average_rating', 0)
            ))
            conn.commit()


    # Методы для работы с прогрессом чтения
    def save_reading_progress(self, reader: Reader, book: Book, pages_read: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            reader_id = self.save_reader(reader)
            book_id = self.save_book(book)

            cursor.execute('''
                INSERT OR REPLACE INTO reading_progress (reader_id, book_id, pages_read)
                VALUES (?, ?, ?)
            ''', (reader_id, book_id, pages_read))
            conn.commit()

    def get_reading_progress(self, reader_id: int) -> Dict[int, int]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT book_id, pages_read FROM reading_progress 
                WHERE reader_id=?
            ''', (reader_id,))
            progress_data = cursor.fetchall()

            return {book_id: pages_read for book_id, pages_read in progress_data}

    # Методы для сохранения отчетов
    def save_report(self, reader_id: int, report_data: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            import json
            cursor.execute('''
                INSERT INTO reports (reader_id, report_date, report_data)
                VALUES (?, ?, ?)
            ''', (reader_id, datetime.now().isoformat(), json.dumps(report_data)))
            conn.commit()

    def get_reports(self, reader_id: int) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reports WHERE reader_id=?', (reader_id,))
            reports_data = cursor.fetchall()

            import json
            reports = []
            for report_data in reports_data:
                reports.append({
                    'report_id': report_data[0],
                    'reader_id': report_data[1],
                    'report_date': report_data[2],
                    'report_data': json.loads(report_data[3])
                })
            return reports

    def check_database(self):
        """Проверяет содержимое БД"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            print("\n=== ПРОВЕРКА БАЗЫ ДАННЫХ ===")

            # Проверяем таблицы
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("Таблицы в БД:", [table[0] for table in tables])

            # Проверяем книги
            cursor.execute("SELECT * FROM books")
            books = cursor.fetchall()
            print(f"Книг в БД: {len(books)}")
            for book in books:
                print(f"  ID: {book[0]}, Название: {book[1]}")

            # Проверяем читателей
            cursor.execute("SELECT * FROM readers")
            readers = cursor.fetchall()
            print(f"Читателей в БД: {len(readers)}")

            # Проверяем статистику
            cursor.execute("SELECT * FROM statistics")
            stats = cursor.fetchall()
            print(f"Записей статистики: {len(stats)}")