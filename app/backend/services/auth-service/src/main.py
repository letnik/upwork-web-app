"""
Auth Service - Мікросервіс авторизації та аутентифікації
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.config.settings import settings
from shared.config.logging import setup_logging, get_logger
from shared.database.connection import get_db, db_manager
from shared.utils.oauth_manager import oauth_manager
from .models import User, UserSecurity, Role
from .oauth import router as oauth_router

from .mfa import router as mfa_router
from .jwt_manager import router as jwt_router
from .password_reset import router as password_reset_router
from .session_manager import router as session_manager_router

# Налаштування логування
setup_logging(service_name="auth-service")
logger = get_logger("auth-service")

# Створюємо FastAPI додаток
app = FastAPI(
    title="Auth Service",
    description="Мікросервіс авторизації та аутентифікації",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic моделі
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str = None
    last_name: str = None

# Security
security = HTTPBearer()

# Підключаємо роутери
app.include_router(oauth_router, prefix="/auth/oauth", tags=["OAuth"])

app.include_router(mfa_router, prefix="/auth/mfa", tags=["MFA"])
app.include_router(jwt_router, prefix="/auth/jwt", tags=["JWT"])
app.include_router(password_reset_router, prefix="/auth/password", tags=["Password Reset"])
app.include_router(session_manager_router, prefix="/auth/sessions", tags=["Session Management"])


@app.on_event("startup")
async def startup_event():
    """Подія запуску сервісу"""
    logger.info("🚀 Запуск Auth Service...")
    
    # Тестуємо підключення до БД
    if not db_manager.test_connection():
        logger.warning("⚠️ Попередження: Проблеми з підключенням до БД")
    else:
        logger.info("✅ Підключення до БД успішне")
        # Створюємо таблиці якщо їх немає
        try:
            db_manager.create_tables()
            logger.info("✅ Таблиці БД створені/перевірені")
        except Exception as e:
            logger.error(f"❌ Помилка створення таблиць: {e}")


@app.get("/")
async def root():
    """Головна сторінка сервісу"""
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Перевірка здоров'я сервісу"""
    db_status = "healthy" if db_manager.test_connection() else "unhealthy"
    redis_status = "healthy" if db_manager.test_redis_connection() else "unhealthy"
    
    return {
        "status": "healthy",
        "service": "auth-service",
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/test")
async def test_endpoint():
    """Тестовий endpoint без бази даних"""
    return {
        "message": "Auth service is working!",
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/auth/login-test", tags=["Authentication"])
async def login_user_test(credentials: LoginRequest):
    """Тестовий endpoint для входу без БД"""
    return {
        "access_token": "test_token_123",
        "refresh_token": "test_refresh_123",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": credentials.email,
            "first_name": "Test",
            "last_name": "User",
            "mfa_enabled": False
        }
    }


@app.post("/auth/register", tags=["Authentication"])
async def register_user(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Реєстрація нового користувача"""
    try:
        # Перевіряємо чи користувач вже існує
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Користувач з такою email адресою вже існує"
            )
        
        # Хешуємо пароль
        from shared.utils.encryption import hash_password
        hashed_password = hash_password(user_data.password)
        
        # Створюємо користувача
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=True,
            is_verified=False,
            role_id=1  # Default role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Створюємо запис безпеки для користувача
        from .models import UserSecurity
        user_security = UserSecurity(
            user_id=new_user.id,
            mfa_enabled=False,
            failed_login_attempts=0
        )
        db.add(user_security)
        db.commit()
        
        logger.info(f"✅ Користувач зареєстрований: {user_data.email}")
        
        return {
            "message": "Користувач успішно зареєстрований",
            "user_id": new_user.id,
            "email": new_user.email,
            "status": "pending_verification"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Помилка реєстрації користувача: {e}")
        # Правильна обробка сесії БД
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка реєстрації користувача"
        )


@app.post("/auth/login", tags=["Authentication"])
async def login_user(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Авторизація користувача"""
    try:
        # Знаходимо користувача
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильний email або пароль"
            )
        
        # Перевіряємо чи користувач активний
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Обліковий запис деактивовано"
            )
        
        # Перевіряємо пароль
        from shared.utils.encryption import verify_password
        if not verify_password(credentials.password, user.password_hash):
            # Збільшуємо лічильник невдалих спроб
            user_security = db.query(UserSecurity).filter(UserSecurity.user_id == user.id).first()
            if user_security:
                user_security.failed_login_attempts += 1
                db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильний email або пароль"
            )
        
        # Скидаємо лічильник невдалих спроб
        user_security = db.query(UserSecurity).filter(UserSecurity.user_id == user.id).first()
        if user_security:
            user_security.failed_login_attempts = 0
            user_security.last_login = datetime.utcnow()
            db.commit()
        
        # Генеруємо JWT токени
        from .jwt_manager import create_access_token, create_refresh_token
        
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
        
        logger.info(f"✅ Користувач авторизований: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_verified": user.is_verified,
                "mfa_enabled": user_security.mfa_enabled if user_security else False
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Помилка авторизації: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка авторизації"
        )


@app.get("/auth/profile", tags=["Authentication"])
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Отримання профілю користувача
    
    Args:
        credentials: JWT токен
        db: Сесія БД
    """
    try:
        from .jwt_manager import verify_token
        
        # Верифікуємо токен
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний токен"
            )
        
        # Знаходимо користувача
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Користувач не знайдений"
            )
        
        # Отримуємо інформацію про безпеку
        user_security = db.query(UserSecurity).filter(
            UserSecurity.user_id == user.id
        ).first()
        
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "mfa_enabled": user_security.mfa_enabled if user_security else False,
            "last_login": user_security.last_login.isoformat() if user_security and user_security.last_login else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Помилка отримання профілю: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання профілю"
        )


# ============================================================================
# OAuth 2.0 Endpoints для Upwork (видалено - використовуємо існуючий роутер)
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 