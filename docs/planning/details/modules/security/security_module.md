# Модуль безпеки v2.0.0

> **Модуль для забезпечення комплексної безпеки системи**
> **МЕТА:** Оновлений модуль безпеки з урахуванням аудиту та поточного стану
> **ВЕРСІЯ:** 2.0.0

---

## Зміст

1. [Поточний стан](#поточний-стан)
2. [Огляд модуля](#огляд-модуля)
3. [Архітектура модуля](#архітектура-модуля)
4. [Критичні проблеми](#критичні-проблеми)
5. [API Endpoints](#api-endpoints)
6. [Аспекти безпеки](#аспекти-безпеки)
7. [Інтеграція](#інтеграція)
8. [Тестування](#тестування)
9. [Моніторинг](#моніторинг)
10. [План реалізації](#план-реалізації)

---

## Поточний стан

### **Результати аудиту (грудень 2024)**
- ❌ **Модуль не реалізований** - відсутній в поточному коді
- ❌ **Відсутня автентифікація** - API доступне без авторизації
- ❌ **Відсутня авторизація** - немає перевірки прав доступу
- ❌ **Відсутнє шифрування** - дані зберігаються в відкритому вигляді
- ❌ **Відсутній захист API** - немає rate limiting та валідації

### **Статистика проблем**
- **Критичні**: 4 проблеми
- **Високі**: 3 проблеми
- **Середні**: 3 проблеми

### **Пріоритет реалізації**
- **КРИТИЧНИЙ** - потребує негайної реалізації
- **БЛОКУЄ РОЗРОБКУ** - інші модулі не можуть працювати без безпеки

---

## Огляд модуля

### Призначення
- Комплексна безпека всіх компонентів системи
- Моніторинг та відстеження загроз
- Інцідент-менеджмент
- Аудит безпеки
- Захист даних користувачів

### Основні функції
- Моніторинг безпеки в реальному часі
- Виявлення аномалій
- Автоматичні сповіщення
- Аудит дій користувачів
- Захист від атак

### Ключові особливості
- **Повна ізоляція даних** - кожен користувач бачить тільки свої дані
- **Многофакторна автентифікація** - TOTP, SMS, backup коди
- **Шифрування даних** - всі чутливі дані зашифровані
- **Моніторинг безпеки** - real-time сповіщення про загрози
- **Аудит дій** - детальне логування всіх операцій

---

## Архітектура модуля

### Компоненти

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Module                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Threat Detector│  │ Incident Mgmt│  │ Audit Logger │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Anomaly     │  │ Alert       │  │ Compliance  │        │
│  │ Detection   │  │ System      │  │ Monitor     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Data        │  │ Network     │  │ Access      │        │
│  │ Protection  │  │ Security    │  │ Control     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Взаємодія з іншими модулями

- **Auth Module**: Моніторинг авторизації
- **All Modules**: Аудит та моніторинг
- **Database**: Захист даних
- **API**: Захист endpoints

### Структура файлів
```
src/security/
├── __init__.py
├── models.py              # Моделі безпеки
├── schemas.py             # Pydantic схеми
├── dependencies.py        # FastAPI залежності
├── jwt_manager.py         # JWT управління
├── password_manager.py    # Управління паролями
├── encryption_manager.py  # Шифрування
├── mfa_manager.py         # MFA функціональність
├── rate_limiter.py        # Rate limiting
├── security_logger.py     # Логування безпеки
├── anomaly_detector.py    # Детекція аномалій
├── alert_system.py        # Система сповіщень
└── routes.py              # API endpoints
```

---

## Критичні проблеми

### **1. Відсутність автентифікації**
**Рівень ризику**: КРИТИЧНИЙ
**Поточний стан**:
```python
# Всі endpoints доступні без автентифікації
@app.get("/jobs")
@app.post("/applications")
@app.get("/analytics")
```

**Рішення**:
- ✅ Додати JWT автентифікацію
- ✅ Реалізувати OAuth 2.0 з Upwork
- ✅ Додати MFA (TOTP)
- ✅ Створити систему ролей

### **2. Відсутність авторизації**
**Рівень ризику**: КРИТИЧНИЙ
**Поточний стан**:
```python
# Немає перевірки user_id
@app.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
# Кожен може отримати будь-яку вакансію
```

**Рішення**:
- ✅ Додати middleware для авторизації
- ✅ Реалізувати RBAC (Role-Based Access Control)
- ✅ Додати перевірку власності ресурсів
- ✅ Створити систему дозволів

### **3. Відсутність шифрування**
**Рівень ризику**: КРИТИЧНИЙ
**Поточний стан**:
```python
# Паролі та токени в відкритому вигляді
POSTGRES_PASSWORD=postgres  # В docker-compose.yml
```

**Рішення**:
- ✅ Шифрування чутливих полів (AES-256)
- ✅ Хешування паролів (bcrypt)
- ✅ Шифрування токенів (Fernet)
- ✅ Безпечне зберігання ключів

### **4. Відсутність захисту API**
**Рівень ризику**: КРИТИЧНИЙ
**Поточний стан**:
```python
# Немає rate limiting
# Немає валідації вхідних даних
# Немає захисту від SQL injection
```

**Рішення**:
- ✅ Rate limiting (100 запитів/хв)
- ✅ Валідація вхідних даних (Pydantic)
- ✅ Захист від SQL injection (ORM)
- ✅ CORS налаштування

---

## API Endpoints

### Моніторинг безпеки

```python
# Отримання статусу безпеки
GET /api/security/status
Headers: Authorization: Bearer <token>
Response: {
    "overall_status": "secure",
    "threat_level": "low",
    "active_incidents": 0,
    "last_scan": "2024-12-19T15:30:00Z",
    "components": {
        "authentication": "secure",
        "network": "secure",
        "data_protection": "secure",
        "compliance": "compliant"
    }
}

# Отримання активних загроз
GET /api/security/threats
Headers: Authorization: Bearer <token>
Query params: severity, status, limit
Response: {
    "threats": [
        {
            "id": "threat_123",
            "type": "brute_force",
            "severity": "medium",
            "source_ip": "192.168.1.100",
            "target": "auth_endpoint",
            "timestamp": "2024-12-19T15:30:00Z",
            "status": "active"
        }
    ]
}

# Отримання логів безпеки
GET /api/security/logs
Headers: Authorization: Bearer <token>
Query params: event_type, user_id, start_date, end_date, limit
Response: {
    "logs": [
        {
            "id": "log_123",
            "event_type": "login_success",
            "user_id": 123,
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "timestamp": "2024-12-19T15:30:00Z",
            "details": {
                "method": "oauth",
                "provider": "upwork"
            }
        }
    ]
}
```

### Управління безпекою

```python
# Налаштування MFA
POST /api/security/mfa/setup
Headers: Authorization: Bearer <token>
Response: {
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "backup_codes": ["12345678", "87654321", ...]
}

# Верифікація MFA
POST /api/security/mfa/verify
Headers: Authorization: Bearer <token>
Body: {"token": "123456"}
Response: {"success": true}

# Зміна пароля
POST /api/security/password/change
Headers: Authorization: Bearer <token>
Body: {
    "current_password": "old_password",
    "new_password": "new_secure_password"
}
Response: {"success": true}

# Отримання активних сесій
GET /api/security/sessions
Headers: Authorization: Bearer <token>
Response: {
    "sessions": [
        {
            "id": "session_123",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "created_at": "2024-12-19T15:30:00Z",
            "last_activity": "2024-12-19T16:30:00Z",
            "is_current": true
        }
    ]
}

# Завершення сесії
DELETE /api/security/sessions/{session_id}
Headers: Authorization: Bearer <token>
Response: {"success": true}
```

### Адміністративні функції

```python
# Отримання статистики безпеки
GET /api/admin/security/stats
Headers: Authorization: Bearer <admin_token>
Response: {
    "total_users": 1000,
    "active_sessions": 500,
    "failed_login_attempts": 25,
    "suspicious_activities": 3,
    "security_incidents": 1
}

# Блокування користувача
POST /api/admin/security/users/{user_id}/block
Headers: Authorization: Bearer <admin_token>
Body: {"reason": "suspicious_activity", "duration": 3600}
Response: {"success": true}

# Отримання системних алертів
GET /api/admin/security/alerts
Headers: Authorization: Bearer <admin_token>
Response: {
    "alerts": [
        {
            "id": "alert_123",
            "type": "brute_force_attack",
            "severity": "high",
            "description": "Multiple failed login attempts",
            "timestamp": "2024-12-19T15:30:00Z",
            "status": "active"
        }
    ]
}
```

---

## Аспекти безпеки

### 1. **Authentication Security**
- **OAuth 2.0 з PKCE** - безпечна авторизація через Upwork
- **JWT токени** - короткочасні access токени (15 хв)
- **Refresh токени** - довгочасні токени для оновлення
- **MFA (TOTP)** - двофакторна автентифікація
- **Backup коди** - резервні коди для відновлення

### 2. **Authorization Security**
- **RBAC (Role-Based Access Control)** - система ролей
- **Resource ownership** - перевірка власності ресурсів
- **Permission matrix** - матриця дозволів
- **Session management** - управління сесіями

### 3. **Data Protection**
- **Encryption at rest** - шифрування даних в спокої
- **Encryption in transit** - шифрування при передачі
- **Token encryption** - шифрування токенів
- **Password hashing** - хешування паролів (bcrypt)

### 4. **API Security**
- **Rate limiting** - обмеження частоти запитів
- **Input validation** - валідація вхідних даних
- **SQL injection protection** - захист від SQL ін'єкцій
- **CORS protection** - захист від CORS атак

### 5. **Monitoring Security**
- **Security logging** - логування подій безпеки
- **Anomaly detection** - виявлення аномалій
- **Alert system** - система сповіщень
- **Audit trail** - аудит дій

---

## Інтеграція

### Інтеграція з Auth Module
```python
from ..auth.dependencies import get_current_user
from ..auth.models import User

async def get_security_context(current_user: User = Depends(get_current_user)):
    """Отримує контекст безпеки для користувача"""
    return {
        "user_id": current_user.id,
        "roles": current_user.roles,
        "permissions": current_user.permissions,
        "mfa_enabled": current_user.mfa_enabled
    }
```

### Інтеграція з Database
```python
from ..database.models import SecurityLog, UserSession

class SecurityRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def log_security_event(self, event: SecurityLog):
        """Логує подію безпеки"""
        self.db.add(event)
        self.db.commit()
    
    def get_user_sessions(self, user_id: int) -> List[UserSession]:
        """Отримує активні сесії користувача"""
        return self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
```

### Інтеграція з API
```python
from fastapi import Depends, HTTPException
from .dependencies import get_security_context

@app.get("/jobs")
async def get_jobs(
    security_context = Depends(get_security_context),
    db: Session = Depends(get_db)
):
    """Захищений endpoint для отримання вакансій"""
# Перевірка прав доступу
    if not security_context["permissions"].can_read_jobs:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
# Логування доступу
    security_logger.log_event(
        "job_access",
        user_id=security_context["user_id"],
        details={"action": "read_jobs"}
    )
    
# Повернення даних
    return db.query(Job).filter(Job.user_id == security_context["user_id"]).all()
```

---

## 🧪 Тестування

### Unit тести
```python
import pytest
from ..security.jwt_manager import JWTManager
from ..security.password_manager import PasswordManager

class TestSecurityModule:
    def test_jwt_token_creation(self):
        """Тест створення JWT токена"""
        jwt_manager = JWTManager()
        token = jwt_manager.create_access_token({"user_id": 123})
        assert token is not None
        assert len(token) > 0
    
    def test_password_hashing(self):
        """Тест хешування пароля"""
        password_manager = PasswordManager()
        password = "secure_password_123"
        hashed = password_manager.hash_password(password)
        
        assert hashed != password
        assert password_manager.verify_password(password, hashed)
    
    def test_mfa_verification(self):
        """Тест верифікації MFA"""
        mfa_manager = MFAManager()
        secret = mfa_manager.generate_secret()
        token = pyotp.TOTP(secret).now()
        
        assert mfa_manager.verify_totp(secret, token)
```

### Інтеграційні тести
```python
class TestSecurityIntegration:
    def test_authentication_flow(self, client):
        """Тест повного flow автентифікації"""
# Реєстрація
        register_response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        assert register_response.status_code == 201
        
# Вхід
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
# Доступ до захищеного ресурсу
        headers = {"Authorization": f"Bearer {token}"}
        jobs_response = client.get("/jobs", headers=headers)
        assert jobs_response.status_code == 200
    
    def test_rate_limiting(self, client):
        """Тест rate limiting"""
# Відправляємо багато запитів
        for _ in range(101):
            response = client.get("/jobs")
            if response.status_code == 429:
                break
        else:
            pytest.fail("Rate limiting not working")
```

### Тести безпеки
```python
class TestSecurityVulnerabilities:
    def test_sql_injection_protection(self, client):
        """Тест захисту від SQL ін'єкцій"""
        malicious_input = "'; DROP TABLE users; --"
        response = client.get(f"/jobs?search={malicious_input}")
        assert response.status_code == 400
    
    def test_xss_protection(self, client):
        """Тест захисту від XSS"""
        malicious_input = "<script>alert('xss')</script>"
        response = client.post("/jobs", json={
            "title": malicious_input
        })
# Перевіряємо що скрипт не виконався
        assert "<script>" not in response.text
    
    def test_csrf_protection(self, client):
        """Тест захисту від CSRF"""
# Тест CSRF токенів
        pass
```

---

## Моніторинг

### Метрики безпеки
```python
class SecurityMetrics:
    def __init__(self):
        self.metrics = {
            "failed_login_attempts": 0,
            "successful_logins": 0,
            "suspicious_activities": 0,
            "security_incidents": 0,
            "active_sessions": 0,
            "mfa_enabled_users": 0
        }
    
    def increment_metric(self, metric_name: str):
        """Збільшує метрику"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += 1
    
    def get_metrics(self) -> dict:
        """Отримує поточні метрики"""
        return self.metrics.copy()
```

### Алерти безпеки
```python
class SecurityAlertSystem:
    def __init__(self):
        self.alert_rules = {
            "brute_force": {
                "threshold": 5,
                "time_window": 300,  # 5 хвилин
                "severity": "high"
            },
            "suspicious_ip": {
                "threshold": 3,
                "time_window": 3600,  # 1 година
                "severity": "medium"
            }
        }
    
    async def check_alerts(self, event_type: str, user_id: int, ip_address: str):
        """Перевіряє чи потрібно створити алерт"""
        if event_type in self.alert_rules:
            rule = self.alert_rules[event_type]
            count = await self.get_event_count(event_type, user_id, ip_address, rule["time_window"])
            
            if count >= rule["threshold"]:
                await self.create_alert(event_type, rule["severity"], user_id, ip_address)
```

### Логування безпеки
```python
class SecurityLogger:
    def __init__(self, db: Session):
        self.db = db
    
    def log_event(self, event_type: str, user_id: int = None, 
                  ip_address: str = None, details: dict = None):
        """Логує подію безпеки"""
        security_log = SecurityLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            details=details or {}
        )
        
        self.db.add(security_log)
        self.db.commit()
        
# Перевіряємо алерти
        asyncio.create_task(self.alert_system.check_alerts(event_type, user_id, ip_address))
```

---

## План реалізації

### **Етап 1: Базова безпека (1-2 тижні)**
- [ ] Створити структуру папок security/
- [ ] Додати залежності для безпеки
- [ ] Створити модель користувача з безпекою
- [ ] Реалізувати JWT автентифікацію
- [ ] Додати middleware для авторизації
- [ ] Налаштувати валідацію вхідних даних

### **Етап 2: OAuth та MFA (2-4 тижні)**
- [ ] Реалізувати OAuth 2.0 з Upwork
- [ ] Додати TOTP MFA
- [ ] Створити backup коди
- [ ] Налаштувати QR код
- [ ] Інтеграція з Auth модулем

### **Етап 3: Шифрування (1-2 тижні)**
- [ ] Шифрування токенів (Fernet)
- [ ] Хешування паролів (bcrypt)
- [ ] Шифрування чутливих даних (AES-256)
- [ ] Безпечне зберігання ключів
- [ ] Інтеграція з Database модулем

### **Етап 4: Моніторинг (1-2 тижні)**
- [ ] Логування безпеки
- [ ] Rate limiting
- [ ] Детекція аномалій
- [ ] Система сповіщень
- [ ] Метрики безпеки

### **Етап 5: Тестування (1 тиждень)**
- [ ] Unit тести безпеки
- [ ] Інтеграційні тести
- [ ] Тести вразливостей
- [ ] Penetration testing
- [ ] Security audit

### **Етап 6: Інтеграція (1 тиждень)**
- [ ] Інтеграція з усіма модулями
- [ ] Оновлення API endpoints
- [ ] Налаштування middleware
- [ ] Тестування інтеграції
- [ ] Документація

---

## Очікуваний результат

### **Після реалізації**
- ✅ Повна ізоляція даних користувачів
- ✅ Безпечна автентифікація з MFA
- ✅ Шифроване зберігання даних
- ✅ Моніторинг безпеки
- ✅ Захист від основних атак

### **Відповідність вимогам**
- ✅ Безпека для роботи з конкурентами
- ✅ Офіційний API Upwork
- ✅ Багатокористувацька система
- ✅ Масштабованість

---

**Детальний звіт аудиту**: [security_audit_report_v1.0.0.md](../../../newspaper/report/security_audit_report_v1.0.0.md)

**План реалізації**: [security_improvement_plan_v1.0.0.md](../../../newspaper/report/security_improvement_plan_v1.0.0.md)

---

*Версія: 2.0.0* 