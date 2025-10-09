from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, Any, List

# Базовый класс для всех сущностей библиотеки
class LibraryEntity(ABC):

    def __init__(self, name: str, entity_id: int = None):
        self._name = name
        self._entity_id = entity_id

    @abstractmethod
    def get_info(self):
        pass

    @property
    @abstractmethod
    def entity_type(self):
        pass

    # Dunder-методы
    def __str__(self):
        return f"{self.entity_type}: '{self.name}'"

    # Managed-атрибуты
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value:
            raise ValueError("Название не может быть пустым")
        self._name = value

    @property
    def entity_id(self) -> int:
        return self._entity_id

# Класс книги
class Book(LibraryEntity):
    def __init__(self, title: str, author: str, total_pages: int):
        super().__init__(title)
        self._author = author
        self._total_pages = total_pages
        self._pages_read = 0

    # Абстрактные методы
    @property
    def entity_type(self):
        return "Книга"

    def get_info(self):
        return f"Книга: '{self.name}' - {self.author}"

    # Dunder-методы
    def __len__(self):
        return self.total_pages

    # Managed-атрибуты
    @property
    def author(self):
        return self._author

    @property
    def total_pages(self) -> int:
        return self._total_pages

    @property
    def pages_read(self) -> int:
        return self._pages_read

    # Основные методы
    def read_pages(self, pages: int) -> bool:
        if self.pages_read + pages <= self.total_pages:
            self._pages_read += pages
            return True
        return False

    def is_finished(self) -> bool:
        return self.pages_read >= self.total_pages

    def to_dict(self) -> Dict[str, Any]:
        return{
            'book_id': self.entity_id,
            'title': self.name,
            'author': self.author,
            'total_pages': self.total_pages,
            'pages_read': self.pages_read
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        book = cls(
            title=data['title'],
            author=data['author'],
            total_pages=data['total_pages']
        )
        if 'book_id' in data and data['book_id'] is not None:
            book._entity_id = data['book_id']
        # ИСПРАВИТЬ СКОБКИ: data.get() а не data.get[]
        book._pages_read = data.get('pages_read', 0)  # КРУГЛЫЕ СКОБКИ!
        return book

# Класс читателя
class Reader(LibraryEntity):

    def __init__(self, name: str, reader_id: int = None):
        super().__init__(name, reader_id)
        self._books_in_progress = {}

    # Абстрактные методы
    @property
    def entity_type(self):
        return "Читатель"

    def get_info(self):
        return f"Читатель: {self.name}"

    # Dunder-методы
    def __len__(self):
        return len(self.books_in_progress)

    # Managed-атрибуты
    @property
    def reader_id(self):
        return self.entity_id

    @property
    def books_in_progress(self):
        return self._books_in_progress

    # Основные методы
    def read_book(self, book: Book, pages: int) -> bool:
        if book not in self.books_in_progress:
            self.books_in_progress[book] = 0

        if book.read_pages(pages):
            self.books_in_progress[book] += pages
            return True
        return False

    def get_total_pages_read(self):
        return sum(self.books_in_progress.values())

    def get_reading_statistics(self):
        total_books = len(self.books_in_progress)
        total_pages = self.get_total_pages_read()
        finished_books = sum(1 for book in self.books_in_progress if book.is_finished())

        return {
            'total_books': total_books,
            'finished_books': finished_books,
            'total_pages': total_pages,
            'in_progress_books': total_books - finished_books
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            'reader_id': self.entity_id,
            'name': self.name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(data['name'], data['reader_id'])


#Класс абонемент
class Subscription(LibraryEntity):

    def __init__(self, reader: Reader, duration_days: int = 365):
        super().__init__(f"Абонемент {reader.name}")
        self._reader = reader
        self._start_date = datetime.now()
        self._duration_days = duration_days

    # Абстрактные методы
    @property
    def entity_type(self):
        return "Абонемент"

    def get_info(self):
        return f"Абонемент {self.reader.name}"

    # Dunder-методы
    def __bool__(self):
        return self.is_active

    # Managed-атрибуты
    @property
    def reader(self):
        return self._reader

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._start_date + timedelta(days=self._duration_days)

    @property
    def is_active(self):
        return datetime.now() <= self.end_date

    @property
    def days_remaining(self):
        remaining = self.end_date - datetime.now()
        return max(0, remaining.days)

    def get_status_info(self):

        return {
            'reader_name': self.reader.name,
            'start_date': self.start_date.strftime('%d.%m.%Y'),
            'end_date': self.end_date.strftime('%d.%m.%Y'),
            'is_active': self.is_active,
            'days_remaining': self.days_remaining
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            'subscription_id': self.entity_id,
            'reader_id': self.reader.reader_id,
            'start_date': self.start_date.isoformat(),
            'duration_days': self._duration_days
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], reader: Reader):
        subscription = cls(reader, data['duration_days'])
        if 'subscription_id' in data and data['subscription_id'] is not None:
            subscription._entity_id = data['subscription_id']
        subscription._start_date = datetime.fromisoformat(data['start_date'])
        return subscription

