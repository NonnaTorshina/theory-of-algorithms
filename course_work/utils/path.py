from typing import List


# Класс для представления пути в задаче коммивояжера
class Path:
    def __init__(self, indices: List[int], length: float, name: str = ""):
        # Список индексов точек в порядке обхода маршрута
        self.indices = indices
        # Общая длина пути (сумма расстояний между последовательными точками)
        self.length = length
        # Название пути (например, "ACO Solution" или название алгоритма)
        self.name = name

    def __str__(self):
        # Строковое представление пути в формате: "Название: длина.ед"
        return f"{self.name}: {self.length:.2f} units"