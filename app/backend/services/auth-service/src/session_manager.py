"""
Модуль для управління сесіями користувачів
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import secrets
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import get_logger
from shared.database.connection import get_db
from .models import User, Session as UserSession
from .jwt_manager import get_current_user

# Налаштування логування
logger = get_logger("session_manager")

# Створюємо роутер
router = APIRouter()

# Security
security = HTTPBearer()


def generate_session_token() -> str:
    """Генерація токену сесії"""
    return secrets.token_urlsafe(32)


def generate_refresh_token() -> str:
    """Генерація refresh токену"""
    return secrets.token_urlsafe(32)


def create_user_session(
    user_id: int,
    ip_address: str = None,
    user_agent: str = None,
    db: Session = None
) -> UserSession:
    """
    Створення нової сесії користувача
    
    Args:
        user_id: ID користувача
        ip_address: IP адреса
        user_agent: User Agent
        db: Сесія БД
        
    Returns:
        Об'єкт сесії
    """
    session_token = generate_session_token()
    refresh_token = generate_refresh_token()
    expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_DURATION_HOURS)
    
    user_session = UserSession(
        user_id=user_id,
        session_token=session_token,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
        is_active=True
    )
    
    db.add(user_session)
    db.commit()
    db.refresh(user_session)
    
    logger.info(f"Створено нову сесію для користувача {user_id}")
    return user_session


def get_active_sessions(user_id: int, db: Session) -> List[UserSession]:
    """
    Отримання активних сесій користувача
    
    Args:
        user_id: ID користувача
        db: Сесія БД
        
    Returns:
        Список активних сесій
    """
    return db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).all()


def deactivate_session(session_id: int, user_id: int, db: Session) -> bool:
    """
    Деактивація сесії
    
    Args:
        session_id: ID сесії
        user_id: ID користувача
        db: Сесія БД
        
    Returns:
        True якщо сесія деактивована
    """
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == user_id
    ).first()
    
    if not session:
        return False
    
    session.is_active = False
    db.commit()
    
    logger.info(f"Деактивовано сесію {session_id} для користувача {user_id}")
    return True


def deactivate_all_sessions(user_id: int, db: Session) -> int:
    """
    Деактивація всіх сесій користувача
    
    Args:
        user_id: ID користувача
        db: Сесія БД
        
    Returns:
        Кількість деактивованих сесій
    """
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    ).all()
    
    for session in sessions:
        session.is_active = False
    
    db.commit()
    
    logger.info(f"Деактивовано {len(sessions)} сесій для користувача {user_id}")
    return len(sessions)


def cleanup_expired_sessions(db: Session) -> int:
    """
    Очищення застарілих сесій
    
    Args:
        db: Сесія БД
        
    Returns:
        Кількість видалених сесій
    """
    expired_sessions = db.query(UserSession).filter(
        UserSession.expires_at < datetime.utcnow()
    ).all()
    
    for session in expired_sessions:
        db.delete(session)
    
    db.commit()
    
    logger.info(f"Видалено {len(expired_sessions)} застарілих сесій")
    return len(expired_sessions)


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отримання активних сесій користувача
    
    Args:
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        sessions = get_active_sessions(current_user.id, db)
        
        session_data = []
        for session in sessions:
            session_data.append({
                "id": session.id,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "is_current": session.session_token == getattr(current_user, 'current_session_token', None)
            })
        
        return {
            "sessions": session_data,
            "total": len(session_data)
        }
        
    except Exception as e:
        logger.error(f"Помилка отримання сесій: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання сесій"
        )


@router.delete("/sessions/{session_id}")
async def deactivate_user_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Деактивація конкретної сесії
    
    Args:
        session_id: ID сесії
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        if deactivate_session(session_id, current_user.id, db):
            return {"message": "Сесію деактивовано"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сесію не знайдено"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка деактивації сесії: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка деактивації сесії"
        )


@router.delete("/sessions/all")
async def deactivate_all_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Деактивація всіх сесій користувача
    
    Args:
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        count = deactivate_all_sessions(current_user.id, db)
        return {
            "message": f"Деактивовано {count} сесій",
            "deactivated_count": count
        }
        
    except Exception as e:
        logger.error(f"Помилка деактивації всіх сесій: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка деактивації сесій"
        )


@router.post("/refresh")
async def refresh_session(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Оновлення сесії з refresh токеном
    
    Args:
        refresh_token: Refresh токен
        db: Сесія БД
    """
    try:
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний або застарілий refresh токен"
            )
        
        # Генеруємо нові токени
        new_session_token = generate_session_token()
        new_refresh_token = generate_refresh_token()
        new_expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_DURATION_HOURS)
        
        # Оновлюємо сесію
        session.session_token = new_session_token
        session.refresh_token = new_refresh_token
        session.expires_at = new_expires_at
        
        db.commit()
        
        logger.info(f"Оновлено сесію для користувача {session.user_id}")
        
        return {
            "session_token": new_session_token,
            "refresh_token": new_refresh_token,
            "expires_at": new_expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка оновлення сесії: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка оновлення сесії"
        )


@router.delete("/cleanup")
async def cleanup_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Очищення застарілих сесій (тільки для адміністраторів)
    
    Args:
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        # Перевіряємо, чи користувач є адміністратором
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостатньо прав"
            )
        
        count = cleanup_expired_sessions(db)
        
        return {
            "message": f"Видалено {count} застарілих сесій",
            "cleaned_count": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка очищення сесій: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка очищення сесій"
        ) 