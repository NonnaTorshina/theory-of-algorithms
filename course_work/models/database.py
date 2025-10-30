import sqlite3
from datetime import datetime
from typing import List, Tuple, Dict, Any
import json

# Класс для управления базой данных SQLite для хранения результатов расчетов
class DatabaseManager:
    def __init__(self, db_path: str = "tsp_results.db"):
        # Путь к файлу базы данных
        self.db_path = db_path
        # Инициализация базы данных при создании объекта
        self._init_database()

    # Метод инициализации структуры базы данных
    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Создание таблицы для хранения результатов, если она не существует
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tsp_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    points_count INTEGER NOT NULL,
                    algorithm_params TEXT NOT NULL,
                    path_length REAL NOT NULL,
                    path_indices TEXT NOT NULL,
                    computation_time REAL NOT NULL
                )
            ''')
            # Подтверждение изменений в базе данных
            conn.commit()

    # Метод сохранения результата расчета в базу данных
    def save_result(self, points_count: int, algorithm_params: Dict[str, Any],
                    path_length: float, path_indices: List[int],
                    computation_time: float):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # SQL-запрос для вставки данных о результате расчета
            cursor.execute('''
                INSERT INTO tsp_results 
                (timestamp, points_count, algorithm_params, path_length, path_indices, computation_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                # Временная метка выполнения расчета
                datetime.now().isoformat(),
                # Количество точек в задаче
                points_count,
                # Параметры алгоритма в формате JSON
                json.dumps(algorithm_params),
                # Длина найденного пути
                path_length,
                # Индексы точек в порядке обхода (в формате JSON)
                json.dumps(path_indices),
                # Время выполнения расчета в секундах
                computation_time
            ))
            # Подтверждение сохранения данных
            conn.commit()

    # Метод получения всех результатов из базы данных
    def get_all_results(self) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # SQL-запрос для выборки всех записей, отсортированных по времени (новые первыми)
            cursor.execute('''
                SELECT * FROM tsp_results ORDER BY timestamp DESC
            ''')
            # Возврат всех найденных записей
            return cursor.fetchall()

    # Метод получения результатов по количеству точек
    def get_results_by_points_count(self, points_count: int) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # SQL-запрос для выборки записей с определенным количеством точек
            cursor.execute('''
                SELECT * FROM tsp_results WHERE points_count = ? ORDER BY path_length ASC
            ''', (points_count,))
            # Возврат отсортированных результатов (лучшие решения первыми)
            return cursor.fetchall()