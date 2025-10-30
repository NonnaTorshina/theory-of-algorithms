from math import inf, sqrt
from random import random, shuffle
from typing import List, Tuple
from utils.path import Path


# Класс реализации муравьиного алгоритма для решения задачи коммивояжера
class ACOAlgorithm:
    def __init__(self, ants: int = 100, iterations: int = 20,
                 alpha: float = 1.5, beta: float = 1.2,
                 rho: float = 0.6, q: float = 10):
        # Количество муравьев в колонии
        self.ants = ants
        # Количество итераций алгоритма
        self.iterations = iterations
        # Параметр влияния феромона на выбор пути
        self.alpha = alpha
        # Параметр влияния эвристической информации (обратное расстояние)
        self.beta = beta
        # Коэффициент испарения феромона
        self.rho = rho
        # Константа для количества откладываемого феромона
        self.q = q

    # Статический метод для выбора следующей точки на основе вероятностей
    @staticmethod
    def _select_index(selection: List[float]) -> int:
        # Сумма всех вероятностей выбора
        sum_num = sum(selection)
        # Если все вероятности нулевые, выбираем последний элемент
        if sum_num == 0:
            return len(selection) - 1
        # Генерация случайного числа для выбора на основе вероятностей
        tmp_num = random()
        prob = 0
        # Накопительное суммирование вероятностей для выбора
        for i in range(len(selection)):
            prob += selection[i] / sum_num
            # Когда накопленная вероятность превышает случайное число - выбираем этот индекс
            if prob >= tmp_num:
                return i
        # Запасной вариант - возвращаем последний индекс
        return len(selection) - 1

    # Метод создания пути для одного муравья
    def _create_path(self, distance_matrix: List[List[float]],
                     pheromone_matrix: List[List[float]]) -> List[int]:
        # Количество точек (городов)
        n = len(distance_matrix)
        # Список непосещенных точек (изначально все точки)
        unvisited_indices = list(range(n))
        # Перемешиваем точки для случайного начального выбора
        shuffle(unvisited_indices)
        # Начинаем путь с случайной точки
        visited_indices = [unvisited_indices.pop()]

        # Посещаем оставшиеся n-1 точек
        for _ in range(n - 1):
            # Текущая позиция муравья (последняя посещенная точка)
            i = visited_indices[-1]
            selection = []
            # Для каждой непосещенной точки вычисляем вероятность перехода
            for j in unvisited_indices:
                # Уровень феромона на ребре i-j
                pheromone = pheromone_matrix[i][j]
                # Привлекательность ребра (обратно пропорциональна расстоянию)
                attractiveness = 1 / max(distance_matrix[i][j], 10 ** -5)
                # Вычисление вероятности выбора точки j
                selection.append(
                    (pheromone ** self.alpha) * (attractiveness ** self.beta)
                )
            # Выбор следующей точки на основе вероятностей
            selected_index = self._select_index(selection)
            # Добавляем выбранную точку в путь и удаляем из непосещенных
            visited_indices.append(unvisited_indices.pop(selected_index))

        # Замыкаем цикл - возвращаемся в начальную точку
        visited_indices.append(visited_indices[0])
        return visited_indices

    # Метод обновления матрицы феромонов
    def _update_pheromone(self, pheromone_matrix: List[List[float]],
                          paths: List[List[int]], lengths: List[float]) -> None:
        n = len(pheromone_matrix)

        # Испарение феромона на всех ребрах
        for i in range(n):
            for j in range(n):
                pheromone_matrix[i][j] *= (1 - self.rho)

        # Добавление нового феромона на основе пройденных путей
        for k in range(self.ants):
            # Количество феромона пропорционально качеству пути
            delta = self.q / lengths[k]
            path = paths[k]
            # Обновляем феромон на всех ребрах пройденного пути
            for idx in range(len(path) - 1):
                i = path[idx]
                j = path[idx + 1]
                pheromone_matrix[i][j] += delta
                pheromone_matrix[j][i] += delta

    # Статический метод вычисления длины пути
    @staticmethod
    def _calculate_path_length(distance_matrix: List[List[float]],
                               path: List[int]) -> float:
        total_length = 0.0
        # Суммируем расстояния между последовательными точками пути
        for i in range(len(path) - 1):
            total_length += distance_matrix[path[i]][path[i + 1]]
        return total_length

    # Основной метод решения задачи коммивояжера
    def solve_tsp(self, points: List[Tuple[float, float]]) -> Path:
        # Проверка минимального количества точек
        if len(points) < 3:
            raise ValueError("Need at least 3 points for TSP")

        n = len(points)

        # Создание матрицы расстояний между всеми парами точек
        distance_matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                # Вычисление евклидова расстояния между точками i и j
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                distance = sqrt(dx * dx + dy * dy)
                # Матрица симметрична
                distance_matrix[i][j] = distance
                distance_matrix[j][i] = distance

        # Инициализация матрицы феромонов единичными значениями
        pheromone_matrix = [[1.0] * n for _ in range(n)]

        # Лучший найденный путь и его длина
        best_path = []
        best_length = inf

        # Основной цикл алгоритма по итерациям
        for iteration in range(self.iterations):
            paths = []
            lengths = []

            # Создание путей для всех муравьев в колонии
            for _ in range(self.ants):
                path = self._create_path(distance_matrix, pheromone_matrix)
                length = self._calculate_path_length(distance_matrix, path)
                paths.append(path)
                lengths.append(length)

                # Обновление лучшего решения если найден более короткий путь
                if length < best_length:
                    best_length = length
                    best_path = path

            # Обновление феромонов после завершения итерации
            self._update_pheromone(pheromone_matrix, paths, lengths)

        # Возврат лучшего найденного пути
        return Path(indices=best_path, length=best_length, name="ACO Solution")