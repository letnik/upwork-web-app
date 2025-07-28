<!--
ФАЙЛ: upwork_official_api_guide.md
ОПИС: Детальний гід по офіційному API Upwork
ПРИЗНАЧЕННЯ: Інструкції по використанню офіційного API Upwork
ЩО ЗБЕРІГАЄ: Документація API, приклади використання, налаштування
-->

# 🔗 Офіційне API Upwork: Повний гід

## 📋 Огляд

Upwork надає офіційне API для розробників, яке дозволяє отримувати доступ до даних платформи легально та безпечно.

## 🚀 Реєстрація та налаштування

### 1. Створення акаунту розробника
- **URL**: https://developers.upwork.com/
- **Процес**: Реєстрація → Створення додатку → Отримання ключів

### 2. Типи акаунтів
- **Free**: Базовий доступ з обмеженими квотами
- **Paid**: Розширений доступ з більшими лімітами
- **Enterprise**: Корпоративні рішення

## 🔑 Отримання API ключів

### Кроки реєстрації:
1. **Реєстрація на developers.upwork.com**
2. **Створення нового додатку**
3. **Налаштування OAuth 2.0**
4. **Отримання Client ID та Client Secret**
5. **Налаштування callback URL**

### Необхідні дані:
```python
# Конфігурація API
UPWORK_CLIENT_ID = "your_client_id"
UPWORK_CLIENT_SECRET = "your_client_secret"
UPWORK_CALLBACK_URL = "http://localhost:8000/callback"
```

## 📚 Встановлення бібліотеки

### Офіційна Python бібліотека:
```bash
pip install upwork
```

### Альтернативні бібліотеки:
```bash
# REST API клієнт
pip install requests

# OAuth 2.0
pip install oauthlib
```

## 🔧 Базове використання

### 1. Ініціалізація клієнта
```python
import upwork

# Створення клієнта
client = upwork.Client(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Авторизація
client.auth()
```

### 2. Пошук вакансій
```python
# Базовий пошук
jobs = client.search_jobs(
    q="python developer",
    paging=0,
    count=20
)

# Розширений пошук
jobs = client.search_jobs(
    q="python developer",
    paging=0,
    count=100,
    job_type="hourly",  # hourly, fixed
    budget_min=50,
    budget_max=200,
    skills=["python", "django"],
    category="web-development"
)
```

### 3. Отримання деталей вакансії
```python
# Отримання повної інформації про вакансію
job_details = client.get_job_details(job_id)

# Структура відповіді
{
    "id": "~0123456789012345",
    "title": "Python Developer Needed",
    "description": "We need a Python developer...",
    "budget": {
        "min": 1000,
        "max": 5000,
        "type": "fixed"
    },
    "client": {
        "id": "~0123456789012345",
        "name": "John Doe",
        "rating": 4.8,
        "reviews_count": 15
    },
    "skills": ["python", "django", "postgresql"],
    "posted_time": "2024-01-15T10:30:00Z",
    "category": "Web Development",
    "subcategory": "Web Programming",
    "experience_level": "intermediate",
    "project_length": "3-6 months",
    "hours_per_week": "10-30 hrs/week"
}
```

## 📊 Доступні API endpoints

### Jobs API
```python
# Пошук вакансій
jobs = client.search_jobs(q="query", paging=0, count=20)

# Деталі вакансії
job = client.get_job_details(job_id)

# Вакансії клієнта
client_jobs = client.get_client_jobs(client_id)

# Вакансії за категорією
category_jobs = client.get_jobs_by_category(category_id)
```

### Freelancers API
```python
# Пошук фрілансерів
freelancers = client.search_freelancers(q="python", paging=0, count=20)

# Профіль фрілансера
profile = client.get_freelancer_profile(freelancer_id)

# Портфоліо фрілансера
portfolio = client.get_freelancer_portfolio(freelancer_id)
```

### Clients API
```python
# Інформація про клієнта
client_info = client.get_client_info(client_id)

# Історія роботи клієнта
client_history = client.get_client_job_history(client_id)

# Відгуки про клієнта
client_reviews = client.get_client_reviews(client_id)
```

### Categories API
```python
# Список категорій
categories = client.get_categories()

# Підкатегорії
subcategories = client.get_subcategories(category_id)

# Вакансії в категорії
category_jobs = client.get_jobs_by_category(category_id)
```

## 🔄 OAuth 2.0 авторизація

### 1. Ініціалізація OAuth
```python
from upwork import Client

# Створення клієнта
client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Отримання URL для авторизації
auth_url = client.get_authorization_url(
    redirect_uri="http://localhost:8000/callback",
    scope=["jobs", "freelancers", "clients"]
)
```

### 2. Обробка callback
```python
# Отримання access token
access_token = client.get_access_token(
    authorization_code="code_from_callback",
    redirect_uri="http://localhost:8000/callback"
)

# Збереження токена
client.save_access_token(access_token)
```

### 3. Використання токена
```python
# Автоматичне оновлення токена
client.refresh_access_token()

# Перевірка валідності
is_valid = client.is_token_valid()
```

## 📈 Rate Limiting та квоти

### Безкоштовний план:
- **Запити на день**: 1,000
- **Запити на хвилину**: 10
- **Максимальний розмір відповіді**: 1MB

### Платний план:
- **Запити на день**: 10,000+
- **Запити на хвилину**: 100+
- **Максимальний розмір відповіді**: 10MB

### Обробка лімітів:
```python
import time

def make_api_request(client, *args, **kwargs):
    try:
        return client.search_jobs(*args, **kwargs)
    except upwork.exceptions.RateLimitExceeded:
        # Чекаємо 60 секунд при перевищенні ліміту
        time.sleep(60)
        return client.search_jobs(*args, **kwargs)
```

## 🔍 Фільтрація та сортування

### Параметри пошуку вакансій:
```python
# Базові параметри
jobs = client.search_jobs(
    q="python developer",           # Пошуковий запит
    paging=0,                      # Номер сторінки
    count=20,                      # Кількість результатів
    job_type="hourly",             # Тип роботи (hourly/fixed)
    budget_min=50,                 # Мінімальний бюджет
    budget_max=200,                # Максимальний бюджет
    skills=["python", "django"],   # Необхідні навички
    category="web-development",    # Категорія
    experience_level="intermediate", # Рівень досвіду
    posted_within=7,              # Опубліковано за останні N днів
    sort="recency"                # Сортування (recency/relevance)
)
```

### Параметри пошуку фрілансерів:
```python
# Пошук фрілансерів
freelancers = client.search_freelancers(
    q="python developer",
    paging=0,
    count=20,
    skills=["python", "django"],
    category="web-development",
    hourly_rate_min=20,
    hourly_rate_max=100,
    availability="full-time",
    location="United States"
)
```

## 📊 Обробка даних

### Структура відповіді API:
```python
# Приклад відповіді API
{
    "jobs": [
        {
            "id": "~0123456789012345",
            "title": "Python Developer",
            "description": "We need a Python developer...",
            "budget": {
                "min": 1000,
                "max": 5000,
                "type": "fixed"
            },
            "client": {
                "id": "~0123456789012345",
                "name": "John Doe",
                "rating": 4.8,
                "reviews_count": 15,
                "total_spent": 50000,
                "location": "United States"
            },
            "skills": ["python", "django", "postgresql"],
            "posted_time": "2024-01-15T10:30:00Z",
            "category": "Web Development",
            "subcategory": "Web Programming",
            "experience_level": "intermediate",
            "project_length": "3-6 months",
            "hours_per_week": "10-30 hrs/week",
            "job_type": "hourly",
            "url": "https://www.upwork.com/jobs/~0123456789012345"
        }
    ],
    "paging": {
        "total": 1500,
        "offset": 0,
        "count": 20
    }
}
```

### Парсинг відповіді:
```python
def parse_jobs_response(response):
    """Парсинг відповіді API"""
    jobs = []
    
    for job_data in response.get('jobs', []):
        job = {
            'upwork_id': job_data['id'],
            'title': job_data['title'],
            'description': job_data['description'],
            'budget_min': job_data['budget']['min'],
            'budget_max': job_data['budget']['max'],
            'budget_type': job_data['budget']['type'],
            'client_id': job_data['client']['id'],
            'client_name': job_data['client']['name'],
            'client_rating': job_data['client']['rating'],
            'client_reviews_count': job_data['client']['reviews_count'],
            'skills': job_data['skills'],
            'posted_time': job_data['posted_time'],
            'category': job_data['category'],
            'subcategory': job_data['subcategory'],
            'experience_level': job_data['experience_level'],
            'project_length': job_data['project_length'],
            'hours_per_week': job_data['hours_per_week'],
            'job_type': job_data['job_type'],
            'url': job_data['url']
        }
        jobs.append(job)
    
    return jobs
```

## 🛠️ Інтеграція з проектом

### Структура класу для API:
```python
class UpworkAPIParser:
    """Парсер з використанням офіційного API"""
    
    def __init__(self, client_id, client_secret, db_session):
        self.client = upwork.Client(client_id, client_secret)
        self.db = db_session
        self._authenticate()
    
    def _authenticate(self):
        """Авторизація в API"""
        try:
            self.client.auth()
        except Exception as e:
            logger.error(f"Помилка авторизації: {e}")
            raise
    
    def search_jobs(self, query, max_results=100):
        """Пошук вакансій через API"""
        jobs = []
        offset = 0
        count_per_request = 20
        
        while len(jobs) < max_results:
            try:
                response = self.client.search_jobs(
                    q=query,
                    paging=offset,
                    count=count_per_request
                )
                
                if not response.get('jobs'):
                    break
                
                parsed_jobs = self._parse_jobs(response['jobs'])
                jobs.extend(parsed_jobs)
                
                offset += count_per_request
                
                # Затримка між запитами
                time.sleep(1)
                
            except upwork.exceptions.RateLimitExceeded:
                logger.warning("Перевищення ліміту запитів, чекаємо...")
                time.sleep(60)
            except Exception as e:
                logger.error(f"Помилка API запиту: {e}")
                break
        
        return jobs[:max_results]
    
    def _parse_jobs(self, jobs_data):
        """Парсинг даних вакансій"""
        parsed_jobs = []
        
        for job_data in jobs_data:
            job = Job(
                upwork_id=job_data['id'],
                title=job_data['title'],
                description=job_data['description'],
                budget_min=job_data['budget']['min'],
                budget_max=job_data['budget']['max'],
                skills=json.dumps(job_data['skills']),
                category=job_data['category'],
                subcategory=job_data['subcategory'],
                client_country=job_data['client'].get('location'),
                client_rating=job_data['client']['rating'],
                client_reviews_count=job_data['client']['reviews_count'],
                posted_time=datetime.fromisoformat(job_data['posted_time'].replace('Z', '+00:00')),
                job_type=job_data['job_type'],
                experience_level=job_data['experience_level'],
                project_length=job_data['project_length'],
                hours_per_week=job_data['hours_per_week'],
                url=job_data['url']
            )
            parsed_jobs.append(job)
        
        return parsed_jobs
    
    def save_jobs_to_db(self, jobs):
        """Збереження вакансій в базу даних"""
        for job in jobs:
            # Перевірка на дублікати
            existing_job = self.db.query(Job).filter(
                Job.upwork_id == job.upwork_id
            ).first()
            
            if not existing_job:
                self.db.add(job)
        
        self.db.commit()
        logger.info(f"Збережено {len(jobs)} нових вакансій")
```

## 🔒 Безпека та найкращі практики

### 1. Збереження ключів
```python
# Використання змінних середовища
import os

UPWORK_CLIENT_ID = os.getenv('UPWORK_CLIENT_ID')
UPWORK_CLIENT_SECRET = os.getenv('UPWORK_CLIENT_SECRET')
```

### 2. Обробка помилок
```python
def safe_api_call(func, *args, **kwargs):
    """Безпечний виклик API з обробкою помилок"""
    try:
        return func(*args, **kwargs)
    except upwork.exceptions.RateLimitExceeded:
        logger.warning("Перевищення ліміту запитів")
        time.sleep(60)
        return func(*args, **kwargs)
    except upwork.exceptions.AuthenticationError:
        logger.error("Помилка авторизації")
        raise
    except upwork.exceptions.APIError as e:
        logger.error(f"Помилка API: {e}")
        raise
    except Exception as e:
        logger.error(f"Невідома помилка: {e}")
        raise
```

### 3. Логування
```python
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upwork_api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('upwork_api')
```

## 📊 Моніторинг та метрики

### Відстеження використання API:
```python
class APIMonitor:
    """Моніторинг використання API"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
    
    def track_request(self, success=True):
        """Відстеження запиту"""
        self.request_count += 1
        if not success:
            self.error_count += 1
    
    def get_stats(self):
        """Отримання статистики"""
        elapsed_time = time.time() - self.start_time
        return {
            'total_requests': self.request_count,
            'error_rate': self.error_count / self.request_count if self.request_count > 0 else 0,
            'requests_per_minute': self.request_count / (elapsed_time / 60),
            'uptime_minutes': elapsed_time / 60
        }
```

## 🚀 Приклад повної інтеграції

```python
# main.py
from upwork_api_parser import UpworkAPIParser
from database import get_db_session
import os

def main():
    # Отримання сесії БД
    db_session = get_db_session()
    
    # Створення парсера
    parser = UpworkAPIParser(
        client_id=os.getenv('UPWORK_CLIENT_ID'),
        client_secret=os.getenv('UPWORK_CLIENT_SECRET'),
        db_session=db_session
    )
    
    # Пошук вакансій
    search_queries = [
        "python developer",
        "django developer", 
        "flask developer",
        "web developer"
    ]
    
    for query in search_queries:
        try:
            jobs = parser.search_jobs(query, max_results=50)
            parser.save_jobs_to_db(jobs)
            print(f"Знайдено {len(jobs)} вакансій для '{query}'")
        except Exception as e:
            print(f"Помилка при пошуку '{query}': {e}")

if __name__ == "__main__":
    main()
```

## 📋 Контрольний список

### Перед використанням:
- [ ] Реєстрація на developers.upwork.com
- [ ] Створення додатку
- [ ] Отримання API ключів
- [ ] Налаштування OAuth 2.0
- [ ] Встановлення бібліотеки upwork
- [ ] Тестування підключення

### При розробці:
- [ ] Обробка rate limiting
- [ ] Логування помилок
- [ ] Збереження токенів
- [ ] Валідація даних
- [ ] Тестування API

### Для продакшену:
- [ ] Моніторинг використання
- [ ] Резервне копіювання
- [ ] Обробка збоїв
- [ ] Масштабування
- [ ] Документація

## 🎯 Висновки

### Переваги офіційного API:
- ✅ **Легальний доступ** - повна відповідність ToS
- ✅ **Стабільна робота** - гарантована доступність
- ✅ **Структуровані дані** - JSON формат
- ✅ **Висока швидкість** - оптимізовані запити
- ✅ **Підтримка** - офіційна документація

### Недоліки:
- ❌ **Обмежені квоти** - ліміти на запити
- ❌ **Платний доступ** - для великих обсягів
- ❌ **Реєстрація** - потребує створення акаунту
- ❌ **Обмежений функціонал** - не всі дані доступні

### Рекомендації:
1. **Почніть з безкоштовного плану** для тестування
2. **Використовуйте rate limiting** для стабільності
3. **Зберігайте токени** для повторного використання
4. **Моніторте використання** для оптимізації
5. **Обробляйте помилки** для надійності

---
*Дата: 2024-12-19*
*Статус: Завершено* 