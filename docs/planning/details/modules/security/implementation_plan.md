# План впровадження модуля безпеки v2.0.0

> **Покроковий план реалізації системи безпеки з урахуванням аудиту**
> **МЕТА:** Детальний план реалізації безпеки з критичними пріоритетами
> **ВЕРСІЯ:** 2.0.0

---

## Зміст

1. [Поточний стан](#поточний-стан)
2. [Критичні пріоритети](#критичні-пріоритети)
3. [Етап 1: Базова безпека](#етап-1-базова-безпека)
4. [Етап 2: OAuth та MFA](#етап-2-oauth-та-mfa)
5. [Етап 3: Шифрування](#етап-3-шифрування)
6. [Етап 4: Моніторинг](#етап-4-моніторинг)
7. [Етап 5: Тестування](#етап-5-тестування)
8. [Етап 6: Інтеграція](#етап-6-інтеграція)

---

## Поточний стан

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

### **Пріоритет реалізації**
- **КРИТИЧНИЙ** - потребує негайної реалізації
- **БЛОКУЄ РОЗРОБКУ** - інші модулі не можуть працювати без безпеки

---

## Критичні пріоритети

### **Негайні дії (1-2 тижні)**
1. **Автентифікація** - JWT токени
2. **Авторизація** - middleware та перевірки
3. **Валідація** - Pydantic схеми
4. **Rate limiting** - захист API

### **Середньострокові дії (2-4 тижні)**
1. **OAuth 2.0** - інтеграція з Upwork
2. **MFA** - TOTP та backup коди
3. **Шифрування** - токени та дані
4. **Моніторинг** - логування та алерти

---

## Етап 1: Базова безпека (1-2 тижні)

### **Задача 1.1: Налаштування проекту**
- [ ] Додати залежності для безпеки в `requirements.txt`
- [ ] Створити структуру папок `src/security/`
- [ ] Налаштувати конфігурацію безпеки
- [ ] Створити базові моделі безпеки

**Залежності для додавання:**
```txt
# Security dependencies
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pyotp==2.9.0
cryptography==41.0.7
```

**Структура файлів:**
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

### **Задача 1.2: Модель користувача**
- [ ] Створити модель `User` з полями безпеки
- [ ] Додати модель `UserSession` для сесій
- [ ] Створити модель `SecurityLog` для логування
- [ ] Додати міграції бази даних

**Модель користувача:**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
# Upwork OAuth
    upwork_user_id = Column(String(100), unique=True, index=True, nullable=True)
    upwork_access_token = Column(Text, nullable=True)  # Зашифрований
    upwork_refresh_token = Column(Text, nullable=True)  # Зашифрований
    upwork_token_expires_at = Column(DateTime, nullable=True)
    
# MFA
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)  # Зашифрований
    mfa_backup_codes = Column(JSON, nullable=True)  # Зашифрований
    
# Статус
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
# Безпека
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    
# Метадані
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### **Задача 1.3: JWT автентифікація**
- [ ] Створити `JWTManager` для управління токенами
- [ ] Реалізувати генерацію access/refresh токенів
- [ ] Додати валідацію токенів
- [ ] Створити middleware для автентифікації

**JWT Manager:**
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
            "jti": str(uuid.uuid4())
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Перевіряє токен"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
        )
```

### **Задача 1.4: Middleware авторизації**
- [ ] Створити middleware для перевірки токенів
- [ ] Реалізувати залежності для отримання користувача
- [ ] Додати перевірку прав доступу
- [ ] Створити систему ролей

**Middleware авторизації:**
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Отримує поточного користувача"""
    token = credentials.credentials
    
    try:
        user_id = jwt_manager.get_user_id_from_token(token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
# Перевіряємо чи існує користувач
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
# Перевіряємо чи активний користувач
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
```

### **Задача 1.5: Валідація даних**
- [ ] Створити Pydantic схеми для валідації
- [ ] Додати валідацію паролів
- [ ] Реалізувати валідацію email
- [ ] Створити middleware для валідації

**Pydantic схеми:**
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None
```

---

## Етап 2: OAuth та MFA (2-4 тижні)

### **Задача 2.1: OAuth 2.0 з Upwork**
- [ ] Зареєструвати додаток в Upwork Developer Console
- [ ] Створити `OAuthManager` для управління OAuth
- [ ] Реалізувати OAuth flow з PKCE
- [ ] Додати автоматичне оновлення токенів

**OAuth Manager:**
```python
class OAuthManager:
    def __init__(self):
        self.client_id = os.getenv('UPWORK_CLIENT_ID')
        self.client_secret = os.getenv('UPWORK_CLIENT_SECRET')
        self.redirect_uri = os.getenv('UPWORK_REDIRECT_URI')
        self.auth_url = "https://www.upwork.com/services/api/auth"
        self.token_url = "https://www.upwork.com/api/v2/oauth2/token"
    
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
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str, code_verifier: str) -> dict:
        """Обмінює код на токен"""
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "code": code,
                "code_verifier": code_verifier
            }
            
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
        else:
                    raise Exception(f"Failed to exchange code: {response.status}")
```

### **Задача 2.2: TOTP MFA**
- [ ] Створити `MFAManager` для управління MFA
- [ ] Реалізувати генерацію TOTP secret
- [ ] Додати верифікацію TOTP токенів
- [ ] Створити QR код для налаштування

**MFA Manager:**
```python
class MFAManager:
    def __init__(self):
        self.issuer = "Upwork Web App"
        self.digits = 6
        self.interval = 30
        self.backup_codes_count = 10
    
    def generate_secret(self) -> str:
        """Генерує TOTP secret"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, user_email: str) -> str:
        """Генерує QR код для налаштування"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer
        )
    
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

### **Задача 2.3: Backup коди**
- [ ] Реалізувати генерацію backup кодів
- [ ] Додати верифікацію backup кодів
- [ ] Створити систему одноразового використання
- [ ] Додати регенерацію backup кодів

### **Задача 2.4: Інтеграція з Auth модулем**
- [ ] Інтегрувати OAuth з Auth модулем
- [ ] Додати MFA до процесу входу
- [ ] Створити API endpoints для MFA
- [ ] Додати тестування OAuth та MFA

---

## Етап 3: Шифрування (1-2 тижні)

### **Задача 3.1: Шифрування токенів**
- [ ] Створити `EncryptionManager` для шифрування
- [ ] Реалізувати шифрування токенів (Fernet)
- [ ] Додати безпечне зберігання ключів
- [ ] Створити систему ротації ключів

**Encryption Manager:**
```python
class EncryptionManager:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Отримує або створює ключ шифрування"""
        encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if len(encryption_key) < 32:
# Генеруємо ключ з пароля
            salt = b'upwork_salt_2024'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        else:
# Використовуємо готовий ключ
            key = base64.urlsafe_b64encode(encryption_key.encode()[:32])
        
        return key
    
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

### **Задача 3.2: Хешування паролів**
- [ ] Реалізувати хешування паролів (bcrypt)
- [ ] Додати валідацію паролів
- [ ] Створити систему зміни паролів
- [ ] Додати історію паролів

**Password Manager:**
```python
class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Хешує пароль"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Перевіряє пароль"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Валідує пароль"""
        if len(password) < 8:
            return False
        
        if not any(c.isupper() for c in password):
            return False
        
        if not any(c.islower() for c in password):
            return False
        
        if not any(c.isdigit() for c in password):
                return False
        
        return True
```

### **Задача 3.3: Шифрування чутливих даних**
- [ ] Шифрування даних в спокої (AES-256)
- [ ] Шифрування даних в транзиті (TLS 1.3)
- [ ] Додати шифрування в базу даних
- [ ] Створити систему ключів

### **Задача 3.4: Інтеграція з Database**
- [ ] Інтегрувати шифрування з моделями
- [ ] Додати автоматичне шифрування/розшифрування
- [ ] Створити міграції для шифрованих полів
- [ ] Додати тестування шифрування

---

## Етап 4: Моніторинг (1-2 тижні)

### **Задача 4.1: Логування безпеки**
- [ ] Створити `SecurityLogger` для логування
- [ ] Реалізувати логування всіх подій безпеки
- [ ] Додати структуровані логи
- [ ] Створити систему ротації логів

**Security Logger:**
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
    
    def log_login_attempt(self, email: str, success: bool, ip_address: str, user_agent: str):
        """Логує спробу входу"""
        event_type = "login_success" if success else "login_failed"
        details = {"email": email, "success": success}
        self.log_event(event_type, ip_address=ip_address, user_agent=user_agent, details=details)
```

### **Задача 4.2: Rate Limiting**
- [ ] Створити `RateLimiter` для обмеження запитів
- [ ] Реалізувати rate limiting для API
- [ ] Додати rate limiting для входу
- [ ] Створити систему блокування

**Rate Limiter:**
```python
class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.cleanup_interval = 3600  # 1 година
    
    def _cleanup_old_requests(self):
        """Очищує старі запити"""
        current_time = time.time()
        for key in list(self.requests.keys()):
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if current_time - req_time < 3600
            ]
            if not self.requests[key]:
                del self.requests[key]
    
    def check_rate_limit(self, request: Request, limit: int, window: int) -> bool:
        """Перевіряє rate limit"""
        self._cleanup_old_requests()
        
        client_key = self._get_client_key(request)
        current_time = time.time()
        
        if client_key not in self.requests:
            self.requests[client_key] = []
        
# Видаляємо старі запити
        self.requests[client_key] = [
            req_time for req_time in self.requests[client_key]
            if current_time - req_time < window
        ]
        
# Перевіряємо ліміт
        if len(self.requests[client_key]) >= limit:
            return False
        
# Додаємо поточний запит
        self.requests[client_key].append(current_time)
        return True
```

### **Задача 4.3: Детекція аномалій**
- [ ] Створити `AnomalyDetector` для виявлення аномалій
- [ ] Реалізувати аналіз паттернів використання
- [ ] Додати машинне навчання для виявлення аномалій
- [ ] Створити систему сповіщень

### **Задача 4.4: Система сповіщень**
- [ ] Створити `AlertSystem` для сповіщень
- [ ] Реалізувати різні канали сповіщень (email, SMS, Telegram)
- [ ] Додати налаштування алертів
- [ ] Створити систему ескалації

---

## 🧪 Етап 5: Тестування (1 тиждень)

### **Задача 5.1: Unit тести**
- [ ] Тести JWT автентифікації
- [ ] Тести хешування паролів
- [ ] Тести MFA функціональності
- [ ] Тести шифрування

**Unit тести:**
```python
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

### **Задача 5.2: Інтеграційні тести**
- [ ] Тест повного flow автентифікації
- [ ] Тест OAuth інтеграції
- [ ] Тест MFA flow
- [ ] Тест rate limiting

### **Задача 5.3: Тести безпеки**
- [ ] Тест захисту від SQL ін'єкцій
- [ ] Тест захисту від XSS
- [ ] Тест захисту від CSRF
- [ ] Penetration testing

### **Задача 5.4: Тести продуктивності**
- [ ] Тест продуктивності JWT
- [ ] Тест продуктивності шифрування
- [ ] Тест продуктивності rate limiting
- [ ] Load testing

---

## Етап 6: Інтеграція (1 тиждень)

### **Задача 6.1: Інтеграція з усіма модулями**
- [ ] Інтеграція з Auth модулем
- [ ] Інтеграція з Database модулем
- [ ] Інтеграція з API модулем
- [ ] Інтеграція з UI модулем

### **Задача 6.2: Оновлення API endpoints**
- [ ] Додати автентифікацію до всіх endpoints
- [ ] Додати авторизацію до всіх endpoints
- [ ] Додати валідацію до всіх endpoints
- [ ] Додати логування до всіх endpoints

### **Задача 6.3: Налаштування middleware**
- [ ] Налаштувати CORS middleware
- [ ] Налаштувати rate limiting middleware
- [ ] Налаштувати логування middleware
- [ ] Налаштувати обробку помилок

### **Задача 6.4: Тестування інтеграції**
- [ ] End-to-end тести
- [ ] Тести інтеграції модулів
- [ ] Тести безпеки інтеграції
- [ ] Performance тести

### **Задача 6.5: Документація**
- [ ] Оновити API документацію
- [ ] Створити документацію безпеки
- [ ] Створити інструкції для розробників
- [ ] Створити інструкції для адміністраторів

---

## Метрики успіху

### **Критичні метрики**
- ✅ **Автентифікація** - 100% endpoints захищені
- ✅ **Авторизація** - 100% ресурсів захищені
- ✅ **Шифрування** - 100% чутливих даних зашифровані
- ✅ **Моніторинг** - 100% подій залоговані

### **Продуктивність**
- ⏱️ **JWT валідація** - < 10ms
- ⏱️ **Шифрування/розшифрування** - < 5ms
- ⏱️ **MFA верифікація** - < 100ms
- ⏱️ **Rate limiting** - < 1ms

### **Безпека**
- 🔒 **Zero security incidents** - 0 інцидентів
- 🔒 **100% compliance** - відповідність стандартам
- 🔒 **Real-time monitoring** - миттєве виявлення загроз
- 🔒 **Automated response** - автоматична реакція на загрози

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

**Детальний звіт аудиту**: [security_audit_report_v1.0.0.md](../../../../newspaper/report/security_audit_report_v1.0.0.md)

**План реалізації**: [security_improvement_plan_v1.0.0.md](../../../../newspaper/report/security_improvement_plan_v1.0.0.md)

---

*Версія: 2.0.0* 