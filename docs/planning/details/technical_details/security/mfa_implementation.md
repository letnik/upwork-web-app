# MFA Реалізація

> **Детальна реалізація многофакторної автентифікації з TOTP та backup кодами**

---

## Зміст

1. [Огляд MFA](#огляд-mfa)
2. [Архітектура](#архітектура)
3. [TOTP Реалізація](#totp-реалізація)
4. [Backup Коди](#backup-коди)
5. [API Endpoints](#api-endpoints)
6. [Безпека](#безпека)
7. [Тестування](#тестування)

---

## Огляд MFA

### Призначення
Многофакторна автентифікація (MFA) забезпечує додатковий рівень безпеки для акаунтів користувачів через TOTP (Time-based One-Time Password) та backup коди.

### Методи MFA
- **TOTP** - часові одноразові паролі (Google Authenticator, Authy)
- **Backup коди** - резервні коди для відновлення доступу
- **SMS верифікація** - додатковий метод (майбутнє)
- **Email верифікація** - додатковий метод (майбутнє)

### TOTP Configuration
- **Algorithm**: SHA1
- **Digits**: 6
- **Interval**: 30 секунд
- **Issuer**: "Upwork Web App"
- **Backup codes**: 10 одноразових кодів

---

## Архітектура

### Компоненти MFA
```
┌─────────────────────────────────────┐
│           MFA System               │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ TOTP        │ │   Backup    │   │
│  │ Generator   │ │   Codes     │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ QR Code     │ │   Secret    │   │
│  │ Generator   │ │  Manager    │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Verification│ │   Recovery  │   │
│  │ Engine      │ │   Manager   │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

### База даних
```sql
-- Таблиця MFA налаштувань користувача
CREATE TABLE user_mfa (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    totp_secret VARCHAR(32) NOT NULL,
    totp_enabled BOOLEAN DEFAULT FALSE,
    backup_codes_hash TEXT[], -- Хешовані backup коди
    backup_codes_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблиця MFA спроб
CREATE TABLE mfa_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    attempt_type VARCHAR(20) NOT NULL, -- 'totp', 'backup'
    success BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## TOTP Реалізація

### Основна реалізація
```python
import pyotp
import qrcode
import base64
import secrets
from io import BytesIO
from datetime import datetime, timedelta

class TOTPManager:
    def __init__(self, encryption_manager):
        self.encryption_manager = encryption_manager
        self.issuer = "Upwork Web App"
        self.algorithm = pyotp.TOTP.ALGORITHM_SHA1
        self.digits = 6
        self.interval = 30  # секунди
    
    def generate_secret(self) -> str:
        """Генерує TOTP secret"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, user_email: str) -> str:
        """Генерує QR код для додатку аутентифікації"""
        totp = pyotp.TOTP(secret)
        
# URI для QR коду
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer
        )
        
# Створюємо QR код
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
# Конвертуємо в base64
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_totp(self, secret: str, token: str, window: int = 1) -> bool:
        """Перевіряє TOTP токен"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)
    
    def get_current_totp(self, secret: str) -> str:
        """Отримує поточний TOTP токен (для тестування)"""
        totp = pyotp.TOTP(secret)
        return totp.now()
```

### Інтеграція з базою даних
```python
class MFADatabase:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def setup_mfa(self, user_id: int, totp_secret: str, backup_codes: List[str]):
        """Налаштовує MFA для користувача"""
# Хешуємо backup коди
        backup_codes_hash = [hashlib.sha256(code.encode()).hexdigest() for code in backup_codes]
        
        mfa_settings = UserMFA(
            user_id=user_id,
            totp_secret=totp_secret,
            totp_enabled=True,
            backup_codes_hash=backup_codes_hash,
            backup_codes_used=0
        )
        
        self.db.add(mfa_settings)
        await self.db.commit()
    
    async def get_mfa_settings(self, user_id: int) -> Optional[UserMFA]:
        """Отримує MFA налаштування користувача"""
        return await self.db.query(UserMFA).filter(
            UserMFA.user_id == user_id
        ).first()
    
    async def log_mfa_attempt(self, user_id: int, attempt_type: str, 
                            success: bool, ip_address: str, user_agent: str):
        """Логує спробу MFA"""
        attempt = MFAAttempt(
            user_id=user_id,
            attempt_type=attempt_type,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(attempt)
        await self.db.commit()
```

---

## Backup Коди

### Генерація backup кодів
```python
class BackupCodeManager:
    def __init__(self):
        self.code_length = 8
        self.code_count = 10
        self.code_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    def generate_backup_codes(self, count: int = None) -> List[str]:
        """Генерує backup коди"""
        if count is None:
            count = self.code_count
        
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(self.code_chars) for _ in range(self.code_length))
            codes.append(code)
        
        return codes
    
    def verify_backup_code(self, stored_codes_hash: List[str], 
                          provided_code: str) -> bool:
        """Перевіряє backup код"""
        provided_code_hash = hashlib.sha256(provided_code.encode()).hexdigest()
        return provided_code_hash in stored_codes_hash
    
    def mark_backup_code_used(self, user_id: int, used_code_hash: str):
        """Позначає backup код як використаний"""
# Отримуємо MFA налаштування
        mfa_settings = self.get_mfa_settings(user_id)
        
        if mfa_settings:
# Видаляємо використаний код
            if used_code_hash in mfa_settings.backup_codes_hash:
                mfa_settings.backup_codes_hash.remove(used_code_hash)
                mfa_settings.backup_codes_used += 1
                
# Якщо залишилося мало кодів, генеруємо нові
                if len(mfa_settings.backup_codes_hash) < 3:
                    new_codes = self.generate_backup_codes(5)
                    new_codes_hash = [hashlib.sha256(code.encode()).hexdigest() 
                                    for code in new_codes]
                    mfa_settings.backup_codes_hash.extend(new_codes_hash)
                
                self.db.commit()
```

---

## API Endpoints

### Налаштування MFA
```python
@app.post("/auth/mfa/setup")
async def setup_mfa(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Налаштовує MFA для користувача"""
    
# Перевіряємо, чи MFA вже налаштовано
    existing_mfa = await get_mfa_settings(current_user.id)
    if existing_mfa and existing_mfa.totp_enabled:
        raise HTTPException(status_code=400, detail="MFA already enabled")
    
# Генеруємо TOTP secret
    totp_secret = totp_manager.generate_secret()
    
# Генеруємо backup коди
    backup_codes = backup_code_manager.generate_backup_codes()
    
# Генеруємо QR код
    qr_code = totp_manager.generate_qr_code(totp_secret, current_user.email)
    
# Зберігаємо в базі даних
    await mfa_database.setup_mfa(current_user.id, totp_secret, backup_codes)
    
    return {
        "totp_secret": totp_secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes,
        "message": "MFA setup successful. Please scan QR code with your authenticator app."
    }
```

### Верифікація MFA
```python
@app.post("/auth/mfa/verify")
async def verify_mfa(
    request: MFAVerificationRequest,
    current_user: User = Depends(get_current_user)
):
    """Верифікує MFA токен"""
    
# Отримуємо MFA налаштування
    mfa_settings = await get_mfa_settings(current_user.id)
    if not mfa_settings or not mfa_settings.totp_enabled:
        raise HTTPException(status_code=400, detail="MFA not enabled")
    
# Логуємо спробу
    await log_mfa_attempt(
        current_user.id, 
        "totp", 
        False, 
        request.client.host, 
        request.headers.get("user-agent", "")
    )
    
# Перевіряємо TOTP токен
    if totp_manager.verify_totp(mfa_settings.totp_secret, request.token):
# Успішна верифікація
        await log_mfa_attempt(
            current_user.id, 
            "totp", 
            True, 
            request.client.host, 
            request.headers.get("user-agent", "")
        )
        
        return {
            "success": True,
            "message": "MFA verification successful"
        }
    
# Перевіряємо backup код
    if backup_code_manager.verify_backup_code(
        mfa_settings.backup_codes_hash, 
        request.token
    ):
# Позначаємо backup код як використаний
        await backup_code_manager.mark_backup_code_used(
            current_user.id, 
            hashlib.sha256(request.token.encode()).hexdigest()
        )
        
        await log_mfa_attempt(
            current_user.id, 
            "backup", 
            True, 
            request.client.host, 
            request.headers.get("user-agent", "")
        )
        
        return {
            "success": True,
            "message": "Backup code verification successful"
        }
    
# Неуспішна верифікація
    raise HTTPException(status_code=401, detail="Invalid MFA token")
```

### Вимкнення MFA
```python
@app.post("/auth/mfa/disable")
async def disable_mfa(
    request: MFAVerificationRequest,
    current_user: User = Depends(get_current_user)
):
    """Вимкає MFA для користувача"""
    
# Отримуємо MFA налаштування
    mfa_settings = await get_mfa_settings(current_user.id)
    if not mfa_settings or not mfa_settings.totp_enabled:
        raise HTTPException(status_code=400, detail="MFA not enabled")
    
# Перевіряємо MFA перед вимкненням
    if not totp_manager.verify_totp(mfa_settings.totp_secret, request.token):
        raise HTTPException(status_code=401, detail="Invalid MFA token")
    
# Вимкаємо MFA
    mfa_settings.totp_enabled = False
    mfa_settings.backup_codes_hash = []
    mfa_settings.backup_codes_used = 0
    
    await self.db.commit()
    
    return {
        "success": True,
        "message": "MFA disabled successfully"
    }
```

---

## Безпека

### Захист від брутфорс атак
```python
class MFARateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 хвилин
    
    def check_mfa_attempts(self, user_id: int) -> bool:
        """Перевіряє кількість спроб MFA"""
        key = f"mfa_attempts:{user_id}"
        attempts = self.redis.get(key)
        
        if attempts and int(attempts) >= self.max_attempts:
            return False
        
        return True
    
    def increment_mfa_attempts(self, user_id: int):
        """Збільшує лічильник спроб MFA"""
        key = f"mfa_attempts:{user_id}"
        self.redis.incr(key)
        self.redis.expire(key, self.lockout_duration)
    
    def reset_mfa_attempts(self, user_id: int):
        """Скидає лічильник спроб MFA"""
        key = f"mfa_attempts:{user_id}"
        self.redis.delete(key)
```

### Шифрування секретів
```python
class MFASecretManager:
    def __init__(self, encryption_manager):
        self.encryption_manager = encryption_manager
    
    def encrypt_totp_secret(self, secret: str) -> str:
        """Шифрує TOTP secret"""
        return self.encryption_manager.encrypt(secret)
    
    def decrypt_totp_secret(self, encrypted_secret: str) -> str:
        """Розшифровує TOTP secret"""
        return self.encryption_manager.decrypt(encrypted_secret)
    
    def secure_backup_codes(self, codes: List[str]) -> List[str]:
        """Безпечно зберігає backup коди"""
        return [hashlib.sha256(code.encode()).hexdigest() for code in codes]
```

---

## 🧪 Тестування

### Unit Tests
```python
class TestMFAManager:
    def test_totp_generation(self):
        """Тестує генерацію TOTP"""
# Arrange
        totp_manager = TOTPManager(encryption_manager)
        
# Act
        secret = totp_manager.generate_secret()
        current_token = totp_manager.get_current_totp(secret)
        
# Assert
        assert len(secret) == 32
        assert len(current_token) == 6
        assert current_token.isdigit()
    
    def test_totp_verification(self):
        """Тестує верифікацію TOTP"""
# Arrange
        totp_manager = TOTPManager(encryption_manager)
        secret = totp_manager.generate_secret()
        current_token = totp_manager.get_current_totp(secret)
        
# Act
        result = totp_manager.verify_totp(secret, current_token)
        
# Assert
        assert result == True
    
    def test_backup_codes_generation(self):
        """Тестує генерацію backup кодів"""
# Arrange
        backup_manager = BackupCodeManager()
        
# Act
        codes = backup_manager.generate_backup_codes(5)
        
# Assert
        assert len(codes) == 5
        for code in codes:
            assert len(code) == 8
            assert code.isalnum()
```

### Integration Tests
```python
class TestMFAIntegration:
    async def test_complete_mfa_flow(self):
        """Тестує повний MFA flow"""
# Arrange
        client = TestClient(app)
        user = create_test_user()
        login_response = client.post("/auth/login", json={
            "email": user.email,
            "password": "testpassword"
        })
        access_token = login_response.json()["access_token"]
        
# Act - Налаштування MFA
        setup_response = client.post(
            "/auth/mfa/setup",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
# Assert
        assert setup_response.status_code == 200
        data = setup_response.json()
        assert "totp_secret" in data
        assert "qr_code" in data
        assert "backup_codes" in data
        
# Act - Верифікація MFA
        totp_manager = TOTPManager(encryption_manager)
        current_token = totp_manager.get_current_totp(data["totp_secret"])
        
        verify_response = client.post("/auth/mfa/verify", json={
            "token": current_token
        })
        
# Assert
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["success"] == True
```

---

## Моніторинг

### MFA метрики
```python
class MFAMetrics:
    def __init__(self):
        self.metrics = {
            "mfa_setups": 0,
            "mfa_disables": 0,
            "totp_verifications": 0,
            "backup_code_uses": 0,
            "failed_attempts": 0,
            "lockouts": 0
        }
    
    def increment_metric(self, metric_name: str):
        """Збільшує метрику"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += 1
    
    def get_mfa_stats(self) -> dict:
        """Повертає статистику MFA"""
        return {
            "total_users_with_mfa": self.get_users_with_mfa_count(),
            "mfa_success_rate": self.calculate_success_rate(),
            "average_verification_time": self.calculate_avg_verification_time(),
            "backup_codes_usage": self.get_backup_codes_usage()
        }
```

### Логування MFA подій
```python
class MFALogger:
    def __init__(self):
        self.logger = logging.getLogger('mfa')
    
    def log_mfa_setup(self, user_id: int, ip_address: str):
        """Логує налаштування MFA"""
        self.logger.info(f"MFA setup - User: {user_id}, IP: {ip_address}")
    
    def log_mfa_verification(self, user_id: int, method: str, success: bool, ip_address: str):
        """Логує верифікацію MFA"""
        status = "success" if success else "failure"
        self.logger.info(f"MFA verification - User: {user_id}, Method: {method}, Status: {status}, IP: {ip_address}")
    
    def log_mfa_lockout(self, user_id: int, ip_address: str):
        """Логує блокування MFA"""
        self.logger.warning(f"MFA lockout - User: {user_id}, IP: {ip_address}")
```

---

## Контрольні списки

### Реалізація
- [ ] TOTP генератор та верифікатор
- [ ] QR код генератор
- [ ] Backup коди система
- [ ] База даних схема
- [ ] API endpoints
- [ ] Rate limiting
- [ ] Шифрування секретів

### Тестування
- [ ] Unit тести для TOTP
- [ ] Unit тести для backup кодів
- [ ] Integration тести
- [ ] Security тести
- [ ] Performance тести

### Безпека
- [ ] Захист від брутфорс атак
- [ ] Шифрування секретів
- [ ] Безпечне зберігання backup кодів
- [ ] Логування всіх подій
- [ ] Моніторинг аномалій

---

## Посилання

- [Архітектура безпеки](../architecture/security_architecture.md)
- [Модуль авторизації](../modules/auth/auth_module.md)
- [Система шифрування](encryption_system.md)

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 15:30 