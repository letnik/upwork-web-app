# Налаштування API Upwork

## Переваги офіційного API

✅ **Обхід Cloudflare** - прямий доступ до даних  
✅ **Легальний доступ** - офіційно підтримується  
✅ **Структуровані дані** - JSON формат  
✅ **Висока швидкість** - без обмежень браузера  
✅ **Стабільна робота** - без блокувань  

## Кроки налаштування

### 1. Реєстрація на Upwork Developers

1. **Перейдіть на** https://developers.upwork.com/
2. **Створіть акаунт** або увійдіть в існуючий
3. **Підтвердіть email** та налаштуйте профіль

### 2. Створення додатку

1. **Перейдіть в розділ "My Apps"**
2. **Натисніть "Create App"**
3. **Заповніть форму:**
   - **App Name**: `Upwork Parser`
   - **App Description**: `Parser for job data collection`
   - **App Type**: `Web`
   - **Callback URL**: `http://localhost:8000/auth/upwork/callback`

### 3. Отримання API ключів

Після створення додатку ви отримаєте:
- **API Key** (Consumer Key)
- **API Secret** (Consumer Secret)

### 4. Отримання Access Token

1. **Перейдіть в розділ "My Apps"**
2. **Виберіть ваш додаток**
3. **Натисніть "Generate Access Token"**
4. **Авторизуйтесь через Upwork**
5. **Скопіюйте:**
   - **Access Token**
   - **Access Token Secret**

## Налаштування credentials

### Варіант 1: Через файл конфігурації

Створіть файл `api_config.json`:

```json
{
  "api_credentials": {
    "api_key": "your_api_key_here",
    "api_secret": "your_api_secret_here", 
    "access_token": "your_access_token_here",
    "access_token_secret": "your_access_token_secret_here"
  },
  "search_queries": [
    "python developer",
    "web designer", 
    "data scientist",
    "React developer",
    "UI/UX designer"
  ],
  "max_results_per_query": 50,
  "rate_limiting": {
    "requests_per_minute": 60,
    "delay_between_requests": 1.0
  }
}
```

### Варіант 2: Через змінні середовища

Додайте в `.env` файл:

```env
UPWORK_API_KEY=your_api_key_here
UPWORK_API_SECRET=your_api_secret_here
UPWORK_ACCESS_TOKEN=your_access_token_here
UPWORK_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

## Використання API парсера

### Базовий приклад:

```python
from src.parsers.upwork_api_parser import UpworkAPIParser

# Створюємо парсер
parser = UpworkAPIParser(
    api_key="your_api_key",
    api_secret="your_api_secret", 
    access_token="your_access_token",
    access_token_secret="your_access_token_secret"
)

# Пошук вакансій
jobs = parser.search_jobs("python developer", max_results=50)

# Парсинг даних
for job in jobs:
    parsed_job = parser.parse_job_data(job)
    print(f"Назва: {parsed_job['title']}")
    print(f"Бюджет: ${parsed_job['budget_min']}-${parsed_job['budget_max']}")
```

### Повний приклад з БД:

```python
from src.parsers.upwork_api_parser import UpworkAPIParser
from src.database.connection import db_manager

# Отримуємо сесію БД
db_session = db_manager.SessionLocal()

# Створюємо парсер
parser = UpworkAPIParser(
    api_key="your_api_key",
    api_secret="your_api_secret",
    access_token="your_access_token", 
    access_token_secret="your_access_token_secret"
)

# Запускаємо сесію парсингу
result = parser.run_parsing_session(
    search_queries=["python developer", "web designer"],
    max_results_per_query=50,
    db_session=db_session
)

print(f"Результат: {result}")
```

## API Endpoints

### Пошук вакансій:
```
GET /api/v2/search/jobs
```

**Параметри:**
- `q` - пошуковий запит
- `paging` - зміщення (для пагінації)
- `count` - кількість результатів (макс 100)
- `sort` - сортування

### Деталі вакансії:
```
GET /api/v2/jobs/{job_id}
```

## Структура відповіді API

```json
{
  "jobs": [
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
  ]
}
```

## Обмеження API

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

## Тестування API

### 1. Тест без credentials:
```bash
python3 test_api_parser.py
```

### 2. Тест з credentials:
```python
# Замініть на реальні значення
api_key = "your_real_api_key"
api_secret = "your_real_api_secret"
access_token = "your_real_access_token"
access_token_secret = "your_real_access_token_secret"

parser = UpworkAPIParser(api_key, api_secret, access_token, access_token_secret)
jobs = parser.search_jobs("python developer", max_results=10)
print(f"Знайдено {len(jobs)} вакансій")
```

## Troubleshooting

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

## Моніторинг використання

### Перевірка квот:
1. Перейдіть на https://developers.upwork.com/
2. Виберіть ваш додаток
3. Перегляньте розділ "Usage"

### Логування:
```python
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Логування запитів
logger.info(f"API запит: {url}")
logger.info(f"Відповідь: {response.status_code}")
```

## Рекомендації

### Для розробки:
1. **Почніть з тестування** - перевірте API без БД
2. **Використовуйте мокові дані** - для розробки логіки
3. **Додайте логування** - для діагностики
4. **Тестуйте rate limiting** - не перевищуйте ліміти

### Для продакшену:
1. **Використовуйте змінні середовища** - не хардкодьте credentials
2. **Додайте retry логіку** - для обробки помилок
3. **Моніторте використання** - відстежуйте квоти
4. **Кешуйте результати** - зменшіть кількість запитів

---
*Дата: 2024-12-19*
*Статус: Готово до використання* 