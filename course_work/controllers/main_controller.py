import time
from models.graph_model import GraphModel
from models.aco_algorithm import ACOAlgorithm
from models.database import DatabaseManager
from views.main_window import MainWindow
from utils.path import Path
from PySide6.QtWidgets import QInputDialog


class MainController:
    def __init__(self):
        self.model = GraphModel()
        self.database = DatabaseManager()
        self.view = MainWindow(self)
        self.selected_point = None
        self.mode = "add_points"

    def handle_graph_click(self, x: float, y: float):
        print(f"Controller: клик в ({x:.1f}, {y:.1f})")

        if self.mode == "add_points":
            point_id = self.add_point(x, y)
            self.view.update_results(
                f"Создана точка {point_id}. Продолжайте добавлять точки или начните создавать ребра.")

        elif self.mode == "add_edges":
            point_id = self.find_nearest_point(x, y)
            if point_id is not None:
                self.handle_point_selection(point_id)

    def find_nearest_point(self, x: float, y: float, max_distance: float = 20.0) -> int:
        if not self.model.points:
            return None

        min_distance = float('inf')
        nearest_point = None

        for i, point in enumerate(self.model.points):
            distance = ((point.x - x) ** 2 + (point.y - y) ** 2) ** 0.5
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                nearest_point = i

        return nearest_point

    def handle_point_selection(self, point_id: int):
        if self.selected_point is None:
            self.selected_point = point_id
            self.view.highlight_point(point_id)
            self.view.update_results(f" Выбрана точка {point_id}. Кликните на другую точку для создания ребра.")
        elif self.selected_point == point_id:
            self.view.unhighlight_point(point_id)
            self.selected_point = None
            self.view.update_results("Выбор точки отменен.")
        else:
            first_point = self.selected_point
            second_point = point_id

            self.view.unhighlight_point(self.selected_point)
            self.selected_point = None

            # ИЗМЕНЕНИЕ: вызываем метод с запросом веса
            self.add_edge_with_weight(first_point, second_point)

    def add_edge_with_weight(self, point1_idx: int, point2_idx: int):
        """Добавляет ребро с запросом веса у пользователя"""
        if point1_idx != point2_idx:
            # Вычисляем расстояние по умолчанию
            default_weight = self.model.points[point1_idx].distance_to(self.model.points[point2_idx])

            # Запрашиваем вес у пользователя
            weight, ok = QInputDialog.getDouble(
                self.view,
                "Добавление ребра",
                f"Введите вес для ребра {point1_idx}-{point2_idx}:",
                value=default_weight,
                minValue=0.1,
                maxValue=1000.0,
                decimals=1
            )

            if ok:
                # Используем новый метод добавления ребра с весом
                self.model.add_edge(point1_idx, point2_idx, weight)
                self.view.add_edge_to_view(point1_idx, point2_idx, weight)
                self.view.update_results(f" Создано ребро: {point1_idx} → {point2_idx} (вес: {weight:.1f})")
            else:
                self.view.update_results("Создание ребра отменено")

    # Остальные методы остаются БЕЗ ИЗМЕНЕНИЙ...
    def switch_to_edge_mode(self):
        self.mode = "add_edges"
        self.selected_point = None
        self.view.update_results("Режим создания ребер. Кликните на первую точку для создания ребра.")

    def switch_to_point_mode(self):
        self.mode = "add_points"
        self.selected_point = None
        self.view.update_results("Режим создания точек. Кликните в любом месте для добавления новой точки.")

    def run(self):
        self.view.show()
        self.switch_to_point_mode()

    def add_point(self, x: float, y: float) -> int:
        for i, existing_point in enumerate(self.model.points):
            distance = ((existing_point.x - x) ** 2 + (existing_point.y - y) ** 2) ** 0.5
            if distance < 20.0:
                self.view.show_error(
                    f"Точка ({x:.1f}, {y:.1f}) слишком близко к существующей точке {i}")
                return None

        try:
            point_id = self.model.add_point(x, y)
            view_point_id = self.view.add_point_to_view(x, y)
            print(f"Controller: добавлена точка {point_id} в ({x:.1f}, {y:.1f})")
            return point_id
        except Exception as e:
            self.view.show_error(f"Ошибка при добавлении точки: {str(e)}")
            return None

    # Удаляем старый метод add_edge и заменяем его на add_edge_with_weight
    def add_edge(self, point1_idx: int, point2_idx: int):
        """Старый метод - больше не используется"""
        pass

    def clear_graph(self):
        self.model.clear()
        self.view.clear_graph_view()
        self.selected_point = None
        self.switch_to_point_mode()
        self.view.update_results("Граф очищен. Режим создания точек.")

    def solve_tsp(self, params: dict):
        if len(self.model.points) < 3:
            self.view.show_error("Для решения задачи нужно как минимум 3 точки")
            return

        try:
            start_time = time.time()

            algorithm = ACOAlgorithm(
                ants=params['ants'],
                iterations=params['iterations'],
                alpha=params['alpha'],
                beta=params['beta'],
                rho=params['rho'],
                q=params['q']
            )

            points = self.model.get_points()
            solution = algorithm.solve_tsp(points)

            computation_time = time.time() - start_time

            self.database.save_result(
                points_count=len(points),
                algorithm_params=params,
                path_length=solution.length,
                path_indices=solution.indices,
                computation_time=computation_time
            )

            self.view.draw_solution(solution.indices)

            result_text = f"""
Решение задачи коммивояжера найдено!

Алгоритм: Муравьиный алгоритм
Точек: {len(points)}
Длина пути: {solution.length:.2f}
Время расчета: {computation_time:.2f} секунд

Параметры:
- Муравьев: {params['ants']}
- Итераций: {params['iterations']}
- Альфа: {params['alpha']}
- Бета: {params['beta']}
- Ро: {params['rho']}
- Q: {params['q']}

Маршрут: {' → '.join(map(str, solution.indices))}
            """

            self.view.update_results(result_text)

        except Exception as e:
            self.view.show_error(f"Ошибка при решении задачи: {str(e)}")

    def show_history(self):
        try:
            results = self.database.get_all_results()
            history_text = "История расчетов:\n\n"

            for result in results[:10]:
                history_text += f"ID: {result[0]}\n"
                history_text += f"Дата: {result[1]}\n"
                history_text += f"Точек: {result[2]}\n"
                history_text += f"Длина: {result[4]:.2f}\n"
                history_text += f"Время: {result[6]:.2f}с\n"
                history_text += "-" * 40 + "\n"

            self.view.update_results(history_text)

        except Exception as e:
            self.view.show_error(f"Ошибка загрузки истории: {str(e)}")