# ARCHITECTURE - Архітектура системи

> **Комплексна архітектура Upwork AI Assistant**

---

## Зміст

1. [Системна архітектура](#системна-архітектура)
2. [API архітектура](#api-архітектура)
3. [База даних](#база-даних)
4. [Мікросервіси](#мікросервіси)
5. [Безпека](#безпека)
6. [Моніторинг](#моніторинг)
7. [Розгортання](#розгортання)

---

## Системна архітектура

> 📖 **Детальний опис**: [System Architecture](details/architecture/system_architecture.md)

### **Пов'язані таски**
- **AUTH-001**: [Базова структура Auth](MASTER_TASKS.md#auth---авторизація-та-аутентифікація)
        [Auth Service](details/architecture/system_architecture.md#auth-сервіс)
        [Auth Module](details/modules/auth/auth_module.md)
        [Auth Plan](details/modules/auth/implementation_plan.md)

- **UPWORK-001**: [API інтеграція](MASTER_TASKS.md#upwork---інтеграція-з-upwork)
        [Upwork Service](details/architecture/system_architecture.md#upwork-сервіс)
        [Upwork Module](details/modules/upwork_integration/upwork_integration_module.md)
        [Upwork Plan](details/modules/upwork_integration/implementation_plan.md)

- **AI-001**: [OpenAI інтеграція](MASTER_TASKS.md#ai---штучний-інтелект)
        [AI Service](details/architecture/system_architecture.md#ai-сервіс)
        [AI Module](details/modules/ai/ai_module.md)
        [AI Plan](details/modules/ai/implementation_plan.md)

- **ANALYTICS-001**: [Базові метрики](MASTER_TASKS.md#analytics---аналітика)
        [Analytics Service](details/architecture/system_architecture.md#analytics-сервіс)
        [Analytics Module](details/modules/analytics/analytics_module.md)
        [Analytics Plan](details/modules/analytics/implementation_plan.md)

### **Загальна схема**
```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer                           │
│                         (Nginx/HAProxy)                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    API Gateway                                 │
│                   (FastAPI)                                    │
└─────────┬───────────┬───────────┬───────────┬───────────────────┘
          │           │           │           │
┌─────────▼─────────┐ │ ┌─────────▼─────────┐ │ ┌─────────────────┐
│   Auth Service    │ │ │  Upwork Service   │ │ │  AI Service     │
│   (JWT/OAuth 2.0) │ │ │  (API Integration)│ │ │ (OpenAI/Claude) │
│   "Sign in with   │ │ │  "Sign in with    │ │ │                 │
│    Upwork"        │ │ │   Upwork"         │ │ │                 │
└───────────────────┘ │ └───────────────────┘ │ └─────────────────┘
                      │                       │
┌─────────────────────▼───────────────────────▼───────────────────┐
│                    Analytics Service                            │
│                   (Data Processing)                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Database Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ PostgreSQL  │ │    Redis    │ │   S3        │ │   Elastic   │ │
│  │ (Main DB)   │ │ (Cache/Sessions)│ │ (Files/Media)│ │ (Search/Logs)│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### **Технологічний стек**
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy ✅
- **Frontend**: React 18+, TypeScript, Material-UI ✅
- **Database**: PostgreSQL 15+, Redis 7+ ✅
- **AI**: OpenAI GPT-4, Claude, Scikit-learn 🚧
- **Infrastructure**: Docker, Kubernetes, DigitalOcean/AWS 🚧

---

## API архітектура

> 📖 **Детальний опис**: [API Architecture](details/architecture/api_architecture.md)

### **Пов'язані таски**
- **AUTH-002**: [JWT токени](MASTER_TASKS.md#auth---авторизація-та-аутентифікація)
        [Auth API](details/architecture/api_architecture.md#авторизація-auth)
        [Auth Module](details/modules/auth/auth_module.md)
        [Auth Plan](details/modules/auth/implementation_plan.md)

- **UPWORK-003**: [Jobs API](MASTER_TASKS.md#upwork---інтеграція-з-upwork)
        [Jobs API](details/architecture/api_architecture.md#вакансії-jobs)
        [Upwork Module](details/modules/upwork_integration/upwork_integration_module.md)
        [Upwork Plan](details/modules/upwork_integration/implementation_plan.md)

- **AI-003**: [ProposalGenerator](MASTER_TASKS.md#ai---штучний-інтелект)
        [AI API](details/architecture/api_architecture.md#ai-ai)
        [AI Module](details/modules/ai/ai_module.md)
        [AI Plan](details/modules/ai/implementation_plan.md)

- **ANALYTICS-002**: [User dashboard](MASTER_TASKS.md#analytics---аналітика)
        [Analytics API](details/architecture/api_architecture.md#аналітика-analytics)
        [Analytics Module](details/modules/analytics/analytics_module.md)
        [Analytics Plan](details/modules/analytics/implementation_plan.md)

### **RESTful API Design**
```
/api/v1/
├── /auth/           # Авторизація та аутентифікація
│   ├── /login       # POST - вхід в систему
│   ├── /register    # POST - реєстрація
│   ├── /refresh     # POST - оновлення токена
│   └── /logout      # POST - вихід з системи
├── /upwork/         # Інтеграція з Upwork
│   ├── /jobs        # GET - пошук вакансій
│   ├── /proposals   # POST - відправка пропозицій
│   └── /messages    # GET/POST - повідомлення
├── /ai/             # AI функції
│   ├── /generate    # POST - генерація відгуків
│   ├── /analyze     # POST - аналіз вакансій
│   └── /filter      # POST - розумна фільтрація
├── /analytics/      # Аналітика
│   ├── /metrics     # GET - метрики користувача
│   ├── /reports     # GET - звіти
│   └── /trends      # GET - тренди
└── /users/          # Управління користувачами
    ├── /profile     # GET/PUT - профіль
    ├── /settings    # GET/PUT - налаштування
    └── /billing     # GET/POST - оплата
```

### **API Версіонування**
- **v1**: Поточна стабільна версія
- **v2**: Планується для майбутніх змін
- **Backward compatibility**: Підтримка старих версій

### **Rate Limiting**
```
- Free Plan: 100 requests/hour
- Basic Plan: 1000 requests/hour  
- Premium Plan: 5000 requests/hour
- Enterprise Plan: Unlimited
```

---

## База даних

> 📖 **Детальний опис**: [Database Architecture](details/architecture/database_architecture.md)

### **Пов'язані таски**
- **SECURITY-003**: [Input validation](MASTER_TASKS.md#security---безпека)
        [Database Security](details/architecture/security_architecture.md#encryption-layer)
        [Security Module](details/modules/security/security_module.md)
        [Security Plan](details/modules/security/implementation_plan.md)

- **AUTH-006**: [Session management](MASTER_TASKS.md#auth---авторизація-та-аутентифікація)
        [Database Sessions](details/architecture/database_architecture.md#session-storage)
        [Auth Module](details/modules/auth/auth_module.md)
        [Auth Plan](details/modules/auth/implementation_plan.md)

### **PostgreSQL - Основна БД**
```sql
-- Основні таблиці
users (id, email, password_hash, created_at, updated_at)
profiles (user_id, first_name, last_name, skills, hourly_rate)
jobs (id, upwork_id, title, description, budget, skills, client_id)
proposals (id, user_id, job_id, cover_letter, bid_amount, status)
analytics (id, user_id, date, applications_sent, responses_received)
settings (user_id, ai_preferences, notification_settings)
```

### **Redis - Кешування та сесії**
```
- Session storage: user sessions
- Cache: job listings, AI responses
- Rate limiting: API request counters
- Real-time data: live updates
```

### **S3 - Файлове сховище**
```
- User uploads: profile pictures, portfolios
- AI generated content: proposal templates
- Backup files: database dumps, logs
- Media files: videos, images
```

---

## Мікросервіси

### **Пов'язані таски**
- **AUTH-001 до AUTH-007**: [Auth Module](MASTER_TASKS.md#auth---авторизація-та-аутентифікація)
        [Auth Service](details/architecture/system_architecture.md#auth-сервіс)
        [Auth Module](details/modules/auth/auth_module.md)
        [Auth Plan](details/modules/auth/implementation_plan.md)

- **UPWORK-001 до UPWORK-008**: [Upwork Module](MASTER_TASKS.md#upwork---інтеграція-з-upwork)
        [Upwork Service](details/architecture/system_architecture.md#upwork-сервіс)
        [Upwork Module](details/modules/upwork_integration/upwork_integration_module.md)
        [Upwork Plan](details/modules/upwork_integration/implementation_plan.md)

- **AI-001 до AI-010**: [AI Module](MASTER_TASKS.md#ai---штучний-інтелект)
        [AI Service](details/architecture/system_architecture.md#ai-сервіс)
        [AI Module](details/modules/ai/ai_module.md)
        [AI Plan](details/modules/ai/implementation_plan.md)

- **ANALYTICS-001 до ANALYTICS-008**: [Analytics Module](MASTER_TASKS.md#analytics---аналітика)
        [Analytics Service](details/architecture/system_architecture.md#analytics-сервіс)
        [Analytics Module](details/modules/analytics/analytics_module.md)
        [Analytics Plan](details/modules/analytics/implementation_plan.md)

### **Auth Service**
**Технології**: FastAPI, JWT, OAuth2, PostgreSQL
**Функції**:
- User registration та authentication
- JWT token management
- OAuth 2.0 integration
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)

### **Upwork Service**
**Технології**: FastAPI, Upwork API, Redis, PostgreSQL
**Функції**:
- Upwork API integration
- Job search та filtering
- Proposal submission
- Message handling
- Rate limiting management

### **AI Service**
**Технології**: OpenAI API, Claude API, Scikit-learn, Redis
**Функції**:
- Proposal generation
- Job analysis
- Smart filtering
- Response optimization
- Cost management

### **Analytics Service**
**Технології**: Pandas, NumPy, PostgreSQL, Redis
**Функції**:
- User metrics calculation
- Performance tracking
- Trend analysis
- Report generation
- Data visualization

---

## Безпека

> 📖 **Детальний опис**: [Security Architecture](details/architecture/security_architecture.md)

### **Пов'язані таски**
- **SECURITY-001 до SECURITY-011**: [Security Module](MASTER_TASKS.md#security---безпека)
        [Security Architecture](details/architecture/security_architecture.md)
        [Security Module](details/modules/security/security_module.md)
        [Security Plan](details/modules/security/implementation_plan.md)

### **Аутентифікація та авторизація**
- **JWT tokens** для API access
- **OAuth 2.0** для Upwork integration
- **Multi-factor authentication** (TOTP)
- **Session management** з Redis
- **Role-based access control** (RBAC)

### **Шифрування**
- **HTTPS/TLS** для всіх з'єднань
- **Fernet encryption** для чутливих даних
- **Password hashing** з bcrypt
- **API key encryption** в базі даних

### **Захист від атак**
- **SQL Injection** prevention через ORM
- **XSS protection** через input validation
- **CSRF protection** для форм
- **Rate limiting** для API endpoints
- **Input validation** з Pydantic

### **Аудит та логування**
- **Audit logs** для всіх дій
- **Security monitoring** з алертами
- **Error tracking** з Sentry
- **Performance monitoring** з Prometheus

---

## Моніторинг

### **Пов'язані таски**
- **ANALYTICS-001 до ANALYTICS-008**: [Analytics Module](MASTER_TASKS.md#analytics---аналітика)
        [Analytics Service](details/architecture/system_architecture.md#analytics-сервіс)
        [Analytics Module](details/modules/analytics/analytics_module.md)
        [Analytics Plan](details/modules/analytics/implementation_plan.md)

- **SECURITY-008 до SECURITY-011**: [Security Monitoring](MASTER_TASKS.md#security---безпека)
        [Security Monitoring](details/architecture/security_architecture.md#monitoring-layer)
        [Security Module](details/modules/security/security_module.md)
        [Security Plan](details/modules/security/implementation_plan.md)

### **Метрики продуктивності**
- **Response time** для API endpoints
- **Throughput** (requests per second)
- **Error rate** та success rate
- **Database performance** metrics
- **Cache hit ratio** для Redis

### **Бізнес метрики**
- **User engagement** metrics
- **Feature usage** statistics
- **Revenue tracking** per plan
- **Churn rate** analysis
- **Conversion rates** для планів

### **Інфраструктурні метрики**
- **CPU/Memory usage** per service
- **Disk space** utilization
- **Network traffic** patterns
- **Container health** status
- **Database connections** pool

### **Алерти та сповіщення**
- **Critical errors** → Slack/Email
- **Performance degradation** → PagerDuty
- **Security incidents** → Security team
- **Infrastructure issues** → DevOps team

---

## Розгортання

### **Пов'язані таски**
- **UI-001 до UI-005**: [Web Interface](MASTER_TASKS.md#ui---веб-інтерфейс)
        [Web Interface Module](details/modules/web_interface/web_interface_module.md)
        [Web Interface Plan](details/modules/web_interface/implementation_plan.md)

- **Deployment**: [Docker Configuration](details/technical_details/deployment/docker_configuration.md)
        [CI/CD Pipeline](details/technical_details/deployment/ci_cd_pipeline.md)

### **Docker контейнеризація**
```yaml
# docker-compose.yml
version: '3.8'
services:
  api-gateway:
    build: ./api-gateway
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/upwork_app
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
  
  auth-service:
    build: ./auth-service
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/upwork_app
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
  
  ai-service:
    build: ./ai-service
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - REDIS_URL=redis://redis:6379
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=upwork_app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### **Kubernetes розгортання**
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: upwork-ai-assistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: upwork-ai-assistant
  template:
    metadata:
      labels:
        app: upwork-ai-assistant
    spec:
      containers:
      - name: api-gateway
        image: upwork-ai-assistant:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
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
      run: pytest
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: kubectl apply -f k8s/
```

---

## Швидкі посилання

- [📋 MASTER_TASKS.md](MASTER_TASKS.md) - Всі завдання проекту
- [🚀 PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Загальний огляд проекту
- [🧪 TESTING.md](TESTING.md) - План тестування
- [📚 GUIDES.md](GUIDES.md) - Гайди та інструкції
- [🧭 NAVIGATION.md](NAVIGATION.md) - Навігація по документації

**Детальні архітектурні файли**: [details/architecture/](details/architecture/)

---

**Статус**: Створено  
**Версія**: 1.0.0 