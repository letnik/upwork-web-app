"""
Конфігурація для API Upwork
"""

import os
import json
from typing import Dict, Optional
from pathlib import Path


class APIConfig:
    """Конфігурація API Upwork"""
    
    def __init__(self, config_file: str = "api_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Завантаження конфігурації"""
        # Спочатку перевіряємо змінні середовища
        env_config = self._load_from_env()
        if env_config:
            return env_config
        
        # Потім перевіряємо файл конфігурації
        file_config = self._load_from_file()
        if file_config:
            return file_config
        
        # Повертаємо дефолтну конфігурацію
        return self._get_default_config()
    
    def _load_from_env(self) -> Optional[Dict]:
        """Завантаження з змінних середовища"""
        api_key = os.getenv('UPWORK_API_KEY')
        api_secret = os.getenv('UPWORK_API_SECRET')
        access_token = os.getenv('UPWORK_ACCESS_TOKEN')
        access_token_secret = os.getenv('UPWORK_ACCESS_TOKEN_SECRET')
        
        if all([api_key, api_secret, access_token, access_token_secret]):
            return {
                "api_credentials": {
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "access_token": access_token,
                    "access_token_secret": access_token_secret
                },
                "search_settings": {
                    "max_results_per_query": int(os.getenv('UPWORK_MAX_RESULTS', '50')),
                    "delay_between_requests": float(os.getenv('UPWORK_DELAY', '1.0')),
                    "retry_attempts": int(os.getenv('UPWORK_RETRY_ATTEMPTS', '3'))
                },
                "queries": self._parse_queries_from_env()
            }
        
        return None
    
    def _load_from_file(self) -> Optional[Dict]:
        """Завантаження з файлу"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Помилка завантаження конфігурації з файлу: {e}")
        
        return None
    
    def _get_default_config(self) -> Dict:
        """Дефолтна конфігурація"""
        return {
            "api_credentials": {
                "api_key": "your_api_key_here",
                "api_secret": "your_api_secret_here",
                "access_token": "your_access_token_here",
                "access_token_secret": "your_access_token_secret_here"
            },
            "search_settings": {
                "max_results_per_query": 50,
                "delay_between_requests": 1.0,
                "retry_attempts": 3
            },
            "queries": [
                "python developer",
                "web designer",
                "data scientist",
                "React developer",
                "UI/UX designer"
            ]
        }
    
    def _parse_queries_from_env(self) -> list:
        """Парсинг запитів з змінних середовища"""
        queries_str = os.getenv('UPWORK_QUERIES', '')
        if queries_str:
            return [q.strip() for q in queries_str.split(',')]
        return []
    
    def get_api_credentials(self) -> Dict[str, str]:
        """Отримання API credentials"""
        return self.config.get("api_credentials", {})
    
    def get_search_settings(self) -> Dict:
        """Отримання налаштувань пошуку"""
        return self.config.get("search_settings", {})
    
    def get_queries(self) -> list:
        """Отримання списку запитів"""
        return self.config.get("queries", [])
    
    def is_configured(self) -> bool:
        """Перевірка чи налаштована конфігурація"""
        credentials = self.get_api_credentials()
        required_keys = ['api_key', 'api_secret', 'access_token', 'access_token_secret']
        
        return all(
            credentials.get(key) and credentials.get(key) != f"your_{key}_here"
            for key in required_keys
        )
    
    def save_config(self, config: Dict = None):
        """Збереження конфігурації в файл"""
        if config:
            self.config = config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Конфігурація збережена в {self.config_file}")
        except Exception as e:
            print(f"❌ Помилка збереження конфігурації: {e}")
    
    def create_template(self):
        """Створення шаблону конфігурації"""
        template = {
            "api_credentials": {
                "api_key": "your_api_key_here",
                "api_secret": "your_api_secret_here",
                "access_token": "your_access_token_here",
                "access_token_secret": "your_access_token_secret_here"
            },
            "search_settings": {
                "max_results_per_query": 50,
                "delay_between_requests": 1.0,
                "retry_attempts": 3
            },
            "queries": [
                "python developer",
                "web designer",
                "data scientist",
                "React developer",
                "UI/UX designer"
            ]
        }
        
        self.save_config(template)
        return template


# Глобальний екземпляр конфігурації
api_config = APIConfig() 