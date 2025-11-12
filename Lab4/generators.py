import random
import re
import time
from threading import Thread
from queue import Queue
import concurrent.futures


# Класс для генерации музыкальных нот и математических последовательностей
class MusicMathGenerator:

    # Генератор случайных нот
    @staticmethod
    def note_generator(limit=1_000_000):
        p = ['до', 'ре', 'ми', 'фа', 'соль', 'ля', 'си']
        count = 0
        while count < limit:
            try:
                yield random.choice(p)
                count += 1
            except Exception as e:
                print(f"Ошибка в генераторе нот: {e}")
                break
    # Генератор чисел, кратных 3, начиная с a
    @staticmethod
    def multiples_of_three(a):
        current = a
        while True:
            try:
                if current % 3 == 0:
                    yield current
                current += 1
            except Exception as e:
                print(f"Ошибка в генераторе чисел: {e}")
                break

    # Валидация email-адресов
    @staticmethod
    def validate_emails(email_list):
        if email_list is None or not isinstance(email_list, (list, tuple)):
            return []

        valid_emails = []
        pattern = r'^[a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$'

        for email in email_list:
            try:
                if re.match(pattern, email.strip()):
                    valid_emails.append(email.strip())
            except Exception as e:
                print(f"Ошибка при валидации email {email}: {e}")

        return valid_emails

    # Многопоточная версия генератора нот
    @staticmethod
    def threaded_note_generator(limit=1_000_000, num_threads=4):
        def worker(result_queue, notes_per_thread, thread_id):
            p = ['до', 'ре', 'ми', 'фа', 'соль', 'ля', 'си']
            for i in range(notes_per_thread):
                result_queue.put(random.choice(p))

        result_queue = Queue()
        threads = []

        # Распределяем notes_per_thread более точно
        base_notes_per_thread = limit // num_threads
        extra_notes = limit % num_threads

        # Запуск потоков
        for i in range(num_threads):
            notes_for_this_thread = base_notes_per_thread + (1 if i < extra_notes else 0)
            thread = Thread(target=worker, args=(result_queue, notes_for_this_thread, i))
            threads.append(thread)
            thread.start()

        # Ожидание завершения потоков
        for thread in threads:
            thread.join()

        # Возврат результатов из очереди
        generated_count = 0
        while generated_count < limit and not result_queue.empty():
            yield result_queue.get()
            generated_count += 1

    # Параллельный генератор с использованием ThreadPoolExecutor
    @staticmethod
    def parallel_note_generator(limit=1_000_000):

        def generate_notes_chunk(chunk_size):
            p = ['до', 'ре', 'ми', 'фа', 'соль', 'ля', 'си']
            return [random.choice(p) for _ in range(chunk_size)]

        # Распределяем нагрузку более точно
        num_chunks = 4
        base_chunk_size = limit // num_chunks
        extra_notes = limit % num_chunks

        chunks = []
        for i in range(num_chunks):
            chunk_size = base_chunk_size + (1 if i < extra_notes else 0)
            chunks.append(chunk_size)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(generate_notes_chunk, chunk_size) for chunk_size in chunks]

            for future in concurrent.futures.as_completed(futures):
                for note in future.result():
                    yield note

    # Упрощенная версия для надежного тестирования
    @staticmethod
    def simple_threaded_note_generator(limit=1_000_000, num_threads=4):
        p = ['до', 'ре', 'ми', 'фа', 'соль', 'ля', 'си']
        count = 0
        while count < limit:
            yield random.choice(p)
            count += 1