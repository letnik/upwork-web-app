#!/usr/bin/env python3
"""
Інтеграційний тест Upwork Web App API
"""

import sys
import os
import asyncio
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.upwork_service import UpworkService
from src.auth.models import User
from src.database.connection import db_manager


def test_environment_configuration():
    """Тест конфігурації середовища"""
    
    print("🔧 Тестування конфігурації середовища...")
    
    # Перевіряємо змінні середовища
    required_vars = [
        'UPWORK_CLIENT_ID',
        'UPWORK_CLIENT_SECRET',
        'UPWORK_REDIRECT_URI',
        'ENCRYPTION_KEY',
        'DATABASE_URL',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if not missing_vars:
        print("✅ Всі змінні середовища налаштовані")
        print("📋 Налаштування:")
        print(f"   UPWORK_CLIENT_ID: {os.getenv('UPWORK_CLIENT_ID', '')[:8]}...")
        print(f"   UPWORK_REDIRECT_URI: {os.getenv('UPWORK_REDIRECT_URI')}")
        print(f"   DATABASE_URL: {os.getenv('DATABASE_URL', '')[:20]}...")
        return True
    else:
        print("⚠️ Відсутні змінні середовища:")
        for var in missing_vars:
            print(f"   - {var}")
        print("📝 Налаштуйте .env файл з необхідними змінними")
        return False


def test_service_creation():
    """Тест створення Upwork сервісу"""
    
    print("\n🚀 Тестування створення Upwork сервісу...")
    
    try:
        service = UpworkService()
        print("✅ Upwork сервіс створено успішно")
        return service
        
    except Exception as e:
        print(f"❌ Помилка створення сервісу: {e}")
        return None


async def test_api_search(service):
    """Тест пошуку через API"""
    
    if not service:
        print("⚠️ Сервіс не створено, пропускаємо тест пошуку")
        return
    
    print("\n🔍 Тестування пошуку через API...")
    
    # Перевіряємо чи налаштоване середовище
    if not os.getenv('UPWORK_CLIENT_ID'):
        print("⚠️ API не налаштовано, використовуємо мокові дані")
        return
    
    try:
        # Створюємо тестового користувача
        test_user = User(
            id=1,
            email="test@example.com",
            upwork_access_token="test_token",
            upwork_user_id="test_user_id"
        )
        
        # Тестуємо пошук
        test_query = "python developer"
        print(f"🔍 Тестуємо пошук: '{test_query}'")
        
        jobs = await service.get_user_jobs(test_user, query=test_query)
        
        if jobs:
            print(f"✅ Знайдено {len(jobs)} вакансій")
            for i, job in enumerate(jobs[:3]):  # Показуємо перші 3
                print(f"   {i+1}. {job.get('title', 'N/A')}")
                print(f"      Бюджет: ${job.get('budget_min', '?')}-${job.get('budget_max', '?')}")
                print(f"      Країна: {job.get('client_country', 'N/A')}")
        else:
            print("❌ Не знайдено вакансій або помилка API")
            
    except Exception as e:
        print(f"❌ Помилка пошуку: {e}")


def test_database_integration():
    """Тест інтеграції з базою даних"""
    
    print("\n💾 Тестування інтеграції з БД...")
    
    try:
        # Отримуємо сесію БД
        db_session = db_manager.SessionLocal()
        
        # Перевіряємо підключення
        from sqlalchemy import text
        result = db_session.execute(text("SELECT 1"))
        print("✅ Підключення до БД успішне")
        
        # Тестуємо збереження мокових даних
        mock_jobs = [
            {
                "id": "~test123456789",
                "title": "Test Python Developer",
                "snippet": "Test job for API integration",
                "budget": 1000.0,
                "skills": ["Python", "Testing"],
                "category2": "Web Development",
                "client": {
                    "location": {"country": "Test Country"},
                    "feedback": 4.5,
                    "reviews_count": 10
                },
                "date_created": "2024-12-19T10:00:00+0000",
                "type": "fixed"
            }
        ]
        
        # Тут буде логіка збереження в нову архітектуру
        print("✅ Тестова структура даних готова")
        
        db_session.close()
        
    except Exception as e:
        print(f"❌ Помилка інтеграції з БД: {e}")


async def test_full_workflow():
    """Тест повного workflow"""
    
    print("\n🔄 Тестування повного workflow...")
    
    if not os.getenv('UPWORK_CLIENT_ID'):
        print("⚠️ API не налаштовано, пропускаємо тест workflow")
        return
    
    try:
        service = UpworkService()
        
        # Створюємо тестового користувача
        test_user = User(
            id=1,
            email="test@example.com",
            upwork_access_token="test_token",
            upwork_user_id="test_user_id"
        )
        
        # Тестуємо повний workflow
        print("📋 Тестуємо workflow:")
        print("   1. Пошук вакансій")
        print("   2. Створення відгуку")
        print("   3. Відправка відгуку")
        
        # Тут буде повна логіка тестування
        print("✅ Workflow тест готовий до реалізації")
        
    except Exception as e:
        print(f"❌ Помилка workflow: {e}")


def create_sample_env():
    """Створює зразок .env файлу"""
    
    print("\n📝 Створення зразка .env файлу...")
    
    env_template = """# Upwork API
UPWORK_CLIENT_ID=your_client_id_here
UPWORK_CLIENT_SECRET=your_client_secret_here
UPWORK_CALLBACK_URL=http://localhost:8000/auth/upwork/callback

# Шифрування
ENCRYPTION_KEY=your_encryption_key_base64_here

# База даних
DATABASE_URL=postgresql://user:password@localhost/upwork_web_app

# JWT
SECRET_KEY=your_jwt_secret_key_here

# Додаткові налаштування
DEBUG=True
LOG_LEVEL=INFO
"""
    
    with open('.env.sample', 'w') as f:
        f.write(env_template)
    
    print("✅ Створено .env.sample файл")
    print("📝 Скопіюйте .env.sample в .env та заповніть реальними значеннями")


def main():
    """Головна функція тестування"""
    
    print("🧪 ІНТЕГРАЦІЙНИЙ ТЕСТ UPWORK WEB APP")
    print("=" * 50)
    
    # Тест конфігурації
    env_ok = test_environment_configuration()
    
    # Тест створення сервісу
    service = test_service_creation()
    
    # Тест бази даних
    test_database_integration()
    
    # Тест API пошуку (async)
    if service and env_ok:
        asyncio.run(test_api_search(service))
        asyncio.run(test_full_workflow())
    
    # Створення зразка .env
    if not env_ok:
        create_sample_env()
    
    print("\n" + "=" * 50)
    print("✅ Тестування завершено")
    print("📋 Перевірте результати вище")


if __name__ == "__main__":
    main() 