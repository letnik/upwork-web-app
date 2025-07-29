# Архітектура безпеки Upwork Web App v2.0.0

> **Система безпеки для багатокористувацької платформи з максимальним захистом даних**
> **МЕТА:** Оновлена архітектура безпеки з урахуванням аудиту та поточного стану
> **ВЕРСІЯ:** 2.0.0

---

## Зміст

1. [Поточний стан безпеки](#поточний-стан-безпеки)
2. [Критичні проблеми](#критичні-проблеми)
3. [Принципи безпеки](#принципи-безпеки)
4. [Компоненти безпеки](#компоненти-безпеки)
5. [Модель загроз](#модель-загроз)
6. [Архітектурні рішення](#архітектурні-рішення)
7. [Протоколи безпеки](#протоколи-безпеки)
8. [Моніторинг та реагування](#моніторинг-та-реагування)
9. [План покращення](#план-покращення)

---

## Поточний стан безпеки

### **Результати аудиту (грудень 2024)**
- ❌ **КРИТИЧНИЙ РІВЕНЬ РИЗИКУ** - проект не готовий для продакшену
- ❌ **Відсутня автентифікація** - API доступне без авторизації
- ❌ **Відсутня авторизація** - немає перевірки прав доступу
- ❌ **Відсутнє шифрування** - дані зберігаються в відкритому вигляді
- ❌ **Відсутній захист API** - немає rate limiting та валідації

### **Статистика проблем**
- **Критичні**: 4 проблеми
- **Високі**: 3 проблеми
- **Середні**: 3 проблеми

### **Технічний стек (поточний)**
- **Backend**: FastAPI (без безпеки)
- **База даних**: PostgreSQL (без шифрування)
- **Кеш**: Redis (без автентифікації)
- **Контейнеризація**: Docker (базова конфігурація)

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

## Принципи безпеки

### 1. **Defense in Depth**
- Багаторівневий захист
- Кожен рівень незалежний
- Навіть при збої одного рівня система захищена

### 2. **Zero Trust**
- Не довіряй нікому
- Перевіряй кожен запит
- Мінімальні привілеї

### 3. **Privacy by Design**
- Приватність вбудована в архітектуру
- Шифрування за замовчуванням
- Мінімізація збору даних

### 4. **Security First**
- Безпека важливіша за зручність
- Регулярні аудити
- Постійне покращення

### 5. **Competitor Protection**
- Повна ізоляція даних користувачів
- Захист від внутрішніх загроз
- Моніторинг підозрілої активності

---

## Компоненти безпеки

### 1. **Authentication Layer**
```
┌─────────────────────────────────────┐
│        Authentication Layer         │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ OAuth 2.0   │ │   JWT       │   │
│  │ (Upwork)    │ │  Tokens     │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │    MFA      │ │  Password   │   │
│  │ (TOTP/SMS)  │ │  Manager    │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- OAuth 2.0 інтеграція з Upwork
- JWT токени (access/refresh)
- Многофакторна автентифікація
- Управління паролями

**JWT Configuration:**
- Algorithm: HS256 (для початку), RS256 (для продакшену)
- Access token expiration: 15 хвилин
- Refresh token expiration: 7 днів
- Secret key: 256-bit

### 2. **Authorization Layer**
```
┌─────────────────────────────────────┐
│       Authorization Layer           │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Role-Based  │ │ Permission  │   │
│  │ Access      │ │  Manager    │   │
│  │ Control     │ │             │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Resource    │ │   Policy    │   │
│  │ Protection  │ │  Engine     │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- Role-Based Access Control (RBAC)
- Управління дозволами
- Захист ресурсів
- Політики безпеки

### 3. **Encryption Layer**
```
┌─────────────────────────────────────┐
│         Encryption Layer            │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Data at     │ │ Data in     │   │
│  │ Rest        │ │ Transit     │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Token       │ │ Password    │   │
│  │ Encryption  │ │ Hashing     │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- Шифрування даних в спокої (AES-256)
- Шифрування даних в транзиті (TLS 1.3)
- Шифрування токенів (Fernet)
- Хешування паролів (bcrypt)

### 4. **API Protection Layer**
```
┌─────────────────────────────────────┐
│        API Protection Layer         │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Rate        │ │ Input       │   │
│  │ Limiting    │ │ Validation  │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ CORS        │ │ SQL         │   │
│  │ Protection  │ │ Injection   │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- Rate limiting (100 запитів/хв)
- Валідація вхідних даних (Pydantic)
- CORS захист
- Захист від SQL injection

### 5. **Monitoring Layer**
```
┌─────────────────────────────────────┐
│         Monitoring Layer            │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Security    │ │ Anomaly     │   │
│  │ Logging     │ │ Detection   │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Alert       │ │ Audit       │   │
│  │ System      │ │ Trail       │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

**Функції:**
- Логування безпеки
- Детекція аномалій
- Система сповіщень
- Аудит дій

---

## Модель загроз

### 1. **Authentication Threats**
- **Brute Force Attacks** - перебір паролів
- **Credential Stuffing** - використання викрадених облікових даних
- **Session Hijacking** - викрадення сесій
- **MFA Bypass** - обхід многофакторної автентифікації

### 2. **Authorization Threats**
- **Privilege Escalation** - підвищення привілеїв
- **Horizontal Privilege Escalation** - доступ до чужих даних
- **API Abuse** - зловживання API
- **Resource Exhaustion** - вичерпання ресурсів

### 3. **Data Protection Threats**
- **Data Breach** - виток даних
- **SQL Injection** - ін'єкції SQL
- **XSS Attacks** - cross-site scripting
- **CSRF Attacks** - cross-site request forgery

### 4. **Infrastructure Threats**
- **DDoS Attacks** - distributed denial of service
- **Man-in-the-Middle** - атаки типу "людина посередині"
- **DNS Spoofing** - підробка DNS
- **Physical Access** - фізичний доступ

### 5. **Competitor Threats**
- **Data Leakage** - виток даних конкурентам
- **Internal Threats** - загрози від співробітників
- **Business Intelligence** - збір конкурентної розвідки
- **Sabotage** - саботаж системи

---

## Архітектурні рішення

### 1. **OAuth 2.0 + PKCE**
```python
class OAuthManager:
    def __init__(self):
        self.client_id = os.getenv('UPWORK_CLIENT_ID')
        self.client_secret = os.getenv('UPWORK_CLIENT_SECRET')
        self.redirect_uri = os.getenv('UPWORK_REDIRECT_URI')
    
    def get_auth_url(self, state: str, code_challenge: str) -> str:
        """Генерує URL для авторизації"""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        return f"{self.auth_url}?{urlencode(params)}"
```

### 2. **JWT Token Management**
```python
class JWTManager:
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY')
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 15
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, data: dict) -> str:
        """Створює короткочасний access токен"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "jti": str(uuid.uuid4())  # JWT ID для відстеження
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
```

### 3. **MFA Implementation**
```python
class MFAManager:
    def __init__(self):
        self.totp = pyotp.TOTP
        self.backup_codes_count = 10
    
    def generate_secret(self) -> str:
        """Генерує TOTP secret"""
        return pyotp.random_base32()
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Перевіряє TOTP токен"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self) -> List[str]:
        """Генерує backup коди"""
        codes = []
        for _ in range(self.backup_codes_count):
            code = secrets.token_hex(4).upper()[:8]
            codes.append(code)
        return codes
```

### 4. **Encryption System**
```python
class EncryptionManager:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Шифрує дані"""
        if not data:
            return data
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Розшифровує дані"""
        if not encrypted_data:
            return encrypted_data
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {e}")
```

---

## Протоколи безпеки

### 1. **Password Policy**
- Мінімальна довжина: 8 символів
- Обов'язкові: великі літери, малі літери, цифри, спеціальні символи
- Заборона повторного використання останніх 5 паролів
- Автоматична зміна кожні 90 днів

### 2. **Session Management**
- Максимальна тривалість сесії: 8 годин
- Автоматичне завершення при неактивності: 30 хвилин
- Обмеження кількості активних сесій: 5 на користувача
- Примусове завершення всіх сесій при зміні пароля

### 3. **Rate Limiting**
- API запити: 100/хвилину
- Спроби входу: 5/15 хвилин
- MFA спроби: 3/5 хвилин
- Реєстрація: 3/день з IP

### 4. **Data Classification**
- **Public**: загальнодоступна інформація
- **Internal**: внутрішня інформація
- **Confidential**: конфіденційна інформація
- **Restricted**: обмежена інформація

---

## Моніторинг та реагування

### 1. **Security Logging**
```python
class SecurityLogger:
    def log_event(self, event_type: str, user_id: int = None, 
                  ip_address: str = None, details: dict = None):
        """Логує подію безпеки"""
        security_log = SecurityLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            details=details
        )
        db.add(security_log)
        db.commit()
```

### 2. **Anomaly Detection**
- Аналіз паттернів використання
- Детекція підозрілої активності
- Машинне навчання для виявлення аномалій
- Real-time сповіщення

### 3. **Incident Response**
- Автоматичне блокування підозрілих IP
- Ескалація інцидентів
- Документування інцидентів
- Пост-інцідентний аналіз

### 4. **Compliance Monitoring**
- GDPR відповідність
- SOC 2 Type II
- ISO 27001
- Регулярні аудити

---

## План покращення

### **Етап 1: Базова безпека (1-2 тижні)**
- [ ] Додати залежності для безпеки
- [ ] Створити модель користувача
- [ ] Реалізувати JWT автентифікацію
- [ ] Додати middleware для авторизації
- [ ] Налаштувати валідацію вхідних даних

### **Етап 2: OAuth та MFA (2-4 тижні)**
- [ ] Реалізувати OAuth 2.0 з Upwork
- [ ] Додати TOTP MFA
- [ ] Створити backup коди
- [ ] Налаштувати QR код

### **Етап 3: Шифрування (1-2 тижні)**
- [ ] Шифрування токенів
- [ ] Хешування паролів
- [ ] Шифрування чутливих даних
- [ ] Безпечне зберігання ключів

### **Етап 4: Моніторинг (1-2 тижні)**
- [ ] Логування безпеки
- [ ] Rate limiting
- [ ] Детекція аномалій
- [ ] Система сповіщень

### **Етап 5: Тестування (1 тиждень)**
- [ ] Unit тести безпеки
- [ ] Інтеграційні тести
- [ ] Penetration testing
- [ ] Security audit

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

**Детальний звіт аудиту**: [security_audit_report_v1.0.0.md](../../newspaper/report/security_audit_report_v1.0.0.md)

**План реалізації**: [security_improvement_plan_v1.0.0.md](../../newspaper/report/security_improvement_plan_v1.0.0.md)

---

*Версія: 2.0.0* 