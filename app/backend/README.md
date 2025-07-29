# Upwork AI Assistant - Backend

## 🏗️ Архітектура

Проект використовує **мікросервісну архітектуру** з наступними компонентами:

### 🔧 Мікросервіси

1. **API Gateway** (порт 8000) - Центральна точка входу для всіх запитів
2. **Auth Service** (порт 8001) - Аутентифікація та авторизація
3. **Upwork Service** (порт 8002) - Інтеграція з Upwork API
4. **AI Service** (порт 8003) - AI функціональність
5. **Analytics Service** (порт 8004) - Аналітика та звітність
6. **Notification Service** (порт 8005) - Сповіщення

### 🗄️ Бази даних

- **PostgreSQL** - Основна база даних
- **Redis** - Кешування та сесії

### 🔒 Безпека

- JWT токени для API аутентифікації
- MFA (Multi-Factor Authentication)
- OAuth 2.0 для Upwork інтеграції
- Шифрування чутливих даних
- Rate limiting

## 🚀 Швидкий старт

### Вимоги

- Docker та Docker Compose
- Python 3.11+
- PostgreSQL
- Redis

### Запуск

1. **Клонування репозиторію:**
```bash
git clone <repository-url>
cd upwork/app/backend
```

2. **Налаштування змінних середовища:**
```bash
cp .env.example .env
# Відредагуйте .env файл з вашими налаштуваннями
```

3. **Запуск з Docker Compose:**
```bash
docker-compose up -d
```

4. **Перевірка статусу:**
```bash
# API Gateway
curl http://localhost:8000/health

# Auth Service
curl http://localhost:8001/health

# Upwork Service
curl http://localhost:8002/health

# AI Service
curl http://localhost:8003/health

# Analytics Service
curl http://localhost:8004/health

# Notification Service
curl http://localhost:8005/health
```

## 📁 Структура проекту

```
app/backend/
├── api-gateway/           # API Gateway мікросервіс
│   ├── src/
│   ├── requirements.txt
│   └── Dockerfile
├── services/              # Мікросервіси
│   ├── auth-service/      # Сервіс аутентифікації
│   ├── upwork-service/    # Сервіс Upwork інтеграції
│   ├── ai-service/        # AI сервіс
│   ├── analytics-service/ # Сервіс аналітики
│   └── notification-service/ # Сервіс сповіщень
├── shared/                # Спільні компоненти
│   ├── config/           # Налаштування
│   ├── database/         # Підключення до БД
│   └── utils/            # Утиліти
├── docker-compose.yml    # Docker Compose конфігурація
└── README.md
```

## 🔧 API Endpoints

### API Gateway (порт 8000)

- `GET /` - Інформація про сервіс
- `GET /health` - Статус здоров'я
- `GET /auth/*` - Маршрутизація до Auth Service
- `GET /upwork/*` - Маршрутизація до Upwork Service
- `GET /ai/*` - Маршрутизація до AI Service
- `GET /analytics/*` - Маршрутизація до Analytics Service
- `GET /notifications/*` - Маршрутизація до Notification Service

### Auth Service (порт 8001)

- `POST /auth/register` - Реєстрація користувача
- `POST /auth/login` - Вхід користувача
- `GET /auth/profile` - Профіль користувача
- `POST /auth/mfa/setup` - Налаштування MFA
- `POST /auth/oauth/upwork/authorize` - OAuth авторизація Upwork

### Upwork Service (порт 8002)

- `GET /upwork/jobs` - Список вакансій
- `GET /upwork/jobs/{job_id}` - Деталі вакансії
- `POST /upwork/jobs/search` - Пошук вакансій
- `GET /upwork/applications` - Список заявок
- `POST /upwork/applications` - Створення заявки

### AI Service (порт 8003)

- `POST /ai/generate/proposal` - Генерація пропозиції
- `POST /ai/analyze/job` - Аналіз вакансії
- `POST /ai/filter/jobs` - Розумна фільтрація
- `POST /ai/optimize/proposal` - Оптимізація пропозиції

### Analytics Service (порт 8004)

- `GET /analytics/dashboard` - Дані дашборду
- `GET /analytics/reports/performance` - Звіт продуктивності
- `GET /analytics/reports/revenue` - Звіт доходів
- `GET /analytics/metrics` - Метрики
- `POST /analytics/track/event` - Відстеження подій

### Notification Service (порт 8005)

- `GET /notifications` - Список сповіщень
- `POST /notifications` - Створення сповіщення
- `POST /notifications/{id}/read` - Позначення як прочитане
- `POST /notifications/send/email` - Відправка email
- `POST /notifications/send/telegram` - Відправка Telegram
- `POST /notifications/send/push` - Push сповіщення

## 🔒 Безпека

### Аутентифікація

- JWT токени для API доступу
- Access та Refresh токени
- Автоматичне оновлення токенів

### MFA (Multi-Factor Authentication)

- TOTP (Time-based One-Time Password)
- Google Authenticator підтримка
- Резервні коди для відновлення

### OAuth 2.0

- Інтеграція з Upwork API
- Безпечне зберігання токенів
- Автоматичне оновлення токенів

### Шифрування

- Fernet шифрування для чутливих даних
- bcrypt для хешування паролів
- Безпечне зберігання API ключів

## 📊 Моніторинг

### Логування

- Структуровані логи з Loguru
- Різні рівні логування (DEBUG, INFO, WARNING, ERROR)
- Ротація лог файлів

### Health Checks

- Кожен сервіс має `/health` endpoint
- Перевірка підключення до БД
- Перевірка Redis підключення

### Метрики

- Відстеження API запитів
- Час відповіді сервісів
- Помилки та винятки

## 🧪 Тестування

### Unit Tests

```bash
# Тестування Auth Service
cd services/auth-service
pytest

# Тестування Upwork Service
cd services/upwork-service
pytest

# Тестування AI Service
cd services/ai-service
pytest
```

### Integration Tests

```bash
# Тестування API Gateway
cd api-gateway
pytest tests/integration/

# Тестування мікросервісів
cd services
pytest tests/integration/
```

### End-to-End Tests

```bash
# E2E тести
cd tests/e2e
pytest
```

## 🚀 Розгортання

### Development

```bash
docker-compose up -d
```

### Production

```bash
# Збірка образів
docker-compose -f docker-compose.prod.yml build

# Запуск
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Налаштування

### Змінні середовища

Створіть `.env` файл з наступними змінними:

```env
# База даних
DATABASE_URL=postgresql://user:password@localhost:5432/upwork_db
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Шифрування
ENCRYPTION_KEY=your-encryption-key

# Upwork API
UPWORK_CLIENT_ID=your-client-id
UPWORK_CLIENT_SECRET=your-client-secret
UPWORK_REDIRECT_URI=http://localhost:8001/auth/oauth/upwork/callback

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_IDS=chat_id1,chat_id2

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Налаштування
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000"]
```

## 🤝 Розробка

### Додавання нового мікросервісу

1. Створіть папку в `services/`
2. Додайте `main.py`, `requirements.txt`, `Dockerfile`
3. Оновіть `docker-compose.yml`
4. Додайте маршрутизацію в API Gateway

### Спільні компоненти

Використовуйте компоненти з папки `shared/`:

- `shared/config/settings.py` - Налаштування
- `shared/config/logging.py` - Логування
- `shared/database/connection.py` - Підключення до БД
- `shared/utils/encryption.py` - Шифрування

## 📝 Ліцензія

MIT License

## 🤝 Підтримка

Для підтримки звертайтеся до документації або створюйте issues в репозиторії.
