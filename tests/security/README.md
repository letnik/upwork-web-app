# 🔒 Security Tests

> **Тестування безпеки та вразливостей системи**

---

## 📋 **Огляд**

Security тести перевіряють:
- Автентифікацію та авторизацію
- Валідацію вводу
- Шифрування даних
- Захист від атак
- Безпеку API

---

## 🏗️ **Архітектура**

```
tests/security/
├── authentication/                # Тести автентифікації
│   ├── test_login_security.py    # Безпека входу
│   ├── test_password_policy.py   # Політика паролів
│   ├── test_session_management.py # Управління сесіями
│   └── test_mfa_security.py      # Безпека MFA
├── authorization/                 # Тести авторизації
│   ├── test_role_based_access.py # Role-based access
│   ├── test_permission_checks.py # Перевірка дозволів
│   └── test_api_authorization.py # Авторизація API
├── input_validation/             # Валідація вводу
│   ├── test_sql_injection.py     # SQL ін'єкції
│   ├── test_xss_protection.py    # XSS захист
│   ├── test_csrf_protection.py   # CSRF захист
│   └── test_input_sanitization.py # Санитизація вводу
├── encryption/                   # Тести шифрування
│   ├── test_data_encryption.py   # Шифрування даних
│   ├── test_token_encryption.py  # Шифрування токенів
│   └── test_password_hashing.py  # Хешування паролів
├── sql_injection/                # SQL ін'єкції
│   ├── test_login_bypass.py      # Обхід авторизації
│   ├── test_data_extraction.py   # Видобування даних
│   └── test_blind_injection.py   # Сліпі ін'єкції
├── xss_protection/               # XSS захист
│   ├── test_stored_xss.py        # Stored XSS
│   ├── test_reflected_xss.py     # Reflected XSS
│   └── test_dom_xss.py          # DOM XSS
└── rate_limiting/                # Rate limiting
    ├── test_api_rate_limits.py   # API rate limits
    ├── test_brute_force.py       # Brute force захист
    └── test_ddos_protection.py   # DDoS захист
```

---

## 🚀 **Запуск тестів**

```bash
# Всі security тести
./tools/scripts/testing/run_tests.sh security

# Конкретні security тести
pytest tests/security/authentication/ -v
pytest tests/security/input_validation/ -v
pytest tests/security/encryption/ -v

# З різними рівнями безпеки
pytest tests/security/ --security-level=high
pytest tests/security/ --penetration-testing
```

---

## 📊 **Покриття**

### **Планується покриття:**
- **Authentication**: 100%
- **Authorization**: 95%
- **Input Validation**: 100%
- **Encryption**: 100%
- **SQL Injection**: 100%
- **XSS Protection**: 100%
- **Rate Limiting**: 90%

---

## 🔧 **Налаштування**

### **Security конфігурація:**
```python
# tests/security/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.backend.api_gateway.src.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def malicious_payloads():
    return {
        "sql_injection": [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --"
        ],
        "xss": [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ],
        "csrf": [
            "malicious_token",
            "invalid_session"
        ]
    }
```

### **Security tools:**
```python
# tests/security/tools/
├── sqlmap_integration.py
├── burp_suite_integration.py
├── owasp_zap_integration.py
└── custom_security_scanner.py
```

---

## 📋 **Чекліст**

### **Перед створенням security тесту:**
- [ ] Визначити тип атаки
- [ ] Створити безпечні payload'и
- [ ] Налаштувати тестове середовище
- [ ] Визначити очікувані результати
- [ ] Планувати cleanup

### **Під час написання тесту:**
- [ ] Використовувати безпечні payload'и
- [ ] Перевіряти відповіді сервера
- [ ] Тестувати обробку помилок
- [ ] Валідувати безпеку
- [ ] Документувати вразливості

### **Після написання тесту:**
- [ ] Запустити тест ізольовано
- [ ] Перевірити безпеку
- [ ] Документувати результати
- [ ] Додати до CI/CD pipeline
- [ ] Оновити security policy

---

## 🎯 **Приклади тестів**

### **SQL Injection Test:**
```python
def test_sql_injection_protection(client, malicious_payloads):
    """Тест захисту від SQL ін'єкцій"""
    for payload in malicious_payloads["sql_injection"]:
        response = client.post("/auth/login", json={
            "email": payload,
            "password": "test_password"
        })
        
        # Перевіряємо що система не вразлива
        assert response.status_code in [400, 401, 422]
        assert "error" in response.json() or "detail" in response.json()
```

### **XSS Protection Test:**
```python
def test_xss_protection(client, malicious_payloads):
    """Тест захисту від XSS атак"""
    for payload in malicious_payloads["xss"]:
        response = client.post("/api/proposals", json={
            "job_id": "test_job",
            "cover_letter": payload,
            "proposal_text": payload
        })
        
        # Перевіряємо що XSS payload'и не виконуються
        assert response.status_code in [400, 422]
        assert "invalid" in response.json().get("detail", "").lower()
```

### **Authentication Security Test:**
```python
def test_brute_force_protection(client):
    """Тест захисту від brute force атак"""
    for i in range(10):
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": f"wrong_password_{i}"
        })
        
        if i < 5:
            # Перші 5 спроб повинні повертати 401
            assert response.status_code == 401
        else:
            # Після 5 спроб повинен бути rate limiting
            assert response.status_code == 429
```

---

## 🚨 **Важливі правила**

### **✅ Дозволено:**
- Тестування в ізольованому середовищі
- Використання безпечних payload'ів
- Документування вразливостей
- Автоматизоване тестування
- Регулярні security аудити

### **❌ Заборонено:**
- Тестування в production середовищі
- Використання реальних атак
- Зміна production даних
- Ігнорування security проблем
- Відсутність документації

---

## 🛡️ **Security Best Practices**

### **Authentication:**
- Сильні паролі
- MFA обов'язково
- Session management
- Password rotation

### **Authorization:**
- Role-based access control
- Principle of least privilege
- API authorization
- Resource-level permissions

### **Input Validation:**
- Whitelist validation
- Input sanitization
- Output encoding
- Content Security Policy

### **Encryption:**
- TLS/SSL обов'язково
- Data encryption at rest
- Token encryption
- Secure key management

---

## 📈 **Security Monitoring**

### **Real-time monitoring:**
- Failed login attempts
- Suspicious activities
- Rate limiting violations
- Security events

### **Security metrics:**
- Authentication failures
- Authorization denials
- Input validation errors
- Security incidents

---

**Статус**: 🚧 В розробці  
**Пріоритет**: Високий  
**Останнє оновлення**: 2024-12-19 