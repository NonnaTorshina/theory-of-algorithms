from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                               QGroupBox, QFormLayout, QTextEdit, QMessageBox,
                               QGraphicsView, QGraphicsScene,
                               QGraphicsEllipseItem, QGraphicsLineItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QMouseEvent
import time


# Класс для графического представления графа и визуализации решения
class GraphView(QGraphicsView):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setSceneRect(0, 0, 800, 600)

        self.points = []
        self.point_items = []
        self.edge_items = []
        self.solution_items = []
        self.edge_labels = []  # Добавляем список для текстовых элементов с весами

    def clear(self):
        self.scene.clear()
        self.points.clear()
        self.point_items.clear()
        self.edge_items.clear()
        self.solution_items.clear()
        self.edge_labels.clear()  # Очищаем метки весов

    def add_point(self, x: float, y: float):
        """Добавляет точку на сцену"""
        point_id = len(self.points)
        self.points.append((x, y))

        ellipse = QGraphicsEllipseItem(x - 8, y - 8, 20, 20)
        ellipse.setBrush(QColor(0, 255, 0))
        ellipse.setPen(QPen(QColor(30, 80, 180), 2))
        ellipse.setData(0, point_id)
        ellipse.setZValue(1)
        self.scene.addItem(ellipse)
        self.point_items.append(ellipse)

        label = self.scene.addText(str(point_id))
        label.setDefaultTextColor(QColor(0, 0, 0))
        label.setPos(x + 10, y - 12)
        label.setFont(QFont("Arial", 9, QFont.Bold))
        label.setZValue(2)

        return point_id

    def add_edge(self, point1_idx: int, point2_idx: int, weight: float):
        """Добавляет ребро между двумя точками с отображением веса"""
        if point1_idx >= len(self.points) or point2_idx >= len(self.points):
            return

        x1, y1 = self.points[point1_idx]
        x2, y2 = self.points[point2_idx]

        # Создаем линию ребра
        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setPen(QPen(QColor(100, 100, 100), 2))
        line.setZValue(0)
        self.scene.addItem(line)
        self.edge_items.append(line)

        # Добавляем текст с весом
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        weight_label = self.scene.addText(f"{weight:.1f}")
        weight_label.setDefaultTextColor(QColor(0, 0, 255))  # Синий цвет для веса
        weight_label.setFont(QFont("Arial", 8, QFont.Bold))
        weight_label.setPos(mid_x, mid_y - 10)
        weight_label.setZValue(3)  # Высокий Z-value чтобы текст был поверх всего

        self.edge_labels.append(weight_label)

    # Остальные методы остаются без изменений...
    def highlight_point(self, point_id: int):
        if 0 <= point_id < len(self.point_items):
            self.point_items[point_id].setBrush(QColor(255, 200, 50))

    def unhighlight_point(self, point_id: int):
        if 0 <= point_id < len(self.point_items):
            self.point_items[point_id].setBrush(QColor(0, 255, 0))

    def draw_solution(self, path_indices: list):
        for item in self.solution_items:
            self.scene.removeItem(item)
        self.solution_items.clear()

        if not path_indices or len(path_indices) < 2:
            return

        pen = QPen(QColor(255, 50, 50), 4)
        for i in range(len(path_indices) - 1):
            idx1 = path_indices[i]
            idx2 = path_indices[i + 1]

            if idx1 < len(self.points) and idx2 < len(self.points):
                x1, y1 = self.points[idx1]
                x2, y2 = self.points[idx2]

                line = QGraphicsLineItem(x1, y1, x2, y2)
                line.setPen(pen)
                line.setZValue(0)
                self.scene.addItem(line)
                self.solution_items.append(line)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.controller.handle_graph_click(scene_pos.x(), scene_pos.y())

        super().mousePressEvent(event)

# Главное окно приложения - основной пользовательский интерфейс
class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        # Ссылка на контроллер для управления логикой
        self.controller = controller
        # Установка заголовка окна
        self.setWindowTitle("Решатель задачи коммивояжера - Муравьиный алгоритм")
        # Установка позиции и размеров окна (x, y, width, height)
        self.setGeometry(100, 100, 1200, 800)

        self.setup_ui()

    def setup_ui(self):
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Основной горизонтальный layout
        main_layout = QHBoxLayout(central_widget)

        # Левая панель - управление
        left_panel = QWidget()
        # Ограничение максимальной ширины левой панели
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)

        # Группа управления графом
        control_group = QGroupBox("Управление графом")
        control_layout = QVBoxLayout(control_group)

        # Кнопка очистки графа
        self.clear_btn = QPushButton("Очистить граф")
        self.clear_btn.clicked.connect(self.controller.clear_graph)
        control_layout.addWidget(self.clear_btn)

        # Кнопки переключения режимов
        self.point_mode_btn = QPushButton("Режим добавления точек")
        self.point_mode_btn.clicked.connect(self.controller.switch_to_point_mode)
        control_layout.addWidget(self.point_mode_btn)

        self.edge_mode_btn = QPushButton("Режим создания ребер")
        self.edge_mode_btn.clicked.connect(self.controller.switch_to_edge_mode)
        control_layout.addWidget(self.edge_mode_btn)

        # Инструкция для пользователя
        instruction_label = QLabel(
            "Инструкция:\n"
            "1. В режиме точек: кликните в пустое место\n"
            "2. В режиме ребер: кликните на две точки\n"
            "   для соединения их ребром"
        )
        instruction_label.setWordWrap(True)
        control_layout.addWidget(instruction_label)

        left_layout.addWidget(control_group)

        # Группа параметров алгоритма
        algo_group = QGroupBox("Параметры муравьиного алгоритма")
        algo_layout = QFormLayout(algo_group)

        # Поле ввода количества муравьев
        self.ants_spin = QSpinBox()
        self.ants_spin.setRange(1, 1000)
        self.ants_spin.setValue(100)
        self.ants_spin.setToolTip(
            "Количество муравьев в колонии. Больше муравьев - лучше поиск, но медленнее вычисления")
        algo_layout.addRow("Количество муравьев:", self.ants_spin)

        # Поле ввода количества итераций
        self.iterations_spin = QSpinBox()
        self.iterations_spin.setRange(1, 1000)
        self.iterations_spin.setValue(20)
        self.iterations_spin.setToolTip("Количество итераций алгоритма. Больше итераций - лучше решение, но дольше расчет")
        algo_layout.addRow("Количество итераций:", self.iterations_spin)

        # Поле ввода параметра Alpha (влияние феромона)
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.1, 5.0)
        self.alpha_spin.setValue(1.5)
        self.alpha_spin.setSingleStep(0.1)
        self.alpha_spin.setToolTip(
            "Влияние феромона на выбор пути. Высокое значение - муравьи сильнее следуют феромонным следам")
        algo_layout.addRow("Альфа (влияние феромона):", self.alpha_spin)

        # Поле ввода параметра Beta (влияние расстояния)
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setRange(0.1, 5.0)
        self.beta_spin.setValue(1.2)
        self.beta_spin.setSingleStep(0.1)
        self.beta_spin.setToolTip(
            "Влияние расстояния на выбор пути. Высокое значение - муравьи предпочитают короткие пути")
        algo_layout.addRow("Бета (влияние расстояния):", self.beta_spin)

        # Поле ввода параметра Rho (испарение феромона)
        self.rho_spin = QDoubleSpinBox()
        self.rho_spin.setRange(0.0, 1.0)
        self.rho_spin.setValue(0.6)
        self.rho_spin.setSingleStep(0.1)
        self.rho_spin.setToolTip("Скорость испарения феромона. Высокое значение - быстрее забываются плохие пути")
        algo_layout.addRow("Ро (испарение феромона):", self.rho_spin)

        # Поле ввода параметра Q (интенсивность феромона)
        self.q_spin = QDoubleSpinBox()
        self.q_spin.setRange(0.1, 100.0)
        self.q_spin.setValue(10.0)
        self.q_spin.setSingleStep(1.0)
        self.q_spin.setToolTip("Интенсивность феромона. Влияет на количество оставляемого феромона")
        algo_layout.addRow("Q (интенсивность феромона):", self.q_spin)

        # Кнопка запуска решения задачи
        self.solve_btn = QPushButton("Решить задачу коммивояжера")
        self.solve_btn.clicked.connect(self.solve_tsp)
        algo_layout.addRow(self.solve_btn)

        left_layout.addWidget(algo_group)

        # Группа результатов
        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout(results_group)

        # Текстовое поле для отображения результатов
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setPlaceholderText("Здесь будут отображаться результаты расчетов...")
        results_layout.addWidget(self.results_text)

        # Кнопка показа истории расчетов
        self.history_btn = QPushButton("Показать историю расчетов")
        self.history_btn.clicked.connect(self.controller.show_history)
        results_layout.addWidget(self.history_btn)

        left_layout.addWidget(results_group)
        left_layout.addStretch()

        # Правая панель - графическое представление графа
        self.graph_view = GraphView(self.controller)

        # Добавление левой панели и графического представления в основной layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.graph_view, 1)

    def solve_tsp(self):
        # Сбор параметров алгоритма из интерфейса
        params = {
            'ants': self.ants_spin.value(),
            'iterations': self.iterations_spin.value(),
            'alpha': self.alpha_spin.value(),
            'beta': self.beta_spin.value(),
            'rho': self.rho_spin.value(),
            'q': self.q_spin.value()
        }
        # Передача параметров контроллеру для решения задачи
        self.controller.solve_tsp(params)

    def add_point_to_view(self, x: float, y: float) -> int:
        """Добавляет точку в представление и возвращает её ID"""
        return self.graph_view.add_point(x, y)

    def add_edge_to_view(self, point1_idx: int, point2_idx: int, weight: float):
        """Добавляет ребро с весом в представление"""
        self.graph_view.add_edge(point1_idx, point2_idx, weight)

    def update_edge_weight_display(self, point1_idx: int, point2_idx: int, weight: float):
        """Обновляет отображение веса ребра"""
        self.graph_view.update_edge_weight_display(point1_idx, point2_idx, weight)
    def clear_graph_view(self):
        """Очищает графическое представление"""
        self.graph_view.clear()

    def draw_solution(self, path_indices: list):
        """Отрисовывает решение"""
        self.graph_view.draw_solution(path_indices)

    def highlight_point(self, point_id: int):
        """Подсвечивает точку"""
        self.graph_view.highlight_point(point_id)

    def unhighlight_point(self, point_id: int):
        """Убирает подсветку с точки"""
        self.graph_view.unhighlight_point(point_id)

    def update_results(self, text: str):
        """Обновляет текстовое поле результатов"""
        self.results_text.setText(text)

    def show_error(self, message: str):
        """Показывает сообщение об ошибке"""
        QMessageBox.critical(self, "Ошибка", message)