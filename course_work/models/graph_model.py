from typing import List, Tuple, Optional
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

    # Хэш-функция для использования точки в множествах и словарях
    def __hash__(self):
        return hash((self.x, self.y))


# Модель графа для представления задачи коммивояжера
class GraphModel:
    def __init__(self):
        # Список вершин графа (точек)
        self.points: List[Point] = []
        # Список ребер графа как пар индексов точек
        self.edges: List[Tuple[int, int]] = []
        # Матрица расстояний между всеми парами точек
        self.distance_matrix: Optional[List[List[float]]] = None

    # Добавление новой точки в граф
    def add_point(self, x: float, y: float) -> int:
        # Создание объекта точки
        point = Point(x, y)
        # Добавление точки в список
        self.points.append(point)
        # Обновление матрицы расстояний
        self._update_distance_matrix()
        # Возврат индекса добавленной точки
        return len(self.points) - 1

    # Добавление ребра между двумя точками по их индексам
    def add_edge(self, point1_idx: int, point2_idx: int):
        # Проверяем валидность индексов
        if (point1_idx < 0 or point1_idx >= len(self.points) or
                point2_idx < 0 or point2_idx >= len(self.points)):
            return  # Не добавляем ребро если индексы невалидны

        if point1_idx != point2_idx:
            edge = (min(point1_idx, point2_idx), max(point1_idx, point2_idx))
            if edge not in self.edges:
                self.edges.append(edge)

    # Очистка графа (удаление всех точек и ребер)
    def clear(self):
        # Очистка списка точек
        self.points.clear()
        # Очистка списка ребер
        self.edges.clear()
        # Сброс матрицы расстояний
        self.distance_matrix = None

    # Обновление матрицы расстояний между всеми точками
    def _update_distance_matrix(self):
        # Количество точек в графе
        n = len(self.points)
        # Инициализация матрицы нулями
        self.distance_matrix = [[0.0] * n for _ in range(n)]

        # Заполнение матрицы расстояний
        for i in range(n):
            for j in range(i + 1, n):
                # Вычисление расстояния между точками i и j
                distance = self.points[i].distance_to(self.points[j])
                # Заполнение обоих направлений (матрица симметрична)
                self.distance_matrix[i][j] = distance
                self.distance_matrix[j][i] = distance

    # Получение списка координат всех точек
    def get_points(self) -> List[Tuple[float, float]]:
        # Преобразование объектов Point в кортежи координат
        return [(p.x, p.y) for p in self.points]