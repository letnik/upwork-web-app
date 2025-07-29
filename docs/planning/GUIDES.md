# GUIDES - Гайди та інструкції

> **Практичні гайди для розробки Upwork AI Assistant**

---

## Зміст

1. [Налаштування середовища](#налаштування-середовища)
2. [Розробка](#розробка)
3. [Тестування](#тестування)
4. [Розгортання](#розгортання)
5. [Моніторинг](#моніторинг)
6. [Безпека](#безпека)

---

## Налаштування середовища

> 📖 **Детальний гайд**: [Setup Environment Guide](details/guides/development/setup_environment.md)

### **Швидкий старт**
```bash
# 1. Клонування репозиторію
git clone https://github.com/your-org/upwork-ai-assistant.git
cd upwork-ai-assistant

# 2. Налаштування Python середовища
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate     # Windows

# 3. Встановлення залежностей
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Налаштування змінних середовища
cp .env.example .env
# Відредагуйте .env файл з вашими ключами

# 5. Запуск бази даних
docker-compose up -d postgres redis

# 6. Запуск міграцій
alembic upgrade head

# 7. Запуск додатку
uvicorn src.main:app --reload
```

### **Необхідні інструменти**
> 📖 **Детальний опис**: [ARCHITECTURE.md](ARCHITECTURE.md#технологічний-стек)

- **Python 3.11+** - основна мова розробки
- **Node.js 18+** - для frontend розробки
- **Docker & Docker Compose** - для контейнеризації
- **PostgreSQL 15+** - основна база даних
- **Redis 7+** - кешування та сесії
- **Git** - система контролю версій

### **Змінні середовища**
```bash
# .env файл
DATABASE_URL=postgresql://user:password@localhost:5432/upwork_app
REDIS_URL=redis://localhost:6379

# API ключі
UPWORK_CLIENT_ID=your_upwork_client_id
UPWORK_CLIENT_SECRET=your_upwork_client_secret
OPENAI_API_KEY=your-openai-api-key
CLAUDE_API_KEY=your-claude-api-key

# Безпека
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Налаштування
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## Розробка

### **Структура проекту**
```
upwork-ai-assistant/
├── backend/                 # Python FastAPI додаток
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Бізнес-логіка
│   │   ├── models/         # Database моделі
│   │   ├── utils/          # Допоміжні функції
│   │   └── main.py         # Точка входу
│   ├── tests/              # Тести
│   ├── alembic/            # Database міграції
│   └── requirements.txt    # Python залежності
├── frontend/               # React додаток
│   ├── src/
│   │   ├── components/     # React компоненти
│   │   ├── pages/          # Сторінки
│   │   ├── services/       # API клієнти
│   │   └── utils/          # Допоміжні функції
│   ├── public/             # Статичні файли
│   └── package.json        # Node.js залежності
├── docker-compose.yml      # Docker конфігурація
└── README.md              # Документація
```

### **Робочий процес Git**
```bash
# 1. Створення нової гілки
git checkout -b feature/AI-001-openai-integration

# 2. Розробка функціональності
# ... пишіть код ...

# 3. Додавання змін
git add .

# 4. Коміт з описом
git commit -m "feat: add OpenAI integration for proposal generation

- Add OpenAI API client
- Implement proposal generation service
- Add error handling and retry logic
- Update tests for new functionality"

# 5. Push в репозиторій
git push origin feature/AI-001-openai-integration

# 6. Створення Pull Request
# Перейдіть на GitHub та створіть PR
```

### **Стандарти коду**
```python
# Python - PEP 8
def generate_proposal(job_data: dict, user_profile: dict) -> str:
    """
    Генерує пропозицію для вакансії на основі даних вакансії та профілю користувача.
    
    Args:
        job_data: Дані вакансії
        user_profile: Профіль користувача
        
    Returns:
        str: Згенерована пропозиція
        
    Raises:
        ValueError: Якщо дані невалідні
    """
    if not job_data or not user_profile:
        raise ValueError("Job data and user profile are required")
    
# Логіка генерації
    return "Generated proposal content"
```

```typescript
// TypeScript - ESLint + Prettier
interface JobData {
  id: string;
  title: string;
  description: string;
  budget: {
    min: number;
    max: number;
  };
  skills: string[];
}

const generateProposal = async (
  jobData: JobData,
  userProfile: UserProfile
): Promise<string> => {
  if (!jobData || !userProfile) {
    throw new Error('Job data and user profile are required');
  }
  
  // Логіка генерації
  return 'Generated proposal content';
};
```

### **API розробка**
```python
# src/api/endpoints/jobs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database.connection import get_db
from src.services.job_service import JobService
from src.schemas.job import JobCreate, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/", response_model=List[JobResponse])
async def search_jobs(
    q: str = "",
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Пошук вакансій з фільтрацією"""
    job_service = JobService(db)
    jobs = job_service.search_jobs(q, limit, offset)
    return jobs

@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db)
):
    """Створення нової вакансії"""
    job_service = JobService(db)
    job = job_service.create_job(job_data)
    return job
```

---

## 🧪 Тестування

### **Запуск тестів**
```bash
# Unit тести
pytest tests/unit/

# Integration тести
pytest tests/integration/

# E2E тести
pytest tests/e2e/

# Всі тести з покриттям
pytest tests/ --cov=src --cov-report=html

# Frontend тести
cd frontend
npm test

# E2E тести (Playwright)
npx playwright test
```

### **Тестування API**
```bash
# Тестування health check
curl http://localhost:8000/health

# Тестування пошуку вакансій
curl "http://localhost:8000/api/v1/upwork/jobs?q=python"

# Тестування генерації пропозиції
curl -X POST http://localhost:8000/api/v1/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Developer",
    "description": "We need a Python developer",
    "budget": {"min": 1000, "max": 5000}
  }'
```

### **Performance тестування**
```bash
# Load тестування з Locust
locust -f tests/performance/locustfile.py

# Stress тестування
pytest tests/performance/test_stress.py

# Memory profiling
python -m memory_profiler src/main.py
```

---

## Розгортання

### **Локальне розгортання**
```bash
# Запуск всіх сервісів
docker-compose up -d

# Перевірка статусу
docker-compose ps

# Перегляд логів
docker-compose logs -f api-gateway

# Зупинка сервісів
docker-compose down
```

### **Staging розгортання**
```bash
# Налаштування staging середовища
export DATABASE_URL=postgresql://staging_user:pass@staging-db:5432/staging_db
export REDIS_URL=redis://staging-redis:6379
export ENVIRONMENT=staging

# Запуск staging
docker-compose -f docker-compose.staging.yml up -d

# Запуск міграцій
alembic upgrade head

# Тестування staging
pytest tests/ --env=staging
```

### **Production розгортання**
```bash
# Kubernetes розгортання
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Перевірка статусу
kubectl get pods -n upwork-ai-assistant
kubectl get services -n upwork-ai-assistant

# Моніторинг логів
kubectl logs -f deployment/upwork-ai-assistant -n upwork-ai-assistant
```

### **CI/CD Pipeline**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run tests
      run: pytest tests/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Build Docker image
      run: docker build -t upwork-ai-assistant .
    
    - name: Push to registry
      run: docker push your-registry/upwork-ai-assistant:latest
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: kubectl apply -f k8s/
```

---

## Моніторинг

### **Логування**
```python
# Налаштування логування
import logging
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def some_function():
    logger.info("Function started")
    try:
# Логіка функції
        logger.debug("Processing data")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise
```

### **Метрики**
```python
# Prometheus метрики
from prometheus_client import Counter, Histogram, generate_latest

# Лічильники
requests_total = Counter('http_requests_total', 'Total HTTP requests')
proposals_generated = Counter('proposals_generated_total', 'Total proposals generated')

# Гістограми
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Використання
@request_duration.time()
def api_endpoint():
    requests_total.inc()
# Логіка endpoint
```

### **Health checks**
```python
# Health check endpoint
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "database": check_database_connection(),
            "redis": check_redis_connection(),
            "upwork_api": check_upwork_api_connection()
        }
    }
```

### **Алерти**
```yaml
# prometheus/alerts.yml
groups:
  - name: upwork-ai-assistant
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"
```

---

## Безпека

### **Аутентифікація**
```python
# JWT токени
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = jwt.decode(
            credentials.credentials, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

### **Валідація вхідних даних**
```python
# Pydantic моделі для валідації
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

### **Rate Limiting**
```python
# Rate limiting middleware
from fastapi import Request, HTTPException
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        minute_ago = now - 60
        
# Очищення старих запитів
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
# Перевірка ліміту
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False
        
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )
    
    response = await call_next(request)
    return response
```

### **Шифрування**
```python
# Шифрування чутливих даних
from cryptography.fernet import Fernet
import base64

class EncryptionService:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, data: str) -> str:
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(decoded)
        return decrypted.decode()

# Використання
encryption_service = EncryptionService(ENCRYPTION_KEY)

# Шифрування API ключів
encrypted_api_key = encryption_service.encrypt(user_api_key)

# Розшифрування для використання
api_key = encryption_service.decrypt(encrypted_api_key)
```

---

## Швидкі посилання

- [📋 MASTER_TASKS.md](MASTER_TASKS.md) - Всі завдання проекту
- [🚀 PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Загальний огляд проекту
- [🏗️ ARCHITECTURE.md](ARCHITECTURE.md) - Архітектура системи
- [🧪 TESTING.md](TESTING.md) - План тестування
- [🧭 NAVIGATION.md](NAVIGATION.md) - Навігація по документації

**Детальні гайди**: [details/guides/](details/guides/)

---

## Інструкції по роботі

### **Як почати роботу**
1. Прочитайте [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) для розуміння проекту
2. Налаштуйте середовище розробки згідно з цим гайдом
3. Виберіть завдання з [MASTER_TASKS.md](MASTER_TASKS.md)
4. Створіть гілку та почніть розробку
5. Напишіть тести та оновіть документацію

### **Як відстежувати прогрес**
1. Відмічайте завдання як `[x]` після завершення
2. Оновлюйте статус в [MASTER_TASKS.md](MASTER_TASKS.md)
3. Додавайте коментарі про прогрес
4. Оновлюйте метрики успіху

### **Як додавати нові завдання**
1. Створіть унікальний ID (наприклад: AI-011)
2. Додайте в відповідну категорію
3. Вкажіть залежності
4. Оновіть загальну статистику

### **Як працювати з детальними планами**
- Кожен модуль має свій `implementation_plan.md` в папці `details/modules/`
- Детальні технічні специфікації знаходяться в `details/`
- Архітектурна документація в `details/architecture/`

---

**Статус**: Створено  
**Версія**: 1.0.0 