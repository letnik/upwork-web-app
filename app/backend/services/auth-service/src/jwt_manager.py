"""
JWT менеджер для Auth Service
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import secrets
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import get_logger
from shared.database.connection import get_db
from .models import User, Session as UserSession

# Налаштування логування
logger = get_logger("jwt-manager")

# Створюємо роутер
router = APIRouter()

# Security
security = HTTPBearer()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Створення access токена
    
    Args:
        data: Дані для токена
        expires_delta: Час життя токена
        
    Returns:
        JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Створення refresh токена
    
    Args:
        data: Дані для токена
        
    Returns:
        JWT refresh токен
    """
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Верифікація JWT токена
    
    Args:
        token: JWT токен
        
    Returns:
        Дані токена
        
    Raises:
        HTTPException: Якщо токен невірний
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний токен"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен застарів"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний токен"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Отримання поточного користувача з токена
    
    Args:
        credentials: JWT токен
        db: Сесія БД
        
    Returns:
        Об'єкт користувача
        
    Raises:
        HTTPException: Якщо користувач не знайдений
    """
    try:
        payload = verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний токен"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Користувач не знайдений"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Користувач заблокований"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка отримання користувача: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Помилка автентифікації"
        )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Оновлення access токена
    
    Args:
        refresh_token: Refresh токен
        db: Сесія БД
    """
    try:
        # Верифікуємо refresh токен
        payload = verify_token(refresh_token)
        
        # Перевіряємо тип токена
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний тип токена"
            )
        
        user_id = payload.get("sub")
        
        # Перевіряємо чи користувач існує
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Користувач не знайдений або заблокований"
            )
        
        # Створюємо новий access токен
        new_access_token = create_access_token(data={"sub": str(user.id)})
        
        logger.info(f"Токен оновлено для користувача {user.id}")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка оновлення токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка оновлення токена"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Вихід з системи
    
    Args:
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        # Деактивуємо всі сесії користувача
        sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).all()
        
        for session in sessions:
            session.is_active = False
        
        db.commit()
        
        logger.info(f"Користувач {current_user.id} вийшов з системи")
        
        return {"message": "Успішний вихід з системи"}
        
    except Exception as e:
        logger.error(f"Помилка виходу: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка виходу з системи"
        )


@router.post("/logout/all")
async def logout_all_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Вихід з усіх пристроїв
    
    Args:
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        # Деактивуємо всі сесії користувача
        sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id
        ).all()
        
        for session in sessions:
            session.is_active = False
        
        db.commit()
        
        logger.info(f"Користувач {current_user.id} вийшов з усіх пристроїв")
        
        return {"message": "Успішний вихід з усіх пристроїв"}
        
    except Exception as e:
        logger.error(f"Помилка виходу з усіх пристроїв: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка виходу з усіх пристроїв"
        )


@router.get("/validate")
async def validate_token(
    current_user: User = Depends(get_current_user)
):
    """
    Валідація токена
    
    Args:
        current_user: Поточний користувач
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name
        }
    }


def create_session_token() -> str:
    """Створення унікального токена сесії"""
    return secrets.token_urlsafe(32)


def save_session(
    user_id: int,
    access_token: str,
    refresh_token: str,
    ip_address: str = None,
    user_agent: str = None,
    db: Session = None
) -> UserSession:
    """
    Збереження сесії користувача
    
    Args:
        user_id: ID користувача
        access_token: Access токен
        refresh_token: Refresh токен
        ip_address: IP адреса
        user_agent: User Agent
        db: Сесія БД
        
    Returns:
        Об'єкт сесії
    """
    session = UserSession(
        user_id=user_id,
        session_token=access_token,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    )
    
    if db:
        db.add(session)
        db.commit()
        db.refresh(session)
    
    return session 