"""
Upwork Service - Мікросервіс для роботи з Upwork API
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import setup_logging, get_logger
from shared.database.connection import get_db, db_manager

# Налаштування логування
setup_logging(service_name="upwork-service")
logger = get_logger("upwork-service")

# Створюємо FastAPI додаток
app = FastAPI(
    title="Upwork Service",
    description="Мікросервіс для роботи з Upwork API",
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
    logger.info("🚀 Запуск Upwork Service...")
    
    # Тестуємо підключення до БД
    if not db_manager.test_connection():
        logger.warning("⚠️ Попередження: Проблеми з підключенням до БД")
    else:
        logger.info("✅ Підключення до БД успішне")


@app.get("/")
async def root():
    """Головна сторінка сервісу"""
    return {
        "service": "Upwork Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Перевірка здоров'я сервісу"""
    db_status = "healthy" if db_manager.test_connection() else "unhealthy"
    redis_status = "healthy" if db_manager.test_redis_connection() else "unhealthy"
    
    return {
        "status": "healthy",
        "service": "upwork-service",
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/upwork/jobs")
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Отримання списку вакансій (заглушка)"""
    return {
        "message": "Upwork Service - Jobs endpoint",
        "status": "not_implemented",
        "skip": skip,
        "limit": limit
    }


@app.get("/upwork/jobs/{job_id}")
async def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Отримання деталей вакансії (заглушка)"""
    return {
        "message": "Upwork Service - Job details endpoint",
        "status": "not_implemented",
        "job_id": job_id
    }


@app.post("/upwork/jobs/search")
async def search_jobs(
    query: str,
    db: Session = Depends(get_db)
):
    """Пошук вакансій (заглушка)"""
    return {
        "message": "Upwork Service - Job search endpoint",
        "status": "not_implemented",
        "query": query
    }


@app.get("/upwork/applications")
async def get_applications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Отримання списку заявок (заглушка)"""
    return {
        "message": "Upwork Service - Applications endpoint",
        "status": "not_implemented",
        "skip": skip,
        "limit": limit
    }


@app.post("/upwork/applications")
async def create_application(
    job_id: str,
    proposal_text: str,
    db: Session = Depends(get_db)
):
    """Створення заявки (заглушка)"""
    return {
        "message": "Upwork Service - Create application endpoint",
        "status": "not_implemented",
        "job_id": job_id
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 