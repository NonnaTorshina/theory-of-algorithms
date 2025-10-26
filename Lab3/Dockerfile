FROM python:3.9-slim

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для базы данных и копируем её
RUN mkdir -p /data
COPY sleep_tracker.db /data/sleep_tracker.db

# Устанавливаем правильные права доступа
RUN chmod 644 /data/sleep_tracker.db

# Указываем переменную окружения для пути к БД
ENV DATABASE_PATH=/data/sleep_tracker.db

# Команда для запуска приложения
CMD ["python", "main.py"]