import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Dict, Any
import json
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = None):
        # Используем путь из переменной окружения или по умолчанию
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'tsp_results.db')
        print(f"Database path: {self.db_path}")  # Для отладки
        self._init_database()

    @contextmanager
    def _get_connection(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self):
        # Создаем директорию для БД если не существует
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
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
            conn.commit()

    def save_result(self, points_count: int, algorithm_params: Dict[str, Any],
                    path_length: float, path_indices: List[int],
                    computation_time: float):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tsp_results 
                (timestamp, points_count, algorithm_params, path_length, path_indices, computation_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                points_count,
                json.dumps(algorithm_params),
                path_length,
                json.dumps(path_indices),
                computation_time
            ))
            conn.commit()

    def get_all_results(self) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tsp_results ORDER BY timestamp DESC
            ''')
            return cursor.fetchall()

    def get_results_by_points_count(self, points_count: int) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tsp_results WHERE points_count = ? ORDER BY path_length ASC
            ''', (points_count,))
            return cursor.fetchall()