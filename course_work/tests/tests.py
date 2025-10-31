import pytest
import math
import sys
import tempfile
import os
import json
from models.graph_model import Point, GraphModel
from models.database import DatabaseManager
from models.aco_algorithm import ACOAlgorithm
from utils.path import Path

from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent,QColor

from controllers.main_controller import MainController
from views.main_window import MainWindow, GraphView

# Тесты для класса Point
class TestPoint:
    # тест создания точки
    def test_point_creation(self):
        point = Point(3.5, 4.2)
        assert point.x == 3.5
        assert point.y == 4.2

    # тест вычисления расстояния между точками
    def test_distance_to(self):
        point1 = Point(0, 0)
        point2 = Point(3, 4)
        assert point1.distance_to(point2) == 5.0

        point3 = Point(1, 1)
        point4 = Point(4, 5)
        expected = math.sqrt((1 - 4) ** 2 + (1 - 5) ** 2)
        assert point3.distance_to(point4) == expected

    # тест расстояния точки до самой себя
    def test_distance_to_same_point(self):
        point = Point(2, 3)
        assert point.distance_to(point) == 0.0

    # тест сравнения точек
    def test_equality(self):
        point1 = Point(1.0, 2.0)
        point2 = Point(1.0, 2.0)
        point3 = Point(1.0, 2.1)

        assert point1 == point2
        assert point1 != point3
        assert point2 != point3

    # тест хэширования точек
    def test_hash(self):
        point1 = Point(1.0, 2.0)
        point2 = Point(1.0, 2.0)
        point3 = Point(1.0, 2.1)

        assert hash(point1) == hash(point2)
        assert hash(point1) != hash(point3)

        # проверяем, что точки можно использовать в множестве
        points_set = {point1, point2, point3}
        assert len(points_set) == 2  # point1 и point2 одинаковые

# Тесты для класса GraphModel
class TestGraphModel:

    # настройка перед каждым тестом
    def setup_method(self):
        self.graph = GraphModel()

    # тест начального состояния графа
    def test_initial_state(self):
        assert len(self.graph.points) == 0
        assert len(self.graph.edges) == 0
        assert self.graph.distance_matrix is None

    # тест добавления точек
    def test_add_point(self):
        point_id1 = self.graph.add_point(0, 0)
        point_id2 = self.graph.add_point(1, 1)
        point_id3 = self.graph.add_point(2, 2)

        assert point_id1 == 0
        assert point_id2 == 1
        assert point_id3 == 2
        assert len(self.graph.points) == 3

        # проверяем координаты точек
        assert self.graph.points[0].x == 0
        assert self.graph.points[0].y == 0
        assert self.graph.points[1].x == 1
        assert self.graph.points[1].y == 1

    # тест добавления рёбер
    def test_add_edge(self):
        # добавляем точки
        self.graph.add_point(0, 0)
        self.graph.add_point(1, 1)
        self.graph.add_point(2, 2)

        # добавляем ребра
        self.graph.add_edge(0, 1)
        self.graph.add_edge(1, 2)

        assert len(self.graph.edges) == 2
        assert (0, 1) in self.graph.edges
        assert (1, 2) in self.graph.edges

    # тест предотвращения дублирования рёбер
    def test_add_edge_prevents_duplicates(self):
        self.graph.add_point(0, 0)
        self.graph.add_point(1, 1)

        self.graph.add_edge(0, 1)
        self.graph.add_edge(1, 0)  # Дубликат
        self.graph.add_edge(0, 1)  # Дубликат

        assert len(self.graph.edges) == 1
        assert (0, 1) in self.graph.edges

    # тест предотвращения петель
    def test_add_edge_prevents_self_loop(self):
        self.graph.add_point(0, 0)

        self.graph.add_edge(0, 0)  # Петля

        assert len(self.graph.edges) == 0

    # тест добавления рёбер с невалидными индексами
    def test_add_edge_invalid_indices(self):
        self.graph.add_point(0, 0)

        # попытка добавить ребро с несуществующими точками
        self.graph.add_edge(0, 5)
        self.graph.add_edge(5, 0)
        self.graph.add_edge(5, 10)

        # не должно быть добавлено никаких ребер
        assert len(self.graph.edges) == 0

    # тест очистки графа
    def test_clear(self):
        # Добавляем данные
        self.graph.add_point(0, 0)
        self.graph.add_point(1, 1)
        self.graph.add_edge(0, 1)

        # очищаем
        self.graph.clear()

        assert len(self.graph.points) == 0
        assert len(self.graph.edges) == 0
        assert self.graph.distance_matrix is None

    # тест создания матрицы расстояний
    def test_distance_matrix_creation(self):
        # добавляем точки образующие прямоугольный треугольник
        self.graph.add_point(0, 0)
        self.graph.add_point(3, 0)
        self.graph.add_point(0, 4)

        matrix = self.graph.distance_matrix
        assert matrix is not None
        assert len(matrix) == 3
        assert len(matrix[0]) == 3

        # проверяем расстояния
        assert matrix[0][1] == 3.0  # (0,0) - (3,0)
        assert matrix[0][2] == 4.0  # (0,0) - (0,4)
        assert matrix[1][2] == 5.0  # (3,0) - (0,4)

        # проверяем симметричность
        assert matrix[0][1] == matrix[1][0]
        assert matrix[0][2] == matrix[2][0]
        assert matrix[1][2] == matrix[2][1]

        # Диагональ должна быть 0
        assert matrix[0][0] == 0.0
        assert matrix[1][1] == 0.0
        assert matrix[2][2] == 0.0

    # тест получения списка координат
    def test_get_points(self):
        self.graph.add_point(1.5, 2.5)
        self.graph.add_point(3.0, 4.0)

        points = self.graph.get_points()

        assert points == [(1.5, 2.5), (3.0, 4.0)]
        assert isinstance(points[0], tuple)
        assert isinstance(points[1], tuple)

# Тесты для класса ACOAlgorithm
class TestACOAlgorithm:
    # тест инициализации алгоритма
    def test_initialization(self):
        algo = ACOAlgorithm(
            ants=50,
            iterations=100,
            alpha=1.0,
            beta=2.0,
            rho=0.5,
            q=10.0
        )

        assert algo.ants == 50
        assert algo.iterations == 100
        assert algo.alpha == 1.0
        assert algo.beta == 2.0
        assert algo.rho == 0.5
        assert algo.q == 10.0

    # тест параметров по умолчанию
    def test_default_parameters(self):
        algo = ACOAlgorithm()

        assert algo.ants == 100
        assert algo.iterations == 20
        assert algo.alpha == 1.5
        assert algo.beta == 1.2
        assert algo.rho == 0.6
        assert algo.q == 10.0

    # тест выбора индекса на основе вероятностей
    def test_select_index(self):
        # все вероятности равны
        selection = [1.0, 1.0, 1.0]
        result = ACOAlgorithm._select_index(selection)
        assert 0 <= result <= 2

        # одна большая вероятность
        selection = [0.1, 0.1, 0.8]
        result = ACOAlgorithm._select_index(selection)
        # должен с большой вероятностью выбрать индекс 2

        # все нулевые вероятности
        selection = [0.0, 0.0, 0.0]
        result = ACOAlgorithm._select_index(selection)
        assert result == 2  # должен вернуть последний индекс

    # тест вычисления длины пути
    def test_calculate_path_length(self):
        distance_matrix = [
            [0, 10, 15],
            [10, 0, 20],
            [15, 20, 0]
        ]

        path = [0, 1, 2, 0]
        length = ACOAlgorithm._calculate_path_length(distance_matrix, path)

        expected = 10 + 20 + 15  # 0->1 + 1->2 + 2->0
        assert length == expected

        # неполный путь
        path = [0, 1, 2]
        length = ACOAlgorithm._calculate_path_length(distance_matrix, path)
        expected = 10 + 20  # 0->1 + 1->2
        assert length == expected

    # тест решения с недостаточным количеством точек
    def test_solve_tsp_insufficient_points(self):
        algo = ACOAlgorithm()

        # меньше 3 точек
        with pytest.raises(ValueError, match="Need at least 3 points for TSP"):
            algo.solve_tsp([(0, 0), (1, 1)])

        with pytest.raises(ValueError, match="Need at least 3 points for TSP"):
            algo.solve_tsp([(0, 0)])

        with pytest.raises(ValueError, match="Need at least 3 points for TSP"):
            algo.solve_tsp([])

    # тест базовой функциональности решения
    def test_solve_tsp_basic_functionality(self):
        algo = ACOAlgorithm(ants=10, iterations=5)  # меньшие параметры для скорости

        # простой треугольник
        points = [(0, 0), (3, 0), (0, 4)]

        solution = algo.solve_tsp(points)

        assert isinstance(solution, Path)
        assert solution.name == "ACO Solution"
        assert len(solution.indices) == 4  # 3 точки + возврат в начало
        assert solution.length > 0

        # проверяем, что путь начинается и заканчивается в одной точке
        assert solution.indices[0] == solution.indices[-1]

        # проверяем, что все точки посещены
        unique_points = set(solution.indices[:-1])
        assert len(unique_points) == 3
        assert 0 in unique_points
        assert 1 in unique_points
        assert 2 in unique_points

    # тест решения для квадрата
    def test_solve_tsp_square(self):
        algo = ACOAlgorithm(ants=20, iterations=10)

        # квадрат 1x1
        points = [(0, 0), (1, 0), (1, 1), (0, 1)]

        solution = algo.solve_tsp(points)

        assert len(solution.indices) == 5  # 4 точки + возврат в начало
        assert solution.indices[0] == solution.indices[-1]

        # проверяем посещение всех точек
        unique_points = set(solution.indices[:-1])
        assert len(unique_points) == 4

        # длина пути должна быть около 4.0 для оптимального пути (но алгоритм может найти не оптимальный)
        assert 3.5 <= solution.length <= 5.0

    # тест обновления феромонов
    def test_update_pheromone(self):
        algo = ACOAlgorithm(ants=2, iterations=1)
        pheromone_matrix = [[1.0, 0.5], [0.5, 1.0]]
        paths = [[0, 1, 0], [1, 0, 1]]
        lengths = [2.0, 3.0]

        algo._update_pheromone(pheromone_matrix, paths, lengths)
        # Проверяем что феромоны изменились

# Тесты для класса DatabaseManager
class TestDatabaseManager:

    # настройка перед каждым тестом
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseManager(self.db_path)

    # очистка после каждого теста
    def teardown_method(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # тест инициализации базы данных
    def test_initialization(self):
        assert os.path.exists(self.db_path)

        # проверяем, что таблица создана
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tsp_results'")
            result = cursor.fetchone()
            assert result is not None

    # тест сохранения результата
    def test_save_result(self):
        params = {
            'ants': 100,
            'iterations': 20,
            'alpha': 1.5,
            'beta': 1.2,
            'rho': 0.6,
            'q': 10.0
        }

        self.db.save_result(
            points_count=5,
            algorithm_params=params,
            path_length=123.45,
            path_indices=[0, 1, 2, 3, 4, 0],
            computation_time=1.23
        )

        results = self.db.get_all_results()
        assert len(results) == 1

        record = results[0]
        assert record[2] == 5  # points_count
        assert record[4] == 123.45  # path_length
        assert record[6] == 1.23  # computation_time

        # проверяем JSON параметры
        saved_params = json.loads(record[3])
        assert saved_params == params

        # проверяем JSON индексы
        saved_indices = json.loads(record[5])
        assert saved_indices == [0, 1, 2, 3, 4, 0]

    # тест получения всех результатов
    def test_get_all_results(self):
        # добавляем несколько записей
        for i in range(3):
            self.db.save_result(
                points_count=i + 3,
                algorithm_params={'ants': 50},
                path_length=100.0 + i,
                path_indices=[0, 1, 0],
                computation_time=0.1 + i
            )

        results = self.db.get_all_results()
        assert len(results) == 3

        # проверяем сортировку по времени (новые первыми)
        timestamps = [r[1] for r in results]
        assert timestamps == sorted(timestamps, reverse=True)

    # тест получения результатов по количеству точек
    def test_get_results_by_points_count(self):
        # добавляем записи с разным количеством точек
        points_counts = [5, 5, 10, 5, 10]
        for count in points_counts:
            self.db.save_result(
                points_count=count,
                algorithm_params={'ants': 50},
                path_length=100.0,
                path_indices=[0, 1, 0],
                computation_time=0.1
            )

        # получаем результаты для 5 точек
        results_5 = self.db.get_results_by_points_count(5)
        assert len(results_5) == 3

        # получаем результаты для 10 точек
        results_10 = self.db.get_results_by_points_count(10)
        assert len(results_10) == 2

        # проверяем сортировку по длине пути
        lengths_5 = [r[4] for r in results_5]
        assert lengths_5 == sorted(lengths_5)

    # тест работы с пустой базой данных
    def test_empty_results(self):
        results = self.db.get_all_results()
        assert len(results) == 0

        results_by_count = self.db.get_results_by_points_count(5)
        assert len(results_by_count) == 0

# Тесты для класса Path
class TestPath:

    # тест создания пути
    def test_path_creation(self):
        indices = [0, 1, 2, 0]
        length = 123.45
        name = "Test Path"

        path = Path(indices=indices, length=length, name=name)

        assert path.indices == indices
        assert path.length == length
        assert path.name == name

    # тест пути с именем по умолчанию
    def test_path_default_name(self):
        path = Path(indices=[0, 1, 0], length=100.0)

        assert path.indices == [0, 1, 0]
        assert path.length == 100.0
        assert path.name == ""

    # тест строкового представления
    def test_string_representation(self):
        path = Path(indices=[0, 1, 0], length=123.45, name="Test")

        assert str(path) == "Test: 123.45 units"

        path_no_name = Path(indices=[0, 1, 0], length=123.45)
        assert str(path_no_name) == ": 123.45 units"

# Тесты для класса MainController
class TestMainController:

    def setup_method(self):
        # Настройка перед каждым тестом
        # Создаем моки для зависимостей
        self.mock_model = Mock(spec=GraphModel)
        self.mock_database = Mock(spec=DatabaseManager)
        self.mock_view = Mock(spec=MainWindow)

        # Патчим создание зависимостей в контроллере
        with patch('controllers.main_controller.GraphModel', return_value=self.mock_model), \
                patch('controllers.main_controller.DatabaseManager', return_value=self.mock_database), \
                patch('controllers.main_controller.MainWindow', return_value=self.mock_view):
            self.controller = MainController()

    # Тест инициализации контроллера
    def test_initialization(self):
        assert self.controller.model == self.mock_model
        assert self.controller.database == self.mock_database
        assert self.controller.view == self.mock_view
        assert self.controller.selected_point is None
        assert self.controller.mode == "add_points"

    # Тест переключения в режим добавления точек
    def test_switch_to_point_mode(self):
        self.controller.switch_to_point_mode()

        assert self.controller.mode == "add_points"
        assert self.controller.selected_point is None
        self.mock_view.update_results.assert_called_with(
            "Режим создания точек. Кликните в любом месте для добавления новой точки."
        )

    # Тест переключения в режим создания ребер
    def test_switch_to_edge_mode(self):
        self.controller.switch_to_edge_mode()

        assert self.controller.mode == "add_edges"
        assert self.controller.selected_point is None
        self.mock_view.update_results.assert_called_with(
            "Режим создания ребер. Кликните на первую точку для создания ребра."
        )

    # Тест добавления точки
    def test_add_point(self):
        # Настраиваем моки
        self.mock_model.add_point.return_value = 5
        self.mock_view.add_point_to_view.return_value = 5

        point_id = self.controller.add_point(10.5, 20.5)

        assert point_id == 5
        self.mock_model.add_point.assert_called_once_with(10.5, 20.5)
        self.mock_view.add_point_to_view.assert_called_once_with(10.5, 20.5)

    # Тест добавления ребра
    def test_add_edge(self):
        self.controller.add_edge(1, 2)

        self.mock_model.add_edge.assert_called_once_with(1, 2)
        self.mock_view.add_edge_to_view.assert_called_once_with(1, 2)

    # Тест предотвращения добавления петли
    def test_add_edge_prevents_self_loop(self):
        self.controller.add_edge(1, 1)

        self.mock_model.add_edge.assert_not_called()
        self.mock_view.add_edge_to_view.assert_not_called()

    # Тест очистки графа
    def test_clear_graph(self):
        self.controller.clear_graph()

        self.mock_model.clear.assert_called_once()
        self.mock_view.clear_graph_view.assert_called_once()
        assert self.controller.selected_point is None
        assert self.controller.mode == "add_points"
        self.mock_view.update_results.assert_called_with("Граф очищен. Режим создания точек.")

    # Тест поиска ближайшей точки при отсутствии точек
    def test_find_nearest_point_no_points(self):
        self.mock_model.points = []

        result = self.controller.find_nearest_point(10, 20)

        assert result is None

    # Тест поиска ближайшей точки
    def test_find_nearest_point_with_points(self):
        # Создаем mock точки
        mock_point1 = Mock()
        mock_point1.x = 0
        mock_point1.y = 0

        mock_point2 = Mock()
        mock_point2.x = 10
        mock_point2.y = 10

        mock_point3 = Mock()
        mock_point3.x = 20
        mock_point3.y = 20

        self.mock_model.points = [mock_point1, mock_point2, mock_point3]

        # Ищем ближайшую к точке (12, 12)
        result = self.controller.find_nearest_point(12, 12)

        # Должна быть найдена точка с индексом 1 (10, 10)
        assert result == 1

    # Тест поиска точки вне максимального расстояния
    def test_find_nearest_point_out_of_range(self):
        mock_point = Mock()
        mock_point.x = 100
        mock_point.y = 100
        self.mock_model.points = [mock_point]

        # Точка слишком далеко (макс расстояние по умолчанию 20)
        result = self.controller.find_nearest_point(10, 10)

        assert result is None

    # Тест обработки первого выбора точки
    def test_handle_point_selection_first_selection(self):
        self.controller.handle_point_selection(3)

        assert self.controller.selected_point == 3
        self.mock_view.highlight_point.assert_called_once_with(3)
        self.mock_view.update_results.assert_called_with(
            " Выбрана точка 3. Кликните на другую точку для создания ребра.")

    # Тест обработки выбора той же точки
    def test_handle_point_selection_same_point(self):
        self.controller.selected_point = 3

        self.controller.handle_point_selection(3)

        assert self.controller.selected_point is None
        self.mock_view.unhighlight_point.assert_called_once_with(3)
        self.mock_view.update_results.assert_called_with("Выбор точки отменен.")

    # Тест создания ребра при выборе второй точки
    def test_handle_point_selection_create_edge(self):
        self.controller.selected_point = 1

        self.controller.handle_point_selection(2)

        self.mock_model.add_edge.assert_called_once_with(1, 2)
        self.mock_view.add_edge_to_view.assert_called_once_with(1, 2)
        self.mock_view.unhighlight_point.assert_called_once_with(1)
        assert self.controller.selected_point is None
        # Теперь используется сохраненное значение
        self.mock_view.update_results.assert_called_with(" Создано ребро: 1 → 2")

    # Тест обработки клика в режиме точек
    def test_handle_graph_click_point_mode(self):
        self.controller.mode = "add_points"
        self.controller.add_point = Mock(return_value=4)

        self.controller.handle_graph_click(15.5, 25.5)

        self.controller.add_point.assert_called_once_with(15.5, 25.5)
        self.mock_view.update_results.assert_called_with(
            "Создана точка 4. Продолжайте добавлять точки или начните создавать ребра."
        )

    # Тест обработки клика в режиме ребер (точка не найдена)
    def test_handle_graph_click_edge_mode_no_point(self):
        self.controller.mode = "add_edges"
        self.controller.find_nearest_point = Mock(return_value=None)
        # Создаем mock для handle_point_selection
        self.controller.handle_point_selection = Mock()

        self.controller.handle_graph_click(15.5, 25.5)

        self.controller.find_nearest_point.assert_called_once_with(15.5, 25.5)
        # Проверяем что handle_point_selection не был вызван
        self.controller.handle_point_selection.assert_not_called()

    # Тест обработки клика в режиме ребер (точка найдена)
    def test_handle_graph_click_edge_mode_with_point(self):
        self.controller.mode = "add_edges"
        self.controller.find_nearest_point = Mock(return_value=2)
        self.controller.handle_point_selection = Mock()

        self.controller.handle_graph_click(15.5, 25.5)

        self.controller.find_nearest_point.assert_called_once_with(15.5, 25.5)
        self.controller.handle_point_selection.assert_called_once_with(2)

    # Тест решения TSP с недостаточным количеством точек
    def test_solve_tsp_insufficient_points(self):
        self.mock_model.points = [Mock(), Mock()]  # Только 2 точки

        params = {'ants': 100, 'iterations': 20}
        self.controller.solve_tsp(params)

        self.mock_view.show_error.assert_called_with("Для решения задачи нужно как минимум 3 точки")

    # Тест успешного решения TSP
    @patch('controllers.main_controller.time.time')
    @patch('controllers.main_controller.ACOAlgorithm')
    def test_solve_tsp_success(self, mock_aco_class, mock_time):
        # Настраиваем моки
        self.mock_model.points = [Mock(), Mock(), Mock(), Mock()]  # 4 точки
        self.mock_model.get_points.return_value = [(0, 0), (1, 1), (2, 2), (3, 3)]

        mock_time.side_effect = [1000, 1002]  # start_time, end_time

        mock_algorithm = Mock()
        mock_aco_class.return_value = mock_algorithm

        mock_solution = Mock(spec=Path)
        mock_solution.length = 123.45
        mock_solution.indices = [0, 1, 2, 3, 0]
        mock_algorithm.solve_tsp.return_value = mock_solution

        params = {
            'ants': 100,
            'iterations': 20,
            'alpha': 1.5,
            'beta': 1.2,
            'rho': 0.6,
            'q': 10.0
        }

        self.controller.solve_tsp(params)

        # Проверяем вызовы
        mock_aco_class.assert_called_once_with(
            ants=100, iterations=20, alpha=1.5, beta=1.2, rho=0.6, q=10.0
        )
        mock_algorithm.solve_tsp.assert_called_once_with([(0, 0), (1, 1), (2, 2), (3, 3)])

        self.mock_database.save_result.assert_called_once()
        self.mock_view.draw_solution.assert_called_once_with([0, 1, 2, 3, 0])
        self.mock_view.update_results.assert_called_once()

    # Тест обработки исключения при решении TSP
    @patch('controllers.main_controller.time.time')
    @patch('controllers.main_controller.ACOAlgorithm')
    def test_solve_tsp_exception(self, mock_aco_class, mock_time):
        self.mock_model.points = [Mock(), Mock(), Mock()]
        self.mock_model.get_points.return_value = [(0, 0), (1, 1), (2, 2)]

        mock_algorithm = Mock()
        mock_aco_class.return_value = mock_algorithm

        # Создаем исключение с конкретным сообщением
        test_exception = Exception("Test error")
        mock_algorithm.solve_tsp.side_effect = test_exception

        # Полный набор параметров для избежания KeyError
        params = {
            'ants': 100,
            'iterations': 20,
            'alpha': 1.5,
            'beta': 1.2,
            'rho': 0.6,
            'q': 10.0
        }

        self.controller.solve_tsp(params)

        # Проверяем что show_error был вызван с правильным сообщением
        self.mock_view.show_error.assert_called_once()
        call_args = self.mock_view.show_error.call_args[0][0]
        assert "Ошибка при решении задачи:" in call_args

    # Тест успешного показа истории
    def test_show_history_success(self):
        mock_results = [
            (1, '2024-01-01', 5, '{}', 100.0, '[0,1,2,0]', 1.0),
            (2, '2024-01-02', 10, '{}', 200.0, '[0,1,2,3,0]', 2.0)
        ]
        self.mock_database.get_all_results.return_value = mock_results

        self.controller.show_history()

        self.mock_view.update_results.assert_called_once()
        call_args = self.mock_view.update_results.call_args[0][0]
        assert "История расчетов" in call_args
        assert "ID: 1" in call_args
        assert "ID: 2" in call_args

    # Тест обработки исключения при показе истории
    def test_show_history_exception(self):
        self.mock_database.get_all_results.side_effect = Exception("DB error")

        self.controller.show_history()

        self.mock_view.show_error.assert_called_with("Ошибка загрузки истории: DB error")

    # Тест запуска приложения
    def test_run(self):
        self.controller.run()

        self.mock_view.show.assert_called_once()
        assert self.controller.mode == "add_points"