<!--
ФАЙЛ: SETUP.md
ОПИС: Інструкції по встановленню та налаштуванню Upwork Web App
ПРИЗНАЧЕННЯ: Покрокові інструкції для запуску проекту
ЩО ЗБЕРІГАЄ: Інструкції встановлення, налаштування, тестування
-->

# 🚀 Інструкції по встановленню Upwork Web App

## 📋 Вимоги

### Обов'язкові:
- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**
- **Upwork Developer Account** (https://developers.upwork.com/)

### Рекомендовані:
- **VS Code** або інший IDE
- **Postman** для тестування API
- **OpenAI API Key** для AI функцій

## 🐳 Встановлення Docker

### macOS:
```bash
# Через Homebrew
brew install --cask docker

# Або завантажте з офіційного сайту
# https://www.docker.com/products/docker-desktop
```

### Linux (Ubuntu/Debian):
```bash
# Оновлення пакетів
sudo apt-get update

# Встановлення залежностей
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Додавання GPG ключа
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Додавання репозиторію
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Встановлення Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Встановлення Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Windows:
1. Завантажте Docker Desktop з офіційного сайту
2. Встановіть та запустіть Docker Desktop
3. Перезавантажте комп'ютер

## 🔧 Налаштування проекту

### 1. Клонування репозиторію
```bash
git clone <repository-url>
cd upwork_web_app
```

### 2. Створення .env файлу
```bash
# Скопіюйте приклад
cp .env.example .env

# Відредагуйте .env файл
nano .env
```

### 3. Налаштування Upwork API
```bash
# 1. Зареєструйтесь на https://developers.upwork.com/
# 2. Створіть новий додаток
# 3. Отримайте API ключі
# 4. Додайте ключі в .env файл
```

### 4. Налаштування OpenAI API (опціонально)
```bash
# 1. Зареєструйтесь на https://platform.openai.com/
# 2. Отримайте API ключ
# 3. Додайте ключ в .env файл
```

## 🚀 Запуск проекту

### Через Docker (рекомендовано):
```bash
# Збірка образів
docker-compose build

# Запуск всіх сервісів
docker-compose up -d

# Перевірка статусу
docker-compose ps

# Перегляд логів
docker-compose logs -f
```

### Локальний запуск:
```bash
# Встановлення залежностей
pip install -r requirements.txt

# Налаштування бази даних
python -m src.database.connection

# Запуск FastAPI сервера
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔑 Налаштування API ключів

### Upwork API:
1. Перейдіть на https://developers.upwork.com/
2. Створіть новий додаток
3. Отримайте API ключі:
   - **API Key** (Consumer Key)
   - **API Secret** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**

### OpenAI API:
1. Перейдіть на https://platform.openai.com/
2. Створіть API ключ
3. Додайте ключ в конфігурацію

## 📊 База даних

### PostgreSQL:
```bash
# Створення бази даних
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE upwork_web_app;"

# Застосування міграцій
python -m src.database.migrations
```

### Redis (для кешування):
```bash
# Redis запускається автоматично з Docker Compose
# Перевірка статусу
docker-compose exec redis redis-cli ping
```

## 🔧 Конфігурація

### Основні змінні середовища (.env):
```bash
# Upwork API
UPWORK_API_KEY=your_api_key_here
UPWORK_API_SECRET=your_api_secret_here
UPWORK_ACCESS_TOKEN=your_access_token_here
UPWORK_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# OpenAI API
OPENAI_API_KEY=your_openai_key_here

# База даних
DATABASE_URL=postgresql://postgres:password@localhost:5432/upwork_web_app

# Redis
REDIS_URL=redis://localhost:6379

# Telegram Bot (опціонально)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## 🧪 Тестування

### Запуск тестів:
```bash
# Всі тести
pytest

# Конкретний тест
pytest tests/test_api_integration.py

# З покриттям
pytest --cov=src tests/
```

### Тестування API:
```bash
# Запуск сервера
uvicorn src.main:app --reload

# Тестування через curl
curl http://localhost:8000/health
curl http://localhost:8000/jobs
```

## 📈 Моніторинг

### Логи:
```bash
# Перегляд логів
docker-compose logs -f app

# Логи бази даних
docker-compose logs -f postgres

# Логи Redis
docker-compose logs -f redis
```

### Метрики:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **API документація**: http://localhost:8000/docs

## 🚀 Розгортання

### Production:
```bash
# Збірка production образів
docker-compose -f docker-compose.prod.yml build

# Запуск production
docker-compose -f docker-compose.prod.yml up -d
```

### Staging:
```bash
# Збірка staging образів
docker-compose -f docker-compose.staging.yml build

# Запуск staging
docker-compose -f docker-compose.staging.yml up -d
```

## 🔧 Troubleshooting

### Проблеми з Docker:
```bash
# Очищення образів
docker system prune -a

# Перезапуск Docker
sudo systemctl restart docker
```

### Проблеми з базою даних:
```bash
# Скидання бази даних
docker-compose down -v
docker-compose up -d postgres
```

### Проблеми з API:
```bash
# Перевірка API ключів
python -c "from src.config.api_config import api_config; print(api_config.test_connection())"

# Тестування підключення
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.upwork.com/api/v2/jobs
```

## 📚 Корисні команди

### Розробка:
```bash
# Запуск в режимі розробки
docker-compose -f docker-compose.dev.yml up

# Hot reload
uvicorn src.main:app --reload

# Лінтер
flake8 src/
black src/
```

### Адміністрація:
```bash
# Backup бази даних
docker-compose exec postgres pg_dump -U postgres upwork_web_app > backup.sql

# Restore бази даних
docker-compose exec -T postgres psql -U postgres upwork_web_app < backup.sql

# Очищення логів
docker-compose exec app find /app/logs -name "*.log" -mtime +7 -delete
```

## 🆘 Підтримка

### Корисні посилання:
- **Upwork API документація**: https://developers.upwork.com/
- **FastAPI документація**: https://fastapi.tiangolo.com/
- **Docker документація**: https://docs.docker.com/

### Контакты:
- **GitHub Issues**: https://github.com/your-repo/issues
- **Email**: support@your-domain.com

---
*Дата: 2024-12-19* 