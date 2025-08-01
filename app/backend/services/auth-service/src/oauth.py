"""
OAuth модуль для інтеграції з Upwork
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import requests
import sys
import os
import secrets
import hashlib
import time

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.config.settings import settings
from shared.config.logging import get_logger
from shared.database.connection import get_db
from shared.utils.encryption import encrypt_data, decrypt_data
from shared.utils.rate_limiter import rate_limiter
from .models import User, OAuthConnection
from .jwt_manager import get_current_user

logger = get_logger("oauth")
router = APIRouter()

# Безпечний кеш для state (в продакшені використовувати Redis)
class StateCache:
    def __init__(self):
        self._cache = {}
        self._max_age = 300  # 5 хвилин
    
    def set(self, user_id: int, state: str):
        self._cache[user_id] = {
            'state': state,
            'timestamp': time.time()
        }
    
    def get(self, user_id: int) -> str:
        if user_id not in self._cache:
            return None
        
        data = self._cache[user_id]
        if time.time() - data['timestamp'] > self._max_age:
            del self._cache[user_id]
            return None
        
        return data['state']
    
    def remove(self, user_id: int):
        self._cache.pop(user_id, None)

# Глобальний кеш для state
state_cache = StateCache()


@router.get("/upwork/authorize")
async def upwork_authorize(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Початок OAuth flow для Upwork з покращеною безпекою"""
    try:
        # Rate limiting
        client_ip = request.client.host
        if not rate_limiter.allow_request(f"oauth_authorize:{client_ip}", max_requests=10, window=3600):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Забагато запитів на авторизацію"
            )
        
        # Генерація безпечного state
        state = secrets.token_urlsafe(32)
        
        # Додаємо додаткову безпеку - хеш користувача
        user_hash = hashlib.sha256(f"{current_user.id}:{current_user.email}".encode()).hexdigest()[:16]
        state_with_hash = f"{state}.{user_hash}"
        
        # Параметри авторизації
        from urllib.parse import urlencode
        
        params = {
            'response_type': 'code',
            'client_id': settings.UPWORK_CLIENT_ID or 'test_client_id',
            'redirect_uri': settings.UPWORK_CALLBACK_URL or 'http://localhost:8000/auth/upwork/callback',
            'scope': ' '.join([
                'jobs:read',
                'jobs:write',
                'freelancers:read', 
                'clients:read',
                'messages:read',
                'messages:write',
                'workdiary:read',
                'workdiary:write'
            ]),
            'state': state_with_hash
        }
        
        # Зберігаємо state з часовою міткою
        state_cache.set(current_user.id, state_with_hash)
        
        auth_url = f"https://www.upwork.com/services/api/auth?{urlencode(params)}"
        
        logger.info(f"OAuth URL згенеровано для користувача {current_user.id} з IP {client_ip}")
        
        return {
            "authorization_url": auth_url,
            "state": state_with_hash,
            "expires_in": 300  # 5 хвилин
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка генерації OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка генерації URL авторизації"
        )


@router.get("/upwork/test")
async def upwork_test():
    """Тестовий endpoint для перевірки роботи OAuth роутера"""
    return {
        "message": "OAuth router is working",
        "status": "ok",
        "security_features": [
            "Rate limiting",
            "State validation",
            "User hash verification",
            "Token encryption",
            "Secure callback handling"
        ]
    }


@router.get("/upwork/callback")
async def upwork_callback(
    code: str,
    state: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Callback для OAuth Upwork з покращеною безпекою"""
    try:
        # Rate limiting для callback
        client_ip = request.client.host
        if not rate_limiter.allow_request(f"oauth_callback:{client_ip}", max_requests=5, window=3600):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Забагато спроб callback"
            )
        
        # Валідація state з додатковою перевіркою
        cached_state = state_cache.get(current_user.id)
        if not cached_state or cached_state != state:
            logger.warning(f"Invalid state для користувача {current_user.id} з IP {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
        # Перевіряємо хеш користувача в state
        try:
            state_part, user_hash = state.split('.')
            expected_hash = hashlib.sha256(f"{current_user.id}:{current_user.email}".encode()).hexdigest()[:16]
            if user_hash != expected_hash:
                logger.warning(f"Invalid user hash для користувача {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state parameter"
                )
        except ValueError:
            logger.warning(f"Invalid state format для користувача {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state format"
            )
        
        # Очищаємо state
        state_cache.remove(current_user.id)
        
        # Валідація authorization code
        if not code or len(code) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization code"
            )
        
        # Обмінюємо код на токени
        token_url = "https://api.upwork.com/api/v3/oauth2/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.UPWORK_CLIENT_ID or 'test_client_id',
            "client_secret": settings.UPWORK_CLIENT_SECRET or 'test_client_secret',
            "redirect_uri": settings.UPWORK_CALLBACK_URL or 'http://localhost:8000/auth/upwork/callback'
        }
        
        # В тестовому режимі симулюємо успішну відповідь
        if not settings.UPWORK_CLIENT_SECRET:
            token_data = {
                "access_token": "test_access_token_" + secrets.token_urlsafe(16),
                "refresh_token": "test_refresh_token_" + secrets.token_urlsafe(16),
                "expires_in": 3600,
                "scope": "jobs:read jobs:write freelancers:read clients:read messages:read messages:write",
                "user_id": f"test_user_{current_user.id}"
            }
        else:
            response = requests.post(token_url, data=data, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Помилка отримання токенів: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Помилка отримання токенів від Upwork"
                )
            
            token_data = response.json()
        
        # Перевіряємо чи вже є активне з'єднання
        existing_connection = db.query(OAuthConnection).filter(
            OAuthConnection.user_id == current_user.id,
            OAuthConnection.provider == "upwork",
            OAuthConnection.is_active == True
        ).first()
        
        if existing_connection:
            # Оновлюємо існуюче з'єднання
            existing_connection.access_token = encrypt_data(token_data["access_token"])
            existing_connection.refresh_token = encrypt_data(token_data.get("refresh_token", ""))
            existing_connection.expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
            existing_connection.scopes = token_data.get("scope", "").split()
            existing_connection.updated_at = datetime.utcnow()
        else:
            # Створюємо нове з'єднання
            oauth_connection = OAuthConnection(
                user_id=current_user.id,
                provider="upwork",
                provider_user_id=token_data.get("user_id", ""),
                access_token=encrypt_data(token_data["access_token"]),
                refresh_token=encrypt_data(token_data.get("refresh_token", "")),
                expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
                scopes=token_data.get("scope", "").split(),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(oauth_connection)
        
        db.commit()
        
        logger.info(f"Upwork OAuth підключено для користувача {current_user.id} з IP {client_ip}")
        
        return {
            "message": "Upwork успішно підключено", 
            "status": "success",
            "provider": "upwork",
            "expires_at": (datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))).isoformat()
        }
        
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
    """Отримання активних OAuth з'єднань користувача"""
    try:
        connections = db.query(OAuthConnection).filter(
            OAuthConnection.user_id == current_user.id,
            OAuthConnection.is_active == True
        ).all()
        
        return [{
            "provider": conn.provider,
            "provider_user_id": conn.provider_user_id,
            "scopes": conn.scopes,
            "is_active": conn.is_active,
            "created_at": conn.created_at.isoformat() if conn.created_at else None,
            "updated_at": conn.updated_at.isoformat() if conn.updated_at else None,
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
    """Відключення OAuth з'єднання з додатковою безпекою"""
    try:
        # Валідація provider
        if provider not in ["upwork", "github", "google"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Непідтримуваний провайдер"
            )
        
        connection = db.query(OAuthConnection).filter(
            OAuthConnection.user_id == current_user.id,
            OAuthConnection.provider == provider,
            OAuthConnection.is_active == True
        ).first()
        
        if connection:
            connection.is_active = False
            connection.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"OAuth {provider} відключено для користувача {current_user.id}")
            
        return {"message": f"{provider} відключено", "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка відключення OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка відключення"
        )


@router.post("/upwork/refresh")
async def refresh_upwork_token(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Оновлення Upwork access token з покращеною безпекою"""
    try:
        # Rate limiting для refresh
        client_ip = request.client.host
        if not rate_limiter.allow_request(f"oauth_refresh:{client_ip}", max_requests=20, window=3600):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Забагато запитів на оновлення токена"
            )
        
        # Знаходимо активне з'єднання
        connection = db.query(OAuthConnection).filter(
            OAuthConnection.user_id == current_user.id,
            OAuthConnection.provider == "upwork",
            OAuthConnection.is_active == True
        ).first()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upwork з'єднання не знайдено"
            )
        
        # Перевіряємо чи потрібно оновлювати токен
        if connection.expires_at and connection.expires_at > datetime.utcnow():
            return {
                "message": "Токен ще дійсний", 
                "expires_at": connection.expires_at.isoformat(),
                "status": "valid"
            }
        
        # Оновлюємо токен
        refresh_token = decrypt_data(connection.refresh_token)
        
        if not settings.UPWORK_CLIENT_SECRET:
            # Тестовий режим
            new_token_data = {
                "access_token": "test_access_token_" + secrets.token_urlsafe(16),
                "refresh_token": "test_refresh_token_" + secrets.token_urlsafe(16),
                "expires_in": 3600
            }
        else:
            # Реальний режим
            token_url = "https://api.upwork.com/api/v3/oauth2/token"
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": settings.UPWORK_CLIENT_ID,
                "client_secret": settings.UPWORK_CLIENT_SECRET
            }
            
            response = requests.post(token_url, data=data, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Помилка оновлення токена: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Помилка оновлення токена"
                )
            
            new_token_data = response.json()
        
        # Оновлюємо з'єднання
        connection.access_token = encrypt_data(new_token_data["access_token"])
        if new_token_data.get("refresh_token"):
            connection.refresh_token = encrypt_data(new_token_data["refresh_token"])
        connection.expires_at = datetime.utcnow() + timedelta(seconds=new_token_data.get("expires_in", 3600))
        connection.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Upwork токен оновлено для користувача {current_user.id} з IP {client_ip}")
        
        return {
            "message": "Токен успішно оновлено",
            "expires_at": connection.expires_at.isoformat(),
            "status": "refreshed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка оновлення токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка оновлення токена"
        ) 