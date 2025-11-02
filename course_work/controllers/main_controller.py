import time
from models.graph_model import GraphModel
from models.aco_algorithm import ACOAlgorithm
from models.database import DatabaseManager
from views.main_window import MainWindow
from utils.path import Path


# Основной контроллер приложения, реализующий логику MVC-архитектуры
class MainController:
    def __init__(self):
        # Модель графа для хранения данных о точках и ребрах
        self.model = GraphModel()
        # Менеджер базы данных для сохранения результатов расчетов
        self.database = DatabaseManager()
        # Главное окно приложения (View)
        self.view = MainWindow(self)

        # Текущая выбранная точка для создания ребра
        self.selected_point = None
        # Текущий режим работы: "add_points" - добавление точек, "add_edges" - создание ребер
        self.mode = "add_points"

    def handle_graph_click(self, x: float, y: float):
        """Обработчик кликов по графической области"""
        print(f"Controller: клик в ({x:.1f}, {y:.1f})")

        if self.mode == "add_points":
            # Режим добавления точек - просто создаем новую точку
            point_id = self.add_point(x, y)
            self.view.update_results(
                f"Создана точка {point_id}. Продолжайте добавлять точки или начните создавать ребра.")

        elif self.mode == "add_edges":
            # Режим создания ребер - ищем ближайшую точку
            point_id = self.find_nearest_point(x, y)
            if point_id is not None:
                self.handle_point_selection(point_id)

    def find_nearest_point(self, x: float, y: float, max_distance: float = 20.0) -> int:
        """Находит ближайшую точку к указанным координатам"""
        if not self.model.points:
            return None

        min_distance = float('inf')
        nearest_point = None

        # Поиск ближайшей точки среди всех точек графа
        for i, point in enumerate(self.model.points):
            distance = ((point.x - x) ** 2 + (point.y - y) ** 2) ** 0.5
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                nearest_point = i

        return nearest_point

    def handle_point_selection(self, point_id: int):
        """Обрабатывает выбор точки для создания ребра"""
        if self.selected_point is None:
            # Первый выбор точки - запоминаем и подсвечиваем
            self.selected_point = point_id
            self.view.highlight_point(point_id)
            self.view.update_results(f" Выбрана точка {point_id}. Кликните на другую точку для создания ребра.")
        elif self.selected_point == point_id:
            # Клик на ту же точку - отмена выбора
            self.view.unhighlight_point(point_id)
            self.selected_point = None
            self.view.update_results("Выбор точки отменен.")
        else:
            # Выбрана вторая точка - создаем ребро между двумя точками
            # Сохраняем значение перед сбросом
            first_point = self.selected_point
            second_point = point_id

            # Сбрасываем выделение
            self.view.unhighlight_point(self.selected_point)
            self.selected_point = None

            # Создаем ребро
            self.add_edge(first_point, second_point)
            self.view.update_results(f" Создано ребро: {first_point} → {second_point}")

    def switch_to_edge_mode(self):
        """Переключает режим на создание ребер"""
        self.mode = "add_edges"
        self.selected_point = None
        self.view.update_results("Режим создания ребер. Кликните на первую точку для создания ребра.")

    def switch_to_point_mode(self):
        """Переключает режим на создание точек"""
        self.mode = "add_points"
        self.selected_point = None
        self.view.update_results("Режим создания точек. Кликните в любом месте для добавления новой точки.")

    def run(self):
        # Запуск главного окна приложения
        self.view.show()
        # Начинаем в режиме добавления точек
        self.switch_to_point_mode()

    def add_point(self, x: float, y: float) -> int:
        # Проверка на существующие точки перед добавлением
        for i, existing_point in enumerate(self.model.points):
            distance = ((existing_point.x - x) ** 2 + (existing_point.y - y) ** 2) ** 0.5
            if distance < 20.0:  # Минимальное расстояние 20 пикселей
                self.view.show_error(
                    f"Точка ({x:.1f}, {y:.1f}) слишком близко к существующей точке {i} "
                    f"({existing_point.x:.1f}, {existing_point.y:.1f}). "
                    f"Минимальное расстояние: 20 пикселей"
                )
                return None

        # Добавление точки в модель и представление
        try:
            point_id = self.model.add_point(x, y)
            view_point_id = self.view.add_point_to_view(x, y)
            print(f"Controller: добавлена точка {point_id} в ({x:.1f}, {y:.1f})")
            return point_id
        except Exception as e:
            self.view.show_error(f"Ошибка при добавлении точки: {str(e)}")
            return None

    def add_edge(self, point1_idx: int, point2_idx: int):
        # Добавление ребра между двумя точками (если это не петля)
        if point1_idx != point2_idx:
            self.model.add_edge(point1_idx, point2_idx)
            self.view.add_edge_to_view(point1_idx, point2_idx)

    def clear_graph(self):
        # Очистка графа: модели, представления и состояния
        self.model.clear()
        self.view.clear_graph_view()
        self.selected_point = None
        self.switch_to_point_mode()
        self.view.update_results("Граф очищен. Режим создания точек.")

    def solve_tsp(self, params: dict):
        # Решение задачи коммивояжера с использованием муравьиного алгоритма
        if len(self.model.points) < 3:
            self.view.show_error("Для решения задачи нужно как минимум 3 точки")
            return

        try:
            start_time = time.time()

            # Создание экземпляра алгоритма с заданными параметрами
            algorithm = ACOAlgorithm(
                ants=params['ants'],
                iterations=params['iterations'],
                alpha=params['alpha'],
                beta=params['beta'],
                rho=params['rho'],
                q=params['q']
            )

            # Получение точек и решение задачи
            points = self.model.get_points()
            solution = algorithm.solve_tsp(points)

            computation_time = time.time() - start_time

            # Сохранение результата в базу данных
            self.database.save_result(
                points_count=len(points),
                algorithm_params=params,
                path_length=solution.length,
                path_indices=solution.indices,
                computation_time=computation_time
            )

            # Обновление графического представления с решением
            self.view.draw_solution(solution.indices)

            # Формирование и отображение текста с результатами
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
        # Отображение истории расчетов из базы данных
        try:
            results = self.database.get_all_results()
            history_text = "История расчетов:\n\n"

            # Формирование текста с последними 10 результатами
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