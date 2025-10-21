"""Модуль для работы с базой данных SQLite"""
import sqlite3
from datetime import date
from contextlib import contextmanager


class DatabaseManager:

    def __init__(self, db_name = "sleep_tracker.db"):
        self.db_name = db_name
        self._create_tables()

    # Контекстный менеджер для подключения к БД
    @contextmanager
    def _get_connection(self):

        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row # Чтобы получить данные, как словарь
        try:
            yield conn
        finally:
            conn.close()

    # Создает таблицы в базе данных
    def _create_tables(self):
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS sleep_records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sleep_date TEXT NOT NULL,
            duration_hours REAL NOT NULL,
            quality INTEGER NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            conn.commit()

    # Добавляет запись о сне в базу данных
    def add_sleep_record(self, record):
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO sleep_records (sleep_date, duration_hours, quality, notes)
                VALUES (?, ?, ?, ?)
            """, (record.sleep_date.isoformat(), record.duration_hours, record.quality, record.notes))
            conn.commit()
            return cursor.lastrowid

    # Возвращает все записи о сне из базы данных
    def get_all_records(self):
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT sleep_date, duration_hours, quality, notes 
                FROM sleep_records 
                ORDER BY sleep_date DESC
            """)
            records = []
            for row in cursor:
                sleep_date = date.fromisoformat(row['sleep_date'])
                from model import SleepRecord
                record = SleepRecord(
                    sleep_date=sleep_date,
                    duration_hours=row['duration_hours'],
                    quality=row['quality'],
                    notes=row['notes']
                )
                records.append(record)
            return records

    # Рассчитывает среднюю продолжительность сна за 7 дней
    def get_weekly_average(self):
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT AVG(duration_hours) as avg_duration
                FROM sleep_records 
                WHERE sleep_date >= date('now', '-7 days')
            """)
            result = cursor.fetchone()
            return result['avg_duration'] or 0.0

    # Возвращает количество записей в бд
    def get_records_count(self):
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM sleep_records")
            return cursor.fetchone()['count']

    # Очищает все записи (для тестирования)
    def clear_all_records(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM sleep_records")
            conn.commit()