from typing import List, Tuple, Optional, Dict
from math import sqrt

# Класс, представляющий точку в двумерном пространстве
class Point:
    def __init__(self, x: float, y: float):
        # Координата X точки
        self.x = x
        # Координата Y точки
        self.y = y

    # Вычисление евклидова расстояния до другой точки
    def distance_to(self, other: 'Point') -> float:
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    # Проверка равенства двух точек по координатам
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Хэш-функция для использования точки в множествах и слов
    def __hash__(self):
        return hash((self.x, self.y))


# Модель графа для представления задачи коммивояжера
class GraphModel:
    def __init__(self):
        def __init__(self):
        #Список вершин графа (точек)
        self.points: List[Point] = []
        # Храним ребра с весами (point1_idx, point2_idx, weight)
        self.edges: List[Tuple[int, int, float]] = []
        # Словарь для быстрого доступа к весам
        self.edge_weights: Dict[Tuple[int, int], float] = {}
        # Матрица расстояний между всеми парами точек
        self.distance_matrix: Optional[List[List[float]]] = None
        # Минимальное расстояние между точками (в пикселях)
        self.min_distance = 40.0

    # Добавление новой точки в граф
    def add_point(self, x: float, y: float) -> int:
        # Проверка на существующие точки
        for i, existing_point in enumerate(self.points):
            distance = existing_point.distance_to(Point(x, y))
            if distance < self.min_distance:
                raise ValueError(
                    f"Точка ({x:.1f}, {y:.1f}) слишком близко к существующей точке {i}")

        # Создание объекта точки
        point = Point(x, y)
        # Добавление точки в список
        self.points.append(point)
        # Обновление матрицы расстояний
        self._update_distance_matrix()
        # Возврат индекса добавленной точки
        return len(self.points) - 1
    #Добавляет ребро с весом
    def add_edge(self, point1_idx: int, point2_idx: int, weight: float):
        if (point1_idx < 0 or point1_idx >= len(self.points) or
                point2_idx < 0 or point2_idx >= len(self.points)):
            return

        if point1_idx == point2_idx:
            return

        # Нормализуем индексы
        idx1, idx2 = min(point1_idx, point2_idx), max(point1_idx, point2_idx)

        # Удаляем старое ребро если существует
        self.edges = [e for e in self.edges if not (e[0] == idx1 and e[1] == idx2)]

        # Добавляем новое ребро с весом
        edge = (idx1, idx2, weight)
        self.edges.append(edge)
        self.edge_weights[(idx1, idx2)] = weight

        # Обновляем матрицу расстояний
        self._update_distance_matrix()
    #Возвращает вес ребра между двумя точками
    def get_edge_weight(self, point1_idx: int, point2_idx: int) -> Optional[float]:

        idx1, idx2 = min(point1_idx, point2_idx), max(point1_idx, point2_idx)
        return self.edge_weights.get((idx1, idx2))
    # Обновление матрицы расстояний между всеми точками
    def _update_distance_matrix(self):
        # Количество точек в графе
        n = len(self.points)
        # Инициализация матрицы нулями
        self.distance_matrix = [[0.0] * n for _ in range(n)]
        # Заполнение матрицы расстояний
        for i in range(n):
            for j in range(i + 1, n):
                # Используем пользовательский вес если ребро существует, иначе евклидово расстояние
                weight = self.get_edge_weight(i, j)
                if weight is not None:
                    distance = weight
                else:
                    distance = self.points[i].distance_to(self.points[j])

                self.distance_matrix[i][j] = distance
                self.distance_matrix[j][i] = distance

    def clear(self):
        self.points.clear()
        self.edges.clear()
        self.edge_weights.clear()
        self.distance_matrix = None

    # Получение списка координат всех точек
    def get_points(self) -> List[Tuple[float, float]]:
        # Преобразование объектов Point в кортежи координат
        return [(p.x, p.y) for p in self.points]