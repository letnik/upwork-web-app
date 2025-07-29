"""
MFA модуль для двофакторної автентифікації
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import pyotp
import secrets
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import get_logger
from shared.database.connection import get_db
from .models import User, UserSecurity
from .jwt_manager import get_current_user

# Налаштування логування
logger = get_logger("mfa")

# Створюємо роутер
router = APIRouter()

# Security
security = HTTPBearer()


def generate_mfa_secret() -> str:
    """Генерація секретного ключа для MFA"""
    return pyotp.random_base32()


def generate_backup_codes(count: int = 10) -> List[str]:
    """
    Генерація резервних кодів
    
    Args:
        count: Кількість кодів
        
    Returns:
        Список резервних кодів
    """
    codes = []
    for _ in range(count):
        # Генеруємо 8-значний код
        code = ''.join(secrets.choice('0123456789') for _ in range(8))
        codes.append(code)
    return codes


def verify_mfa_code(secret: str, code: str) -> bool:
    """
    Перевірка MFA коду
    
    Args:
        secret: Секретний ключ
        code: Код для перевірки
        
    Returns:
        True якщо код правильний
    """
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
    except Exception as e:
        logger.error(f"Помилка перевірки MFA коду: {e}")
        return False


def verify_backup_code(user_security: UserSecurity, code: str) -> bool:
    """
    Перевірка резервного коду
    
    Args:
        user_security: Об'єкт безпеки користувача
        code: Резервний код
        
    Returns:
        True якщо код правильний
    """
    try:
        if not user_security.mfa_backup_codes:
            return False
        
        backup_codes = user_security.mfa_backup_codes
        if code in backup_codes:
            # Видаляємо використаний код
            backup_codes.remove(code)
            return True
        
        return False
    except Exception as e:
        logger.error(f"Помилка перевірки резервного коду: {e}")
        return False


@router.post("/setup")
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Налаштування MFA для користувача
    
    Args:
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        # Отримуємо або створюємо запис безпеки
        user_security = db.query(UserSecurity).filter(
            UserSecurity.user_id == current_user.id
        ).first()
        
        if not user_security:
            user_security = UserSecurity(
                user_id=current_user.id,
                mfa_enabled=False,
                mfa_secret=None,
                failed_login_attempts=0,
                created_at=datetime.utcnow()
            )
            db.add(user_security)
        
        # Генеруємо новий секрет
        mfa_secret = generate_mfa_secret()
        backup_codes = generate_backup_codes()
        
        # Оновлюємо запис безпеки
        user_security.mfa_secret = mfa_secret
        user_security.mfa_backup_codes = backup_codes
        user_security.mfa_enabled = False  # Поки не підтверджено
        
        db.commit()
        
        # Генеруємо QR код для Google Authenticator
        totp = pyotp.TOTP(mfa_secret)
        provisioning_uri = totp.provisioning_uri(
            name=current_user.email,
            issuer_name="Upwork AI Assistant"
        )
        
        logger.info(f"MFA налаштовано для користувача {current_user.id}")
        
        return {
            "mfa_secret": mfa_secret,
            "backup_codes": backup_codes,
            "qr_code_uri": provisioning_uri,
            "message": "MFA налаштовано. Підтвердіть код для активації."
        }
        
    except Exception as e:
        logger.error(f"Помилка налаштування MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка налаштування MFA"
        )


@router.post("/verify")
async def verify_mfa_setup(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Підтвердження налаштування MFA
    
    Args:
        code: MFA код для підтвердження
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        user_security = db.query(UserSecurity).filter(
            UserSecurity.user_id == current_user.id
        ).first()
        
        if not user_security or not user_security.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA не налаштовано"
            )
        
        # Перевіряємо код
        if not verify_mfa_code(user_security.mfa_secret, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невірний MFA код"
            )
        
        # Активуємо MFA
        user_security.mfa_enabled = True
        db.commit()
        
        logger.info(f"MFA активовано для користувача {current_user.id}")
        
        return {
            "message": "MFA успішно активовано",
            "mfa_enabled": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка підтвердження MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка підтвердження MFA"
        )


@router.post("/disable")
async def disable_mfa(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Вимкнення MFA
    
    Args:
        code: MFA код для підтвердження
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        user_security = db.query(UserSecurity).filter(
            UserSecurity.user_id == current_user.id
        ).first()
        
        if not user_security or not user_security.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA не активовано"
            )
        
        # Перевіряємо код
        if not verify_mfa_code(user_security.mfa_secret, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невірний MFA код"
            )
        
        # Деактивуємо MFA
        user_security.mfa_enabled = False
        user_security.mfa_secret = None
        user_security.mfa_backup_codes = None
        db.commit()
        
        logger.info(f"MFA деактивовано для користувача {current_user.id}")
        
        return {
            "message": "MFA успішно вимкнено",
            "mfa_enabled": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка вимкнення MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка вимкнення MFA"
        )


@router.post("/verify-login")
async def verify_mfa_login(
    user_id: int,
    code: str,
    db: Session = Depends(get_db)
):
    """
    Перевірка MFA коду при вході
    
    Args:
        user_id: ID користувача
        code: MFA код
        db: Сесія БД
    """
    try:
        user_security = db.query(UserSecurity).filter(
            UserSecurity.user_id == user_id
        ).first()
        
        if not user_security or not user_security.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA не активовано"
            )
        
        # Спочатку перевіряємо MFA код
        if verify_mfa_code(user_security.mfa_secret, code):
            logger.info(f"MFA код підтверджено для користувача {user_id}")
            return {"verified": True, "method": "mfa"}
        
        # Якщо MFA код не підійшов, перевіряємо резервний код
        if verify_backup_code(user_security, code):
            db.commit()  # Зберігаємо зміни (видалення використаного коду)
            logger.info(f"Резервний код підтверджено для користувача {user_id}")
            return {"verified": True, "method": "backup"}
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невірний MFA код"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка перевірки MFA при вході: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка перевірки MFA"
        )


@router.post("/regenerate-backup-codes")
async def regenerate_backup_codes(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Регенерація резервних кодів
    
    Args:
        code: Поточний MFA код для підтвердження
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        user_security = db.query(UserSecurity).filter(
            UserSecurity.user_id == current_user.id
        ).first()
        
        if not user_security or not user_security.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA не активовано"
            )
        
        # Перевіряємо поточний код
        if not verify_mfa_code(user_security.mfa_secret, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невірний MFA код"
            )
        
        # Генеруємо нові резервні коди
        new_backup_codes = generate_backup_codes()
        user_security.mfa_backup_codes = new_backup_codes
        db.commit()
        
        logger.info(f"Резервні коди регенеровано для користувача {current_user.id}")
        
        return {
            "backup_codes": new_backup_codes,
            "message": "Резервні коди регенеровано"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка регенерації резервних кодів: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка регенерації резервних кодів"
        )


@router.get("/status")
async def get_mfa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отримання статусу MFA
    
    Args:
        current_user: Поточний користувач
        db: Сесія БД
    """
    try:
        user_security = db.query(UserSecurity).filter(
            UserSecurity.user_id == current_user.id
        ).first()
        
        if not user_security:
            return {
                "mfa_enabled": False,
                "mfa_setup": False
            }
        
        return {
            "mfa_enabled": user_security.mfa_enabled,
            "mfa_setup": user_security.mfa_secret is not None,
            "backup_codes_count": len(user_security.mfa_backup_codes) if user_security.mfa_backup_codes else 0
        }
        
    except Exception as e:
        logger.error(f"Помилка отримання статусу MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання статусу MFA"
        ) 