"""
Модуль для скидання паролю
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import get_logger
from shared.database.connection import get_db
from .models import User, PasswordResetToken
from .jwt_manager import get_current_user

# Налаштування логування
logger = get_logger("password_reset")

# Створюємо роутер
router = APIRouter()

# Security
security = HTTPBearer()


def generate_reset_token() -> str:
    """Генерація токену для скидання паролю"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Хешування токену для безпечного зберігання"""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_reset_token(token: str, hashed_token: str) -> bool:
    """Перевірка токену скидання паролю"""
    return hash_token(token) == hashed_token


def send_reset_email(email: str, reset_token: str, user_name: str) -> bool:
    """
    Відправка email з токеном скидання паролю
    
    Args:
        email: Email користувача
        reset_token: Токен для скидання
        user_name: Ім'я користувача
        
    Returns:
        True якщо email відправлено успішно
    """
    try:
        # Тут буде інтеграція з email сервісом
        # Поки що використовуємо мок
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        # Логуємо для тестування
        logger.info(f"Password reset email sent to {email}")
        logger.info(f"Reset URL: {reset_url}")
        
        # В реальному проекті тут буде відправка email
        # send_email(
        #     to_email=email,
        #     subject="Скидання паролю - Upwork AI Assistant",
        #     template="password_reset.html",
        #     context={
        #         "user_name": user_name,
        #         "reset_url": reset_url,
        #         "expires_in": "1 година"
        #     }
        # )
        
        return True
        
    except Exception as e:
        logger.error(f"Помилка відправки email: {e}")
        return False


@router.post("/forgot-password")
async def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Запит на скидання паролю
    
    Args:
        email: Email користувача
        db: Сесія БД
    """
    try:
        # Знаходимо користувача
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Не показуємо, що користувач не існує
            logger.info(f"Password reset requested for non-existent email: {email}")
            return {
                "message": "Якщо email існує в системі, ви отримаєте інструкції для скидання паролю"
            }
        
        # Генеруємо токен
        reset_token = generate_reset_token()
        hashed_token = hash_token(reset_token)
        
        # Встановлюємо час закінчення (1 година)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Зберігаємо токен в БД
        reset_token_record = PasswordResetToken(
            user_id=user.id,
            hashed_token=hashed_token,
            expires_at=expires_at,
            used=False
        )
        db.add(reset_token_record)
        db.commit()
        
        # Відправляємо email
        user_name = user.first_name or user.email.split('@')[0]
        if send_reset_email(user.email, reset_token, user_name):
            logger.info(f"Password reset email sent to {user.email}")
            return {
                "message": "Якщо email існує в системі, ви отримаєте інструкції для скидання паролю"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Помилка відправки email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка запиту скидання паролю: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка обробки запиту"
        )


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Скидання паролю з токеном
    
    Args:
        token: Токен скидання паролю
        new_password: Новий пароль
        db: Сесія БД
    """
    try:
        # Знаходимо токен
        hashed_token = hash_token(token)
        reset_token_record = db.query(PasswordResetToken).filter(
            PasswordResetToken.hashed_token == hashed_token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невірний або застарілий токен"
            )
        
        # Знаходимо користувача
        user = db.query(User).filter(User.id == reset_token_record.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Користувач не знайдений"
            )
        
        # Валідуємо новий пароль
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль повинен містити мінімум 8 символів"
            )
        
        # Оновлюємо пароль
        from .models import hash_password
        user.password_hash = hash_password(new_password)
        
        # Позначаємо токен як використаний
        reset_token_record.used = True
        
        db.commit()
        
        logger.info(f"Password reset successful for user {user.id}")
        
        return {
            "message": "Пароль успішно змінено"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка скидання паролю: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка скидання паролю"
        )


@router.post("/verify-reset-token")
async def verify_reset_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Перевірка валідності токену скидання паролю
    
    Args:
        token: Токен для перевірки
        db: Сесія БД
    """
    try:
        hashed_token = hash_token(token)
        reset_token_record = db.query(PasswordResetToken).filter(
            PasswordResetToken.hashed_token == hashed_token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_token_record:
            return {"valid": False, "message": "Невірний або застарілий токен"}
        
        return {"valid": True, "message": "Токен валідний"}
        
    except Exception as e:
        logger.error(f"Помилка перевірки токену: {e}")
        return {"valid": False, "message": "Помилка перевірки токену"}


@router.delete("/cleanup-expired-tokens")
async def cleanup_expired_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Очищення застарілих токенів скидання паролю
    (Тільки для адміністраторів)
    """
    try:
        # Перевіряємо, чи користувач є адміністратором
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостатньо прав"
            )
        
        # Видаляємо застарілі токени
        expired_tokens = db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < datetime.utcnow()
        ).all()
        
        for token in expired_tokens:
            db.delete(token)
        
        db.commit()
        
        logger.info(f"Cleaned up {len(expired_tokens)} expired reset tokens")
        
        return {
            "message": f"Видалено {len(expired_tokens)} застарілих токенів"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка очищення токенів: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка очищення токенів"
        ) 