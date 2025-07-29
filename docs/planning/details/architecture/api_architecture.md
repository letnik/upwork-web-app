# Архітектура API

> **RESTful API архітектура для Upwork Web App з максимальною безпекою**

---

## Зміст

1. [Огляд API](#огляд-api)
2. [Архітектура](#архітектура)
3. [Endpoints](#endpoints)
4. [Middleware](#middleware)
5. [Валідація](#валідація)
6. [Документація](#документація)

---

## Огляд API

### Технології
- **FastAPI** - сучасний веб-фреймворк
- **Pydantic** - валідація даних
- **SQLAlchemy** - ORM
- **JWT** - автентифікація
- **OpenAPI** - автоматична документація

### Принципи
- **RESTful дизайн** - стандартні HTTP методи
- **Безпека перш за все** - автентифікація та авторизація
- **Валідація даних** - перевірка всіх вхідних даних
- **Документація** - автоматична генерація OpenAPI

---

## Архітектура

### Структура API
```
┌─────────────────────────────────────┐
│         API Gateway                 │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Auth API    │ │ Jobs API    │   │
│  │ /auth/*     │ │ /jobs/*     │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ AI API      │ │ Analytics   │   │
│  │ /ai/*       │ │ /analytics/*│   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Messages    │ │ Security    │   │
│  │ /messages/* │ │ /security/* │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

### Middleware Stack
```
Request → CORS → Rate Limiting → Auth → Logging → Route Handler → Response
```

---

## Endpoints

### Авторизація (`/auth/*`)
```python
# OAuth 2.0
POST /auth/upwork/init
POST /auth/upwork/callback
POST /auth/refresh
POST /auth/logout

# MFA
POST /auth/mfa/setup
POST /auth/mfa/verify
POST /auth/mfa/disable

# Профіль
GET /auth/profile
PUT /auth/profile
PUT /auth/password
```

### Вакансії (`/jobs/*`)
```python
# CRUD операції
GET /jobs
GET /jobs/{job_id}
POST /jobs
PUT /jobs/{job_id}
DELETE /jobs/{job_id}

# Фільтрація та пошук
GET /jobs/search
GET /jobs/favorites
POST /jobs/{job_id}/favorite
DELETE /jobs/{job_id}/favorite

# Синхронізація з Upwork
POST /jobs/sync
GET /jobs/sync/status
```

### Пропозиції (`/proposals/*`)
```python
# CRUD операції
GET /proposals
GET /proposals/{proposal_id}
POST /proposals
PUT /proposals/{proposal_id}
DELETE /proposals/{proposal_id}

# Статуси
PUT /proposals/{proposal_id}/submit
PUT /proposals/{proposal_id}/withdraw

# AI генерація
POST /proposals/{proposal_id}/generate
POST /proposals/generate-cover-letter
```

### AI (`/ai/*`)
```python
# Генерація контенту
POST /ai/generate/proposal
POST /ai/generate/cover-letter
POST /ai/generate/message

# Аналіз
POST /ai/analyze/job
POST /ai/analyze/proposal

# Налаштування
GET /ai/settings
PUT /ai/settings
```

### Повідомлення (`/messages/*`)
```python
# CRUD операції
GET /messages
GET /messages/{message_id}
POST /messages
PUT /messages/{message_id}
DELETE /messages/{message_id}

# Статуси
PUT /messages/{message_id}/read
PUT /messages/{message_id}/unread

# AI генерація
POST /messages/generate
```

### Аналітика (`/analytics/*`)
```python
# Метрики
GET /analytics/overview
GET /analytics/jobs
GET /analytics/proposals
GET /analytics/messages

# Звіти
GET /analytics/reports
POST /analytics/reports/generate
GET /analytics/reports/{report_id}

# Експорт
GET /analytics/export
```

### Безпека (`/security/*`)
```python
# Профіль безпеки
GET /security/profile
PUT /security/profile

# MFA
GET /security/mfa/status
POST /security/mfa/enable
POST /security/mfa/disable

# Логи
GET /security/logs
GET /security/logs/{log_id}

# Сповіщення
GET /security/alerts
PUT /security/alerts/{alert_id}/acknowledge
```

---

## Middleware

### CORS Middleware
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://upwork-web-app.com",
        "https://staging.upwork-web-app.com",
        "http://localhost:3000"  # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Rate-Limit-Remaining"]
)
```

### Rate Limiting Middleware
```python
from fastapi import Request, HTTPException
import redis
import time

class RateLimitMiddleware:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.limits = {
            "default": {"requests": 100, "window": 3600},  # 100 requests per hour
            "auth": {"requests": 10, "window": 900},       # 10 requests per 15 min
            "ai": {"requests": 50, "window": 3600},        # 50 requests per hour
            "sync": {"requests": 5, "window": 3600}        # 5 requests per hour
        }
    
    async def __call__(self, request: Request, call_next):
# Отримуємо користувача
        user_id = self.get_user_id(request)
        if not user_id:
            return await call_next(request)
        
# Визначаємо тип endpoint
        endpoint_type = self.get_endpoint_type(request.url.path)
        limit_config = self.limits.get(endpoint_type, self.limits["default"])
        
# Перевіряємо rate limit
        key = f"rate_limit:{user_id}:{endpoint_type}"
        current = self.redis.get(key)
        
        if current and int(current) >= limit_config["requests"]:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {limit_config['requests']} requests per {limit_config['window']} seconds."
            )
        
# Збільшуємо лічильник
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, limit_config["window"])
        pipe.execute()
        
# Додаємо headers
        response = await call_next(request)
        response.headers["X-Rate-Limit-Remaining"] = str(
            limit_config["requests"] - (int(current) if current else 0)
        )
        
        return response
    
    def get_user_id(self, request: Request) -> Optional[int]:
        """Отримує ID користувача з токена"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload.get("user_id")
        except:
            return None
    
    def get_endpoint_type(self, path: str) -> str:
        """Визначає тип endpoint для rate limiting"""
        if path.startswith("/auth/"):
            return "auth"
        elif path.startswith("/ai/"):
            return "ai"
        elif path.startswith("/jobs/sync"):
            return "sync"
        else:
            return "default"
```

### Authentication Middleware
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Отримує поточного користувача з JWT токена"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Перевіряє, чи активний користувач"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
```

### Logging Middleware
```python
import logging
import time
from fastapi import Request

class LoggingMiddleware:
    def __init__(self):
        self.logger = logging.getLogger("api")
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
# Логуємо запит
        self.logger.info(f"Request: {request.method} {request.url}")
        
# Обробляємо запит
        response = await call_next(request)
        
# Логуємо відповідь
        process_time = time.time() - start_time
        self.logger.info(
            f"Response: {response.status_code} - {process_time:.3f}s"
        )
        
# Додаємо timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

---

## Валідація

### Pydantic моделі
```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class JobCreate(BaseModel):
    upwork_job_id: str
    title: str
    description: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    hourly_rate_min: Optional[float] = None
    hourly_rate_max: Optional[float] = None
    skills: Optional[List[str]] = []
    category: Optional[str] = None
    subcategory: Optional[str] = None
    country: Optional[str] = None
    client_info: Optional[dict] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    duration: Optional[str] = None
    workload: Optional[str] = None
    
    @validator('budget_max')
    def validate_budget(cls, v, values):
        if v and 'budget_min' in values and values['budget_min']:
            if v < values['budget_min']:
                raise ValueError('budget_max must be greater than budget_min')
        return v

class ProposalCreate(BaseModel):
    job_id: int
    cover_letter: str
    bid_amount: Optional[float] = None
    bid_type: str  # 'fixed' or 'hourly'
    
    @validator('bid_type')
    def validate_bid_type(cls, v):
        if v not in ['fixed', 'hourly']:
            raise ValueError('bid_type must be either "fixed" or "hourly"')
        return v

class AIGenerationRequest(BaseModel):
    job_id: int
    generation_type: str  # 'proposal', 'cover_letter', 'message'
    prompt: str
    model: Optional[str] = 'gpt-4'
    
    @validator('generation_type')
    def validate_generation_type(cls, v):
        allowed_types = ['proposal', 'cover_letter', 'message']
        if v not in allowed_types:
            raise ValueError(f'generation_type must be one of: {allowed_types}')
        return v
```

### Валідація запитів
```python
from fastapi import Query, Path

async def get_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of jobs to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_budget: Optional[float] = Query(None, ge=0, description="Minimum budget"),
    max_budget: Optional[float] = Query(None, ge=0, description="Maximum budget"),
    skills: Optional[List[str]] = Query(None, description="Filter by skills"),
    current_user: User = Depends(get_current_active_user)
):
    """Отримує список вакансій з фільтрацією"""
    filters = {
        "user_id": current_user.id,
        "status": status,
        "category": category,
        "min_budget": min_budget,
        "max_budget": max_budget,
        "skills": skills
    }
    
    jobs = await job_service.get_jobs(skip=skip, limit=limit, filters=filters)
    return jobs

async def get_job(
    job_id: int = Path(..., description="Job ID"),
    current_user: User = Depends(get_current_active_user)
):
    """Отримує конкретну вакансію"""
    job = await job_service.get_job(job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
```

---

## Документація

### OpenAPI конфігурація
```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Upwork Web App API",
    description="API для автоматизації роботи з Upwork",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Upwork Web App API",
        version="1.0.0",
        description="API для автоматизації роботи з Upwork через офіційне API з інтеграцією штучного інтелекту",
        routes=app.routes,
    )
    
# Додаємо security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
# Додаємо security до всіх endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method != "parameters":
                openapi_schema["paths"][path][method]["security"] = [
                    {"BearerAuth": []}
                ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Приклад endpoint документації
```python
@app.post(
    "/jobs",
    response_model=JobResponse,
    status_code=201,
    summary="Створити нову вакансію",
    description="Створює нову вакансію для користувача",
    responses={
        201: {"description": "Вакансія успішно створена"},
        400: {"description": "Невірні дані"},
        401: {"description": "Не авторизований"},
        422: {"description": "Помилка валідації"}
    }
)
async def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Створює нову вакансію.
    
    - **job**: Дані вакансії
    - **current_user**: Поточний користувач (автоматично)
    
    Повертає створену вакансію.
    """
    return await job_service.create_job(job, current_user.id)
```

---

## 🧪 Тестування

### Unit тести
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

class TestJobsAPI:
    def test_get_jobs(self, client: TestClient, mock_user: User):
        """Тестує отримання списку вакансій"""
# Arrange
        with patch('app.services.job_service.get_jobs') as mock_get_jobs:
            mock_get_jobs.return_value = [
                {"id": 1, "title": "Test Job", "user_id": mock_user.id}
            ]
            
# Act
            response = client.get(
                "/jobs",
                headers={"Authorization": f"Bearer {mock_user.token}"}
            )
            
# Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["title"] == "Test Job"
    
    def test_create_job(self, client: TestClient, mock_user: User):
        """Тестує створення вакансії"""
# Arrange
        job_data = {
            "upwork_job_id": "test123",
            "title": "Test Job",
            "description": "Test description"
        }
        
        with patch('app.services.job_service.create_job') as mock_create_job:
            mock_create_job.return_value = {
                "id": 1,
                "title": "Test Job",
                "user_id": mock_user.id
            }
            
# Act
            response = client.post(
                "/jobs",
                json=job_data,
                headers={"Authorization": f"Bearer {mock_user.token}"}
            )
            
# Assert
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test Job"
```

### Integration тести
```python
class TestJobsIntegration:
    async def test_complete_job_flow(self, client: TestClient, db_session):
        """Тестує повний flow роботи з вакансіями"""
# Arrange - Створюємо користувача
        user = await create_test_user(db_session)
        token = create_access_token(user.id)
        
# Act 1 - Створюємо вакансію
        job_data = {
            "upwork_job_id": "test123",
            "title": "Integration Test Job",
            "description": "Test description"
        }
        
        create_response = client.post(
            "/jobs",
            json=job_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
# Assert 1
        assert create_response.status_code == 201
        job_id = create_response.json()["id"]
        
# Act 2 - Отримуємо вакансію
        get_response = client.get(
            f"/jobs/{job_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
# Assert 2
        assert get_response.status_code == 200
        job_data = get_response.json()
        assert job_data["title"] == "Integration Test Job"
        
# Act 3 - Оновлюємо вакансію
        update_data = {"title": "Updated Job Title"}
        update_response = client.put(
            f"/jobs/{job_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
# Assert 3
        assert update_response.status_code == 200
        updated_job = update_response.json()
        assert updated_job["title"] == "Updated Job Title"
```

---

## Моніторинг

### API метрики
```python
class APIMetrics:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "requests_by_endpoint": {},
            "requests_by_method": {},
            "error_codes": {}
        }
    
    def record_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Записує метрику запиту"""
        self.metrics["total_requests"] += 1
        
        if 200 <= status_code < 400:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
        
# Оновлюємо середній час відповіді
        current_avg = self.metrics["average_response_time"]
        total_requests = self.metrics["total_requests"]
        self.metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
# Метрики по endpoint
        if endpoint not in self.metrics["requests_by_endpoint"]:
            self.metrics["requests_by_endpoint"][endpoint] = 0
        self.metrics["requests_by_endpoint"][endpoint] += 1
        
# Метрики по методу
        if method not in self.metrics["requests_by_method"]:
            self.metrics["requests_by_method"][method] = 0
        self.metrics["requests_by_method"][method] += 1
        
# Метрики по кодам помилок
        if status_code >= 400:
            if status_code not in self.metrics["error_codes"]:
                self.metrics["error_codes"][status_code] = 0
            self.metrics["error_codes"][status_code] += 1
    
    def get_metrics(self) -> dict:
        """Повертає поточні метрики"""
        return self.metrics.copy()
```

---

## Контрольні списки

### Реалізація
- [ ] Всі API endpoints
- [ ] Middleware (CORS, Auth, Rate Limiting, Logging)
- [ ] Валідація даних (Pydantic)
- [ ] Документація (OpenAPI)
- [ ] Тестування (Unit + Integration)

### Безпека
- [ ] JWT автентифікація
- [ ] Rate limiting
- [ ] CORS налаштування
- [ ] Валідація вхідних даних
- [ ] Логування всіх запитів

### Продуктивність
- [ ] Кешування відповідей
- [ ] Пагінація результатів
- [ ] Оптимізація запитів
- [ ] Моніторинг метрик

---

## Посилання

- [Системна архітектура](system_architecture.md)
- [Архітектура безпеки](security_architecture.md)
- [Дизайн endpoint'ів](api/endpoints_design.md)
- [Middleware](api/middleware_implementation.md)

---

**Версія**: 1.0.0 