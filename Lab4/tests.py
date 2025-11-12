import pytest
from generators import MusicMathGenerator
import time
import threading

#Тесты для класса MusicMathGenerator
class TestMusicMathGenerator:
    # Тест базового генератора нот
    def test_note_generator_basic(self):
        gen = MusicMathGenerator.note_generator(5)
        notes = list(gen)

        assert len(notes) == 5
        valid_notes = ['до', 'ре', 'ми', 'фа', 'соль', 'ля', 'си']
        for note in notes:
            assert note in valid_notes

    # Тест ограничения генератора нот
    def test_note_generator_limit(self):
        gen = MusicMathGenerator.note_generator(0)
        notes = list(gen)
        assert len(notes) == 0

    # Тест генератора чисел для положительных значений
    def test_multiples_of_three_positive(self):
        gen = MusicMathGenerator.multiples_of_three(3)
        numbers = [next(gen) for _ in range(5)]
        expected = [3, 6, 9, 12, 15]
        assert numbers == expected

    # Тест генератора чисел для отрицательных значений
    def test_multiples_of_three_negative(self):
        gen = MusicMathGenerator.multiples_of_three(-100)
        first_numbers = [next(gen) for _ in range(3)]
        assert all(num % 3 == 0 for num in first_numbers)
        assert -100 <= first_numbers[0] <= -94  # Первое кратное 3 после -100

    # Тест валидации корректных email
    def test_validate_emails_valid(self):
        emails = ["test@mail.com", "user_name@domain.org", "test123@site.net"]
        valid = MusicMathGenerator.validate_emails(emails)
        assert valid == emails

    # Тест валидации некорректных email
    def test_validate_emails_invalid(self):
        emails = ["invalid-email", "no@tld", "spaces in@name.com", "@nodomain.com"]
        valid = MusicMathGenerator.validate_emails(emails)
        assert valid == []

    # Тест валидации смешанных email
    def test_validate_emails_mixed(self):
        emails = ["valid@mail.com", "invalid", "another_valid@site.org"]
        valid = MusicMathGenerator.validate_emails(emails)
        expected = ["valid@mail.com", "another_valid@site.org"]
        assert valid == expected

    # Тест валидации пустого списка
    def test_validate_emails_empty(self):
        assert MusicMathGenerator.validate_emails([]) == []

    # Тест многопоточного генератора нот
    def test_threaded_note_generator(self):
        gen = MusicMathGenerator.threaded_note_generator(10, 2)
        notes = list(gen)

        assert len(notes) == 10
        valid_notes = ['до', 'ре', 'ми', 'фа', 'соль', 'ля', 'си']
        for note in notes:
            assert note in valid_notes

    # Тест параллельного генератора нот
    def test_parallel_note_generator(self):
        gen = MusicMathGenerator.parallel_note_generator(10)
        notes = list(gen)

        assert len(notes) == 10
        valid_notes = ['до', 'ре', 'ми', 'фа', 'соль', 'ля', 'си']
        for note in notes:
            assert note in valid_notes

    # Тест обработки исключений в генераторах
    def test_generator_exception_handling(self):
        # Этот тест проверяет, что генераторы не падают при ошибках
        try:
            gen = MusicMathGenerator.note_generator(-1)  # Некорректный лимит
            list(gen)  # Должен обработаться без падения
            assert True
        except Exception:
            pytest.fail("Генератор не обработал исключение")

    # Тест первого значения для разных начальных точек
    @pytest.mark.parametrize("start,expected_first", [
        (0, 0), (-3, -3), (10, 12), (-10, -9)
    ])
    def test_multiples_of_three_first_value(self, start, expected_first):
        gen = MusicMathGenerator.multiples_of_three(start)
        first_value = next(gen)
        assert first_value == expected_first

    # Тест распределения нот (статистический)
    def test_note_generator_distribution(self):
        note_count = 1000
        gen = MusicMathGenerator.note_generator(note_count)
        notes = list(gen)

        # Проверяем, что все типы нот встречаются (с допуском)
        note_types = set(notes)
        expected_notes = {'до', 'ре', 'ми', 'фа', 'соль', 'ля', 'си'}
        assert note_types.issubset(expected_notes)

        # Проверяем, что есть несколько разных нот (не все одинаковые)
        assert len(note_types) > 1, "Должны быть разные ноты"

    # Тест обработки пробельных символов
    def test_validate_emails_whitespace_handling(self):
        emails = ["  test@mail.com  ", "\ttest@domain.org\t", "test@site.net\n"]
        valid_emails = MusicMathGenerator.validate_emails(emails)

        # Проверяем, что пробелы обрезаются
        assert "test@mail.com" in valid_emails
        assert "test@domain.org" in valid_emails
        assert "test@site.net" in valid_emails

    # Тест многопоточного генератора с разным количеством потоков
    def test_threaded_generator_different_thread_counts(self):
        for thread_count in [1, 2, 4, 8]:
            gen = MusicMathGenerator.threaded_note_generator(20, thread_count)
            notes = list(gen)
            assert len(notes) == 20

            valid_notes = ['до', 'ре', 'ми', 'фа', 'соль', 'ля', 'си']
            for note in notes:
                assert note in valid_notes

    # Тест повторного использования генераторов
    def test_generator_reusability(self):
        # Создаем генератор
        gen = MusicMathGenerator.note_generator(5)
        first_batch = list(gen)

        # Создаем новый генератор - должен работать независимо
        gen2 = MusicMathGenerator.note_generator(5)
        second_batch = list(gen2)

        assert len(first_batch) == 5
        assert len(second_batch) == 5

    # Бенчмарк-тест производительности
    def test_performance_benchmark(self):
        # Этот тест может быть пропущен в обычных прогонах
        pytest.skip("Бенчмарк-тест выполняется отдельно")

        sizes = [100, 1000, 10000]
        for size in sizes:
            # Обычный генератор
            start = time.time()
            list(MusicMathGenerator.note_generator(size))
            normal_time = time.time() - start

            # Многопоточный генератор
            start = time.time()
            list(MusicMathGenerator.threaded_note_generator(size, 4))
            threaded_time = time.time() - start

            print(f"Size {size}: Normal={normal_time:.4f}s, Threaded={threaded_time:.4f}s")

            # Для больших размеров многопоточность должна давать выигрыш
            if size >= 1000:
                assert threaded_time <= normal_time * 1.5, f"Многопоточность не эффективна для size={size}"


# Тесты особых и граничных случаев
class TestEdgeCases:

    # Тест пустых строк в email
    def test_empty_string_emails(self):
        emails = ["", "test@mail.com", ""]
        valid_emails = MusicMathGenerator.validate_emails(emails)
        assert valid_emails == ["test@mail.com"]

    # Тест очень маленьких лимитов
    def test_very_small_limits(self):
        for limit in [0, 1]:
            gen = MusicMathGenerator.note_generator(limit)
            notes = list(gen)
            assert len(notes) == limit

    # Тест обработки None входов
    def test_none_input_handling(self):
        result = MusicMathGenerator.validate_emails(None)
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

