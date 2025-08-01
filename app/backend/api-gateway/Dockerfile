FROM python:3.11-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо централізовані файли залежностей
COPY requirements/base.txt requirements/
COPY requirements/api-gateway.txt requirements/

# Встановлюємо Python залежності
RUN pip install --no-cache-dir -r requirements/base.txt -r requirements/api-gateway.txt

# Копіюємо код API Gateway
COPY app/backend/api-gateway/src/ ./src/
COPY app/backend/shared/ ./shared/
COPY app/backend/api-gateway/src/routers/ ./src/routers/

# Створюємо директорію для логів
RUN mkdir -p logs

# Відкриваємо порт
EXPOSE 8000

# Команда запуску
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 