from lib_package.models import Book, Reader, Subscription
from lib_package.services import StatisticsService, LibraryService
from lib_package.utils import ReportGenerator
from lib_package.database import DatabaseManager

# Основная функция программы
def main():
    print("-" * 50)
    print("    Электронная библиотека. Вариант №20 ")
    print("-" * 50)

    db_manager = DatabaseManager("Library.db")
    library_service = LibraryService(db_manager)

    existing_books = db_manager.get_all_books()
    if not existing_books:
        books = [
            Book("Преступление и наказание", "Ф.М.Достоевский", 672),
            Book("Мастер и Маргарита", "М.А.Булгаков", 480),
            Book("1984", "Дж.Оруэлл", 328),
            Book("Принцип 80/20", "Ричард Кох", 350),
            Book("Оставьте брезгливость, съешьте лягушку", "Брайан Трейси", 159),
            Book("Бабушка велела кланяться и передать, что просит прощения", "Фредрик Бакман", 432)
        ]
        for book in books:
            db_manager.save_book(book)
        books = books  # Используем сохраненные книги
    else:
        # Используем существующие книги из БД
        books = existing_books

    for book in books:
        db_manager.save_book(book)

    print("Введите Фамилию, Имя, Отчество")
    reader_name = input("Введите ФИО: ")

    # Создаем читателя
    reader = Reader(reader_name)
    reader_id = db_manager.save_reader(reader)
    # Обновляем объект с полученным ID
    reader = Reader(reader_name, reader_id)

    subscription = Subscription(reader, 30)  # Абонемент на 30 дней
    db_manager.save_subscription(subscription)

    # Загружаем прогресс чтения для этого читателя
    library_service.load_reader_data(reader)

    print(f"\nСоздан читатель: {reader.name} (ID: {reader.reader_id})")

    # Проверка БД
    db_manager.check_database()

    while True:
        print("\n ----МЕНЮ-----")
        print("1. Добавить чтение книги")
        print("2. Показать статистику")
        print("3. Сохранить отчет в DOCX")
        print("4. Сохранить отчет в XLSX")
        print("5. Выйти")

        choice = input("\n Выберите действие:")

        if choice == "1":
            print("\n Доступные книги:")
            for i, book in enumerate(books, 1):
                print(f"{i}. {book.name} - {book.author} ( {book.total_pages} стр.)")


            try:
                book_choice = int(input("Выберите книгу (номер): ")) - 1
                pages = int(input("Сколько страниц прочитано: "))

                if 0 <= book_choice < len(books):
                    if library_service.save_reading_session(reader, books[book_choice], pages):
                        print(f"Успешно прочитано {pages} страниц")
                    else:
                        print("Нельзя прочитать больше или меньше страниц, чем есть в книге")
                else:
                    print("Неверный номер книги")

            except ValueError:
                print("Ошибка: введите число")

        elif choice == "2":

            print("\n Статистика")

            reader_stats = StatisticsService.calculate_reader_statistics(reader)
            print("Статистика читателя: ")
            print(f" Имя: {reader_stats['reader_name']} ")
            print(f" Прочитано книг: {reader_stats['total_books_read']}")
            print(f" Книг в процессе: {reader_stats['books_in_progress']}")
            print(f" Всего страниц: {reader_stats['total_pages_read']}")
            print(f" Рейтинг чтения: {reader_stats['average_rating']}")

            print("\n Рейтинг по книгам:")
            for rating in reader_stats['book_ratings']:
                print(f"{rating['book_name']}: {rating['progress_percent']}% ({rating['pages_read']}/{rating['total_pages']} стр.)")

            sub_stats = StatisticsService.calculate_subscription_statistics(subscription)
            print("Статистика абонемента: ")
            print(f"Статус: {sub_stats['subscription_status']}")
            print(f"Дней осталось: {sub_stats['days_remaining']}")
            print(f" Дата окончания: {sub_stats['end_date']}")

        elif choice == "3":

            print("\n Отчёт в DOCX")
            report_data = library_service.get_complete_report(reader, subscription)
            ReportGenerator.save_to_docx(report_data, "Library_report.docx")

        elif choice == "4":

            print("\n Отчёт в XLSX")
            report_data = library_service.get_complete_report(reader, subscription)
            ReportGenerator.save_to_xlsx(report_data, "Library_report.xlsx")


        elif choice == "5":
            print("\n Выход из программы ...")
            break

        else:

            print("Неверный выбор. Попробуйте снова")

if __name__ == "__main__":
    main()