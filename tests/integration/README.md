# 🔗 Integration Tests

> **Тестування взаємодії між компонентами системи**

---

## 📋 **Огляд**

Integration тести перевіряють взаємодію між різними компонентами системи:
- API Gateway ↔ Services
- Services ↔ Database
- Services ↔ External APIs
- Frontend ↔ Backend APIs

---

## 🏗️ **Архітектура**

```
tests/integration/
├── api_gateway/                   # API Gateway інтеграція
│   ├── test_auth_integration.py  # Auth service інтеграція
│   ├── test_analytics_integration.py # Analytics service інтеграція
│   └── test_ai_integration.py    # AI service інтеграція
├── auth_service/                  # Auth service інтеграція
│   ├── test_oauth_integration.py # OAuth інтеграція
│   ├── test_mfa_integration.py   # MFA інтеграція
│   └── test_jwt_integration.py   # JWT інтеграція
├── analytics_service/             # Analytics service інтеграція
│   ├── test_data_integration.py  # Data інтеграція
│   └── test_export_integration.py # Export інтеграція
├── ai_service/                    # AI service інтеграція
│   ├── test_openai_integration.py # OpenAI інтеграція
│   └── test_analysis_integration.py # Analysis інтеграція
├── database/                      # Database інтеграція
│   ├── test_postgres_integration.py # PostgreSQL інтеграція
│   └── test_redis_integration.py # Redis інтеграція
└── external_apis/                 # Зовнішні API інтеграція
    ├── test_upwork_integration.py # Upwork API інтеграція
    └── test_oauth_providers.py   # OAuth провайдери
```

---

## 🚀 **Запуск тестів**

```bash
# Всі integration тести
./tools/scripts/testing/run_tests.sh integration

# Конкретні integration тести
pytest tests/integration/api_gateway/ -v
pytest tests/integration/auth_service/ -v
pytest tests/integration/analytics_service/ -v
```

---

## 📊 **Покриття**

### **Планується покриття:**
- **API Gateway**: 90%
- **Auth Service**: 95%
- **Analytics Service**: 85%
- **AI Service**: 80%
- **Database**: 90%
- **External APIs**: 75%

---

## 🔧 **Налаштування**

### **Конфігурація:**
```python
# tests/integration/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.backend.api_gateway.src.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}
```

### **Моки для зовнішніх сервісів:**
```python
# tests/integration/mocks/
├── upwork_api_mock.py
├── openai_api_mock.py
├── oauth_providers_mock.py
└── database_mock.py
```

---

## 📋 **Чекліст**

### **Перед створенням integration тесту:**
- [ ] Визначити компоненти для інтеграції
- [ ] Створити моки для зовнішніх залежностей
- [ ] Налаштувати тестове середовище
- [ ] Визначити сценарії тестування
- [ ] Документувати очікувані результати

### **Під час написання тесту:**
- [ ] Використовувати реальні API endpoints
- [ ] Перевіряти статус коди відповідей
- [ ] Валідувати структуру даних
- [ ] Тестувати обробку помилок
- [ ] Перевіряти логування

### **Після написання тесту:**
- [ ] Запустити тест ізольовано
- [ ] Перевірити швидкість виконання
- [ ] Документувати тест
- [ ] Додати до CI/CD pipeline

---

## 🎯 **Приклади тестів**

### **API Gateway Integration:**
```python
def test_auth_service_integration(client):
    """Тест інтеграції з Auth Service"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "test_password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### **Database Integration:**
```python
def test_user_creation_integration(client, db_session):
    """Тест створення користувача в базі даних"""
    user_data = {
        "email": "new@example.com",
        "password": "secure_password"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Перевіряємо що користувач зберігається в БД
    user = db_session.query(User).filter_by(email=user_data["email"]).first()
    assert user is not None
```

---

## 🚨 **Важливі правила**

### **✅ Дозволено:**
- Використання реальних API endpoints
- Тестування взаємодії з базою даних
- Перевірка статус кодів відповідей
- Валідація структури даних
- Тестування обробки помилок

### **❌ Заборонено:**
- Реальні зовнішні API виклики (використовувати моки)
- Зміна production даних
- Повільні тести (> 5 секунд)
- Залежність від стану інших тестів

---

**Статус**: 🚧 В розробці  
**Пріоритет**: Високий  
**Останнє оновлення**: 2024-12-19 