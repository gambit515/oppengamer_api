# Основной образ Python
FROM python:3.10-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование зависимостей и их установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего кода приложения
COPY . .

# Применение миграций при старте контейнера
CMD ["python", "oppengamer_api/manage.py", "migrate"]

# Запуск сервера Django
CMD ["python", "oppengamer_api/manage.py", "runserver", "0.0.0.0:8000"]

