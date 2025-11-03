import json
import time
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from math import inf, sqrt
from random import random, shuffle
from typing import List, Tuple

# Класс реализации муравьиного алгоритма для задачи коммивояжера
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
        # Параметр влияния эвристической информации на выбор пути
        self.beta = beta
        # Коэффициент испарения феромона
        self.rho = rho
        # Параметр количества феромона
        self.q = q

    # Статический метод для выбора следующего узла на основе вероятностей
    @staticmethod
    def _select_index(selection: List[float]) -> int:
        sum_num = sum(selection)
        if sum_num == 0:
            return len(selection) - 1
        tmp_num = random()
        prob = 0
        for i in range(len(selection)):
            prob += selection[i] / sum_num
            if prob >= tmp_num:
                return i
        return len(selection) - 1

    # Метод создания пути для одного муравья
    def _create_path(self, distance_matrix: List[List[float]],
                     pheromone_matrix: List[List[float]]) -> List[int]:
        n = len(distance_matrix)
        unvisited_indices = list(range(n))
        shuffle(unvisited_indices)
        visited_indices = [unvisited_indices.pop()]

        for _ in range(n - 1):
            i = visited_indices[-1]
            selection = []
            for j in unvisited_indices:
                pheromone = pheromone_matrix[i][j]
                attractiveness = 1 / max(distance_matrix[i][j], 10 ** -5)
                selection.append(
                    (pheromone ** self.alpha) * (attractiveness ** self.beta)
                )
            selected_index = self._select_index(selection)
            visited_indices.append(unvisited_indices.pop(selected_index))

        visited_indices.append(visited_indices[0])
        return visited_indices

    # Метод обновления матрицы феромонов после итерации
    def _update_pheromone(self, pheromone_matrix: List[List[float]],
                          paths: List[List[int]], lengths: List[float]) -> None:
        n = len(pheromone_matrix)

        for i in range(n):
            for j in range(n):
                pheromone_matrix[i][j] *= (1 - self.rho)

        for k in range(self.ants):
            delta = self.q / lengths[k]
            path = paths[k]
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
        for i in range(len(path) - 1):
            total_length += distance_matrix[path[i]][path[i + 1]]
        return total_length

    # Основной метод решения задачи коммивояжера
    def solve_tsp(self, points: List[Tuple[float, float]]) -> dict:
        if len(points) < 3:
            raise ValueError("Need at least 3 points for TSP")

        n = len(points)

        # Создание матрицы расстояний
        distance_matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                distance = sqrt(dx * dx + dy * dy)
                distance_matrix[i][j] = distance
                distance_matrix[j][i] = distance

        # Инициализация матрицы феромонов
        pheromone_matrix = [[1.0] * n for _ in range(n)]

        best_path = []
        best_length = inf
        convergence_data = []

        # Основной цикл алгоритма
        for iteration in range(self.iterations):
            paths = []
            lengths = []

            for _ in range(self.ants):
                path = self._create_path(distance_matrix, pheromone_matrix)
                length = self._calculate_path_length(distance_matrix, path)
                paths.append(path)
                lengths.append(length)

                if length < best_length:
                    best_length = length
                    best_path = path

            convergence_data.append(best_length)
            self._update_pheromone(pheromone_matrix, paths, lengths)

        return {
            'optimal_path': best_path,
            'distance': round(best_length, 2),
            'iterations': self.iterations,
            'vertices_count': n,
            'vertices': points
        }

#Функция-обертка для решения TSP
def solve_tsp_aco(vertices_data, ant_count=10, iterations=100,
                  alpha=1.0, beta=2.0, evaporation=0.5, q=100):
    start_time = time.time()

    # Создаем экземпляр алгоритма
    aco = ACOAlgorithm(
        ants=ant_count,
        iterations=iterations,
        alpha=alpha,
        beta=beta,
        rho=evaporation,
        q=q
    )

    # Решаем задачу
    result = aco.solve_tsp(vertices_data)

    # Добавляем время выполнения
    result['execution_time'] = round(time.time() - start_time, 2)

    return result