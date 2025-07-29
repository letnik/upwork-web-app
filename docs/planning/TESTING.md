# 🧪 TESTING - План тестування

> **Комплексна стратегія тестування Upwork AI Assistant**

---

## Зміст

1. [Стратегія тестування](#стратегія-тестування)
2. [Unit тести](#unit-тести)
3. [Integration тести](#integration-тести)
4. [E2E тести](#e2e-тести)
5. [Performance тести](#performance-тести)
6. [Security тести](#security-тести)
7. [Тестова інфраструктура](#тестова-інфраструктура)

---

## Стратегія тестування

### **Піраміда тестування**
```
                    ┌─────────────────┐
                    │   E2E Tests     │ ← 10% (Критичні сценарії)
                    │   (Manual)      │
                    └─────────────────┘
                           │
                    ┌─────────────────┐
                    │ Integration     │ ← 20% (API, Database)
                    │   Tests         │
                    └─────────────────┘
                           │
                    ┌─────────────────┐
                    │   Unit Tests    │ ← 70% (Функції, класи)
                    │   (Automated)   │
                    └─────────────────┘
```

### **Принципи тестування**
- **Test-Driven Development (TDD)** для критичних компонентів
- **Automated testing** для 90% тестів
- **Continuous testing** в CI/CD pipeline
- **Test coverage** > 90% для backend
- **Performance testing** для всіх API endpoints

### **Технологічний стек**
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Frontend**: React 18+, TypeScript, Material-UI
- **Database**: PostgreSQL 15+, Redis 7+
- **AI**: OpenAI GPT-4, Claude, Scikit-learn
- **Infrastructure**: Docker, Kubernetes, DigitalOcean/AWS

---

## 🧪 Unit тести

> 📖 **Детальний план**: [Unit Test Plan](details/testing/unit_tests/unit_test_plan.md)

### **Пов'язані таски**
- **AUTH-001**: [Тестування авторизації](MASTER_TASKS.md#auth---авторизація-та-аутентифікація)
        [Auth тести](details/testing/unit_tests/unit_test_plan.md#auth-тести)

- **AI-001**: [Тестування AI](MASTER_TASKS.md#ai---штучний-інтелект)
        [AI тести](details/testing/unit_tests/unit_test_plan.md#ai-тести)

- **UPWORK-001**: [Тестування Upwork API](MASTER_TASKS.md#upwork---інтеграція-з-upwork)
        [API тести](details/testing/unit_tests/unit_test_plan.md#api-тести)

- **SECURITY-001**: [Тестування безпеки](MASTER_TASKS.md#security---безпека)
        [Security тести](details/testing/unit_tests/unit_test_plan.md#security-тести)

### **Backend тести (Python)**
```python
# tests/test_ai_service.py
import pytest
from unittest.mock import patch
from src.services.ai_service import AIService

class TestAIService:
    def setup_method(self):
        self.ai_service = AIService()
    
    @patch('openai.ChatCompletion.create')
    def mock_openai(self):
        with patch('openai.ChatCompletion.create') as mock:
            mock.return_value.choices[0].message.content = "Test proposal"
            yield mock
    
    def test_generate_proposal_success(self, ai_service, mock_openai):
        job_data = {
            'title': 'Python Developer',
            'description': 'We need a Python developer',
            'budget': {'min': 1000, 'max': 5000},
            'skills': ['Python', 'Django']
        }
        
        result = ai_service.generate_proposal(job_data)
        
        assert result is not None
        assert len(result) > 100
        mock_openai.assert_called_once()
    
    def test_generate_proposal_empty_job(self, ai_service):
        with pytest.raises(ValueError):
            ai_service.generate_proposal({})
    
    def test_generate_proposal_invalid_budget(self, ai_service):
        job_data = {
            'title': 'Test Job',
            'budget': {'min': 5000, 'max': 1000}  # Invalid range
        }
        
        with pytest.raises(ValueError):
            ai_service.generate_proposal(job_data)
```

### **Frontend тести (React)**
```typescript
// tests/components/JobCard.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import JobCard from '../components/JobCard';

const mockJob = {
  id: '1',
  title: 'React Developer',
  description: 'We need a React developer',
  budget: { min: 2000, max: 5000 },
  skills: ['React', 'TypeScript']
};

describe('JobCard Component', () => {
  test('renders job information correctly', () => {
    render(<JobCard job={mockJob} />);
    
    expect(screen.getByText('React Developer')).toBeInTheDocument();
    expect(screen.getByText('We need a React developer')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
  });
  
  test('handles apply button click', () => {
    const mockOnApply = jest.fn();
    render(<JobCard job={mockJob} onApply={mockOnApply} />);
    
    fireEvent.click(screen.getByText('Apply'));
    expect(mockOnApply).toHaveBeenCalledWith(mockJob.id);
  });
});
```

### **Database тести**
```python
# tests/test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, User, Job

class TestDatabase:
    @pytest.fixture
    def db_session(self):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_create_user(self, db_session):
        user = User(
            email='test@example.com',
            password_hash='hashed_password'
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == 'test@example.com'
    
    def test_user_job_relationship(self, db_session):
        user = User(email='test@example.com')
        job = Job(title='Test Job', user_id=user.id)
        
        db_session.add_all([user, job])
        db_session.commit()
        
        assert job.user_id == user.id
        assert len(user.jobs) == 1
```

---

## Integration тести

> 📖 **Детальний план**: [Integration Test Plan](details/testing/integration_tests/integration_test_plan.md)

### **API тести**
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestAPI:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_job_search(self):
        response = client.get("/api/v1/upwork/jobs?q=python")
        assert response.status_code == 200
        assert "jobs" in response.json()
    
    def test_proposal_generation(self):
        job_data = {
            "title": "Python Developer",
            "description": "We need a Python developer",
            "budget": {"min": 1000, "max": 5000}
        }
        
        response = client.post("/api/v1/ai/generate", json=job_data)
        assert response.status_code == 200
        assert "proposal" in response.json()
    
    def test_unauthorized_access(self):
        response = client.get("/api/v1/users/profile")
        assert response.status_code == 401
```

### **Database Integration тести**
```python
# tests/test_integration.py
import pytest
from src.database.connection import get_db
from src.services.job_service import JobService

class TestJobServiceIntegration:
    def test_job_creation_and_retrieval(self, db_session):
        job_service = JobService(db_session)
        
# Create job
        job_data = {
            'title': 'Integration Test Job',
            'description': 'Test description',
            'budget_min': 1000,
            'budget_max': 5000
        }
        
        job = job_service.create_job(job_data)
        assert job.id is not None
        
# Retrieve job
        retrieved_job = job_service.get_job(job.id)
        assert retrieved_job.title == 'Integration Test Job'
    
    def test_job_search_integration(self, db_session):
        job_service = JobService(db_session)
        
# Create multiple jobs
        jobs_data = [
            {'title': 'Python Job', 'description': 'Python developer needed'},
            {'title': 'React Job', 'description': 'React developer needed'},
            {'title': 'Full Stack Job', 'description': 'Full stack developer needed'}
        ]
        
        for job_data in jobs_data:
            job_service.create_job(job_data)
        
# Search for Python jobs
        python_jobs = job_service.search_jobs('Python')
        assert len(python_jobs) == 1
        assert python_jobs[0].title == 'Python Job'
```

---

## E2E тести

> 📖 **Детальний план**: [E2E Test Plan](details/testing/e2e_tests/e2e_test_plan.md)

### **Пов'язані таски**
- **UI-001**: [Dashboard layout](MASTER_TASKS.md#ui---веб-інтерфейс)
        [UI тести](details/testing/e2e_tests/e2e_test_plan.md#ui-тести)

- **UI-002**: [Job search interface](MASTER_TASKS.md#ui---веб-інтерфейс)
        [Пошук вакансій](details/testing/e2e_tests/e2e_test_plan.md#пошук-вакансій)

- **UI-003**: [Proposal creation](MASTER_TASKS.md#ui---веб-інтерфейс)
        [Створення пропозицій](details/testing/e2e_tests/e2e_test_plan.md#створення-пропозицій)

- **AUTH-003**: [OAuth 2.0 flow](MASTER_TASKS.md#auth---авторизація-та-аутентифікація)
        [Авторизація](details/testing/e2e_tests/e2e_test_plan.md#авторизація)

### **Playwright тести**
```typescript
// tests/e2e/job-search.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Job Search E2E', () => {
  test('user can search and apply for jobs', async ({ page }) => {
    // Navigate to job search page
    await page.goto('/jobs');
    
    // Search for jobs
    await page.fill('[data-testid="job-search"]', 'React Developer');
    await page.click('[data-testid="search-button"]');
    
    // Wait for results
    await page.waitForSelector('[data-testid="job-card"]');
    
    // Verify results
    const jobCards = await page.locator('[data-testid="job-card"]');
    expect(await jobCards.count()).toBeGreaterThan(0);
    
    // Click on first job
    await jobCards.first().click();
    
    // Verify job details page
    await expect(page.locator('[data-testid="job-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="apply-button"]')).toBeVisible();
    
    // Apply for job
    await page.click('[data-testid="apply-button"]');
    
    // Verify application form
    await expect(page.locator('[data-testid="proposal-form"]')).toBeVisible();
  });
  
  test('user can generate AI proposal', async ({ page }) => {
    await page.goto('/jobs/1/apply');
    
    // Fill proposal form
    await page.fill('[data-testid="cover-letter"]', 'I am interested in this position');
    
    // Generate AI proposal
    await page.click('[data-testid="generate-ai-proposal"]');
    
    // Wait for AI generation
    await page.waitForSelector('[data-testid="ai-proposal"]');
    
    // Verify AI proposal
    const aiProposal = await page.locator('[data-testid="ai-proposal"]');
    expect(await aiProposal.textContent()).toContain('I am');
  });
});
```

### **Cypress тести**
```javascript
// cypress/e2e/auth.cy.js
describe('Authentication', () => {
  it('user can register and login', () => {
    // Register
    cy.visit('/register');
    cy.get('[data-testid="email"]').type('test@example.com');
    cy.get('[data-testid="password"]').type('password123');
    cy.get('[data-testid="register-button"]').click();
    
    // Verify registration success
    cy.url().should('include', '/dashboard');
    
    // Logout
    cy.get('[data-testid="logout-button"]').click();
    
    // Login
    cy.visit('/login');
    cy.get('[data-testid="email"]').type('test@example.com');
    cy.get('[data-testid="password"]').type('password123');
    cy.get('[data-testid="login-button"]').click();
    
    // Verify login success
    cy.url().should('include', '/dashboard');
  });
});
```

---

## Performance тести

> 📖 **Детальний план**: [Performance Test Plan](details/testing/performance_tests/performance_test_plan.md)

### **Load тести**
```python
# tests/performance/test_load.py
import asyncio
import aiohttp
import time
from locust import HttpUser, task, between

class UpworkAIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
# Login user
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def search_jobs(self):
        self.client.get("/api/v1/upwork/jobs?q=python")
    
    @task(2)
    def generate_proposal(self):
        self.client.post("/api/v1/ai/generate", json={
            "title": "Python Developer",
            "description": "We need a Python developer",
            "budget": {"min": 1000, "max": 5000}
        })
    
    @task(1)
    def get_analytics(self):
        self.client.get("/api/v1/analytics/metrics")
```

### **Stress тести**
```python
# tests/performance/test_stress.py
import pytest
import asyncio
import aiohttp
from src.main import app
from fastapi.testclient import TestClient

class TestStress:
    @pytest.mark.asyncio
    async def test_concurrent_job_searches(self):
        client = TestClient(app)
        
# Simulate 100 concurrent requests
        async def make_request():
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/api/v1/upwork/jobs?q=python") as response:
                    return response.status
        
        tasks = [make_request() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        
# Verify all requests succeeded
        assert all(status == 200 for status in results)
    
    @pytest.mark.asyncio
    async def test_database_connection_pool(self):
# Test database connection pool under load
        client = TestClient(app)
        
        async def create_user():
            return client.post("/api/v1/auth/register", json={
                "email": f"test{time.time()}@example.com",
                "password": "password123"
            })
        
        tasks = [create_user() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
# Verify most requests succeeded
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count >= 45  # 90% success rate
```

---

## Security тести

> 📖 **Детальний план**: [Security Test Plan](details/testing/security_tests/security_test_plan.md)

### **Authentication тести**
```python
# tests/security/test_auth.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestSecurity:
    def test_jwt_token_validation(self):
# Test with invalid token
        response = client.get("/api/v1/users/profile", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401
    
    def test_password_hashing(self):
        from src.services.auth_service import hash_password, verify_password
        
        password = "test_password"
        hashed = hash_password(password)
        
# Verify password is hashed
        assert hashed != password
        assert verify_password(password, hashed) == True
        assert verify_password("wrong_password", hashed) == False
    
    def test_sql_injection_prevention(self):
# Test SQL injection attempts
        malicious_input = "'; DROP TABLE users; --"
        
        response = client.get(f"/api/v1/upwork/jobs?q={malicious_input}")
        assert response.status_code == 200  # Should not crash
    
    def test_xss_prevention(self):
# Test XSS attempts
        malicious_input = "<script>alert('xss')</script>"
        
        response = client.post("/api/v1/ai/generate", json={
            "title": malicious_input,
            "description": "Test description"
        })
        
# Verify response doesn't contain script tags
        assert "<script>" not in response.text
```

### **API Security тести**
```python
# tests/security/test_api_security.py
import pytest
from fastapi.testclient import TestClient

class TestAPISecurity:
    def test_rate_limiting(self, client):
# Make multiple requests quickly
        for _ in range(10):
            response = client.get("/api/v1/upwork/jobs?q=python")
        
# Should be rate limited
        assert response.status_code == 429
    
    def test_cors_headers(self, client):
        response = client.options("/api/v1/upwork/jobs", headers={
            "Origin": "https://malicious-site.com"
        })
        
# Should not allow unauthorized origins
        assert "Access-Control-Allow-Origin" not in response.headers
    
    def test_input_validation(self, client):
# Test with invalid input
        response = client.post("/api/v1/auth/register", json={
            "email": "invalid-email",
            "password": "123"  # Too short
        })
        
        assert response.status_code == 422  # Validation error
```

---

## Тестова інфраструктура

### **Test Environment**
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test-db:
    image: postgres:15
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5433:5432"
  
  test-redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
  
  test-app:
    build: .
    environment:
      DATABASE_URL: postgresql://test_user:test_password@test-db:5432/test_db
      REDIS_URL: redis://test-redis:6379
      TESTING: true
    depends_on:
      - test-db
      - test-redis
```

### **CI/CD Pipeline**
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

### **Test Data Management**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

@pytest.fixture(scope="session")
def engine():
    engine = create_engine("postgresql://test_user:test_password@localhost:5433/test_db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_user(db_session):
    user = User(email="test@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_job(db_session, sample_user):
    job = Job(
        title="Test Job",
        description="Test Description",
        user_id=sample_user.id
    )
    db_session.add(job)
    db_session.commit()
    return job
```

---

## Метрики тестування

### **Coverage метрики**
- **Backend coverage**: > 90%
- **Frontend coverage**: > 80%
- **API coverage**: > 95%
- **Critical path coverage**: 100%

### **Performance метрики**
- **API response time**: < 200ms (95th percentile)
- **Database query time**: < 50ms
- **Memory usage**: < 512MB per service
- **CPU usage**: < 70% under load

### **Quality метрики**
- **Test reliability**: > 99%
- **False positive rate**: < 1%
- **Test execution time**: < 10 minutes
- **Maintenance overhead**: < 20% of development time

---

## Швидкі посилання

- [📋 MASTER_TASKS.md](MASTER_TASKS.md) - Всі завдання проекту
- [🚀 PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Загальний огляд проекту
- [🏗️ ARCHITECTURE.md](ARCHITECTURE.md) - Архітектура системи
- [📚 GUIDES.md](GUIDES.md) - Гайди та інструкції
- [🧭 NAVIGATION.md](NAVIGATION.md) - Навігація по документації

**Детальні тестові файли**: [details/testing/](details/testing/)

---

**Статус**: Створено  
**Версія**: 1.0.0 