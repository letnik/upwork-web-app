"""
Analytics Service - Мікросервіс для аналітики та звітності
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import setup_logging, get_logger
from shared.database.connection import get_db, db_manager

# Налаштування логування
setup_logging(service_name="analytics-service")
logger = get_logger("analytics-service")

# Створюємо FastAPI додаток
app = FastAPI(
    title="Analytics Service",
    description="Мікросервіс для аналітики та звітності",
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
    logger.info("🚀 Запуск Analytics Service...")
    
    # Тестуємо підключення до БД
    if not db_manager.test_connection():
        logger.warning("⚠️ Попередження: Проблеми з підключенням до БД")
    else:
        logger.info("✅ Підключення до БД успішне")


@app.get("/")
async def root():
    """Головна сторінка сервісу"""
    return {
        "service": "Analytics Service",
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
        "service": "analytics-service",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/analytics/dashboard")
async def get_dashboard_data(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Отримання даних для дашборду (заглушка)"""
    return {
        "message": "Analytics Service - Dashboard endpoint",
        "status": "not_implemented",
        "start_date": start_date,
        "end_date": end_date
    }


@app.get("/analytics/reports/performance")
async def get_performance_report(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Звіт про продуктивність (заглушка)"""
    return {
        "message": "Analytics Service - Performance report endpoint",
        "status": "not_implemented",
        "start_date": start_date,
        "end_date": end_date
    }


@app.get("/analytics/reports/revenue")
async def get_revenue_report(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Звіт про доходи (заглушка)"""
    return {
        "message": "Analytics Service - Revenue report endpoint",
        "status": "not_implemented",
        "start_date": start_date,
        "end_date": end_date
    }


@app.get("/analytics/metrics")
async def get_metrics(
    metric_type: str = None,
    db: Session = Depends(get_db)
):
    """Отримання метрик (заглушка)"""
    return {
        "message": "Analytics Service - Metrics endpoint",
        "status": "not_implemented",
        "metric_type": metric_type
    }


@app.post("/analytics/track/event")
async def track_event(
    event_type: str,
    event_data: dict,
    db: Session = Depends(get_db)
):
    """Відстеження події (заглушка)"""
    return {
        "message": "Analytics Service - Track event endpoint",
        "status": "not_implemented",
        "event_type": event_type,
        "event_data": event_data
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 