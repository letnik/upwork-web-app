"""
OAuth модуль для інтеграції з Upwork
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import requests
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import get_logger
from shared.database.connection import get_db
from shared.utils.encryption import encrypt_data, decrypt_data
from .models import User, OAuthConnection
from .jwt_manager import get_current_user

logger = get_logger("oauth")
router = APIRouter()


@router.get("/upwork/authorize")
async def upwork_authorize():
    """Початок OAuth flow для Upwork"""
    try:
        if not settings.UPWORK_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Upwork Client ID не налаштовано"
            )
        
        # Формуємо URL для авторизації
        auth_url = f"https://www.upwork.com/services/api/auth"
        params = {
            "client_id": settings.UPWORK_CLIENT_ID,
            "redirect_uri": settings.UPWORK_CALLBACK_URL,
            "response_type": "code",
            "scope": "r_workdiary r_workdairy r_workdairy_read r_workdairy_write"
        }
        
        return {
            "auth_url": auth_url,
            "params": params
        }
        
    except Exception as e:
        logger.error(f"Помилка авторизації Upwork: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка авторизації"
        )


@router.get("/upwork/callback")
async def upwork_callback(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Callback для OAuth Upwork"""
    try:
        if not settings.UPWORK_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Upwork Client Secret не налаштовано"
            )
        
        # Обмінюємо код на токени
        token_url = "https://api.upwork.com/api/v3/oauth2/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.UPWORK_CLIENT_ID,
            "client_secret": settings.UPWORK_CLIENT_SECRET,
            "redirect_uri": settings.UPWORK_CALLBACK_URL
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Помилка отримання токенів"
            )
        
        token_data = response.json()
        
        # Зберігаємо з'єднання
        oauth_connection = OAuthConnection(
            user_id=current_user.id,
            provider="upwork",
            provider_user_id=token_data.get("user_id", ""),
            access_token=encrypt_data(token_data["access_token"]),
            refresh_token=encrypt_data(token_data.get("refresh_token", "")),
            expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
            scopes=token_data.get("scope", "").split(),
            is_active=True
        )
        
        db.add(oauth_connection)
        db.commit()
        
        logger.info(f"Upwork OAuth підключено для користувача {current_user.id}")
        
        return {"message": "Upwork успішно підключено"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка підключення Upwork"
        )


@router.get("/connections")
async def get_oauth_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отримання OAuth з'єднань користувача"""
    try:
        connections = db.query(OAuthConnection).filter(
            OAuthConnection.user_id == current_user.id,
            OAuthConnection.is_active == True
        ).all()
        
        return [{
            "provider": conn.provider,
            "is_active": conn.is_active,
            "expires_at": conn.expires_at.isoformat() if conn.expires_at else None
        } for conn in connections]
        
    except Exception as e:
        logger.error(f"Помилка отримання OAuth з'єднань: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання з'єднань"
        )


@router.delete("/connections/{provider}")
async def disconnect_oauth(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Відключення OAuth з'єднання"""
    try:
        connection = db.query(OAuthConnection).filter(
            OAuthConnection.user_id == current_user.id,
            OAuthConnection.provider == provider,
            OAuthConnection.is_active == True
        ).first()
        
        if connection:
            connection.is_active = False
            db.commit()
            
            logger.info(f"OAuth {provider} відключено для користувача {current_user.id}")
            
        return {"message": f"{provider} відключено"}
        
    except Exception as e:
        logger.error(f"Помилка відключення OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка відключення"
        ) 