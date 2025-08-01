# 🔒 Test Security Guide v1.0.0

> **МЕТА:** Гайд з безпеки тестів для Upwork AI Assistant
> **ВЕРСІЯ:** 1.0.0

## Зміст
1. [Принципи безпеки тестів](#принципи-безпеки-тестів)
2. [Типи тестів](#типи-тестів)
3. [Безпечні практики](#безпечні-практики)
4. [Заборонені практики](#заборонені-практики)
5. [Моніторинг безпеки](#моніторинг-безпеки)

## Принципи безпеки тестів

### **1. Ніколи не тестувати з реальними даними**
- ❌ Реальні API ключі
- ❌ Реальні токени
- ❌ Реальні паролі
- ❌ Реальні дані користувачів

### **2. Використовувати моки та стаби**
- ✅ Mock об'єкти для API
- ✅ Стабі дані для тестування
- ✅ Ізольовані тестові середовища

### **3. Не експонувати внутрішню логіку**
- ❌ Детальна логіка middleware
- ❌ Алгоритми шифрування
- ❌ Внутрішні структури даних

## Типи тестів

### **🟢 БЕЗПЕЧНІ тести (для продакшену)**

```python
# test_security_safe.py
def test_health_endpoint_accessible(self):
    """Тест доступності health endpoint"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
```

**Характеристики:**
- ✅ Тестують публічні endpoints
- ✅ Не містять внутрішньої логіки
- ✅ Використовують моки
- ✅ Безпечні для продакшену

### **🟡 РОЗРОБНИЦЬКІ тести (тільки для dev)**

```python
# test_security.py
def test_rate_limiter_initialization(self):
    """Тест ініціалізації Rate Limiter"""
    rate_limiter = RateLimiter()
    assert rate_limiter is not None
```

**Характеристики:**
- ⚠️ Тестують внутрішню логіку
- ⚠️ Можуть експонувати структуру
- ⚠️ Тільки для розробки
- ❌ НЕ для продакшену

### **🔴 КРИТИЧНІ тести (тільки локально)**

```python
# test_integration_local.py
def test_real_api_integration(self):
    """Тест реальної інтеграції (ТІЛЬКИ локально)"""
    # Цей файл НЕ комітиться в git
    pass
```

**Характеристики:**
- ❌ Використовують реальні API
- ❌ Містять секрети
- ❌ Тільки локально
- ❌ НЕ в git

## Безпечні практики

### **1. Використання моків**

```python
# ✅ БЕЗПЕЧНО
@patch('services.auth_service.src.oauth.requests.post')
def test_oauth_callback(self, mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test_token",  # Тестовий токен
        "refresh_token": "test_refresh"
    }
    mock_post.return_value = mock_response
```

### **2. Тестові дані**

```python
# ✅ БЕЗПЕЧНО
TEST_USER_DATA = {
    "email": "test@example.com",
    "password": "test_password_123",
    "name": "Test User"
}

def test_user_creation(self):
    user = User(**TEST_USER_DATA)
    assert user.email == "test@example.com"
```

### **3. Ізольовані тести**

```python
# ✅ БЕЗПЕЧНО
@pytest.fixture
def test_db():
    """Ізольована тестова база даних"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

## Заборонені практики

### **❌ НЕ РОБІТЬ ЦЬОГО:**

```python
# ❌ НЕ БЕЗПЕЧНО - реальні ключі
def test_openai_integration(self):
    api_key = "sk-1234567890abcdef"  # Реальний ключ
    client = OpenAI(api_key=api_key)

# ❌ НЕ БЕЗПЕЧНО - реальні токени
def test_jwt_verification(self):
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Реальний JWT
    payload = jwt.decode(token, secret_key)

# ❌ НЕ БЕЗПЕЧНО - експозиція логіки
def test_encryption_algorithm(self):
    # Розкриває внутрішню логіку шифрування
    encrypted = encrypt_data("secret", algorithm="AES-256")
```

### **❌ ФАЙЛИ ЯКІ НЕ КОМІТЯТЬСЯ:**

```bash
# .gitignore
*.test.log
test_secrets.json
test_tokens.txt
.env.test
.env.local
tests/artifacts/
tests/logs/
tests/temp/
```

## Моніторинг безпеки

### **1. Автоматичні перевірки**

```python
# test_security_scan.py
def test_no_real_tokens_in_tests(self):
    """Перевірка що в тестах немає реальних токенів"""
    test_files = [
        "test_security.py",
        "test_oauth.py",
        "test_security_safe.py"
    ]
    
    for file in test_files:
        if os.path.exists(f"tests/{file}"):
            with open(f"tests/{file}", 'r') as f:
                content = f.read()
                # Перевіряємо що немає реальних ключів
                assert "sk-" not in content  # OpenAI keys
                assert "pk_" not in content  # Stripe keys
                assert "ghp_" not in content  # GitHub tokens
                assert "Bearer " not in content  # JWT tokens
```

### **2. Pre-commit hooks**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: test-security-scan
        name: Test Security Scan
        entry: python tests/test_security_scan.py
        language: python
        pass_filenames: false
```

### **3. CI/CD перевірки**

```yaml
# .github/workflows/security.yml
name: Security Tests
on: [push, pull_request]
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Security Tests
        run: |
          python -m pytest tests/test_security_safe.py
          python tests/test_security_scan.py
```

## Рекомендації для адміністраторів

### **1. Тести для адміністраторів**

```python
# admin_tests.py - тільки для адміністраторів
def test_admin_dashboard_access(self):
    """Тест доступу до адмін панелі"""
    # Ці тести можуть бути більш детальними
    # але все одно безпечними
    pass
```

### **2. Моніторинг тестів**

- 🔍 Регулярні перевірки тестових файлів
- 📊 Логування виконання тестів
- 🚨 Сповіщення про підозрілу активність
- 📈 Метрики покриття тестами

### **3. Оновлення безпеки**

- 🔄 Регулярні огляди безпеки тестів
- 📝 Документування змін
- 🎯 Тренування команди
- 🛡️ Аудит безпеки

## Checklist безпеки

### **Перед комітом:**
- [ ] Немає реальних API ключів
- [ ] Немає реальних токенів
- [ ] Немає реальних паролів
- [ ] Використовуються моки
- [ ] Тести ізольовані
- [ ] Немає експозиції логіки

### **Перед деплоєм:**
- [ ] Запущені безпечні тести
- [ ] Перевірено .gitignore
- [ ] Сканування на секрети
- [ ] Перевірка логів
- [ ] Тестування в staging

### **Регулярно:**
- [ ] Огляд тестових файлів
- [ ] Оновлення безпеки
- [ ] Тренування команди
- [ ] Аудит безпеки

---

**Версія**: 1.0.0  
**Останнє оновлення**: 2024-07-29  
**Автор**: Security Team 