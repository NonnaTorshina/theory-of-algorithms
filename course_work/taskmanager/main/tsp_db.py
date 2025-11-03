import sqlite3
import json
from pathlib import Path

#Возвращает путь к БД tsp_results.db
def get_tsp_db_path():
    return Path('C:/python 3.8/theory-of-algorithms/course_work/tsp_results.db')


#Сохраняет расчет в БД
def save_calculation(vertices, optimal_path, distance, execution_time, parameters):
    db_path = get_tsp_db_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаем таблицу если ее нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vertices TEXT NOT NULL,
            optimal_path TEXT NOT NULL,
            distance REAL NOT NULL,
            execution_time REAL NOT NULL,
            vertices_count INTEGER NOT NULL,
            parameters TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Вставляем данные
    cursor.execute('''
        INSERT INTO calculations 
        (vertices, optimal_path, distance, execution_time, vertices_count, parameters)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        json.dumps(vertices),
        json.dumps(optimal_path),
        distance,
        execution_time,
        len(vertices),
        json.dumps(parameters)
    ))

    calculation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return calculation_id

#Получает все расчеты из БД
def get_all_calculations():
    db_path = get_tsp_db_path()

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM calculations 
            ORDER BY created_at DESC
        ''')

        calculations = []
        for row in cursor.fetchall():
            calculations.append({
                'id': row['id'],
                'vertices': json.loads(row['vertices']),
                'optimal_path': json.loads(row['optimal_path']),
                'distance': row['distance'],
                'execution_time': row['execution_time'],
                'vertices_count': row['vertices_count'],
                'parameters': json.loads(row['parameters']),
                'created_at': row['created_at']
            })

        conn.close()
        return calculations

    except Exception as e:
        print(f"Ошибка при чтении из БД: {e}")
        return []