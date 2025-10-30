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
        # Ссылка на контроллер для обратной связи
        self.controller = controller
        # Сцена для отображения графических элементов
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        # Включение сглаживания для лучшего качества отображения
        self.setRenderHint(QPainter.Antialiasing)
        # Установка размеров сцены
        self.setSceneRect(0, 0, 800, 600)

        # Список координат точек в формате [(x, y), ...]
        self.points = []
        # Список графических элементов точек (эллипсы)
        self.point_items = []
        # Список графических элементов ребер (линии)
        self.edge_items = []
        # Список графических элементов решения (красные линии)
        self.solution_items = []

    def clear(self):
        # Полная очистка сцены и всех данных
        self.scene.clear()
        self.points.clear()
        self.point_items.clear()
        self.edge_items.clear()
        self.solution_items.clear()

    def add_point(self, x: float, y: float):
        """Добавляет точку на сцену - увеличенный размер"""
        point_id = len(self.points)
        # Сохранение координат точки
        self.points.append((x, y))

        # Увеличиваем размер точки (было 10x10, стало 16x16)
        ellipse = QGraphicsEllipseItem(x - 8, y - 8, 20, 20)
        # Установка зелёного цвета заливки
        ellipse.setBrush(QColor(0, 255, 0))
        # Установка темно-синей границы толщиной 2 пикселя
        ellipse.setPen(QPen(QColor(30, 80, 180), 2))
        # Сохранение ID точки в данных элемента
        ellipse.setData(0, point_id)
        # Установка высокого Z-value чтобы точки были выше линий
        ellipse.setZValue(1)
        self.scene.addItem(ellipse)
        self.point_items.append(ellipse)

        # Добавляем номер точки
        label = self.scene.addText(str(point_id))
        # Чёрный цвет текста
        label.setDefaultTextColor(QColor(0, 0, 0))
        # Позиционирование текста рядом с точкой
        label.setPos(x + 10, y - 12)
        # Жирный шрифт Arial размера 9
        label.setFont(QFont("Arial", 9, QFont.Bold))
        # Самый высокий Z-value чтобы текст был выше всех элементов
        label.setZValue(2)

        return point_id

    def add_edge(self, point1_idx: int, point2_idx: int):
        """Добавляет ребро между двумя точками"""
        # Проверка валидности индексов точек
        if point1_idx >= len(self.points) or point2_idx >= len(self.points):
            return

        # Получение координат точек
        x1, y1 = self.points[point1_idx]
        x2, y2 = self.points[point2_idx]

        # Создаем графический элемент ребра
        line = QGraphicsLineItem(x1, y1, x2, y2)
        # Серый цвет линии толщиной 2 пикселя
        line.setPen(QPen(QColor(100, 100, 100), 2))
        # Низкий Z-value чтобы ребра были под точками
        line.setZValue(0)
        self.scene.addItem(line)
        self.edge_items.append(line)

    def highlight_point(self, point_id: int):
        """Подсвечивает выбранную точку"""
        if 0 <= point_id < len(self.point_items):
            # Изменение цвета на желтый для выделения
            self.point_items[point_id].setBrush(QColor(255, 200, 50))

    def unhighlight_point(self, point_id: int):
        """Убирает подсветку с точки"""
        if 0 <= point_id < len(self.point_items):
            # Возврат исходного синего цвета
            self.point_items[point_id].setBrush(QColor(70, 130, 230))

    def draw_solution(self, path_indices: list):
        """Отрисовывает решение задачи коммивояжера"""
        # Удаляем предыдущее решение
        for item in self.solution_items:
            self.scene.removeItem(item)
        self.solution_items.clear()

        # Проверка наличия валидного пути
        if not path_indices or len(path_indices) < 2:
            return

        # Рисуем путь решения
        pen = QPen(QColor(255, 50, 50), 4)  # Красный цвет для решения
        for i in range(len(path_indices) - 1):
            idx1 = path_indices[i]
            idx2 = path_indices[i + 1]

            # Проверка валидности индексов
            if idx1 < len(self.points) and idx2 < len(self.points):
                x1, y1 = self.points[idx1]
                x2, y2 = self.points[idx2]

                line = QGraphicsLineItem(x1, y1, x2, y2)
                line.setPen(pen)
                line.setZValue(0)
                self.scene.addItem(line)
                self.solution_items.append(line)

    def mousePressEvent(self, event: QMouseEvent):
        """Обработчик кликов мыши"""
        if event.button() == Qt.LeftButton:
            # Преобразуем координаты мыши в координаты сцены
            scene_pos = self.mapToScene(event.pos())
            # Передаем координаты контроллеру для обработки
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

    def add_edge_to_view(self, point1_idx: int, point2_idx: int):
        """Добавляет ребро в представление"""
        self.graph_view.add_edge(point1_idx, point2_idx)

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