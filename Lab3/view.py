"""Графический интерфейс. Содержит все визуальные элементы прилоения"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QPushButton,
                               QDateEdit, QHeaderView, QMessageBox, QMenuBar, QMenu, QStatusBar,
                               QFormLayout, QGroupBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtGui import QAction, QPainter
from datetime import datetime
from PySide6.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        font = QFont("Arial", 14)
        self.setFont(font)

        self.setWindowTitle("Отслеживание сна / персональный дневник сна")
        self.setGeometry(100,100,1200,800)
        # Центральный виджет и основной макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Создаем все компоненты интерфейса
        self._create_menu()
        self._create_input_section(main_layout)
        self._create_table_section(main_layout)
        self._create_chart_section(main_layout)
        self._create_status_bar()

    # Создает меню приложения
    def _create_menu(self):

        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")

        new_action = QAction("Новая запись", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.clear_inputs)

        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Меню Помощь
        help_menu = menubar.addMenu("Помощь")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    # Создает секцию для ввода данных
    def _create_input_section(self, main_layout):

        input_group = QGroupBox("Добавление новой записи о сне")
        input_layout = QFormLayout()

        # Поле выбора даты
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMaximumDate(QDate.currentDate())  # Нельзя выбрать будущую дату

        # Поле ввода продолжительности
        self.duration_edit = QLineEdit()
        self.duration_edit.setPlaceholderText("Например: 7.5")

        # Поле ввода качества сна
        self.quality_edit = QLineEdit()
        self.quality_edit.setPlaceholderText("От 1 до 10")

        # Поле для заметок
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Необязательные заметки о сне")

        # Кнопка добавления
        self.add_button = QPushButton("Добавить запись о сне")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)

        # Добавляем виджеты в layout
        input_layout.addRow(QLabel("Дата сна:"), self.date_edit)
        input_layout.addRow(QLabel("Продолжительность (в часах):"), self.duration_edit)
        input_layout.addRow(QLabel("Качество сна (1-10):"), self.quality_edit)
        input_layout.addRow(QLabel("Заметки:"), self.notes_edit)
        input_layout.addRow(self.add_button)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

    # Создает секцию с таблицей записей
    def _create_table_section(self, main_layout):

        table_group = QGroupBox("История вашего сна")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Дата", "Длительность (часы)", "Качество", "Заметки"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)

    # Создает секцию с графиком
    def _create_chart_section(self, main_layout):

        chart_group = QGroupBox("Динамика продолжительности сна")
        chart_layout = QVBoxLayout()

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        chart_layout.addWidget(self.chart_view)
        chart_group.setLayout(chart_layout)
        main_layout.addWidget(chart_group)

    # Создает статус бар
    def _create_status_bar(self):

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе. Добавьте вашу первую запись о сне!")

    # Показывает информацию о программе
    def show_about(self):

        QMessageBox.about(self, "О программе",
                          "Трекер сна v1.0\n\n"
                          "Приложение для отслеживания качества и продолжительности сна.\n"
                          "Разработано в рамках лабораторной работы №3.")

    # Возвращает данные из полей ввода
    def get_input_data(self):
        return {
            'date': self.date_edit.date().toPython(),
            'duration': self.duration_edit.text(),
            'quality': self.quality_edit.text(),
            'notes': self.notes_edit.text()
        }

    # Очищает поля ввода
    def clear_inputs(self):

        self.duration_edit.clear()
        self.quality_edit.clear()
        self.notes_edit.clear()
        self.status_bar.showMessage("Поля очищены. Готов к вводу новой записи.")

    # Показывает сообщение об ошибке
    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)

    # Показывает информационное сообщение
    def show_info(self, message):
        QMessageBox.information(self, "Информация", message)

    # Обновляет таблицу данными из списка записей
    def update_table(self, records):
        self.table.setRowCount(0)  # Очищаем таблицу

        for row_number, record in enumerate(records):
            self.table.insertRow(row_number)
            record_data = record.to_list()

            for column_number, data in enumerate(record_data):
                item = QTableWidgetItem(str(data))

                # Красим ячейку качества в зависимости от значения
                if column_number == 2:  # Столбец "Качество"
                    quality = int(data)
                    if quality >= 8:
                        item.setBackground(Qt.green)
                    elif quality >= 5:
                        item.setBackground(Qt.yellow)
                    else:
                        item.setBackground(Qt.red)

                self.table.setItem(row_number, column_number, item)

    # Обновляет график на основе переданных записей
    def update_chart(self, records):
        chart = QChart()

        if not records:
            # Если записей нет, показываем пустой график с сообщением
            chart.setTitle("Нет данных для отображения графика")
            self.chart_view.setChart(chart)
            return

        chart.setTitle("Динамика продолжительности сна за последние 10 записей")

        series = QLineSeries()
        series.setName("Продолжительность сна (часы)")

        # Добавляем точки на график (последние 10 записей)
        for record in records[-10:]:
            # Конвертируем дату в миллисекунды для Qt
            x_value = datetime(record.sleep_date.year,
                               record.sleep_date.month,
                               record.sleep_date.day).timestamp() * 1000
            series.append(x_value, record.duration_hours)

        chart.addSeries(series)

        # Настраиваем оси
        axis_x = QDateTimeAxis()
        axis_x.setFormat("dd MMM")
        axis_x.setTitleText("Дата")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.1f")
        axis_y.setTitleText("Часы сна")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view.setChart(chart)

    # Обновляет статус бар
    def update_status(self, message):
        self.status_bar.showMessage(f"{message}")
