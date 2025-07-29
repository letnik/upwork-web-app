# Мікросервісна архітектура

> **Детальний план мікросервісної архітектури для Upwork Web App**

---

## Зміст

1. [Огляд архітектури](#огляд-архітектури)
2. [Сервіси](#сервіси)
3. [API Gateway](#api-gateway)
4. [Комунікація між сервісами](#комунікація-між-сервісами)
5. [База даних](#база-даних)
6. [Розгортання](#розгортання)
7. [Моніторинг](#моніторинг)
8. [Безпека](#безпека)

---

## Огляд архітектури

### Принципи
- **Незалежність сервісів** - кожен сервіс може розроблятися та розгортатися окремо
- **Спеціалізація** - кожен сервіс відповідає за конкретну функціональність
- **Масштабованість** - можливість масштабувати окремі сервіси
- **Відмовостійкість** - ізоляція збоїв між сервісами

### Технології
- **API Gateway**: Nginx/Envoy
- **Сервіси**: FastAPI (Python)
- **База даних**: PostgreSQL + Redis
- **Контейнеризація**: Docker Compose
- **Моніторинг**: Prometheus + Grafana
- **Container Registry**: Docker Hub (development), AWS ECR (production)
- **Infrastructure as Code**: Terraform
- **Load Testing**: K6
- **CDN**: CloudFlare

---

## Сервіси

### 1. **API Gateway Service**
```
┌─────────────────────────────────────┐
│         API Gateway                 │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Auth        │ │ Rate Limit  │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Load Bal    │ │ SSL/TLS     │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- Маршрутизація запитів до сервісів
- Аутентифікація та авторизація
- Rate limiting
- SSL/TLS термінація
- Load balancing

**Endpoints:**
- `/api/v1/*` - маршрутизація до сервісів
- `/health` - health check
- `/metrics` - метрики

### 2. **Auth Service**
```
┌─────────────────────────────────────┐
│         Auth Service                │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ OAuth 2.0   │ │ JWT Manager │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ TOTP MFA    │ │ User Mgmt   │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- OAuth 2.0 інтеграція з Upwork
- JWT токени
- TOTP MFA
- Управління користувачами
- Сесії

**Endpoints:**
- `/auth/login` - вхід
- `/auth/logout` - вихід
- `/auth/register` - реєстрація
- `/auth/mfa` - MFA налаштування
- `/auth/refresh` - оновлення токенів

### 3. **Upwork Integration Service**
```
┌─────────────────────────────────────┐
│    Upwork Integration Service       │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Jobs API    │ │ Proposals   │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Messages    │ │ Work Diary  │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- Інтеграція з Upwork API
- Синхронізація даних
- Rate limiting для Upwork API
- Кешування відповідей

**Endpoints:**
- `/upwork/jobs` - пошук вакансій
- `/upwork/proposals` - управління пропозиціями
- `/upwork/messages` - повідомлення
- `/upwork/workdiary` - робочий діарій

### 4. **AI Service**
```
┌─────────────────────────────────────┐
│         AI Service                  │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ GPT-4       │ │ Claude      │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Proposal Gen│ │ Job Analysis│   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- Генерація відгуків з GPT-4
- Аналіз вакансій
- Розумна фільтрація
- A/B тестування

**Endpoints:**
- `/ai/generate-proposal` - генерація пропозиції
- `/ai/analyze-job` - аналіз вакансії
- `/ai/filter-jobs` - розумна фільтрація
- `/ai/ab-test` - A/B тестування

### 5. **Analytics Service**
```
┌─────────────────────────────────────┐
│      Analytics Service              │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Metrics     │ │ Reports     │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Dashboard   │ │ Export      │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- Збір метрик
- Генерація звітів
- Аналітика ефективності
- Експорт даних

**Endpoints:**
- `/analytics/metrics` - метрики
- `/analytics/reports` - звіти
- `/analytics/dashboard` - дашборд
- `/analytics/export` - експорт

### 6. **Notification Service**
```
┌─────────────────────────────────────┐
│     Notification Service             │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Email       │ │ Telegram    │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ SMS         │ │ WebSocket   │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- Email сповіщення
- Telegram бот
- SMS сповіщення
- Real-time сповіщення

**Endpoints:**
- `/notifications/email` - email сповіщення
- `/notifications/telegram` - telegram сповіщення
- `/notifications/sms` - SMS сповіщення
- `/notifications/websocket` - WebSocket

### 7. **Web Interface Service**
```
┌─────────────────────────────────────┐
│     Web Interface Service           │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ React App   │ │ Static      │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ WebSocket   │ │ SSR         │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- React додаток
- Статичні ресурси
- WebSocket клієнт
- Server-side rendering

---

## API Gateway

### Конфігурація Nginx
```nginx
upstream auth_service {
    server auth:8000;
}

upstream upwork_service {
    server upwork:8001;
}

upstream ai_service {
    server ai:8002;
}

upstream analytics_service {
    server analytics:8003;
}

upstream notification_service {
    server notification:8004;
}

server {
    listen 80;
    server_name localhost;

# Auth Service
    location /api/v1/auth/ {
        proxy_pass http://auth_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

# Upwork Service
    location /api/v1/upwork/ {
        proxy_pass http://upwork_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

# AI Service
    location /api/v1/ai/ {
        proxy_pass http://ai_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

# Analytics Service
    location /api/v1/analytics/ {
        proxy_pass http://analytics_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

# Notification Service
    location /api/v1/notifications/ {
        proxy_pass http://notification_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

# Web Interface
    location / {
        proxy_pass http://web_interface:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Комунікація між сервісами

### Синхронна комунікація
- **HTTP REST API** - основна комунікація
- **JWT токени** - автентифікація між сервісами
- **Rate limiting** - обмеження навантаження

### Асинхронна комунікація
- **Redis Pub/Sub** - повідомлення між сервісами
- **Celery** - фонові завдання
- **WebSocket** - real-time оновлення

### Приклади комунікації
```python
# Auth Service → Upwork Service
POST /api/v1/upwork/sync
Authorization: Bearer <jwt_token>
{
    "user_id": 123,
    "sync_type": "jobs"
}

# AI Service → Notification Service
POST /api/v1/notifications/email
{
    "user_id": 123,
    "template": "proposal_generated",
    "data": {...}
}
```

---

## База даних

### Схема розподілу даних
```sql
-- Auth Service Database
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    encrypted_password VARCHAR(255) NOT NULL,
    totp_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Upwork Service Database
CREATE TABLE upwork_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    encrypted_access_token TEXT NOT NULL,
    encrypted_refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Service Database
CREATE TABLE ai_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    request_type VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    cost DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics Service Database
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    metric_type VARCHAR(50),
    metric_value DECIMAL(10,2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Розгортання

### Docker Compose конфігурація
```yaml
version: '3.8'

services:
# API Gateway
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - auth
      - upwork
      - ai
      - analytics
      - notification
      - web_interface

# Auth Service
  auth:
    build: ./services/auth
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/auth_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

# Upwork Service
  upwork:
    build: ./services/upwork
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/upwork_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

# AI Service
  ai:
    build: ./services/ai
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/ai_db
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis

# Analytics Service
  analytics:
    build: ./services/analytics
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/analytics_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

# Notification Service
  notification:
    build: ./services/notification
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/notification_db
      - REDIS_URL=redis://redis:6379
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    depends_on:
      - postgres
      - redis

# Web Interface Service
  web_interface:
    build: ./services/web_interface
    environment:
      - REACT_APP_API_URL=http://localhost/api/v1
    ports:
      - "3000:3000"

# Database
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=upwork_app
    volumes:
      - postgres_data:/var/lib/postgresql/data

# Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

# Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  postgres_data:
  redis_data:

---

## Системні вимоги

### Development Environment
- **CPU**: 2-4 cores
- **RAM**: 4-8 GB
- **Storage**: 50-100 GB SSD
- **Network**: 1 Gbps

### Production Environment
- **CPU**: 4-8 cores
- **RAM**: 8-16 GB
- **Storage**: 100-500 GB SSD
- **Network**: 1 Gbps

### Disaster Recovery
- **RTO (Recovery Time Objective)**: < 4 години
- **RPO (Recovery Point Objective)**: < 1 година
- **Backup Strategy**: Щоденні database backups + щотижневі full system backups
```

---

## Моніторинг

### Метрики для кожного сервісу
- **Response time** - час відповіді
- **Error rate** - частота помилок
- **Throughput** - пропускна здатність
- **Resource usage** - використання ресурсів

### Health checks
```python
# Health check endpoint для кожного сервісу
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "auth_service",
        "version": "1.0.0"
    }
```

### Логування
- **Structured logging** - структуровані логи
- **Centralized logging** - централізоване логування
- **Log levels** - рівні логування
- **Correlation IDs** - ідентифікатори кореляції

---

## Безпека

### Міжсервісна автентифікація
- **JWT токени** для автентифікації між сервісами
- **API ключі** для внутрішніх сервісів
- **TLS/SSL** для всіх з'єднань

### Ізоляція даних
- **Окремі бази даних** для кожного сервісу
- **Шифрування** чутливих даних
- **Access control** на рівні сервісів

### Моніторинг безпеки
- **Audit logs** - логи аудиту
- **Security metrics** - метрики безпеки
- **Anomaly detection** - виявлення аномалій

---

**Версія**: 1.0.0 