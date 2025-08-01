"""
OAuth 2.0 Manager для Upwork API
"""
import os
import requests
from urllib.parse import urlencode
from typing import Dict, Optional, Tuple

from shared.config.logging import get_logger

logger = get_logger("oauth-manager")

class UpworkOAuthManager:
    """Менеджер OAuth 2.0 авторизації для Upwork API"""
    
    def __init__(self):
        self.client_id = os.getenv('UPWORK_CLIENT_ID')
        self.client_secret = os.getenv('UPWORK_CLIENT_SECRET')
        self.callback_url = os.getenv('UPWORK_CALLBACK_URL')
        self.auth_url = os.getenv('UPWORK_AUTH_URL', 'https://www.upwork.com/services/api/auth')
        self.token_url = os.getenv('UPWORK_TOKEN_URL', 'https://www.upwork.com/api/v2/oauth2/token')
        
        # Scopes для Upwork API
        self.scopes = [
            'jobs:read',
            'jobs:write',
            'freelancers:read',
            'clients:read',
            'messages:read',
            'messages:write'
        ]
        
        if not all([self.client_id, self.client_secret, self.callback_url]):
            logger.warning("Upwork OAuth credentials not fully configured")
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Генерація URL для авторизації користувача
        
        Args:
            state: Додатковий параметр для безпеки
            
        Returns:
            URL для авторизації
        """
        if not self.client_id:
            raise ValueError("UPWORK_CLIENT_ID not configured")
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.callback_url,
            'scope': ' '.join(self.scopes)
        }
        
        if state:
            params['state'] = state
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        logger.info(f"Generated authorization URL: {auth_url}")
        
        return auth_url
    
    def get_access_token(self, authorization_code: str) -> Dict:
        """
        Отримання access token за допомогою authorization code
        
        Args:
            authorization_code: Код авторизації від Upwork
            
        Returns:
            Словник з токенами та додатковою інформацією
        """
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Upwork OAuth credentials not configured")
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.callback_url
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully obtained access token")
            
            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'token_type': token_data.get('token_type', 'Bearer'),
                'expires_in': token_data.get('expires_in'),
                'scope': token_data.get('scope')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get access token: {e}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Оновлення access token за допомогою refresh token
        
        Args:
            refresh_token: Refresh token для оновлення
            
        Returns:
            Словник з новими токенами
        """
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Upwork OAuth credentials not configured")
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully refreshed access token")
            
            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token', refresh_token),
                'token_type': token_data.get('token_type', 'Bearer'),
                'expires_in': token_data.get('expires_in'),
                'scope': token_data.get('scope')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh access token: {e}")
            raise
    
    def revoke_token(self, token: str, token_type: str = 'access_token') -> bool:
        """
        Відкликання токена
        
        Args:
            token: Токен для відкликання
            token_type: Тип токена ('access_token' або 'refresh_token')
            
        Returns:
            True якщо токен успішно відкликано
        """
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Upwork OAuth credentials not configured")
        
        data = {
            'token': token,
            'token_type_hint': token_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(
                'https://www.upwork.com/api/v2/oauth2/revoke',
                data=data
            )
            response.raise_for_status()
            
            logger.info(f"Successfully revoked {token_type}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to revoke token: {e}")
            return False
    
    def validate_token(self, access_token: str) -> bool:
        """
        Валідація access token
        
        Args:
            access_token: Токен для валідації
            
        Returns:
            True якщо токен валідний
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Тестуємо токен, запитуючи профіль користувача
            response = requests.get(
                'https://www.upwork.com/api/v2/freelancers/me',
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info("Token validation successful")
                return True
            else:
                logger.warning(f"Token validation failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Token validation error: {e}")
            return False

# Глобальний екземпляр менеджера
oauth_manager = UpworkOAuthManager() 