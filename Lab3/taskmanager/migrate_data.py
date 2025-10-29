import os
import django
import sqlite3
import psycopg2
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
django.setup()


def migrate_data():
    print("=== МИГРАЦИЯ ДАННЫХ ИЗ SQLite В PostgreSQL ===")

    try:
        # Подключение к SQLite
        sqlite_conn = sqlite3.connect('/app/db.sqlite3')
        sqlite_cursor = sqlite_conn.cursor()

        # Получаем данные
        sqlite_cursor.execute("SELECT sleep_date, duration_hours, quality, notes FROM sleep_tracker_sleeprecord")
        records = sqlite_cursor.fetchall()

        print(f"Найдено записей в SQLite: {len(records)}")

        if not records:
            print("Нет данных для миграции")
            return

        # Подключение к PostgreSQL
        pg_conn = psycopg2.connect(
            host='db',
            database='sleep_tracker',
            user='postgres',
            password='password'
        )
        pg_cursor = pg_conn.cursor()


        # Переносим данные
        for record in records:
            sleep_date, duration_hours, quality, notes = record
            pg_cursor.execute(
                "INSERT INTO sleep_tracker_sleeprecord (sleep_date, duration_hours, quality, notes, created_at) VALUES (%s, %s, %s, %s, %s)",
                (sleep_date, float(duration_hours), quality, notes, datetime.now())
            )
            print(f"{sleep_date} - {duration_hours}ч")

        pg_conn.commit()
        print(f"Успешно перенесено: {len(records)} записей")

        sqlite_conn.close()
        pg_conn.close()

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == '__main__':
    migrate_data()