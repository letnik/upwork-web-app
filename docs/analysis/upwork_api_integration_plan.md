# План інтеграції з Upwork API

## Огляд

Детальний план інтеграції з офіційним Upwork API для створення повноцінного веб-додатку з автоматизацією роботи з вакансіями, відгуками та перепискою.

## Основні цілі

### 1. **Офіційна інтеграція**
- Реєстрація на developers.upwork.com
- Налаштування OAuth 2.0 авторизації
- Створення UpworkAPIClient
- Безпечний доступ до даних

### 2. **Автоматизація роботи**
- Пошук та фільтрація вакансій
- AI генерація персоналізованих відгуків
- Автоматичне відправлення відгуків
- Ведення переписки з клієнтами

### 3. **Аналітика та оптимізація**
- Відстеження ефективності відгуків
- A/B тестування різних стратегій
- Прогнозування успішності
- Оптимізація процесів

## Етапи інтеграції

### **Етап 1: Реєстрація та налаштування (1 тиждень)**

#### 1.1 Реєстрація на developers.upwork.com
- Створення акаунту розробника
- Заповнення профілю компанії
- Опис плануваного додатку
- Отримання схвалення від Upwork

#### 1.2 Створення додатку
```json
{
  "app_name": "Upwork Automation Suite",
  "description": "AI-powered automation tool for Upwork freelancers",
  "website": "https://your-app-domain.com",
  "callback_url": "http://localhost:8000/auth/upwork/callback",
  "scopes": [
    "jobs:read",
    "jobs:write", 
    "freelancers:read",
    "clients:read",
    "messages:read",
    "messages:write"
  ]
}
```

#### 1.3 Отримання API ключів
```python
# Конфігурація API
UPWORK_CLIENT_ID = "your_client_id"
UPWORK_CLIENT_SECRET = "your_client_secret"
UPWORK_CALLBACK_URL = "http://localhost:8000/auth/upwork/callback"
```

### **Етап 2: OAuth 2.0 авторизація (1 тиждень)**

#### 2.1 Створення OAuth2Manager
```python
class OAuth2Manager:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = UPWORK_CALLBACK_URL
    
    def get_authorization_url(self, state=None):
        """Генерація URL для авторизації"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(UPWORK_SCOPES)
        }
        if state:
            params['state'] = state
        
        return f"{UPWORK_AUTH_URL}?{urlencode(params)}"
    
    def get_access_token(self, authorization_code):
        """Отримання access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(UPWORK_TOKEN_URL, data=data)
        return response.json()
    
    def refresh_token(self, refresh_token):
        """Оновлення access token"""
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(UPWORK_TOKEN_URL, data=data)
        return response.json()
```

#### 2.2 Веб-інтерфейс для авторизації
```python
@app.route('/oauth/authorize')
def oauth_authorize():
    """Початок OAuth процесу"""
    state = generate_state()
    session['oauth_state'] = state
    
    auth_url = oauth_manager.get_authorization_url(state)
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    """Обробка OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    if state != session.get('oauth_state'):
        return 'Invalid state parameter', 400
    
    try:
        token_data = oauth_manager.get_access_token(code)
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data['refresh_token']
        
        return redirect('/dashboard')
    except Exception as e:
        return f'OAuth error: {e}', 400
```

### **Етап 3: UpworkAPIClient (2 тижні)**

#### 3.1 Створення основного клієнта
```python
class UpworkAPIClient:
    def __init__(self, access_token=None):
        self.access_token = access_token
        self.base_url = "https://api.upwork.com/api/v2"
        self.session = requests.Session()
        
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })
    
    def search_jobs(self, query, **filters):
        """Пошук вакансій"""
        endpoint = f"{self.base_url}/jobs/search"
        
        params = {
            'q': query,
            'paging': 0,
            'count': 20
        }
        params.update(filters)
        
        response = self.session.get(endpoint, params=params)
        return response.json()
    
    def get_job_details(self, job_id):
        """Отримання деталей вакансії"""
        endpoint = f"{self.base_url}/jobs/{job_id}"
        response = self.session.get(endpoint)
        return response.json()
    
    def submit_proposal(self, job_id, proposal_data):
        """Відправка відгуку на вакансію"""
        endpoint = f"{self.base_url}/jobs/{job_id}/proposals"
        response = self.session.post(endpoint, json=proposal_data)
        return response.json()
    
    def get_messages(self, job_id=None):
        """Отримання повідомлень"""
        endpoint = f"{self.base_url}/messages"
        params = {}
        if job_id:
            params['job_id'] = job_id
        
        response = self.session.get(endpoint, params=params)
        return response.json()
    
    def send_message(self, message_data):
        """Відправка повідомлення"""
        endpoint = f"{self.base_url}/messages"
        response = self.session.post(endpoint, json=message_data)
        return response.json()
```

#### 3.2 Розширені методи
```python
class UpworkAPIClient:
    def get_client_info(self, client_id):
        """Інформація про клієнта"""
        endpoint = f"{self.base_url}/clients/{client_id}"
        response = self.session.get(endpoint)
        return response.json()
    
    def get_freelancer_profile(self, freelancer_id):
        """Профіль фрілансера"""
        endpoint = f"{self.base_url}/freelancers/{freelancer_id}"
        response = self.session.get(endpoint)
        return response.json()
    
    def get_categories(self):
        """Список категорій"""
        endpoint = f"{self.base_url}/categories"
        response = self.session.get(endpoint)
        return response.json()
    
    def get_skills(self):
        """Список навичок"""
        endpoint = f"{self.base_url}/skills"
        response = self.session.get(endpoint)
        return response.json()
```

### **Етап 4: AI інтеграція (2 тижні)**

#### 4.1 AIGenerator для відгуків
```python
class AIGenerator:
    def __init__(self, openai_api_key):
        self.openai_client = OpenAI(api_key=openai_api_key)
    
    def generate_proposal(self, job_data, freelancer_profile):
        """Генерація персоналізованого відгуку"""
        prompt = self._create_proposal_prompt(job_data, freelancer_profile)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert freelancer writing proposals for Upwork jobs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _create_proposal_prompt(self, job_data, freelancer_profile):
        """Створення промпту для генерації"""
        return f"""
        Job Title: {job_data['title']}
        Job Description: {job_data['description']}
        Budget: {job_data['budget']}
        Required Skills: {', '.join(job_data['skills'])}
        
        Freelancer Profile:
        - Experience: {freelancer_profile['experience']}
        - Skills: {', '.join(freelancer_profile['skills'])}
        - Portfolio: {freelancer_profile['portfolio']}
        
        Write a personalized proposal that:
        1. Addresses the client's specific needs
        2. Highlights relevant experience
        3. Proposes a clear solution
        4. Shows understanding of the project
        5. Includes a call to action
        
        Keep it professional, concise, and compelling.
        """
    
    def generate_message_response(self, message_content, context):
        """Генерація відповіді на повідомлення"""
        prompt = f"""
        Client Message: {message_content}
        Context: {context}
        
        Generate a professional and helpful response that:
        1. Addresses the client's question/concern
        2. Shows expertise and professionalism
        3. Maintains positive communication
        4. Moves the conversation forward
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional freelancer communicating with clients."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.6
        )
        
        return response.choices[0].message.content
```

#### 4.2 SmartFilter для вакансій
```python
class SmartFilter:
    def __init__(self, ai_generator):
        self.ai_generator = ai_generator
    
    def analyze_job_suitability(self, job_data, freelancer_profile):
        """Аналіз підходящості вакансії"""
        prompt = f"""
        Job: {job_data['title']}
        Description: {job_data['description']}
        Budget: {job_data['budget']}
        Skills: {job_data['skills']}
        
        Freelancer Profile:
        - Skills: {freelancer_profile['skills']}
        - Experience: {freelancer_profile['experience']}
        - Rate: {freelancer_profile['hourly_rate']}
        
        Analyze if this job is suitable for the freelancer.
        Consider:
        1. Skill match (0-10)
        2. Budget appropriateness (0-10)
        3. Project complexity match (0-10)
        4. Client rating and history
        5. Overall recommendation (Yes/No)
        
        Return JSON format:
        {{
            "skill_match": 8,
            "budget_match": 7,
            "complexity_match": 9,
            "client_rating": 4.8,
            "recommendation": "Yes",
            "reasoning": "Detailed explanation..."
        }}
        """
        
        response = self.ai_generator.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert job matching analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    def filter_jobs(self, jobs, freelancer_profile, min_score=7):
        """Фільтрація вакансій за критеріями"""
        suitable_jobs = []
        
        for job in jobs:
            analysis = self.analyze_job_suitability(job, freelancer_profile)
            
            if analysis['recommendation'] == 'Yes':
                job['ai_analysis'] = analysis
                suitable_jobs.append(job)
        
# Сортування за загальним балом
        suitable_jobs.sort(
            key=lambda x: (x['ai_analysis']['skill_match'] + 
                          x['ai_analysis']['budget_match'] + 
                          x['ai_analysis']['complexity_match']) / 3,
            reverse=True
        )
        
        return suitable_jobs
```

### **Етап 5: Автоматизація відгуків (2 тижні)**

#### 5.1 ApplicationService
```python
class ApplicationService:
    def __init__(self, api_client, ai_generator, smart_filter):
        self.api_client = api_client
        self.ai_generator = ai_generator
        self.smart_filter = smart_filter
        self.db = Database()
    
    def auto_apply_to_jobs(self, search_queries, freelancer_profile):
        """Автоматичне відгукання на вакансії"""
        for query in search_queries:
            try:
# Пошук вакансій
                jobs = self.api_client.search_jobs(query)
                
# Фільтрація підходящих
                suitable_jobs = self.smart_filter.filter_jobs(
                    jobs['jobs'], 
                    freelancer_profile
                )
                
# Відгукання на топ вакансії
                for job in suitable_jobs[:5]:  # Топ 5 вакансій
                    self.apply_to_job(job, freelancer_profile)
                    
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
    
    def apply_to_job(self, job, freelancer_profile):
        """Відгукання на конкретну вакансію"""
        try:
# Генерація відгуку
            proposal_text = self.ai_generator.generate_proposal(
                job, 
                freelancer_profile
            )
            
# Підготовка даних для відправки
            proposal_data = {
                'cover_letter': proposal_text,
                'bid_amount': self._calculate_bid_amount(job, freelancer_profile),
                'estimated_duration': self._estimate_duration(job),
                'attachments': []
            }
            
# Відправка через API
            response = self.api_client.submit_proposal(
                job['id'], 
                proposal_data
            )
            
# Збереження в базу даних
            self.db.save_application({
                'job_id': job['id'],
                'proposal_text': proposal_text,
                'bid_amount': proposal_data['bid_amount'],
                'status': 'submitted',
                'submitted_at': datetime.now(),
                'ai_generated': True
            })
            
            logger.info(f"Successfully applied to job {job['id']}")
            
        except Exception as e:
            logger.error(f"Error applying to job {job['id']}: {e}")
    
    def _calculate_bid_amount(self, job, freelancer_profile):
        """Розрахунок суми пропозиції"""
        if job['budget']['type'] == 'fixed':
# Для фіксованих проектів
            base_amount = job['budget']['max']
# Адаптація під досвід
            experience_multiplier = min(1.2, 1 + (freelancer_profile['experience_years'] * 0.1))
            return int(base_amount * experience_multiplier)
        else:
# Для погодинних проектів
            return freelancer_profile['hourly_rate']
    
    def _estimate_duration(self, job):
        """Оцінка тривалості проекту"""
# Логіка оцінки на основі опису та складності
        description_length = len(job['description'])
        skills_count = len(job['skills'])
        
        if description_length < 500:
            return "1-3 days"
        elif description_length < 1000:
            return "1-2 weeks"
        else:
            return "2-4 weeks"
```

### **Етап 6: Ведення переписки (2 тижні)**

#### 6.1 MessagingService
```python
class MessagingService:
    def __init__(self, api_client, ai_generator):
        self.api_client = api_client
        self.ai_generator = ai_generator
        self.db = Database()
    
    def auto_respond_to_messages(self):
        """Автоматичні відповіді на повідомлення"""
        try:
# Отримання нових повідомлень
            messages = self.api_client.get_messages()
            
            for message in messages['messages']:
                if not self._is_responded(message['id']):
                    response = self._generate_response(message)
                    self._send_response(message, response)
                    
        except Exception as e:
            logger.error(f"Error processing messages: {e}")
    
    def _generate_response(self, message):
        """Генерація відповіді на повідомлення"""
        context = self._get_message_context(message)
        
        return self.ai_generator.generate_message_response(
            message['content'],
            context
        )
    
    def _get_message_context(self, message):
        """Отримання контексту повідомлення"""
# Отримання інформації про проект та клієнта
        job_info = self.api_client.get_job_details(message['job_id'])
        client_info = self.api_client.get_client_info(message['client_id'])
        
        return {
            'job_title': job_info['title'],
            'client_name': client_info['name'],
            'client_rating': client_info['rating'],
            'project_budget': job_info['budget'],
            'message_history': self._get_message_history(message['job_id'])
        }
    
    def _send_response(self, original_message, response_text):
        """Відправка відповіді"""
        message_data = {
            'job_id': original_message['job_id'],
            'content': response_text,
            'type': 'response'
        }
        
        try:
            result = self.api_client.send_message(message_data)
            
# Збереження в базу даних
            self.db.save_message({
                'original_message_id': original_message['id'],
                'response_text': response_text,
                'sent_at': datetime.now(),
                'ai_generated': True
            })
            
            logger.info(f"Response sent to message {original_message['id']}")
            
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    def _is_responded(self, message_id):
        """Перевірка чи вже відповіли на повідомлення"""
        return self.db.check_message_response(message_id)
    
    def _get_message_history(self, job_id):
        """Отримання історії повідомлень для проекту"""
        messages = self.api_client.get_messages(job_id=job_id)
        return messages['messages'][-5:]  # Останні 5 повідомлень
```

## База даних

### Схема таблиць
```sql
-- Таблиця вакансій
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    upwork_id VARCHAR(50) UNIQUE,
    title VARCHAR(255),
    description TEXT,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    budget_type VARCHAR(20),
    skills JSONB,
    client_id VARCHAR(50),
    client_name VARCHAR(255),
    client_rating DECIMAL(3,2),
    posted_time TIMESTAMP,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    experience_level VARCHAR(50),
    project_length VARCHAR(100),
    hours_per_week VARCHAR(100),
    url TEXT,
    ai_analysis JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблиця відгуків
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50),
    proposal_text TEXT,
    bid_amount DECIMAL(10,2),
    status VARCHAR(50),
    submitted_at TIMESTAMP,
    ai_generated BOOLEAN DEFAULT FALSE,
    template_used VARCHAR(100),
    effectiveness_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблиця повідомлень
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    upwork_message_id VARCHAR(50),
    job_id VARCHAR(50),
    client_id VARCHAR(50),
    content TEXT,
    message_type VARCHAR(20),
    sent_at TIMESTAMP,
    ai_generated BOOLEAN DEFAULT FALSE,
    response_to_message_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблиця шаблонів
CREATE TABLE templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(100),
    content TEXT,
    variables JSONB,
    effectiveness_score DECIMAL(3,2),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблиця аналітики
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    date DATE,
    total_applications INTEGER,
    successful_applications INTEGER,
    response_rate DECIMAL(5,2),
    average_bid_amount DECIMAL(10,2),
    top_performing_template VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Технічна реалізація

### Структура проекту
```
upwork_web_app/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── upwork_client.py
│   │   ├── oauth_manager.py
│   │   ├── ai_generator.py
│   │   ├── smart_filter.py
│   │   ├── application_service.py
│   │   └── messaging_service.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── connection.py
│   │   └── migrations/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── logging.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   └── validators.py
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── public/
│   └── package.json
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Конфігурація
```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
# Upwork API
    UPWORK_CLIENT_ID = os.getenv('UPWORK_CLIENT_ID')
    UPWORK_CLIENT_SECRET = os.getenv('UPWORK_CLIENT_SECRET')
    UPWORK_CALLBACK_URL = os.getenv('UPWORK_CALLBACK_URL')
    
# AI Services
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    
# Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
# Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    
# Rate Limiting
    UPWORK_RATE_LIMIT = 100  # requests per hour
    AI_RATE_LIMIT = 1000     # requests per hour
```

## Розгортання

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - UPWORK_CLIENT_ID=${UPWORK_CLIENT_ID}
      - UPWORK_CLIENT_SECRET=${UPWORK_CLIENT_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/upwork_app
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=upwork_app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Моніторинг та аналітика

### Метрики для відстеження
- Кількість відгуків за день/тиждень/місяць
- Відсоток успішних відгуків (отримання відповіді)
- Середній час відгуку на вакансію
- Ефективність різних AI шаблонів
- Статистика по категоріях та бюджетах
- Аналіз клієнтів та їх відповідності

### Дашборд аналітики
```python
class AnalyticsService:
    def __init__(self, db):
        self.db = db
    
    def get_daily_stats(self, date):
        """Щоденна статистика"""
        return {
            'total_applications': self._count_applications(date),
            'successful_applications': self._count_successful(date),
            'response_rate': self._calculate_response_rate(date),
            'average_bid_amount': self._calculate_avg_bid(date),
            'top_categories': self._get_top_categories(date),
            'ai_effectiveness': self._calculate_ai_effectiveness(date)
        }
    
    def get_performance_trends(self, days=30):
        """Тренди продуктивності"""
        trends = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            stats = self.get_daily_stats(date)
            trends.append({
                'date': date.date(),
                'stats': stats
            })
        return trends
```

## Безпека

### OAuth 2.0 безпека
- Валідація state параметра
- Безпечне зберігання токенів
- Автоматичне оновлення токенів
- Обробка помилок авторизації

### Rate Limiting
```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def check_limit(self, key, limit, window):
        """Перевірка ліміту запитів"""
        current = self.redis.get(key)
        if current and int(current) >= limit:
            return False
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        pipe.execute()
        return True
```

## Контрольний список

### Перед запуском:
- [ ] Реєстрація на developers.upwork.com
- [ ] Створення додатку та отримання ключів
- [ ] Налаштування OAuth 2.0
- [ ] Отримання API ключів для AI сервісів
- [ ] Налаштування бази даних
- [ ] Конфігурація Docker

### При розробці:
- [ ] Тестування OAuth авторизації
- [ ] Валідація API відповідей
- [ ] Тестування AI генерації
- [ ] Перевірка rate limiting
- [ ] Тестування автоматизації

### Для продакшену:
- [ ] Моніторинг використання API
- [ ] Логування помилок
- [ ] Резервне копіювання даних
- [ ] Масштабування системи
- [ ] Документація API

## Висновки

### Переваги офіційної інтеграції:
- ✅ **Легальний доступ** - повна відповідність ToS Upwork
- ✅ **Стабільна робота** - гарантована доступність API
- ✅ **Структуровані дані** - JSON формат відповідей
- ✅ **Висока швидкість** - оптимізовані запити
- ✅ **Підтримка** - офіційна документація

### Ключові компоненти:
1. **OAuth 2.0 авторизація** - безпечний доступ
2. **AI генерація відгуків** - автоматизація процесу
3. **Розумний фільтр вакансій** - ефективний пошук
4. **Автоматичні відгуки** - повна автоматизація
5. **Ведення переписки** - комунікація з клієнтами
6. **Аналітика ефективності** - оптимізація стратегії

### Наступні кроки:
1. **Реєстрація на developers.upwork.com**
2. **Налаштування OAuth 2.0**
3. **Створення UpworkAPIClient**
4. **Інтеграція з AI сервісами**
5. **Розробка веб-інтерфейсу**
6. **Тестування та оптимізація**

---
*Дата: 2024-12-19* 