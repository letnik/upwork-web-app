"""
Auth Middleware - Middleware для авторизації та аутентифікації
"""

from typing import Optional, List
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config.settings import settings
from shared.config.logging import get_logger
from shared.database.connection import get_db

logger = get_logger("auth-middleware")

# Security
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Клас для авторизації та аутентифікації"""
    
    def __init__(self):
        """Ініціалізація middleware"""
        self.public_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/login",
            "/auth/register",
            "/auth/oauth/upwork/authorize",
            "/auth/oauth/upwork/callback"
        ]
        
        self.admin_paths = [
            "/admin/",
            "/api/admin/"
        ]
    
    def _is_public_path(self, path: str) -> bool:
        """
        Перевірка чи шлях публічний
        
        Args:
            path: Шлях запиту
            
        Returns:
            True якщо шлях публічний
        """
        # Спеціальна обробка для auth шляхів
        if path.startswith("/auth/"):
            return True
        
        # Спеціальна обробка для docs шляхів
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
            return True
        
        # Спеціальна обробка для health шляху
        if path == "/health":
            return True
        
        # Спеціальна обробка для кореневого шляху (тільки точний збіг)
        if path == "/":
            return True
        
        # Перевіряємо точний збіг з публічними шляхами
        if path in self.public_paths:
            return True
        
        return False
    
    def _is_admin_path(self, path: str) -> bool:
        """
        Перевірка чи шлях адміністративний
        
        Args:
            path: Шлях запиту
            
        Returns:
            True якщо шлях адміністративний
        """
        for admin_path in self.admin_paths:
            if path.startswith(admin_path):
                return True
        return False
    
    def _verify_token(self, token: str) -> dict:
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
        except jwt.DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний токен"
            )
    
    async def _get_current_user(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
    ):
        """
        Отримання поточного користувача
        
        Args:
            credentials: JWT токен
            db: Сесія БД
            
        Returns:
            Об'єкт користувача
            
        Raises:
            HTTPException: Якщо користувач не знайдений
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не надано"
            )
        
        try:
            payload = self._verify_token(credentials.credentials)
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невірний токен"
                )
            
            # Імпортуємо модель користувача
            from app.backend.services.auth_service.src.models import User
            
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
    
    async def _check_permissions(
        self, 
        user, 
        required_roles: Optional[List[str]] = None,
        required_permissions: Optional[List[str]] = None
    ) -> bool:
        """
        Перевірка прав доступу
        
        Args:
            user: Об'єкт користувача
            required_roles: Необхідні ролі
            required_permissions: Необхідні дозволи
            
        Returns:
            True якщо користувач має права
            
        Raises:
            HTTPException: Якщо користувач не має прав
        """
        # Перевіряємо ролі
        if required_roles:
            user_roles = [role.name for role in user.roles] if hasattr(user, 'roles') else []
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостатньо прав доступу"
                )
        
        # Перевіряємо дозволи
        if required_permissions:
            user_permissions = [perm.name for perm in user.permissions] if hasattr(user, 'permissions') else []
            if not any(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостатньо прав доступу"
                )
        
        return True
    
    async def authenticate_request(self, request: Request) -> None:
        """
        Аутентифікація запиту
        
        Args:
            request: FastAPI запит
            
        Raises:
            HTTPException: Якщо аутентифікація невдала
        """
        # Перевіряємо чи шлях публічний
        if self._is_public_path(request.url.path):
            return
        
        # Отримуємо токен з заголовків
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не надано"
            )
        
        # Перевіряємо формат токена
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний формат токена"
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Верифікуємо токен
            payload = self._verify_token(token)
            
            # Зберігаємо дані користувача в request.state
            request.state.user_id = payload.get("sub")
            request.state.user_payload = payload
            
            # Перевіряємо права для адміністративних шляхів
            if self._is_admin_path(request.url.path):
                # Тут можна додати перевірку адміністративних прав
                pass
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Помилка аутентифікації: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Помилка аутентифікації"
            )


# Глобальний екземпляр middleware
auth_middleware = AuthMiddleware()


async def auth_middleware_handler(request: Request, call_next):
    """
    Middleware handler для авторизації
    
    Args:
        request: FastAPI запит
        call_next: Наступна функція в ланцюжку
        
    Returns:
        FastAPI відповідь
    """
    try:
        # Аутентифікуємо запит
        await auth_middleware.authenticate_request(request)
        
        # Виконуємо запит
        response = await call_next(request)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка авторизації: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка авторизації"
        )


# Dependency для отримання поточного користувача
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency для отримання поточного користувача"""
    return await auth_middleware._get_current_user(credentials, db)


# Dependency для перевірки адміністративних прав
async def require_admin(user = Depends(get_current_user)):
    """Dependency для перевірки адміністративних прав"""
    # Тут можна додати логіку перевірки адміністративних прав
    return user


def get_auth_middleware() -> AuthMiddleware:
    """Отримання екземпляра auth middleware"""
    return auth_middleware 