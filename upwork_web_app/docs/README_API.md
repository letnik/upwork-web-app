# 🚀 Upwork Web App - API Підхід

## 🎯 Огляд

Цей проект реалізує повноцінний веб-додаток для роботи з Upwork через **офіційний API**, що забезпечує:
- ✅ **Легальний доступ** - офіційно підтримується
- ✅ **AI інтеграція** - генерація відгуків та розумна фільтрація
- ✅ **Автоматизація** - автоматичні відгуки та ведення переписки
- ✅ **Веб-інтерфейс** - зручний UI для користувачів
- ✅ **Масштабованість** - підтримка багатокористувацької системи

## 📋 Швидкий старт

### 1. Реєстрація на Upwork Developers

1. **Перейдіть на** https://developers.upwork.com/
2. **Створіть акаунт** або увійдіть в існуючий
3. **Створіть додаток** в розділі "My Apps"
4. **Отримайте API ключі** та Access Token

### 2. Налаштування конфігурації

Створіть файл `api_config.json`:

```json
{
  "api_credentials": {
    "api_key": "your_api_key_here",
    "api_secret": "your_api_secret_here",
    "access_token": "your_access_token_here",
    "access_token_secret": "your_access_token_secret_here"
  },
  "search_settings": {
    "max_results_per_query": 50,
    "delay_between_requests": 1.0,
    "retry_attempts": 3
  },
  "queries": [
    "python developer",
    "web designer",
    "data scientist"
  ]
}
```

### 3. Запуск парсера

```bash
# Тестування API
python3 test_api_parser.py

# Інтеграційний тест
python3 test_api_integration.py

# Запуск основного парсера
python3 src/main.py
```

## 🏗️ Архітектура

### Основні компоненти:

```
src/
├── auth/                       # Система авторизації
│   ├── models.py               # Модель користувача
│   ├── oauth.py               # OAuth 2.0 логіка
│   └── middleware.py          # Auth middleware
├── api/v1/                     # API endpoints
│   ├── auth.py                # Auth endpoints
│   ├── jobs.py                # Jobs endpoints
│   ├── applications.py        # Applications endpoints
│   └── messages.py            # Messages endpoints
├── services/                   # Бізнес-логіка
│   ├── upwork_service.py      # Upwork API service
│   ├── ai_service.py          # AI service
│   └── notification_service.py
├── config/
│   ├── settings.py            # Загальні налаштування
│   └── api_config.py          # API конфігурація
├── database/
│   ├── models.py              # Моделі БД
│   └── connection.py          # Підключення БД
└── utils/
    ├── logger.py              # Логування
    ├── token_manager.py       # Управління токенами
    └── encryption.py          # Шифрування
```

### API Сервіс (`UpworkService`):

```python
from src.services.upwork_service import UpworkService
from src.auth.models import User

# Створення сервісу
service = UpworkService()

# Отримання вакансій користувача
user = get_current_user()
jobs = await service.get_user_jobs(user, query="python developer")

# Відправка відгуку
proposal_data = {
    "cover_letter": "Детальний опис досвіду...",
    "bid_amount": 1000,
    "estimated_hours": 40
}
result = await service.submit_proposal(user, job_id, proposal_data)
```

## 🔧 Конфігурація

### Варіант 1: Змінні середовища

```env
# Upwork API
UPWORK_CLIENT_ID=your_client_id
UPWORK_CLIENT_SECRET=your_client_secret
UPWORK_REDIRECT_URI=http://localhost:8000/auth/upwork/callback

# Шифрування
ENCRYPTION_KEY=your_encryption_key_base64

# База даних
DATABASE_URL=postgresql://user:password@localhost/upwork_web_app

# JWT
SECRET_KEY=your_jwt_secret_key
```

### Варіант 2: Змінні середовища

```env
UPWORK_API_KEY=your_api_key
UPWORK_API_SECRET=your_api_secret
UPWORK_ACCESS_TOKEN=your_access_token
UPWORK_ACCESS_TOKEN_SECRET=your_access_token_secret
UPWORK_MAX_RESULTS=50
UPWORK_DELAY=1.0
UPWORK_RETRY_ATTEMPTS=3
UPWORK_QUERIES=python developer,web designer,data scientist
```

## 📊 API Endpoints

### Авторизація:
```
POST /auth/register          # Реєстрація користувача
POST /auth/login            # Вхід користувача
GET  /auth/upwork/connect   # Підключення Upwork акаунту
POST /auth/upwork/callback  # OAuth callback
```

### Вакансії:
```
GET  /jobs                  # Отримання вакансій користувача
GET  /jobs/{job_id}        # Деталі вакансії
POST /jobs/search          # Пошук вакансій
```

### Відгуки:
```
GET  /applications          # Отримання відгуків
POST /applications          # Створення відгуку
PUT  /applications/{id}     # Оновлення відгуку
```

### Повідомлення:
```
GET  /messages              # Отримання повідомлень
POST /messages              # Відправка повідомлення
```

## 🔍 Структура даних

### Вхідні дані API:
```json
{
  "id": "~0123456789abcdef",
  "title": "Python Developer Needed",
  "snippet": "We need a Python developer...",
  "budget": 1000.0,
  "hourly_rate": 25.0,
  "skills": ["Python", "Web Scraping"],
  "category2": "Web Development",
  "subcategory2": "Python",
  "client": {
    "location": {
      "country": "United States"
    },
    "feedback": 4.8,
    "reviews_count": 15
  },
  "date_created": "2024-12-19T10:00:00+0000",
  "type": "fixed",
  "contractor_tier": "intermediate",
  "duration": "1-3 months",
  "workload": "10-30 hrs/week",
  "team_size": "1-9"
}
```

### Вихідні дані парсера:
```python
{
    'upwork_id': '~0123456789abcdef',
    'title': 'Python Developer Needed',
    'description': 'We need a Python developer...',
    'budget_min': 1000.0,
    'budget_max': 1000.0,
    'hourly_rate_min': 25.0,
    'hourly_rate_max': 25.0,
    'skills': 'Python, Web Scraping',
    'category': 'Web Development',
    'subcategory': 'Python',
    'client_country': 'United States',
    'client_rating': 4.8,
    'client_reviews_count': 15,
    'posted_time': datetime(2024, 12, 19, 10, 0),
    'job_type': 'Fixed',
    'experience_level': 'intermediate',
    'project_length': '1-3 months',
    'hours_per_week': '10-30 hrs/week',
    'team_size': '1-9',
    'url': 'https://www.upwork.com/jobs/~0123456789abcdef',
    'created_at': datetime.now()
}
```

## ⚠️ Обмеження API

### Rate Limiting:
- **60 запитів за хвилину** для пошуку
- **120 запитів за хвилину** для деталей
- **Автоматичне відновлення** через 1 хвилину

### Квоти:
- **Безкоштовний план**: 1000 запитів/місяць
- **Платний план**: від $10/місяць за додаткові запити

### Обмеження результатів:
- **Максимум 100** результатів за запит
- **Пагінація** для отримання більшої кількості

## 🧪 Тестування

### Базовий тест:
```bash
python3 test_api_parser.py
```

### Інтеграційний тест:
```bash
python3 test_api_integration.py
```

### Тест з реальними credentials:
```python
from src.parsers.upwork_api_parser import UpworkAPIParser

parser = UpworkAPIParser(
    api_key="your_real_api_key",
    api_secret="your_real_api_secret",
    access_token="your_real_access_token",
    access_token_secret="your_real_access_token_secret"
)

jobs = parser.search_jobs("python developer", max_results=10)
print(f"Знайдено {len(jobs)} вакансій")
```

## 🛠️ Troubleshooting

### Помилка 401 Unauthorized:
- ✅ Перевірте правильність API ключів
- ✅ Перевірте Access Token
- ✅ Переконайтесь що додаток активний

### Помилка 429 Too Many Requests:
- ✅ Зменшіть частоту запитів
- ✅ Додайте затримки між запитами
- ✅ Перевірте ліміти API

### Помилка 403 Forbidden:
- ✅ Перевірте права доступу додатку
- ✅ Переконайтесь що API активний
- ✅ Зверніться в підтримку Upwork

## 📈 Моніторинг

### Перевірка квот:
1. Перейдіть на https://developers.upwork.com/
2. Виберіть ваш додаток
3. Перегляньте розділ "Usage"

### Логування:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"API запит: {url}")
logger.info(f"Відповідь: {response.status_code}")
```

## 🎯 Переваги API підходу

### Порівняно з веб-скрапінгом:
- ✅ **Обхід Cloudflare** - прямий доступ
- ✅ **Легальність** - офіційна підтримка
- ✅ **Стабільність** - без блокувань
- ✅ **Швидкість** - без обмежень браузера
- ✅ **Структурованість** - JSON формат

### Порівняно з Selenium:
- ✅ **Швидкість** - в 10-100 разів швидше
- ✅ **Ресурси** - мінімальне використання CPU/RAM
- ✅ **Стабільність** - без залежності від браузера
- ✅ **Масштабованість** - легко масштабувати

## 📚 Документація

- [API Setup Guide](API_SETUP_GUIDE.md) - детальна інструкція налаштування
- [API Next Steps](API_NEXT_STEPS.md) - план наступних кроків
- [PARSING_STRATEGY.md](PARSING_STRATEGY.md) - стратегія парсингу

## 🤝 Внесок

1. **Fork** репозиторій
2. **Створіть** feature branch
3. **Зробіть** зміни
4. **Додайте** тести
5. **Створіть** Pull Request

## 📄 Ліцензія

MIT License - дивіться [LICENSE](LICENSE) файл для деталей.

---
*Дата: 2024-12-19*
*Статус: Готово до використання* 