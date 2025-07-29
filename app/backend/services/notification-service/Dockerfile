FROM python:3.11-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли залежностей
COPY requirements.txt .

# Встановлюємо Python залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код сервісу
COPY src/ ./src/

# Створюємо директорію для логів
RUN mkdir -p logs

# Відкриваємо порт
EXPOSE 8005

# Команда запуску
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"] 