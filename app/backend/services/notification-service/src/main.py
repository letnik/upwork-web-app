"""
Notification Service - Мікросервіс для сповіщень
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.config.settings import settings
from shared.config.logging import setup_logging, get_logger
from shared.database.connection import get_db, db_manager

# Налаштування логування
setup_logging(service_name="notification-service")
logger = get_logger("notification-service")

# Створюємо FastAPI додаток
app = FastAPI(
    title="Notification Service",
    description="Мікросервіс для сповіщень",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Подія запуску сервісу"""
    logger.info("🚀 Запуск Notification Service...")
    
    # Тестуємо підключення до БД
    if not db_manager.test_connection():
        logger.warning("⚠️ Попередження: Проблеми з підключенням до БД")
    else:
        logger.info("✅ Підключення до БД успішне")


@app.get("/")
async def root():
    """Головна сторінка сервісу"""
    return {
        "service": "Notification Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Перевірка здоров'я сервісу"""
    db_status = "healthy" if db_manager.test_connection() else "unhealthy"
    
    return {
        "status": "healthy",
        "service": "notification-service",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/notifications")
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    is_read: bool = None,
    db: Session = Depends(get_db)
):
    """Отримання списку сповіщень (заглушка)"""
    return {
        "message": "Notification Service - Get notifications endpoint",
        "status": "not_implemented",
        "skip": skip,
        "limit": limit,
        "is_read": is_read
    }


@app.post("/notifications")
async def create_notification(
    title: str,
    message: str,
    notification_type: str = "info",
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Створення сповіщення (заглушка)"""
    return {
        "message": "Notification Service - Create notification endpoint",
        "status": "not_implemented",
        "title": title,
        "notification_type": notification_type
    }


@app.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Позначення сповіщення як прочитане (заглушка)"""
    return {
        "message": "Notification Service - Mark notification read endpoint",
        "status": "not_implemented",
        "notification_id": notification_id
    }


@app.post("/notifications/send/email")
async def send_email_notification(
    to_email: str,
    subject: str,
    message: str,
    db: Session = Depends(get_db)
):
    """Відправка email сповіщення (заглушка)"""
    return {
        "message": "Notification Service - Send email endpoint",
        "status": "not_implemented",
        "to_email": to_email,
        "subject": subject
    }


@app.post("/notifications/send/telegram")
async def send_telegram_notification(
    chat_id: str,
    message: str,
    db: Session = Depends(get_db)
):
    """Відправка Telegram сповіщення (заглушка)"""
    return {
        "message": "Notification Service - Send telegram endpoint",
        "status": "not_implemented",
        "chat_id": chat_id
    }


@app.post("/notifications/send/push")
async def send_push_notification(
    user_id: int,
    title: str,
    message: str,
    db: Session = Depends(get_db)
):
    """Відправка push сповіщення (заглушка)"""
    return {
        "message": "Notification Service - Send push notification endpoint",
        "status": "not_implemented",
        "user_id": user_id,
        "title": title
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 