# 🏗️ АРХІТЕКТУРА БАГАТОКОРИСТУВАЦЬКОЇ СИСТЕМИ

> **Аналіз варіантів реалізації для багатокористувацького Upwork Web App з максимальною безпекою**

---

## 🎯 **ПРОБЛЕМА**

Наш додаток має підтримувати **багато фрілансерів**, кожен з яких:
- Має свій Upwork акаунт
- Потребує індивідуальний доступ до API
- Має власні дані (вакансії, відгуки, повідомлення)
- Потребує ізоляцію даних від інших користувачів
- **Може бути конкурентом інших користувачів**
- **Потребує максимальну безпеку**

---

## 🔍 **АНАЛІЗ UPWORK API ОБМЕЖЕНЬ**

### **OAuth 2.0 Flow для Upwork:**
1. **Application Registration** - реєстрація додатку в Upwork
2. **User Authorization** - кожен користувач авторизується
3. **Access Token** - індивідуальний токен для кожного користувача
4. **API Calls** - виклики від імені конкретного користувача

### **Обмеження:**
- ❌ **Немає Application-level API** - тільки User-level
- ❌ **Кожен користувач має свій токен** - не можна використовувати один для всіх
- ❌ **Rate limits per user** - обмеження на користувача
- ❌ **Token expiration** - токени мають термін дії

---

## 🏗️ **ВАРІАНТИ АРХІТЕКТУРИ**

### **ВАРІАНТ 1: ІНДИВІДУАЛЬНІ API КЛЮЧІ + МАКСИМАЛЬНА БЕЗПЕКА**

#### **Принцип:**
```
Користувач → Свої API ключі → Прямий доступ до Upwork API
+ Повна ізоляція даних + MFA + Шифрування + Моніторинг
```

#### **Реалізація:**
```python
# Модель користувача з максимальною безпекою
class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String)  # bcrypt
    upwork_access_token = Column(String, encrypted=True)
    upwork_refresh_token = Column(String, encrypted=True)
    upwork_user_id = Column(String)
    role = Column(String, default='freelancer')
    is_verified = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime)
    
    # Власні дані
    jobs = relationship("Job", back_populates="user")
    applications = relationship("Application", back_populates="user")
    messages = relationship("Message", back_populates="user")
    security_logs = relationship("SecurityLog", back_populates="user")
```

#### **Переваги:**
- ✅ **Повна ізоляція** - кожен користувач має свої дані
- ✅ **Легальність** - кожен використовує свої credentials
- ✅ **Масштабованість** - немає обмежень на кількість користувачів
- ✅ **Максимальна безпека** - MFA, шифрування, моніторинг
- ✅ **Захист від конкурентів** - повна ізоляція даних
- ✅ **GDPR compliance** - повна відповідність

#### **Недоліки:**
- ❌ **Складність налаштування** - кожен має налаштувати API
- ❌ **Управління токенами** - потрібно оновлювати expired токени
- ❌ **Технічна складність** - OAuth flow для кожного користувача
- ❌ **Висока вартість розробки** - складність безпеки

---

### **ВАРІАНТ 2: ЦЕНТРАЛІЗОВАНА АРХІТЕКТУРА**

#### **Принцип:**
```
Користувач → Наш сервер → Upwork API (через наші credentials)
```

#### **Реалізація:**
```python
# Центральні налаштування
class SystemConfig(Base):
    id = Column(Integer, primary_key=True)
    upwork_api_key = Column(String)
    upwork_api_secret = Column(String)
    upwork_access_token = Column(String)
    
# Користувачі без API ключів
class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    upwork_user_id = Column(String)  # ID користувача в Upwork
    # Немає власних API ключів
```

#### **Переваги:**
- ✅ **Простота для користувачів** - не потрібно налаштовувати API
- ✅ **Централізоване управління** - один набір credentials
- ✅ **Легше розгортання** - менше конфігурації

#### **Недоліки:**
- ❌ **Порушення ToS** - використання чужих credentials
- ❌ **Обмеження масштабування** - rate limits на один акаунт
- ❌ **Правові ризики** - можливі блокування
- ❌ **Відсутність ізоляції** - всі користувачі використовують один акаунт
- ❌ **Ризик для конкурентів** - можливість перехресного доступу

---

### **ВАРІАНТ 3: ГІБРИДНА АРХІТЕКТУРА**

#### **Принцип:**
```
Користувач → Вибір: Свої API ключі АБО Централізований доступ
```

#### **Реалізація:**
```python
class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    auth_type = Column(String)  # "personal" або "centralized"
    
    # Для особистих ключів
    upwork_access_token = Column(String, encrypted=True, nullable=True)
    upwork_refresh_token = Column(String, encrypted=True, nullable=True)
    
    # Для централізованого доступу
    upwork_user_id = Column(String, nullable=True)
```

#### **Переваги:**
- ✅ **Гнучкість** - користувачі вибирають підхід
- ✅ **Поступове впровадження** - можна почати з централізованого
- ✅ **Масштабування** - особисті ключі для активних користувачів

#### **Недоліки:**
- ❌ **Складність реалізації** - два підходи в одній системі
- ❌ **Складність підтримки** - різні логіки для різних типів
- ❌ **Плутанина** - користувачі можуть не розуміти різниці
- ❌ **Ризики безпеки** - змішані підходи

---

## 🎯 **РЕКОМЕНДОВАНИЙ ВАРІАНТ: ВАРІАНТ 1**

### **Чому саме цей варіант:**

#### **1. Легальність та безпека**
- ✅ Кожен користувач використовує свої credentials
- ✅ Немає порушень Terms of Service
- ✅ Повна відповідність Upwork API guidelines
- ✅ **Максимальна безпека для конкурентів**

#### **2. Масштабованість**
- ✅ Немає обмежень на кількість користувачів
- ✅ Rate limits розподілені між користувачами
- ✅ Кожен користувач має свої обмеження

#### **3. Ізоляція даних**
- ✅ Кожен користувач бачить тільки свої дані
- ✅ Немає ризиків перехресного доступу
- ✅ GDPR compliance
- ✅ **Повна захист від конкурентів**

#### **4. Довгострокова стійкість**
- ✅ Не залежить від одного акаунту
- ✅ Ризик блокування мінімальний
- ✅ Можливість розширення функціоналу

---

## 🔐 **СИСТЕМА БЕЗПЕКИ**

### **1. Многофакторна автентифікація (MFA)**

#### **TOTP (Time-based One-Time Password):**
```python
import pyotp

class MFAManager:
    def generate_secret(self):
        return pyotp.random_base32()
    
    def verify_totp(self, secret, token):
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    
    def generate_qr_code(self, secret, email):
        return pyotp.totp.TOTP(secret).provisioning_uri(
            email, issuer_name="Upwork Web App"
        )
```

#### **Backup коди:**
```python
def generate_backup_codes(self, count=10):
    codes = []
    for _ in range(count):
        code = secrets.token_hex(4).upper()[:8]
        codes.append(code)
    return codes
```

### **2. Шифрування токенів**

#### **EncryptionManager:**
```python
from cryptography.fernet import Fernet

class EncryptionManager:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt_token(self, token):
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        return self.cipher.decrypt(encrypted_token.encode()).decode()
```

### **3. JWT токени**

#### **JWTManager:**
```python
class JWTManager:
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
```

### **4. Rate Limiting**

#### **RateLimiter:**
```python
class RateLimiter:
    def check_rate_limit(self, user_id, action, limit, window):
        key = f"rate_limit:{user_id}:{action}"
        current = self.redis_client.incr(key)
        if current == 1:
            self.redis_client.expire(key, window)
        return current <= limit
```

### **5. Моніторинг безпеки**

#### **SecurityMonitor:**
```python
class SecurityMonitor:
    async def log_security_event(self, user_id, action, ip_address, user_agent, success, details=None):
        log_entry = SecurityLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details
        )
        # Зберігаємо в БД
    
    async def create_security_alert(self, user_id, alert_type, severity, description, details=None):
        alert = SecurityAlert(
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            details=details
        )
        # Відправляємо сповіщення
```

---

## 🏗️ **ДЕТАЛЬНА АРХІТЕКТУРА**

### **База даних:**

```sql
-- Користувачі з максимальною безпекою
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    upwork_access_token TEXT,  -- зашифрований
    upwork_refresh_token TEXT, -- зашифрований
    upwork_user_id VARCHAR(255),
    token_expires_at TIMESTAMP,
    role VARCHAR(50) DEFAULT 'freelancer',
    is_verified BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    phone_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Безпека користувачів (MFA)
CREATE TABLE user_security (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255), -- зашифрований
    backup_codes JSON, -- зашифрований
    phone_number VARCHAR(20),
    phone_verified BOOLEAN DEFAULT false,
    session_timeout INTEGER DEFAULT 3600,
    max_concurrent_sessions INTEGER DEFAULT 5
);

-- Ролі та дозволи
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    permissions JSON NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Логи безпеки
CREATE TABLE security_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    success BOOLEAN DEFAULT true,
    details JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    session_id VARCHAR(255)
);

-- Сповіщення безпеки
CREATE TABLE security_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    details JSON,
    resolved BOOLEAN DEFAULT false,
    resolved_by INTEGER REFERENCES users(id),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Вакансії (з прив'язкою до користувача)
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    upwork_job_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    hourly_rate_min DECIMAL(10,2),
    hourly_rate_max DECIMAL(10,2),
    skills TEXT[],
    category VARCHAR(255),
    client_location VARCHAR(255),
    client_feedback DECIMAL(3,2),
    job_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Відгуки (з прив'язкою до користувача)
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    upwork_job_id VARCHAR(255) NOT NULL,
    proposal_text TEXT NOT NULL,
    cover_letter TEXT,
    bid_amount DECIMAL(10,2),
    estimated_hours INTEGER,
    status VARCHAR(50) DEFAULT 'draft',
    ai_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **API Endpoints:**

```python
# Авторизація
POST /auth/register
POST /auth/login
POST /auth/mfa/verify
POST /auth/upwork/connect
POST /auth/upwork/callback
POST /auth/refresh
POST /auth/logout

# Безпека
GET  /security/profile
POST /security/mfa/enable
POST /security/mfa/disable
POST /security/password
GET  /security/logs
POST /security/verify

# Користувачі
GET /users/profile
PUT /users/profile
GET /users/upwork/status

# Вакансії (з фільтрацією по користувачу)
GET /jobs
GET /jobs/{job_id}
POST /jobs/search

# Відгуки (з фільтрацією по користувачу)
GET /applications
POST /applications
PUT /applications/{application_id}

# Адміністрація (тільки адміни)
GET  /admin/users
GET  /admin/alerts
POST /admin/users/{id}/lock
```

### **OAuth Flow:**

```python
# 1. Користувач натискає "Підключити Upwork"
GET /auth/upwork/connect
# → Перенаправлення на Upwork OAuth

# 2. Upwork перенаправляє назад з кодом
POST /auth/upwork/callback?code=xxx&state=yyy
# → Обмін коду на токени
# → Збереження зашифрованих токенів
# → Перенаправлення на додаток

# 3. Використання токенів для API викликів
GET /jobs
# → Автоматичне використання токенів користувача
```

---

## 📋 **ПЛАН ВПРОВАДЖЕННЯ**

### **Етап 1: Базова безпека (1 тиждень)**
1. **Реєстрація та вхід**
   - Валідація email/пароля
   - bcrypt хешування паролів
   - Rate limiting для входу
   - Блокування після невдалих спроб

2. **JWT токени**
   - Access та refresh токени
   - Автоматичне оновлення
   - Blacklist для logout

### **Етап 2: OAuth 2.0 (1 тиждень)**
1. **Upwork інтеграція**
   - OAuth flow
   - Збереження токенів
   - Автоматичне оновлення

2. **Шифрування**
   - Шифрування токенів в БД
   - Безпечне зберігання

### **Етап 3: Розширена безпека (1 тиждень)**
1. **MFA**
   - TOTP (Google Authenticator)
   - SMS верифікація
   - Backup коди

2. **Моніторинг**
   - Логування всіх дій
   - Система сповіщень
   - Аналіз підозрілої активності

### **Етап 4: Адміністрація (1 тиждень)**
1. **Система ролей**
   - Різні рівні доступу
   - Адміністративна панель

2. **Аудит**
   - Детальні логи
   - Експорт даних
   - Аналітика безпеки

---

## ⚠️ **ВАЖЛИВІ ЗАУВАЖЕННЯ**

### **Безпека:**
- 🔐 **Шифрування токенів** - обов'язково
- 🔐 **HTTPS** - для всіх API викликів
- 🔐 **Валідація** - всіх вхідних даних
- 🔐 **Rate limiting** - для захисту від зловживань

### **Легальність:**
- ✅ **Terms of Service** - дотримуватися Upwork ToS
- ✅ **OAuth 2.0** - використовувати офіційний flow
- ✅ **User consent** - отримувати згоду користувачів
- ✅ **Data privacy** - дотримуватися GDPR

### **Масштабованість:**
- 📈 **Rate limits** - кожен користувач має свої обмеження
- 📈 **Database indexing** - індекси на `user_id`
- 📈 **Caching** - кешування для зменшення API викликів
- 📈 **Monitoring** - моніторинг використання API

### **Захист від конкурентів:**
- 🔒 **Повна ізоляція даних** - кожен бачить тільки свої дані
- 🔒 **Шифрування** - всі чутливі дані зашифровані
- 🔒 **Моніторинг** - відстеження підозрілої активності
- 🔒 **Аудит** - детальні логи всіх дій

---

## 🚀 **НАСТУПНІ КРОКИ**

1. **Затвердити архітектуру** - підтвердити Варіант 1
2. **Реєстрація в Upwork** - створити додаток
3. **Почати з Етапу 1** - підготовка інфраструктури
4. **Інтегрувати в project_plan.md** - додати нові етапи
5. **Оновити документацію** - відобразити зміни

---

*Останнє оновлення: 2024-12-19* 