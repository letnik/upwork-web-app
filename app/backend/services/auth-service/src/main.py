"""
Auth Service - Мікросервіс авторизації та аутентифікації
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import setup_logging, get_logger
from shared.database.connection import get_db, db_manager
from .models import User, UserSecurity, Role
from .oauth import router as oauth_router
from .mfa import router as mfa_router
from .jwt_manager import router as jwt_router

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

# Security
security = HTTPBearer()

# Підключаємо роутери
app.include_router(oauth_router, prefix="/auth/oauth", tags=["OAuth"])
app.include_router(mfa_router, prefix="/auth/mfa", tags=["MFA"])
app.include_router(jwt_router, prefix="/auth/jwt", tags=["JWT"])


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


@app.post("/auth/register", tags=["Authentication"])
async def register_user(
    email: str,
    password: str,
    first_name: str = None,
    last_name: str = None,
    db: Session = Depends(get_db)
):
    """
    Реєстрація нового користувача
    
    Args:
        email: Email користувача
        password: Пароль
        first_name: Ім'я
        last_name: Прізвище
        db: Сесія БД
    """
    try:
        # Перевіряємо чи користувач вже існує
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Користувач з таким email вже існує"
            )
        
        # Створюємо нового користувача
        from shared.utils.encryption import hash_password
        
        hashed_password = hash_password(password)
        
        user = User(
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Створюємо запис безпеки
        user_security = UserSecurity(
            user_id=user.id,
            mfa_enabled=False,
            mfa_secret=None,
            failed_login_attempts=0,
            last_login=None,
            created_at=datetime.utcnow()
        )
        
        db.add(user_security)
        db.commit()
        
        logger.info(f"✅ Користувач зареєстрований: {email}")
        
        return {
            "message": "Користувач успішно зареєстрований",
            "user_id": user.id,
            "email": user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Помилка реєстрації: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка реєстрації користувача"
        )


@app.post("/auth/login", tags=["Authentication"])
async def login_user(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Вхід користувача в систему
    
    Args:
        email: Email користувача
        password: Пароль
        db: Сесія БД
    """
    try:
        # Знаходимо користувача
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний email або пароль"
            )
        
        # Перевіряємо пароль
        from shared.utils.encryption import verify_password
        
        if not verify_password(password, user.password_hash):
            # Оновлюємо лічильник невдалих спроб
            user_security = db.query(UserSecurity).filter(
                UserSecurity.user_id == user.id
            ).first()
            
            if user_security:
                user_security.failed_login_attempts += 1
                db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний email або пароль"
            )
        
        # Перевіряємо чи користувач активний
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Користувач заблокований"
            )
        
        # Оновлюємо інформацію про вхід
        user_security = db.query(UserSecurity).filter(
            UserSecurity.user_id == user.id
        ).first()
        
        if user_security:
            user_security.failed_login_attempts = 0
            user_security.last_login = datetime.utcnow()
            db.commit()
        
        # Генеруємо JWT токени
        from .jwt_manager import create_access_token, create_refresh_token
        
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        logger.info(f"✅ Користувач увійшов: {email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "mfa_enabled": user_security.mfa_enabled if user_security else False
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Помилка входу: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка входу в систему"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 