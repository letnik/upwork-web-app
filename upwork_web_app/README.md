# 🚀 Upwork Parser - API Edition

## 🎯 Огляд

Парсер вакансій з Upwork з використанням **офіційного API**. Забезпечує легальний, швидкий та стабільний доступ до даних платформи.

## ✨ Особливості

- ✅ **Офіційний API** - легальний доступ до даних
- ✅ **Обхід Cloudflare** - прямий доступ без блокувань
- ✅ **Структуровані дані** - JSON формат
- ✅ **Висока швидкість** - без обмежень браузера
- ✅ **Стабільна робота** - без блокувань
- ✅ **Інтеграція з БД** - збереження результатів
- ✅ **Логування** - детальний моніторинг
- ✅ **Експорт даних** - Excel, CSV, JSON

## 🚀 Швидкий старт

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
python3 tests/test_api_parser.py

# Інтеграційний тест
python3 tests/test_api_integration.py

# Запуск основного парсера
python3 src/main.py
```

## 🏗️ Архітектура

```
upwork_web_app/
├── src/
│   ├── parsers/
│   │   ├── upwork_api_parser.py    # API парсер
│   │   ├── upwork_analyzer.py      # Аналізатор
│   │   └── __init__.py
│   ├── config/
│   │   ├── api_config.py           # API конфігурація
│   │   ├── settings.py             # Загальні налаштування
│   │   └── logging_config.py       # Логування
│   ├── database/
│   │   ├── models.py               # Моделі БД
│   │   └── connection.py           # Підключення БД
│   └── utils/
│       ├── logger.py               # Логування
│       └── exporter.py             # Експорт даних
├── tests/
│   ├── test_api_parser.py          # Тест API парсера
│   └── test_api_integration.py     # Інтеграційний тест
├── docs/
│   ├── API_SETUP_GUIDE.md         # Інструкція налаштування
│   └── README_API.md              # Документація API
├── api_config.json                 # Конфігурація API
└── README.md                      # Цей файл
```

## 🔧 Використання

### Базовий приклад:

```python
from src.parsers.upwork_api_parser import UpworkAPIParser

# Створення парсера
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

## 📊 API Endpoints

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

### Базові тести:
```bash
# Тест API парсера
python3 tests/test_api_parser.py

# Інтеграційний тест
python3 tests/test_api_integration.py
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

## 📚 Документація

- [API Setup Guide](docs/API_SETUP_GUIDE.md) - детальна інструкція налаштування
- [README API](docs/README_API.md) - огляд API підходу
- [API Next Steps](API_NEXT_STEPS.md) - план наступних кроків

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
