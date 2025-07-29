# Технічна специфікація Upwork AI Assistant

> **Детальна технічна документація на основі всіх готових відповідей та рекомендацій**

---

## Зміст

1. [Архітектура системи](#архітектура-системи)
2. [API специфікації](#api-специфікації)
3. [База даних](#база-даних)
4. [AI інтеграція](#ai-інтеграція)
5. [Upwork інтеграція](#upwork-інтеграція)
6. [Безпека](#безпека)
7. [Продуктивність](#продуктивність)
8. [Моніторинг](#моніторинг)
9. [DevOps](#devops)
10. [Тестування](#тестування)

---

## Архітектура системи

### **Мікросервісна архітектура**

#### **Сервіси**
1. **API Gateway** (FastAPI)
   - Роутинг та load balancing
   - Rate limiting та authentication
   - Request/response трансформація
   - API documentation (OpenAPI/Swagger)

2. **Auth Service** (Python/FastAPI)
   - JWT token management
   - OAuth 2.0 integration
   - User session management
   - MFA support

3. **AI Service** (Python/FastAPI)
   - OpenAI GPT-4 integration
   - Claude fallback
   - Response caching
   - Prompt engineering

4. **Upwork Service** (Python/FastAPI)
   - Upwork API integration
   - OAuth 2.0 flow
   - Data synchronization
   - Webhook handling

5. **Analytics Service** (Python/FastAPI)
   - Data processing pipeline
   - Business intelligence
   - Real-time analytics
   - Report generation

6. **Frontend** (React/TypeScript)
   - Material-UI components
   - Responsive design
   - Progressive Web App
   - Offline support

### **Технологічний стек**

#### **Backend**
- **Python 3.11+** з type hints
- **FastAPI** для API development
- **SQLAlchemy 2.0** для ORM
- **Pydantic** для data validation
- **Celery** для background tasks
- **Redis** для caching та sessions

#### **Frontend**
- **React 18+** з hooks
- **TypeScript** для type safety
- **Material-UI** для design system
- **React Query** для state management
- **React Router** для navigation
- **Webpack** для bundling

#### **Database**
- **PostgreSQL 15+** як основна БД
- **Redis 7+** для caching
- **Elasticsearch** для пошуку
- **MongoDB** для логів
- **S3** для файлового зберігання

#### **Infrastructure**
- **Docker** для containerization
- **Kubernetes** для orchestration
- **DigitalOcean** для hosting
- **AWS** для масштабування
- **CloudFlare** для CDN

---

## API специфікації

### **REST API Endpoints**

#### **Authentication**
```http
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
POST /api/v1/auth/register
GET  /api/v1/auth/profile
PUT  /api/v1/auth/profile
```

#### **Upwork Integration**
```http
GET  /api/v1/upwork/jobs
GET  /api/v1/upwork/jobs/{job_id}
POST /api/v1/upwork/proposals
GET  /api/v1/upwork/proposals
PUT  /api/v1/upwork/proposals/{proposal_id}
DELETE /api/v1/upwork/proposals/{proposal_id}
```

#### **AI Services**
```http
POST /api/v1/ai/generate-cover-letter
POST /api/v1/ai/analyze-job
POST /api/v1/ai/smart-filter
GET  /api/v1/ai/templates
POST /api/v1/ai/templates
```

#### **Analytics**
```http
GET  /api/v1/analytics/dashboard
GET  /api/v1/analytics/jobs
GET  /api/v1/analytics/proposals
GET  /api/v1/analytics/revenue
GET  /api/v1/analytics/performance
```

### **WebSocket Events**
```javascript
// Real-time job notifications
socket.on('new_job', (job) => {})
socket.on('job_updated', (job) => {})
socket.on('proposal_status', (status) => {})

// AI generation progress
socket.on('ai_progress', (progress) => {})
socket.on('ai_complete', (result) => {})
```

### **API Response Format**
```json
{
  "success": true,
  "data": {},
  "message": "Success",
  "timestamp": "2024-12-19T19:30:00Z",
  "request_id": "uuid"
}
```

---

## База даних

### **PostgreSQL Schema**

#### **Users Table**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    upwork_user_id VARCHAR(100),
    subscription_plan VARCHAR(20) DEFAULT 'free',
    api_usage_count INTEGER DEFAULT 0,
    api_usage_limit INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);
```

#### **API Keys Table**
```sql
CREATE TABLE user_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    provider VARCHAR(50) NOT NULL, -- 'openai', 'claude'
    api_key_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### **Jobs Table**
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upwork_job_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    skills TEXT[],
    category VARCHAR(100),
    subcategory VARCHAR(100),
    client_info JSONB,
    job_type VARCHAR(50), -- 'hourly', 'fixed'
    experience_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

#### **Proposals Table**
```sql
CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    job_id UUID REFERENCES jobs(id),
    cover_letter TEXT,
    bid_amount DECIMAL(10,2),
    estimated_hours INTEGER,
    status VARCHAR(50) DEFAULT 'draft',
    ai_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### **AI Generations Table**
```sql
CREATE TABLE ai_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    job_id UUID REFERENCES jobs(id),
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    model VARCHAR(50) NOT NULL,
    tokens_used INTEGER,
    cost DECIMAL(10,6),
    quality_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **Redis Keys Structure**
```
# User sessions
session:{user_id} -> session_data

# API rate limiting
rate_limit:{user_id}:{endpoint} -> count

# AI response cache
ai_cache:{hash} -> cached_response

# Job cache
job_cache:{job_id} -> job_data

# Real-time notifications
notifications:{user_id} -> notification_queue
```

---

## 🤖 AI інтеграція

### **AI Models Configuration**

#### **Primary AI Provider (OpenAI)**
```python
AI_CONFIG = {
    "primary": {
        "provider": "openai",
        "model": "gpt-4",
        "max_tokens": 2000,
        "temperature": 0.7,
        "fallback_model": "gpt-3.5-turbo"
    },
    "secondary": {
        "provider": "anthropic",
        "model": "claude-3-sonnet",
        "max_tokens": 2000,
        "temperature": 0.7
    },
    "ml": {
        "provider": "scikit-learn",
        "models": ["job_classifier", "skill_matcher", "salary_predictor"]
    }
}
```

#### **Prompt Templates**
```python
COVER_LETTER_TEMPLATE = """
You are an expert freelancer writing a cover letter for an Upwork job.

Job Title: {job_title}
Job Description: {job_description}
Client Budget: {budget}
Required Skills: {skills}

User Profile:
- Experience: {user_experience}
- Skills: {user_skills}
- Portfolio: {user_portfolio}

Write a compelling cover letter that:
1. Addresses the client's specific needs
2. Highlights relevant experience
3. Shows understanding of the project
4. Includes a clear call to action
5. Stays within 300-500 words

Tone: Professional, confident, and solution-oriented
"""

JOB_ANALYSIS_TEMPLATE = """
Analyze this Upwork job posting and provide insights:

Job: {job_title}
Description: {job_description}
Budget: {budget}
Skills: {skills}

Provide analysis on:
1. Difficulty level (1-10)
2. Competition level (1-10)
3. Budget adequacy (1-10)
4. Required skills match
5. Project complexity
6. Client reliability indicators
7. Recommended bid range
8. Success probability
"""
```

### **AI Service Implementation**
```python
class AIService:
    def __init__(self):
        self.openai_client = OpenAI()
        self.claude_client = Anthropic()
        self.cache = RedisCache()
    
    async def generate_cover_letter(self, job_data, user_profile):
# Check cache first
        cache_key = self._generate_cache_key(job_data, user_profile)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
# Generate with primary model
        try:
            response = await self._generate_with_openai(job_data, user_profile)
        except Exception:
# Fallback to Claude
            response = await self._generate_with_claude(job_data, user_profile)
        
# Cache result
        await self.cache.set(cache_key, response, ttl=3600)
        return response
    
    async def analyze_job(self, job_data):
# Use ML models for analysis
        difficulty = await self.ml_classifier.predict_difficulty(job_data)
        competition = await self.ml_classifier.predict_competition(job_data)
        budget_adequacy = await self.ml_classifier.predict_budget_adequacy(job_data)
        
        return {
            "difficulty": difficulty,
            "competition": competition,
            "budget_adequacy": budget_adequacy,
            "recommended_bid": self._calculate_recommended_bid(job_data),
            "success_probability": self._calculate_success_probability(job_data)
        }
```

---

## Upwork інтеграція

### **OAuth 2.0 Configuration**
```python
UPWORK_CONFIG = {
    "client_id": os.getenv("UPWORK_CLIENT_ID"),
    "client_secret": os.getenv("UPWORK_CLIENT_SECRET"),
    "redirect_uri": os.getenv("UPWORK_CALLBACK_URL"),
    "authorization_url": "https://www.upwork.com/services/api/auth",
    "token_url": "https://www.upwork.com/api/auth/v1/oauth/token",
    "scope": "jobs proposals messages contracts payments"
}
```

### **API Rate Limiting**
```python
class UpworkRateLimiter:
    def __init__(self):
        self.redis = Redis()
        self.limits = {
            "jobs": {"requests": 1000, "window": 3600},  # 1000/hour
            "proposals": {"requests": 100, "window": 3600},  # 100/hour
            "messages": {"requests": 500, "window": 3600}   # 500/hour
        }
    
    async def check_rate_limit(self, user_id, endpoint):
        key = f"rate_limit:{user_id}:{endpoint}"
        current = await self.redis.incr(key)
        
        if current == 1:
            await self.redis.expire(key, self.limits[endpoint]["window"])
        
        if current > self.limits[endpoint]["requests"]:
            raise RateLimitExceeded(f"Rate limit exceeded for {endpoint}")
        
        return True
```

### **Data Synchronization**
```python
class UpworkSyncService:
    def __init__(self):
        self.upwork_api = UpworkAPI()
        self.db = Database()
    
    async def sync_jobs(self, user_id, filters=None):
        """Sync jobs from Upwork API"""
        jobs = await self.upwork_api.get_jobs(filters)
        
        for job in jobs:
            await self.db.upsert_job(job)
        
        return len(jobs)
    
    async def sync_proposals(self, user_id):
        """Sync user proposals"""
        proposals = await self.upwork_api.get_proposals(user_id)
        
        for proposal in proposals:
            await self.db.upsert_proposal(proposal)
        
        return len(proposals)
    
    async def handle_webhook(self, event_type, data):
        """Handle Upwork webhooks"""
        if event_type == "job.created":
            await self.db.create_job(data)
        elif event_type == "proposal.updated":
            await self.db.update_proposal(data)
```

---

## Безпека

### **Authentication & Authorization**
```python
class SecurityConfig:
# JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION = 3600  # 1 hour
    JWT_REFRESH_EXPIRATION = 604800  # 7 days
    
# Password Security
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
# API Key Security
    API_KEY_ENCRYPTION_KEY = os.getenv("API_KEY_ENCRYPTION_KEY")
    API_KEY_ALGORITHM = "AES-256-GCM"
```

### **Data Encryption**
```python
class EncryptionService:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY")
        self.cipher = AES.new(self.key, AES.MODE_GCM)
    
    def encrypt_api_key(self, api_key):
        """Encrypt user API keys"""
        ciphertext, tag = self.cipher.encrypt_and_digest(api_key.encode())
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "tag": base64.b64encode(tag).decode(),
            "nonce": base64.b64encode(self.cipher.nonce).decode()
        }
    
    def decrypt_api_key(self, encrypted_data):
        """Decrypt user API keys"""
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        tag = base64.b64decode(encrypted_data["tag"])
        nonce = base64.b64decode(encrypted_data["nonce"])
        
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
```

### **GDPR Compliance**
```python
class GDPRService:
    async def export_user_data(self, user_id):
        """Export all user data for GDPR compliance"""
        user_data = await self.db.get_user_data(user_id)
        return {
            "user": user_data["profile"],
            "jobs": user_data["jobs"],
            "proposals": user_data["proposals"],
            "ai_generations": user_data["ai_generations"],
            "analytics": user_data["analytics"]
        }
    
    async def delete_user_data(self, user_id):
        """Delete user data (right to be forgotten)"""
        await self.db.anonymize_user(user_id)
        await self.db.delete_user_data(user_id)
        await self.cache.delete_user_data(user_id)
    
    async def get_data_processing_info(self, user_id):
        """Get information about data processing"""
        return {
            "data_collected": ["profile", "jobs", "proposals", "analytics"],
            "purpose": ["service_provision", "analytics", "improvement"],
            "retention_period": "2 years for active users",
            "data_sharing": ["Upwork API", "AI providers"],
            "user_rights": ["access", "rectification", "erasure", "portability"]
        }
```

---

## Продуктивність

### **Performance Requirements**
```python
PERFORMANCE_CONFIG = {
    "api_response_time": {
        "p50": "< 200ms",
        "p95": "< 500ms",
        "p99": "< 1000ms"
    },
    "database_queries": {
        "read": "< 50ms",
        "write": "< 100ms",
        "cache_hit_rate": "> 80%"
    },
    "frontend_loading": {
        "first_paint": "< 1.5s",
        "time_to_interactive": "< 3s",
        "bundle_size": "< 500KB"
    },
    "concurrent_users": {
        "mvp": 1000,
        "production": 10000,
        "enterprise": 50000
    }
}
```

### **Caching Strategy**
```python
class CacheService:
    def __init__(self):
        self.redis = Redis()
        self.ttl_config = {
            "job_data": 300,      # 5 minutes
            "ai_responses": 3600, # 1 hour
            "user_sessions": 86400, # 24 hours
            "analytics": 1800     # 30 minutes
        }
    
    async def get_cached_job(self, job_id):
        """Get job data from cache"""
        cache_key = f"job:{job_id}"
        cached = await self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
# Fetch from database
        job = await self.db.get_job(job_id)
        if job:
            await self.redis.setex(
                cache_key, 
                self.ttl_config["job_data"], 
                json.dumps(job)
            )
        
        return job
    
    async def cache_ai_response(self, prompt_hash, response):
        """Cache AI response for similar prompts"""
        cache_key = f"ai:{prompt_hash}"
        await self.redis.setex(
            cache_key,
            self.ttl_config["ai_responses"],
            json.dumps(response)
        )
```

### **Database Optimization**
```sql
-- Indexes for performance
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_jobs_budget ON jobs(budget_min, budget_max);
CREATE INDEX idx_jobs_created ON jobs(created_at);
CREATE INDEX idx_proposals_user ON proposals(user_id);
CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_ai_generations_user ON ai_generations(user_id);

-- Partitioning for large tables
CREATE TABLE ai_generations_partitioned (
    LIKE ai_generations INCLUDING ALL
) PARTITION BY RANGE (created_at);

CREATE TABLE ai_generations_2024 PARTITION OF ai_generations_partitioned
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

---

## Моніторинг

### **Application Monitoring**
```python
class MonitoringService:
    def __init__(self):
        self.prometheus = PrometheusClient()
        self.grafana = GrafanaClient()
        self.alerting = AlertingService()
    
    async def track_api_metrics(self, endpoint, response_time, status_code):
        """Track API performance metrics"""
        self.prometheus.histogram(
            "api_response_time_seconds",
            response_time,
            labels={"endpoint": endpoint}
        )
        
        self.prometheus.counter(
            "api_requests_total",
            labels={"endpoint": endpoint, "status": status_code}
        )
    
    async def track_ai_metrics(self, model, tokens_used, cost, quality_score):
        """Track AI usage metrics"""
        self.prometheus.counter(
            "ai_requests_total",
            labels={"model": model}
        )
        
        self.prometheus.histogram(
            "ai_cost_usd",
            cost,
            labels={"model": model}
        )
        
        self.prometheus.histogram(
            "ai_quality_score",
            quality_score,
            labels={"model": model}
        )
    
    async def check_alerts(self):
        """Check and send alerts"""
        alerts = await self.alerting.check_alerts()
        for alert in alerts:
            await self.send_alert(alert)
```

### **Business Metrics**
```python
class BusinessMetrics:
    async def calculate_mrr(self):
        """Calculate Monthly Recurring Revenue"""
        active_subscriptions = await self.db.get_active_subscriptions()
        mrr = sum(sub.amount for sub in active_subscriptions)
        return mrr
    
    async def calculate_churn_rate(self):
        """Calculate monthly churn rate"""
        total_users = await self.db.get_total_users()
        churned_users = await self.db.get_churned_users()
        churn_rate = churned_users / total_users * 100
        return churn_rate
    
    async def calculate_ltv(self):
        """Calculate Lifetime Value"""
        avg_subscription_value = await self.db.get_avg_subscription_value()
        avg_subscription_length = await self.db.get_avg_subscription_length()
        ltv = avg_subscription_value * avg_subscription_length
        return ltv
```

---

## DevOps

### **Docker Configuration**
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/upwork_ai
      - REDIS_URL=redis://redis:6379
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
    image: postgres:15
    environment:
      - POSTGRES_DB=upwork_ai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### **CI/CD Pipeline**
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t upwork-ai .
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push upwork-ai:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
# Deploy to DigitalOcean/AWS
          kubectl apply -f k8s/
```

---

## 🧪 Тестування

### **Testing Strategy**
```python
# Test configuration
TEST_CONFIG = {
    "unit_tests": {
        "coverage": "> 80%",
        "frameworks": ["pytest", "pytest-asyncio"],
        "focus": ["business_logic", "data_validation"]
    },
    "integration_tests": {
        "coverage": "> 60%",
        "frameworks": ["pytest", "testcontainers"],
        "focus": ["api_endpoints", "database_operations"]
    },
    "e2e_tests": {
        "coverage": "> 40%",
        "frameworks": ["playwright", "selenium"],
        "focus": ["user_flows", "critical_paths"]
    }
}
```

### **Test Examples**
```python
# Unit test example
class TestAIService:
    @pytest.mark.asyncio
    async def test_generate_cover_letter(self):
        service = AIService()
        job_data = {"title": "Python Developer", "description": "..."}
        user_profile = {"skills": ["Python", "Django"]}
        
        result = await service.generate_cover_letter(job_data, user_profile)
        
        assert result is not None
        assert len(result) > 100
        assert "Python" in result

# Integration test example
class TestUpworkIntegration:
    @pytest.mark.asyncio
    async def test_sync_jobs(self):
        service = UpworkSyncService()
        user_id = "test_user"
        
        jobs_count = await service.sync_jobs(user_id)
        
        assert jobs_count > 0
# Verify jobs are saved in database

# E2E test example
class TestUserFlow:
    def test_complete_user_flow(self, browser):
# Login
        page = browser.new_page()
        page.goto("/login")
        page.fill("#email", "test@example.com")
        page.fill("#password", "password")
        page.click("#login-button")
        
# Search jobs
        page.goto("/jobs")
        page.fill("#search", "Python")
        page.click("#search-button")
        
# Generate cover letter
        page.click(".job-card:first-child")
        page.click("#generate-cover-letter")
        
# Verify result
        assert page.locator(".cover-letter").is_visible()
```

---

**Статус**: Створено на основі всіх готових відповідей  
**Пріоритет**: Критичний  
**Останнє оновлення**: 2024-12-19 19:30 