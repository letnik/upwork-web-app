"""
Auth Router для API Gateway
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database.connection import get_db
from shared.database.mvp_models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user(token: str = Depends(None)) -> Optional[User]:
    """Тимчасова функція для отримання поточного користувача"""
    # TODO: Реалізувати повну автентифікацію
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необхідна автентифікація"
        )
    
    # Тимчасово повертаємо тестового користувача
    return User(id=1, email="test@example.com")


@router.get("/test")
async def test_auth():
    """Тестовий endpoint для автентифікації"""
    return {"message": "Auth router is working"} 