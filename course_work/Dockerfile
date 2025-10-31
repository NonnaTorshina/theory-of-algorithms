FROM python:3.8-slim

WORKDIR /app

# Копируем ВЕСЬ проект включая БД
COPY . .

# Переменные окружения
ENV DATABASE_PATH=/app/tsp_results.db

# Устанавливаем SQLite для работы с БД
RUN apt-get update && apt-get install -y sqlite3

# Команда которая держит контейнер активным
CMD ["tail", "-f", "/dev/null"]