import sys
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                               QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
                               QLineEdit, QLabel, QProgressBar, QSpinBox)
from PySide6.QtCore import QThread, Signal
from generators import MusicMathGenerator

# Поток для выполнения генераторов
class GeneratorThread(QThread):
    result_ready = Signal(str)
    progress_updated = Signal(int)
    finished_signal = Signal()

    def __init__(self, generator_func, count, *args):
        super().__init__()
        self.generator_func = generator_func
        self.count = count
        self.args = args

    def run(self):
        try:
            gen = self.generator_func(*self.args)
            results = []
            for i, item in enumerate(gen):
                if i >= self.count:
                    break
                results.append(str(item))
                self.progress_updated.emit(int((i + 1) / self.count * 100))

            self.result_ready.emit("\n".join(results))
            self.finished_signal.emit()
        except Exception as e:
            self.result_ready.emit(f"Ошибка: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music & Math Generator - Вариант 20")
        self.setGeometry(100, 100, 800, 600)

        # Создание вкладок
        tab_widget = QTabWidget()

        # Вкладка 1: Генератор нот
        self.tab1 = QWidget()
        self.setup_tab1()
        tab_widget.addTab(self.tab1, "Генератор нот")

        # Вкладка 2: Числа кратные 3
        self.tab2 = QWidget()
        self.setup_tab2()
        tab_widget.addTab(self.tab2, "Числа кратные 3")

        # Вкладка 3: Валидация email
        self.tab3 = QWidget()
        self.setup_tab3()
        tab_widget.addTab(self.tab3, "Валидация email")

        # Вкладка 4: Производительность
        self.tab4 = QWidget()
        self.setup_tab4()
        tab_widget.addTab(self.tab4, "Производительность")

        self.setCentralWidget(tab_widget)

    def setup_tab1(self):
        layout = QVBoxLayout()

        # Управление
        control_layout = QHBoxLayout()
        self.count_spinbox1 = QSpinBox()
        self.count_spinbox1.setRange(1, 1000)
        self.count_spinbox1.setValue(20)
        control_layout.addWidget(QLabel("Количество нот:"))
        control_layout.addWidget(self.count_spinbox1)

        self.btn_generate_notes = QPushButton("Сгенерировать ноты")
        self.btn_generate_notes.clicked.connect(self.generate_notes)
        control_layout.addWidget(self.btn_generate_notes)

        self.btn_threaded_notes = QPushButton("Многопоточные ноты")
        self.btn_threaded_notes.clicked.connect(self.generate_threaded_notes)
        control_layout.addWidget(self.btn_threaded_notes)

        layout.addLayout(control_layout)

        # Прогресс бар
        self.progress1 = QProgressBar()
        layout.addWidget(self.progress1)

        # Вывод результатов
        self.output1 = QTextEdit()
        self.output1.setPlaceholderText("Здесь появятся сгенерированные ноты...")
        layout.addWidget(self.output1)

        self.tab1.setLayout(layout)

    def setup_tab2(self):
        layout = QVBoxLayout()

        # Управление
        control_layout = QHBoxLayout()
        self.start_spinbox = QSpinBox()
        self.start_spinbox.setRange(-1000, 1000)
        self.start_spinbox.setValue(-100)
        control_layout.addWidget(QLabel("Начальное число:"))
        control_layout.addWidget(self.start_spinbox)

        self.count_spinbox2 = QSpinBox()
        self.count_spinbox2.setRange(1, 1000)
        self.count_spinbox2.setValue(20)
        control_layout.addWidget(QLabel("Количество чисел:"))
        control_layout.addWidget(self.count_spinbox2)

        self.btn_generate_numbers = QPushButton("Сгенерировать числа")
        self.btn_generate_numbers.clicked.connect(self.generate_numbers)
        control_layout.addWidget(self.btn_generate_numbers)

        layout.addLayout(control_layout)

        # Прогресс бар
        self.progress2 = QProgressBar()
        layout.addWidget(self.progress2)

        # Вывод результатов
        self.output2 = QTextEdit()
        self.output2.setPlaceholderText("Здесь появятся числа, кратные 3...")
        layout.addWidget(self.output2)

        self.tab2.setLayout(layout)

    def setup_tab3(self):
        layout = QVBoxLayout()

        # Ввод email
        layout.addWidget(QLabel("Введите email-адреса через пробел:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@mail.com test@domain.org invalid-email")
        layout.addWidget(self.email_input)

        # Кнопка валидации
        self.btn_validate_emails = QPushButton("Проверить email")
        self.btn_validate_emails.clicked.connect(self.validate_emails)
        layout.addWidget(self.btn_validate_emails)

        # Вывод результатов
        self.output3 = QTextEdit()
        self.output3.setPlaceholderText("Здесь появятся корректные email-адреса...")
        layout.addWidget(self.output3)

        self.tab3.setLayout(layout)

    def setup_tab4(self):
        layout = QVBoxLayout()

        # Тестирование производительности
        self.btn_test_performance = QPushButton("Тест производительности")
        self.btn_test_performance.clicked.connect(self.test_performance)
        layout.addWidget(self.btn_test_performance)

        # Вывод результатов теста
        self.output4 = QTextEdit()
        self.output4.setPlaceholderText("Здесь появятся результаты тестирования производительности...")
        layout.addWidget(self.output4)

        self.tab4.setLayout(layout)

    # Слоты для обработки событий
    def generate_notes(self):
        self.btn_generate_notes.setEnabled(False)
        self.progress1.setValue(0)
        count = self.count_spinbox1.value()

        self.thread = GeneratorThread(MusicMathGenerator.note_generator, count)
        self.thread.result_ready.connect(self.output1.setText)
        self.thread.progress_updated.connect(self.progress1.setValue)
        self.thread.finished_signal.connect(lambda: self.btn_generate_notes.setEnabled(True))
        self.thread.start()

    def generate_threaded_notes(self):
        self.btn_threaded_notes.setEnabled(False)
        self.progress1.setValue(0)
        count = self.count_spinbox1.value()

        self.thread = GeneratorThread(MusicMathGenerator.threaded_note_generator, count, 1_000_000, 4)
        self.thread.result_ready.connect(self.output1.setText)
        self.thread.progress_updated.connect(self.progress1.setValue)
        self.thread.finished_signal.connect(lambda: self.btn_threaded_notes.setEnabled(True))
        self.thread.start()

    def generate_numbers(self):
        self.btn_generate_numbers.setEnabled(False)
        self.progress2.setValue(0)
        start = self.start_spinbox.value()
        count = self.count_spinbox2.value()

        self.thread = GeneratorThread(MusicMathGenerator.multiples_of_three, count, start)
        self.thread.result_ready.connect(self.output2.setText)
        self.thread.progress_updated.connect(self.progress2.setValue)
        self.thread.finished_signal.connect(lambda: self.btn_generate_numbers.setEnabled(True))
        self.thread.start()

    def validate_emails(self):
        emails = self.email_input.text().split()
        valid_emails = MusicMathGenerator.validate_emails(emails)

        if valid_emails:
            self.output3.setText("\n".join(valid_emails))
        else:
            self.output3.setText("Корректные email-адреса не найдены")

    def test_performance(self):
        self.output4.clear()
        self.output4.append("Запуск теста производительности...")

        # Тест обычного генератора
        start_time = time.time()
        notes = list(MusicMathGenerator.note_generator(10000))
        normal_time = time.time() - start_time
        self.output4.append(f"Обычный генератор: {normal_time:.4f} сек")

        # Тест многопоточного генератора
        start_time = time.time()
        notes = list(MusicMathGenerator.threaded_note_generator(10000, 4))
        threaded_time = time.time() - start_time
        self.output4.append(f"Многопоточный генератор: {threaded_time:.4f} сек")

        # Тест параллельного генератора
        start_time = time.time()
        notes = list(MusicMathGenerator.parallel_note_generator(10000))
        parallel_time = time.time() - start_time
        self.output4.append(f"Параллельный генератор: {parallel_time:.4f} сек")

        # Сравнение производительности
        speedup_threaded = normal_time / threaded_time if threaded_time > 0 else 0
        speedup_parallel = normal_time / parallel_time if parallel_time > 0 else 0

        self.output4.append(f"\nУскорение многопоточного: {speedup_threaded:.2f}x")
        self.output4.append(f"Ускорение параллельного: {speedup_parallel:.2f}x")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())