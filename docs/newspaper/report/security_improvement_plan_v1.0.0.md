# ПЛАН ПОКРАЩЕННЯ БЕЗПЕКИ ПРОЕКТУ v1.0.0

> **МЕТА:** Покроковий план реалізації безпеки згідно з аудитом
> **ТИП:** [update]
> **ВЕРСІЯ:** 1.0.0

## Зміст

1. [Негайні дії](#негайні-дії)
2. [Етап 1: Базова автентифікація](#етап-1-базова-автентифікація)
3. [Етап 2: OAuth та MFA](#етап-2-oauth-та-mfa)
4. [Етап 3: Шифрування](#етап-3-шифрування)
5. [Етап 4: Моніторинг](#етап-4-моніторинг)
6. [Тестування безпеки](#тестування-безпеки)
7. [Розгортання](#розгортання)

---

## Негайні дії

### **1. Оновлення залежностей**
Додати в `requirements.txt`:

```txt
# Security dependencies
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pyotp==2.9.0
cryptography==41.0.7
python-dotenv==1.0.0
```

### **2. Оновлення налаштувань**
Створити `src/config/security.py`:

```python
import os
from datetime import timedelta
from typing import Optional

class SecuritySettings:
# JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
# Password Configuration
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
# Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
# MFA Configuration
    MFA_ISSUER: str = "Upwork Web App"
    MFA_DIGITS: int = 6
    MFA_INTERVAL: int = 30
    MFA_BACKUP_CODES_COUNT: int = 10
    
# Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-change-this")
    
# CORS Configuration
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "https://yourdomain.com"
    ]
    
# Database Security
    DB_SSL_MODE: str = "require"
    DB_SSL_CERT: Optional[str] = None
    DB_SSL_KEY: Optional[str] = None
    DB_SSL_CA: Optional[str] = None

security_settings = SecuritySettings()
```

### **3. Оновлення docker-compose.yml**
```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: upwork_parser_app
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/upwork_parser
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - upwork_network

  postgres:
    image: postgres:15
    container_name: upwork_parser_postgres
    environment:
      - POSTGRES_DB=upwork_parser
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
# Прибрати зовнішній доступ
# ports:
# - "5432:5432"
    restart: unless-stopped
    networks:
      - upwork_network

  redis:
    image: redis:7-alpine
    container_name: upwork_parser_redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
# Прибрати зовнішній доступ
# ports:
# - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - upwork_network

volumes:
  postgres_data:
  redis_data:

networks:
  upwork_network:
    driver: bridge
```

---

## Етап 1: Базова автентифікація

### **1.1 Модель користувача**
Створити `src/database/models.py`:

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """Модель користувача з безпекою"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
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

class UserSession(Base):
    """Модель сесії користувача"""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True, nullable=False)
    
# Метадані
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

class SecurityLog(Base):
    """Модель логу безпеки"""
    
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(100), nullable=False)  # login, logout, mfa_failed, etc.
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    
# Метадані
    created_at = Column(DateTime, default=datetime.utcnow)
```

### **1.2 Схеми Pydantic**
Створити `src/schemas/auth.py`:

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

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

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
```

### **1.3 JWT менеджер**
Створити `src/utils/jwt_manager.py`:

```python
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from ..config.security import security_settings

class JWTManager:
    def __init__(self):
        self.secret_key = security_settings.SECRET_KEY
        self.algorithm = security_settings.ALGORITHM
        self.access_token_expire_minutes = security_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = security_settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Створює access токен"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Створює refresh токен"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
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
    
    def get_user_id_from_token(self, token: str) -> int:
        """Отримує user_id з токена"""
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return int(user_id)

jwt_manager = JWTManager()
```

### **1.4 Менеджер паролів**
Створити `src/utils/password_manager.py`:

```python
from passlib.context import CryptContext
from ..config.security import security_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        if len(password) < security_settings.PASSWORD_MIN_LENGTH:
            return False
        
        if security_settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False
        
        if security_settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False
        
        if security_settings.PASSWORD_REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            return False
        
        if security_settings.PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        return True

password_manager = PasswordManager()
```

### **1.5 Middleware авторизації**
Створити `src/middleware/auth.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.models import User, UserSession
from ..utils.jwt_manager import jwt_manager

security = HTTPBearer()

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
    
# Перевіряємо чи не заблокований користувач
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is locked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Отримує активного користувача"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Отримує адміністратора"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

---

## Етап 2: OAuth та MFA

### **2.1 MFA менеджер**
Створити `src/utils/mfa_manager.py`:

```python
import pyotp
import secrets
from typing import List, Dict
from ..config.security import security_settings

class MFAManager:
    def __init__(self):
        self.issuer = security_settings.MFA_ISSUER
        self.digits = security_settings.MFA_DIGITS
        self.interval = security_settings.MFA_INTERVAL
        self.backup_codes_count = security_settings.MFA_BACKUP_CODES_COUNT
    
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
    
    def verify_backup_code(self, backup_codes: List[str], code: str) -> bool:
        """Перевіряє backup код"""
        if code in backup_codes:
            backup_codes.remove(code)  # Використовуємо код один раз
            return True
        return False

mfa_manager = MFAManager()
```

### **2.2 OAuth менеджер**
Створити `src/utils/oauth_manager.py`:

```python
import aiohttp
from typing import Dict, Optional
from ..config.security import security_settings

class OAuthManager:
    def __init__(self):
        self.client_id = security_settings.UPWORK_CLIENT_ID
        self.client_secret = security_settings.UPWORK_CLIENT_SECRET
        self.redirect_uri = security_settings.UPWORK_CALLBACK_URL
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
    
    async def exchange_code_for_token(self, code: str, code_verifier: str) -> Dict:
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
    
    async def refresh_token(self, refresh_token: str) -> Dict:
        """Оновлює токен"""
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token
            }
            
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to refresh token: {response.status}")

oauth_manager = OAuthManager()
```

---

## Етап 3: Шифрування

### **3.1 Менеджер шифрування**
Створити `src/utils/encryption_manager.py`:

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from ..config.security import security_settings

class EncryptionManager:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Отримує або створює ключ шифрування"""
        encryption_key = security_settings.ENCRYPTION_KEY
        
        if len(encryption_key) < 32:
# Генеруємо ключ з пароля
            salt = b'upwork_salt_2024'  # В продакшені використовувати унікальну сіль
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
    
    def encrypt_dict(self, data: dict) -> dict:
        """Шифрує словник"""
        encrypted_dict = {}
        for key, value in data.items():
            if isinstance(value, str) and value:
                encrypted_dict[key] = self.encrypt(value)
            else:
                encrypted_dict[key] = value
        return encrypted_dict
    
    def decrypt_dict(self, encrypted_data: dict) -> dict:
        """Розшифровує словник"""
        decrypted_dict = {}
        for key, value in encrypted_data.items():
            if isinstance(value, str) and value:
                decrypted_dict[key] = self.decrypt(value)
            else:
                decrypted_dict[key] = value
        return decrypted_dict

encryption_manager = EncryptionManager()
```

---

## Етап 4: Моніторинг

### **4.1 Менеджер логування безпеки**
Створити `src/utils/security_logger.py`:

```python
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..database.models import SecurityLog, User
from ..database.connection import get_db

class SecurityLogger:
    def __init__(self):
        self.db = get_db
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Логує подію безпеки"""
        try:
            db = next(self.db())
            security_log = SecurityLog(
                user_id=user_id,
                event_type=event_type,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details
            )
            db.add(security_log)
            db.commit()
        except Exception as e:
# Fallback логування
            print(f"Security log error: {e}")
    
    def log_login_attempt(self, email: str, success: bool, ip_address: str, user_agent: str):
        """Логує спробу входу"""
        event_type = "login_success" if success else "login_failed"
        details = {"email": email, "success": success}
        self.log_event(event_type, ip_address=ip_address, user_agent=user_agent, details=details)
    
    def log_mfa_attempt(self, user_id: int, success: bool, ip_address: str):
        """Логує спробу MFA"""
        event_type = "mfa_success" if success else "mfa_failed"
        details = {"success": success}
        self.log_event(event_type, user_id=user_id, ip_address=ip_address, details=details)
    
    def log_suspicious_activity(self, user_id: Optional[int], activity_type: str, details: Dict):
        """Логує підозрілу активність"""
        self.log_event("suspicious_activity", user_id=user_id, details=details)

security_logger = SecurityLogger()
```

### **4.2 Rate Limiting**
Створити `src/middleware/rate_limiter.py`:

```python
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time
from ..config.security import security_settings

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
    
    def _get_client_key(self, request: Request) -> str:
        """Отримує ключ клієнта"""
# Використовуємо IP адресу або user_id якщо авторизований
        client_ip = request.client.host
        user_id = getattr(request.state, 'user_id', None)
        return f"{user_id}:{client_ip}" if user_id else client_ip
    
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

rate_limiter = RateLimiter()

def rate_limit_middleware(limit: int = 100, window: int = 60):
    """Middleware для rate limiting"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            if not rate_limiter.check_rate_limit(request, limit, window):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 🧪 Тестування безпеки

### **Тести автентифікації**
Створити `tests/test_auth.py`:

```python
import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..utils.password_manager import password_manager
from ..utils.jwt_manager import jwt_manager

client = TestClient(app)

def test_user_registration():
    """Тест реєстрації користувача"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@example.com"

def test_user_login():
    """Тест входу користувача"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_protected_endpoint():
    """Тест захищеного endpoint"""
# Спочатку входимо
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    token = login_response.json()["access_token"]
    
# Тестуємо захищений endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/jobs", headers=headers)
    assert response.status_code == 200

def test_invalid_token():
    """Тест невалідного токена"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/jobs", headers=headers)
    assert response.status_code == 401

def test_rate_limiting():
    """Тест rate limiting"""
    for _ in range(101):  # Перевищуємо ліміт
        response = client.get("/jobs")
        if response.status_code == 429:
            break
    else:
        pytest.fail("Rate limiting not working")
```

---

## Розгортання

### **1. Оновлення .env файлу**
```env
# Database
DATABASE_URL=postgresql://postgres:secure_password@postgres:5432/upwork_parser
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_URL=redis://:secure_redis_password@redis:6379
REDIS_PASSWORD=secure_redis_password

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ENCRYPTION_KEY=your-encryption-key-change-this-in-production

# Upwork OAuth
UPWORK_CLIENT_ID=your_upwork_client_id
UPWORK_CLIENT_SECRET=your_upwork_client_secret
UPWORK_REDIRECT_URI=https://yourdomain.com/auth/upwork/callback

# Environment
ENVIRONMENT=production
DEBUG=false
```

### **2. Оновлення main.py**
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .middleware.auth import get_current_user
from .config.security import security_settings

app = FastAPI(
    title="Upwork Web App API",
    description="Secure API for Upwork automation",
    version="1.0.0"
)

# Безпечний CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Захищені endpoints
@app.get("/jobs")
async def get_jobs(current_user = Depends(get_current_user)):
# Логіка з перевіркою прав доступу
    pass

@app.post("/applications")
async def create_application(current_user = Depends(get_current_user)):
# Логіка з перевіркою прав доступу
    pass
```

---

## Чек-лист реалізації

### **Тиждень 1: Базова безпека**
- [ ] Додати залежності для безпеки
- [ ] Створити модель користувача
- [ ] Реалізувати JWT автентифікацію
- [ ] Додати middleware для авторизації
- [ ] Налаштувати валідацію вхідних даних

### **Тиждень 2: OAuth та MFA**
- [ ] Реалізувати OAuth 2.0 з Upwork
- [ ] Додати TOTP MFA
- [ ] Створити backup коди
- [ ] Налаштувати QR код

### **Тиждень 3: Шифрування**
- [ ] Шифрування токенів
- [ ] Хешування паролів
- [ ] Шифрування чутливих даних
- [ ] Безпечне зберігання ключів

### **Тиждень 4: Моніторинг**
- [ ] Логування безпеки
- [ ] Rate limiting
- [ ] Детекція аномалій
- [ ] Система сповіщень

---

*Версія: 1.0.0* 