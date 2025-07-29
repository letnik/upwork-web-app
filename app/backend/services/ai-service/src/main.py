"""
AI Service - Мікросервіс для AI функціональності
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import setup_logging, get_logger
from shared.database.connection import get_redis

# Налаштування логування
setup_logging(service_name="ai-service")
logger = get_logger("ai-service")

# Створюємо FastAPI додаток
app = FastAPI(
    title="AI Service",
    description="Мікросервіс для AI функціональності",
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
    logger.info("🚀 Запуск AI Service...")
    
    # Тестуємо підключення до Redis
    try:
        redis_client = get_redis()
        redis_client.ping()
        logger.info("✅ Підключення до Redis успішне")
    except Exception as e:
        logger.warning(f"⚠️ Попередження: Проблеми з підключенням до Redis: {e}")


@app.get("/")
async def root():
    """Головна сторінка сервісу"""
    return {
        "service": "AI Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Перевірка здоров'я сервісу"""
    try:
        redis_client = get_redis()
        redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"
    
    return {
        "status": "healthy",
        "service": "ai-service",
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/ai/generate/proposal")
async def generate_proposal(
    job_description: str,
    user_profile: str = None
):
    """Генерація пропозиції (заглушка)"""
    return {
        "message": "AI Service - Generate proposal endpoint",
        "status": "not_implemented",
        "job_description": job_description[:100] + "..." if len(job_description) > 100 else job_description
    }


@app.post("/ai/analyze/job")
async def analyze_job(
    job_description: str
):
    """Аналіз вакансії (заглушка)"""
    return {
        "message": "AI Service - Analyze job endpoint",
        "status": "not_implemented",
        "job_description": job_description[:100] + "..." if len(job_description) > 100 else job_description
    }


@app.post("/ai/filter/jobs")
async def filter_jobs(
    jobs: list,
    user_preferences: dict = None
):
    """Розумна фільтрація вакансій (заглушка)"""
    return {
        "message": "AI Service - Filter jobs endpoint",
        "status": "not_implemented",
        "jobs_count": len(jobs)
    }


@app.post("/ai/optimize/proposal")
async def optimize_proposal(
    proposal_text: str,
    job_description: str
):
    """Оптимізація пропозиції (заглушка)"""
    return {
        "message": "AI Service - Optimize proposal endpoint",
        "status": "not_implemented",
        "proposal_length": len(proposal_text)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 