import sqlite3

conn = sqlite3.connect('sleep_tracker.db')
cursor = conn.cursor()

# Проверим количество записей
cursor.execute("SELECT COUNT(*) FROM sleep_records;")
count = cursor.fetchone()[0]
print(f"Количество записей в sleep_records: {count}")

# Покажем первые 3 записи
if count > 0:
    cursor.execute("SELECT * FROM sleep_records LIMIT 3;")
    records = cursor.fetchall()
    print("Первые 3 записи:")
    for record in records:
        print(record)

conn.close()