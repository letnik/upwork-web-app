# 🔧 ТЕХНІЧНІ ДЕТАЛІ РЕАЛІЗАЦІЇ

> **Детальний план технічної реалізації багатокористувацької системи з максимальною безпекою**

---

## 🏗️ **ОНОВЛЕННЯ АРХІТЕКТУРИ ПРОЕКТУ**

### **Поточна структура → Нова структура:**

```
upwork_web_app/
├── src/
│   ├── auth/                    # НОВА ПАПКА - СИСТЕМА БЕЗПЕКИ
│   │   ├── __init__.py
│   │   ├── models.py            # User, UserSecurity, Role моделі
│   │   ├── oauth.py            # OAuth 2.0 логіка
│   │   ├── mfa.py              # Многофакторна автентифікація
│   │   ├── jwt_manager.py      # JWT токени
│   │   ├── encryption.py       # Шифрування даних
│   │   ├── middleware.py       # Auth middleware
│   │   ├── rate_limiter.py     # Rate limiting
│   │   ├── security_monitor.py # Моніторинг безпеки
│   │   └── utils.py            # Auth utilities
│   ├── api/                     # НОВА ПАПКА
│   │   ├── __init__.py
│   │   ├── v1/                 # API версія 1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Auth endpoints
│   │   │   ├── security.py     # Security endpoints
│   │   │   ├── users.py        # User endpoints
│   │   │   ├── jobs.py         # Jobs endpoints
│   │   │   ├── applications.py # Applications endpoints
│   │   │   └── messages.py     # Messages endpoints
│   │   └── dependencies.py     # API dependencies
│   ├── services/                # НОВА ПАПКА
│   │   ├── __init__.py
│   │   ├── upwork_service.py   # Upwork API service
│   │   ├── ai_service.py       # AI service
│   │   ├── security_service.py # Security service
│   │   └── notification_service.py
│   └── utils/
│       ├── token_manager.py    # НОВИЙ ФАЙЛ
│       ├── encryption.py       # НОВИЙ ФАЙЛ
│       └── security_logger.py  # НОВИЙ ФАЙЛ
```

---

## 🔐 **СИСТЕМА БЕЗПЕКИ**

### **1. Моделі бази даних**

#### **User модель:**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # bcrypt
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Upwork credentials (зашифровані)
    upwork_access_token = Column(String(1000), nullable=True)
    upwork_refresh_token = Column(String(1000), nullable=True)
    upwork_user_id = Column(String(255), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Безпека
    role = Column(String(50), default='freelancer')  # freelancer, premium, admin, moderator
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # Логування
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Відносини
    security = relationship("UserSecurity", back_populates="user", uselist=False)
    roles = relationship("UserRole", back_populates="user")
    security_logs = relationship("SecurityLog", back_populates="user")
    alerts = relationship("SecurityAlert", back_populates="user")
```

#### **UserSecurity модель (MFA):**
```python
class UserSecurity(Base):
    __tablename__ = "user_security"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # MFA налаштування
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)  # TOTP secret (зашифрований)
    backup_codes = Column(JSON, nullable=True)  # Backup коди (зашифровані)
        
    # Додаткова верифікація
    phone_number = Column(String(20), nullable=True)
    phone_verified = Column(Boolean, default=False)
    
    # Безпека сесій
    session_timeout = Column(Integer, default=3600)  # в секундах
    max_concurrent_sessions = Column(Integer, default=5)
    
    # Відносини
    user = relationship("User", back_populates="security")
```

#### **Role модель (система ролей):**
```python
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(JSON, nullable=False)  # Список дозволів
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Відносини
    user = relationship("User", back_populates="roles")
    role = relationship("Role")
```

#### **SecurityLog модель (логі безпеки):**
```python
class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Деталі події
    action = Column(String(100), nullable=False)  # login, logout, api_call, data_access
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, default=True)
    details = Column(JSON, nullable=True)
    
    # Метадані
    created_at = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String(255), nullable=True)
```

#### **SecurityAlert модель (сповіщення безпеки):**
```python
class SecurityAlert(Base):
    __tablename__ = "security_alerts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Деталі сповіщення
    alert_type = Column(String(100), nullable=False)  # suspicious_activity, failed_login, data_breach
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    
    # Статус
    resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Метадані
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Відносини
    user = relationship("User", back_populates="alerts")
```

### **2. Шифрування даних**

#### **EncryptionManager:**
```python
from cryptography.fernet import Fernet
import base64
import os
from typing import Optional

class EncryptionManager:
    def __init__(self):
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable is required")
        
        # Конвертуємо base64 ключ в bytes
        self.key = base64.urlsafe_b64encode(key.encode())
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Шифрує дані"""
        if not data:
            return data
        encrypted_bytes = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_bytes).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Розшифровує дані"""
        if not encrypted_data:
            return encrypted_data
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    
    def encrypt_json(self, data: dict) -> str:
        """Шифрує JSON дані"""
        import json
        json_str = json.dumps(data)
        return self.encrypt(json_str)
    
    def decrypt_json(self, encrypted_data: str) -> dict:
        """Розшифровує JSON дані"""
        import json
        decrypted_str = self.decrypt(encrypted_data)
        return json.loads(decrypted_str)
```

### **3. Многофакторна автентифікація (MFA)**

#### **MFAManager:**
```python
import pyotp
import secrets
import qrcode
from typing import List, Tuple

class MFAManager:
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def generate_secret(self) -> str:
        """Генерує TOTP secret"""
        return pyotp.random_base32()
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Генерує backup коди"""
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()[:8]  # 8 символів
            codes.append(code)
        return codes
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Перевіряє TOTP токен"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # 30 сек вікно
    
    def generate_qr_code(self, secret: str, email: str, issuer: str = "Upwork Web App") -> str:
        """Генерує QR код для Google Authenticator"""
        provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            email, issuer_name=issuer
        )
        return provisioning_uri
    
    def create_qr_image(self, secret: str, email: str) -> bytes:
        """Створює QR код як зображення"""
        uri = self.generate_qr_code(secret, email)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Конвертуємо в bytes
        import io
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def verify_backup_code(self, backup_codes: List[str], code: str) -> Tuple[bool, List[str]]:
        """Перевіряє backup код і повертає оновлений список"""
        if code in backup_codes:
            backup_codes.remove(code)  # Використовуємо код
            return True, backup_codes
        return False, backup_codes
```

### **4. JWT токени**

#### **JWTManager:**
```python
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

class JWTManager:
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY')
        if not self.secret_key:
            raise ValueError("SECRET_KEY environment variable is required")
        
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Створює access токен"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Створює refresh токен"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Перевіряє токен"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Декодує токен без перевірки терміну дії"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            return payload
        except jwt.JWTError:
            return None
```

### **5. Rate Limiting**

#### **RateLimiter:**
```python
import redis
import time
from typing import Optional

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Перевіряє rate limit"""
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, window)
        return current <= limit
    
    def get_remaining_attempts(self, key: str) -> int:
        """Повертає кількість залишених спроб"""
        current = self.redis.get(key)
        if current is None:
            return 0
        return int(current)
    
    def reset_rate_limit(self, key: str):
        """Скидає rate limit"""
        self.redis.delete(key)
    
    def check_login_attempts(self, user_id: int) -> Tuple[bool, Optional[int]]:
        """Перевіряє спроби входу користувача"""
        key = f"login_attempts:{user_id}"
        attempts = self.redis.get(key)
        
        if attempts is None:
            return True, None
        
        attempts = int(attempts)
        if attempts >= 5:
            # Експоненціальне блокування
            lock_duration = min(2 ** (attempts - 5), 24 * 3600)  # Максимум 24 години
            return False, lock_duration
        
        return True, None
    
    def increment_login_attempts(self, user_id: int):
        """Збільшує лічильник невдалих спроб"""
        key = f"login_attempts:{user_id}"
        self.redis.incr(key)
        self.redis.expire(key, 3600)  # 1 година
```

### **6. OAuth 2.0 Manager**

#### **OAuth2Manager:**
```python
import aiohttp
import os
from urllib.parse import urlencode
from typing import Dict, Optional

class OAuth2Manager:
    def __init__(self):
        self.client_id = os.getenv('UPWORK_CLIENT_ID')
        self.client_secret = os.getenv('UPWORK_CLIENT_SECRET')
        self.redirect_uri = os.getenv('UPWORK_REDIRECT_URI')
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Missing OAuth configuration")
    
    def get_authorization_url(self, state: str) -> str:
        """Генерує URL для авторизації в Upwork"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'r_workdiary r_workdairy r_workdairy_read r_workdairy_write'
        }
        return f"https://www.upwork.com/services/api/auth?{urlencode(params)}"
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Обмінює код на токени"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://www.upwork.com/api/v2/oauth2/token',
                data=data
            ) as response:
                return await response.json()
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Оновлює access токен"""
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://www.upwork.com/api/v2/oauth2/token',
                data=data
            ) as response:
                return await response.json()
```

### **7. Security Monitor**

#### **SecurityMonitor:**
```python
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

class SecurityMonitor:
    def __init__(self, telegram_bot, email_service):
        self.telegram_bot = telegram_bot
        self.email_service = email_service
    
    async def log_security_event(self, user_id: Optional[int], action: str, 
                                ip_address: str, user_agent: str, 
                                success: bool, details: Dict[str, Any] = None):
        """Логує подію безпеки"""
        log_entry = SecurityLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details
        )
        
        # Зберігаємо в БД
        # db.add(log_entry)
        # db.commit()
        
        # Перевіряємо на підозрілу активність
        await self.check_suspicious_activity(user_id, action, ip_address)
    
    async def check_suspicious_activity(self, user_id: Optional[int], 
                                      action: str, ip_address: str):
        """Перевіряє на підозрілу активність"""
        suspicious_patterns = [
            'multiple_failed_logins',
            'unusual_ip_address',
            'rapid_api_calls',
            'data_access_pattern'
        ]
        
        # Логіка виявлення підозрілої активності
        if action == 'login' and not success:
            await self.check_failed_login_pattern(user_id, ip_address)
        
        if action == 'api_call':
            await self.check_api_usage_pattern(user_id, ip_address)
    
    async def create_security_alert(self, user_id: Optional[int], 
                                  alert_type: str, severity: str, 
                                  description: str, details: Dict[str, Any] = None):
        """Створює сповіщення безпеки"""
        alert = SecurityAlert(
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            details=details
        )
        
        # Зберігаємо в БД
        # db.add(alert)
        # db.commit()
        
        # Відправляємо сповіщення
        await self.send_security_notifications(alert)
    
    async def send_security_notifications(self, alert: SecurityAlert):
        """Відправляє сповіщення про безпеку"""
        # Telegram сповіщення
        if alert.severity in ['high', 'critical']:
            await self.telegram_bot.send_security_alert(alert)
        
        # Email сповіщення
        if alert.user_id:
            await self.email_service.send_security_alert(alert)
```

### **8. API Endpoints**

#### **Auth Endpoints:**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
async def register(user_data: UserCreate):
    """Реєстрація користувача"""
    # Валідація даних
    # Хешування пароля
    # Створення користувача
    # Відправка верифікаційного email
    pass

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Вхід користувача"""
    # Перевірка credentials
    # Перевірка MFA
    # Створення JWT токенів
    # Логування події
    pass

@router.post("/mfa/verify")
async def verify_mfa(token: str, user_id: int):
    """Верифікація MFA"""
    # Перевірка TOTP або backup коду
    # Оновлення статусу користувача
    pass

@router.post("/upwork/connect")
async def connect_upwork():
    """Підключення Upwork акаунту"""
    # Генерація OAuth URL
    # Перенаправлення на Upwork
    pass

@router.post("/upwork/callback")
async def upwork_callback(code: str, state: str):
    """OAuth callback від Upwork"""
    # Обмін коду на токени
    # Збереження токенів
    # Перенаправлення на додаток
    pass

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Оновлення access токена"""
    # Перевірка refresh токена
    # Створення нового access токена
    pass

@router.post("/logout")
async def logout():
    """Вихід користувача"""
    # Додавання токена в blacklist
    # Очищення сесії
    pass
```

#### **Security Endpoints:**
```python
@router.get("/security/profile")
async def get_security_profile(user: User = Depends(get_current_user)):
    """Отримує профіль безпеки користувача"""
    pass

@router.post("/security/mfa/enable")
async def enable_mfa(user: User = Depends(get_current_user)):
    """Увімкнення MFA"""
    pass

@router.post("/security/mfa/disable")
async def disable_mfa(user: User = Depends(get_current_user)):
    """Вимкнення MFA"""
    pass

@router.post("/security/password")
async def change_password(user: User = Depends(get_current_user)):
    """Зміна пароля"""
    pass

@router.get("/security/logs")
async def get_security_logs(user: User = Depends(get_current_user)):
    """Отримує логи безпеки"""
        pass
```

### **9. Middleware**

#### **AuthMiddleware:**
```python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time

class AuthMiddleware:
    def __init__(self, jwt_manager: JWTManager, rate_limiter: RateLimiter):
        self.jwt_manager = jwt_manager
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request: Request, call_next):
        # Логування запиту
        start_time = time.time()
        
        # Rate limiting
        client_ip = request.client.host
        if not self.rate_limiter.check_rate_limit(f"api:{client_ip}", 100, 3600):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )
        
        # Перевірка JWT токена
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = self.jwt_manager.verify_token(token)
            
            if payload:
                request.state.user_id = payload.get("user_id")
                request.state.user_role = payload.get("role")
            else:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token"}
                )
        
        # Обробка запиту
        response = await call_next(request)
        
        # Логування відповіді
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

### **10. Міграція даних**

#### **Створення міграцій:**
```python
# alembic/versions/001_create_security_tables.py

"""Create security tables

Revision ID: 001
Revises: 
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Створення таблиці користувачів
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('upwork_access_token', sa.String(length=1000), nullable=True),
        sa.Column('upwork_refresh_token', sa.String(length=1000), nullable=True),
        sa.Column('upwork_user_id', sa.String(length=255), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('phone_verified', sa.Boolean(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=True),
        sa.Column('account_locked_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Створення таблиці безпеки користувачів
    op.create_table('user_security',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=True),
        sa.Column('mfa_secret', sa.String(length=255), nullable=True),
        sa.Column('backup_codes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('phone_verified', sa.Boolean(), nullable=True),
        sa.Column('session_timeout', sa.Integer(), nullable=True),
        sa.Column('max_concurrent_sessions', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Створення таблиці ролей
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('permissions', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Створення таблиці логів безпеки
    op.create_table('security_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Створення таблиці сповіщень безпеки
    op.create_table('security_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('alert_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('security_alerts')
    op.drop_table('security_logs')
    op.drop_table('roles')
    op.drop_table('user_security')
    op.drop_table('users')
```

---

## 🚀 **ПЛАН ВПРОВАДЖЕННЯ**

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

---

*Останнє оновлення: 2024-12-19* 