FROM python:3.11-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли залежностей
COPY base.txt requirements/
COPY auth-service.txt requirements/

# Встановлюємо Python залежності
RUN pip install --no-cache-dir -r requirements/base.txt -r requirements/auth-service.txt

# Копіюємо код сервісу
COPY src/ ./src/

# Створюємо директорію для логів
RUN mkdir -p logs

# Відкриваємо порт
EXPOSE 8001

# Команда запуску
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"] 