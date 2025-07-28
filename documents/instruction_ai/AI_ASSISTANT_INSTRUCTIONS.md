<!--
ФАЙЛ: AI_ASSISTANT_INSTRUCTIONS.md
ОПИС: Інструкції для AI асистентів проекту Upwork Web App
ПРИЗНАЧЕННЯ: Детальні інструкції для AI асистентів по роботі з документацією та завданнями
ЩО ЗБЕРІГАЄ: Правила роботи, формати файлів, процеси оновлення, стандарти якості
-->

# 🤖 Інструкції для AI асистентів проекту Upwork Web App

> **Детальні інструкції для AI асистентів з урахуванням максимальної безпеки**

---

## 🎯 **ОСНОВНІ ПРИНЦИПИ**

### **Безпека понад усе**
- 🔐 **Максимальна безпека** - головний пріоритет проекту
- 🔐 **Конкуренти серед користувачів** - повна ізоляція даних
- 🔐 **Незнайомі люди** - надійна автентифікація
- 🔐 **Різні цілі** - різні рівні доступу

### **Архітектурні принципи**
- 🏗️ **Індивідуальні API ключі** - кожен користувач має свої credentials
- 🏗️ **OAuth 2.0 авторизація** - безпечне підключення до Upwork API
- 🏗️ **Многофакторна автентифікація (MFA)** - додатковий рівень захисту
- 🏗️ **Шифрування токенів** - всі чутливі дані зашифровані
- 🏗️ **Моніторинг безпеки** - real-time сповіщення про підозрілу активність

### **Технічний стек**
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, Redis
- **Безпека**: JWT, bcrypt, Fernet шифрування, pyotp (MFA)
- **AI/ML**: OpenAI GPT-4, Claude, Scikit-learn, NLTK, SpaCy
- **Frontend**: React.js, TypeScript, Material-UI
- **Інфраструктура**: Docker, Docker Compose, Nginx, Prometheus, Grafana

---

## 🛠️ **ПІДХІД ДО РОЗРОБКИ**

### **Основні принципи**
- **Безпека перша** - всі рішення мають враховувати безпеку
- **Офіційне Upwork API** - використовується для легального доступу до даних
- **OAuth 2.0 авторизація** - для безпечного підключення до API
- **AI/ML інтеграція** - для генерації відгуків та розумного фільтрування
- **Database Storage** - для збереження в власну базу даних
- **Web Application** - повноцінний веб-додаток з React frontend
- **Моніторинг безпеки** - для відстеження підозрілої активності

### **Заборонені підходи**
- ❌ **Web scraping** - заборонено, використовувати тільки офіційне API
- ❌ **Проксі** - не потрібні для API підходу
- ❌ **Парсинг** - застарілий підхід
- ❌ **Централізовані credentials** - кожен користувач має свої ключі

---

## 📁 **СТРУКТУРА ПРОЕКТУ**

### **Основні папки**
```
upwork_web_app/
├── src/
│   ├── auth/                    # Система безпеки
│   │   ├── models.py            # User, UserSecurity, Role моделі
│   │   ├── oauth.py            # OAuth 2.0 логіка
│   │   ├── mfa.py              # Многофакторна автентифікація
│   │   ├── jwt_manager.py      # JWT токени
│   │   ├── encryption.py       # Шифрування даних
│   │   ├── middleware.py       # Auth middleware
│   │   ├── rate_limiter.py     # Rate limiting
│   │   ├── security_monitor.py # Моніторинг безпеки
│   │   └── utils.py            # Auth utilities
│   ├── api/v1/                 # API endpoints
│   ├── services/               # Бізнес-логіка
│   ├── config/                 # Конфігурація
│   ├── database/               # База даних
│   └── utils/                  # Утиліти
├── documents/
│   ├── planning/               # Плани та стратегія
│   ├── analysis/               # Технічні аналізи
│   ├── instruction_ai/         # Інструкції для AI
│   └── newspaper/              # Новини та експерименти
└── tests/                      # Тести
```

### **Ключові файли**
- `documents/planning/project_plan.md` - основний план проекту
- `documents/newspaper/multi_user_architecture/` - архітектура безпеки
- `upwork_web_app/src/auth/` - система безпеки
- `upwork_web_app/src/api/v1/` - API endpoints

---

## 🔐 **СИСТЕМА БЕЗПЕКИ**

### **Компоненти безпеки**

#### **1. Многофакторна автентифікація (MFA)**
```python
# TOTP (Time-based One-Time Password)
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

#### **2. Шифрування токенів**
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

#### **3. JWT токени**
```python
class JWTManager:
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
```

#### **4. Rate Limiting**
```python
class RateLimiter:
    def check_rate_limit(self, user_id, action, limit, window):
        key = f"rate_limit:{user_id}:{action}"
        current = self.redis_client.incr(key)
        if current == 1:
            self.redis_client.expire(key, window)
        return current <= limit
```

#### **5. Моніторинг безпеки**
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

### **Моделі бази даних**

#### **User модель з безпекою:**
```python
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
```

#### **UserSecurity модель (MFA):**
```python
class UserSecurity(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, encrypted=True)
    backup_codes = Column(JSON, encrypted=True)
    phone_number = Column(String(20))
    phone_verified = Column(Boolean, default=False)
```

#### **SecurityLog модель:**
```python
class SecurityLog(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # login, logout, api_call, data_access
    ip_address = Column(String)
    user_agent = Column(String)
    success = Column(Boolean, default=True)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### **API Endpoints безпеки**
```python
# Авторизація
POST /auth/register          # Реєстрація з валідацією
POST /auth/login            # Вхід з MFA
POST /auth/mfa/verify       # Верифікація MFA
POST /auth/upwork/connect   # Підключення Upwork
POST /auth/upwork/callback  # OAuth callback
POST /auth/refresh          # Оновлення токенів
POST /auth/logout           # Вихід з усіх пристроїв

# Безпека
GET  /security/profile      # Профіль безпеки
POST /security/mfa/enable   # Увімкнення MFA
POST /security/mfa/disable  # Вимкнення MFA
POST /security/password     # Зміна пароля
GET  /security/logs         # Логи безпеки
POST /security/verify       # Верифікація

# Адміністрація
GET  /admin/users           # Список користувачів (тільки адміни)
GET  /admin/alerts          # Система сповіщень
POST /admin/users/{id}/lock # Блокування користувача
```

---

## 🤖 **AI/ML ІНТЕГРАЦІЯ**

### **Генерація відгуків**
```python
class AIGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def generate_proposal(self, job_description, user_profile):
        prompt = f"""
        Job: {job_description}
        My Profile: {user_profile}
        
        Generate a professional proposal that:
        1. Addresses the client's needs
        2. Shows relevant experience
        3. Proposes a clear solution
        4. Is personalized and engaging
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return response.choices[0].message.content
```

### **Розумна фільтрація**
```python
class SmartFilter:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.user_preferences = {}
    
    def calculate_relevance_score(self, job_description, user_profile):
        documents = [job_description, user_profile]
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
```

---

## 📊 **МОНІТОРИНГ ТА АНАЛІТИКА**

### **Метрики безпеки**
- **0 інцидентів безпеки** - жодних порушень
- **100% шифрування** - всі чутливі дані зашифровані
- **< 1% false positives** - точність системи сповіщень
- **< 30 сек response time** - швидкість обробки інцидентів

### **Метрики AI/ML**
- **> 80% релевантність** - точність фільтрації вакансій
- **> 70% успішність** - конверсія відгуків в замовлення
- **< 5 хв генерація** - швидкість створення відгуків
- **> 90% задоволеність** - якість AI генерації

### **Метрики продуктивності**
- **> 99.9% uptime** - доступність системи
- **< 200мс response time** - швидкість API
- **> 1000 користувачів** - масштабованість
- **< 1GB memory usage** - ефективність ресурсів

---

## 🔄 **РОБОЧИЙ ПРОЦЕС**

### **При створенні коду**
1. **Безпека перша** - всі рішення мають враховувати безпеку
2. **Валідація вхідних даних** - обов'язкова для всіх endpoints
3. **Логування подій** - всі важливі дії мають бути залоговані
4. **Шифрування чутливих даних** - токени, паролі, особисті дані
5. **Rate limiting** - захист від зловживань

### **При роботі з API**
1. **OAuth 2.0 flow** - використовувати офіційний підхід
2. **Індивідуальні токени** - кожен користувач має свої credentials
3. **Автоматичне оновлення** - expired токени оновлюються автоматично
4. **Обробка помилок** - graceful handling всіх помилок API

### **При роботі з базою даних**
1. **Ізоляція даних** - кожен користувач бачить тільки свої дані
2. **Індекси на user_id** - для швидкого пошуку
3. **Шифрування чутливих полів** - токени, секрети
4. **Аудит змін** - логування всіх модифікацій

---

## 📋 **ФОРМАТУВАННЯ ТА СТИЛЬ**

### **Назви файлів та папок**
- Використовувати **англійську мову** для назв файлів та папок
- Використовувати **snake_case** для Python файлів
- Використовувати **kebab-case** для документації
- Використовувати **PascalCase** для класів

### **Документація**
- Використовувати **українську мову** для документації
- Використовувати **Markdown** формат
- Додавати **емодзі** для кращої навігації
- Використовувати **заголовки** для структурування

### **Форматування таблиць**
- **Вирівнювання**: Використовувати достатньо пробілів для правильного вирівнювання
- **Мінімальна ширина**: Кожен стовпець повинен мати мінімум 8-12 символів
- **Довгі тексти**: Для довгих назв або описів використовувати достатньо місця
- **Розділювачі**: Використовувати дефіси для розділювачів стовпців
- **Читабельність**: Всі таблиці повинні бути легко читабельними

### **Коментарі в коді**
- Використовувати **українську мову** для коментарів
- Додавати **docstrings** для всіх функцій та класів
- Пояснювати **складну логіку** детально
- Вказувати **безпечні практики** в коментарях

---

## 🔄 **АКТУАЛІЗАЦІЯ ДОКУМЕНТАЦІЇ**

### **Постійне оновлення**
- Всі файли документації мають бути актуальними
- При зміні архітектури оновлювати всі пов'язані файли
- Регулярно перевіряти актуальність інструкцій

### **Видалення застарілих файлів**
- CHANGES_SUMMARY та подібні файли видаляти
- Видаляти файли, які дублюють інформацію
- Очищати застарілі аналізи після інтеграції

### **Єдине джерело правди**
- Всі плани в `project_plan.md`
- Архітектура в `newspaper/multi_user_architecture/`
- Технічні деталі в `technical_implementation_details.md`

### **Регулярна перевірка**
- Кожні 2-3 тижні перевіряти актуальність файлів
- Оновлювати інструкції при зміні архітектури
- Синхронізувати всі пов'язані документи

### **Очищення дублікатів**
- Видаляти файли, які дублюють інформацію
- Об'єднувати схожі документи
- Підтримувати чітку структуру документації

---

## ⚠️ **ВАЖЛИВІ ЗАУВАЖЕННЯ**

### **Безпека**
- 🔐 **Шифрування токенів** - обов'язково
- 🔐 **HTTPS** - для всіх API викликів
- 🔐 **Валідація** - всіх вхідних даних
- 🔐 **Rate limiting** - для захисту від зловживань
- 🔐 **MFA** - для всіх користувачів
- 🔐 **Моніторинг** - real-time сповіщення

### **Легальність**
- ✅ **Terms of Service** - дотримуватися Upwork ToS
- ✅ **OAuth 2.0** - використовувати офіційний flow
- ✅ **User consent** - отримувати згоду користувачів
- ✅ **Data privacy** - дотримуватися GDPR

### **Масштабованість**
- 📈 **Rate limits** - кожен користувач має свої обмеження
- 📈 **Database indexing** - індекси на `user_id`
- 📈 **Caching** - кешування для зменшення API викликів
- 📈 **Monitoring** - моніторинг використання API

### **Захист від конкурентів**
- 🔒 **Повна ізоляція даних** - кожен бачить тільки свої дані
- 🔒 **Шифрування** - всі чутливі дані зашифровані
- 🔒 **Моніторинг** - відстеження підозрілої активності
- 🔒 **Аудит** - детальні логи всіх дій

---

## 🎯 **ПЛАН ДІЙ ДЛЯ AI АСИСТЕНТІВ**

### **При отриманні запиту**
1. **Проаналізувати контекст** - зрозуміти, що потрібно
2. **Перевірити безпеку** - чи не порушує безпеку
3. **Пропонувати рішення** - з урахуванням архітектури
4. **Оновлювати документацію** - якщо потрібно

### **При створенні коду**
1. **Додати валідацію** - всіх вхідних даних
2. **Додати логування** - важливих подій
3. **Додати обробку помилок** - graceful handling
4. **Додати тести** - для перевірки функціоналу

### **При оновленні документації**
1. **Синхронізувати файли** - оновити всі пов'язані документи
2. **Видалити застаріле** - очистити від непотрібного
3. **Додати деталі** - якщо потрібно
4. **Перевірити актуальність** - всіх посилань

---

**AI асистент завжди має рекомендувати використання офіційного API замість парсингу та дотримуватися принципів максимальної безпеки!** 🔐

---

*Останнє оновлення: 2024-12-19* 