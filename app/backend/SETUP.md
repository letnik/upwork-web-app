<!--
ФАЙЛ: SETUP.md
ОПИС: Інструкції по встановленню та налаштуванню Upwork Web App з максимальною безпекою
ПРИЗНАЧЕННЯ: Покрокові інструкції для запуску проекту з безпекою
ЩО ЗБЕРІГАЄ: Інструкції встановлення, налаштування, тестування, безпека
-->

# Інструкції по встановленню Upwork Web App

## Вимоги

### Обов'язкові:
- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**
- **Upwork Developer Account** (https://developers.upwork.com/)
- **OpenAI API Key** для AI функцій

### Рекомендовані:
- **VS Code** або інший IDE
- **Postman** для тестування API
- **Redis** для кешування та черг
- **PostgreSQL** для бази даних

## Система безпеки

### **Компоненти безпеки**

#### **1. Многофакторна автентифікація (MFA)**
- **TOTP (Google Authenticator)** - часові одноразові паролі
- **SMS верифікація** - додатковий рівень захисту
- **Backup коди** - резервні коди для відновлення
- **Email верифікація** - підтвердження email адреси

#### **2. Шифрування даних**
- **Fernet шифрування** - для всіх токенів
- **bcrypt хешування** - для паролів
- **JWT токени** - для автентифікації
- **Безпечне зберігання** - всі чутливі дані зашифровані

#### **3. Моніторинг безпеки**
- **SecurityLog** - логування всіх дій
- **SecurityAlert** - сповіщення про підозрілу активність
- **Rate limiting** - захист від зловживань
- **Аудит активності** - детальні логи

#### **4. Захист від атак**
- **Блокування після невдалих спроб** - захист від брутфорс атак
- **HTTPS everywhere** - всі з'єднання захищені
- **CORS налаштування** - обмеження cross-origin запитів
- **Input validation** - валідація всіх вхідних даних

## Встановлення Docker

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

## Налаштування проекту

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

### 3. Налаштування змінних середовища
```env
# Upwork API
UPWORK_CLIENT_ID=your_client_id_here
UPWORK_CLIENT_SECRET=your_client_secret_here
UPWORK_CALLBACK_URL=http://localhost:8000/auth/upwork/callback

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# База даних
DATABASE_URL=postgresql://user:password@localhost/upwork_app

# Безпека
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Redis
REDIS_URL=redis://localhost:6379

# Налаштування
DEBUG=False
ENVIRONMENT=production
```

### 4. Налаштування Upwork API
```bash
# 1. Зареєструйтесь на https://developers.upwork.com/
# 2. Створіть новий додаток
# 3. Отримайте API ключі
# 4. Додайте ключі в .env файл
```

### 5. Налаштування OpenAI API
```bash
# 1. Зареєструйтесь на https://platform.openai.com/
# 2. Отримайте API ключ
# 3. Додайте ключ в .env файл
```

### 6. Генерація ключів безпеки
```bash
# Генерація SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Генерація ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Запуск проекту

### Локальний запуск:
```bash
# Встановлення залежностей
pip install -r requirements.txt

# Міграції бази даних
alembic upgrade head

# Запуск додатку
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker запуск:
```bash
# Збірка та запуск
docker-compose up -d

# Перевірка статусу
docker-compose ps

# Перегляд логів
docker-compose logs -f
```

### Тестування:
```bash
# Запуск тестів
pytest tests/

# Тестування безпеки
pytest tests/test_auth.py

# Інтеграційні тести
pytest tests/test_integration.py
```

## Налаштування безпеки

### 1. HTTPS сертифікати
```bash
# Для production
# Отримайте SSL сертифікат (Let's Encrypt)
sudo certbot --nginx -d your-domain.com

# Для development
# Використовуйте самопідписані сертифікати
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### 2. Налаштування CORS
```python
# В src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 3. Налаштування Rate Limiting
```python
# В src/auth/rate_limiter.py
RATE_LIMITS = {
    "login": "5/minute",
    "register": "3/hour",
    "api": "100/minute",
    "mfa": "3/minute"
}
```

### 4. Налаштування MFA
```python
# В src/auth/mfa.py
MFA_SETTINGS = {
    "totp_issuer": "Upwork Web App",
    "totp_algorithm": "sha1",
    "totp_digits": 6,
    "totp_period": 30
}
```

## Моніторинг

### 1. Логування
```bash
# Перегляд логів
tail -f logs/app.log

# Логи безпеки
tail -f logs/security.log

# Логи помилок
tail -f logs/error.log
```

### 2. Моніторинг безпеки
```bash
# Перегляд сповіщень безпеки
curl -X GET "http://localhost:8000/admin/alerts" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Перегляд логів безпеки
curl -X GET "http://localhost:8000/security/logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Моніторинг продуктивності
```bash
# Статус API
curl -X GET "http://localhost:8000/health"

# Метрики
curl -X GET "http://localhost:8000/metrics"
```

## 🧪 Тестування

### 1. Unit тести
```bash
# Тести безпеки
pytest tests/test_auth.py -v

# Тести API
pytest tests/test_api.py -v

# Тести сервісів
pytest tests/test_services.py -v
```

### 2. Інтеграційні тести
```bash
# Повний workflow
pytest tests/test_integration.py -v

# Тести безпеки
pytest tests/test_security.py -v
```

### 3. Load тести
```bash
# Тестування продуктивності
locust -f tests/load_test.py --host=http://localhost:8000
```

## Troubleshooting

### Помилки безпеки:
```bash
# Перевірка SSL сертифікатів
openssl s_client -connect your-domain.com:443

# Перевірка CORS
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-Requested-With" \
  -X OPTIONS http://localhost:8000/auth/login
```

### Помилки API:
```bash
# Перевірка Upwork API
curl -X GET "https://www.upwork.com/api/v2/search/jobs" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Перевірка OpenAI API
curl -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4","messages":[{"role":"user","content":"Hello"}]}'
```

### Помилки бази даних:
```bash
# Перевірка підключення
psql $DATABASE_URL -c "SELECT version();"

# Перевірка міграцій
alembic current
alembic history
```

## Документація

### API документація:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Документація проекту:
- **Основний план**: [PROJECT_OVERVIEW.md](../instruction/planning/PROJECT_OVERVIEW.md)
- **Завдання**: [MASTER_TASKS.md](../instruction/planning/MASTER_TASKS.md)
- **Архітектура**: [ARCHITECTURE.md](../instruction/planning/ARCHITECTURE.md)
- **API гід**: [upwork_official_api_guide.md](../instruction/analysis/upwork_official_api_guide.md)

## Важливі зауваження

### **Безпека**
- 🔐 **Шифрування токенів** - обов'язково
- 🔐 **HTTPS** - для всіх API викликів
- 🔐 **Валідація** - всіх вхідних даних
- 🔐 **Rate limiting** - для захисту від зловживань
- 🔐 **MFA** - для всіх користувачів
- 🔐 **Моніторинг** - real-time сповіщення

### **Легальність**
- ✅ **Terms of Service** - дотримуватися Upwork ToS
- ✅ **OAuth 2.0** - використовувати офіційний flow
- ✅ **User consent** - отримувати згоду користувачів
- ✅ **Data privacy** - дотримуватися GDPR

### **Масштабованість**
- 📈 **Rate limits** - кожен користувач має свої обмеження
- 📈 **Database indexing** - індекси на `user_id`
- 📈 **Caching** - кешування для зменшення API викликів
- 📈 **Monitoring** - моніторинг використання API

### **Захист від конкурентів**
- 🔒 **Повна ізоляція даних** - кожен бачить тільки свої дані
- 🔒 **Шифрування** - всі чутливі дані зашифровані
- 🔒 **Моніторинг** - відстеження підозрілої активності
- 🔒 **Аудит** - детальні логи всіх дій

---

**AI асистент завжди має рекомендувати використання офіційного API замість парсингу та дотримуватися принципів максимальної безпеки!** 🔐

---

*Останнє оновлення: 2024-12-19* 