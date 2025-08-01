"""
AI Service - Основний сервіс для AI функціональності
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shared.config.logging import get_logger

# Імпортуємо нові покращені компоненти
from .ai_service import AIService
from .proposal_generator import ProposalGenerator
from .job_analyzer import JobAnalyzer
from .smart_filter import SmartFilter

logger = get_logger("ai-service-main")

app = FastAPI(
    title="AI Service",
    description="AI сервіс для Upwork проекту",
    version="2.0.0"
)

# CORS налаштування
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Створюємо глобальні екземпляри компонентів
ai_service = AIService()
proposal_generator = ProposalGenerator()
job_analyzer = JobAnalyzer()
smart_filter = SmartFilter()


# Pydantic моделі для запитів
class JobData(BaseModel):
    title: str
    description: str
    budget: Optional[str] = None
    skills: Optional[List[str]] = None
    client_rating: Optional[float] = None


class UserProfile(BaseModel):
    skills: Optional[List[str]] = None
    experience: Optional[str] = None
    hourly_rate: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    availability: Optional[str] = None
    preferred_categories: Optional[List[str]] = None


class ProposalRequest(BaseModel):
    job_data: JobData
    user_profile: Optional[UserProfile] = None
    template: Optional[str] = None


class JobAnalysisRequest(BaseModel):
    job_data: JobData
    user_profile: Optional[UserProfile] = None


class JobFilterRequest(BaseModel):
    jobs: List[JobData]
    user_profile: Optional[UserProfile] = None
    filters: Optional[Dict[str, Any]] = None


class ProposalOptimizationRequest(BaseModel):
    proposal_text: str
    job_data: Optional[JobData] = None
    user_profile: Optional[UserProfile] = None


@app.get("/")
async def root():
    """Кореневий endpoint"""
    return {
        "service": "AI Service",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Перевірка здоров'я сервісу"""
    return {
        "status": "healthy",
        "components": {
            "ai_service": "available",
            "proposal_generator": "available",
            "job_analyzer": "available",
            "smart_filter": "available"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/ai/generate/proposal")
async def generate_proposal(request: ProposalRequest):
    """Генерація пропозиції з покращеним ProposalGenerator"""
    try:
        # Конвертуємо Pydantic моделі в dict
        job_data = request.job_data.dict()
        user_profile = request.user_profile.dict() if request.user_profile else {}
        
        # Використовуємо покращений ProposalGenerator
        result = await proposal_generator.generate_proposal(job_data, user_profile, request.template)
        
        if result["success"]:
            logger.info(f"✅ Згенеровано пропозицію для вакансії: {job_data.get('title', 'unknown')}")
        else:
            logger.warning(f"❌ Помилка генерації пропозиції: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Помилка генерації пропозиції: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка генерації пропозиції"
        )


@app.post("/ai/analyze/job")
async def analyze_job(request: JobAnalysisRequest):
    """Аналіз вакансії з покращеним JobAnalyzer"""
    try:
        # Конвертуємо Pydantic моделі в dict
        job_data = request.job_data.dict()
        user_profile = request.user_profile.dict() if request.user_profile else {}
        
        # Використовуємо покращений JobAnalyzer
        result = await job_analyzer.analyze_job(job_data, user_profile)
        
        if result["success"]:
            logger.info(f"✅ Проаналізовано вакансію: {job_data.get('title', 'unknown')}")
        else:
            logger.warning(f"❌ Помилка аналізу вакансії: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Помилка аналізу вакансії: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка аналізу вакансії"
        )


@app.post("/ai/filter/jobs")
async def filter_jobs(request: JobFilterRequest):
    """Розумна фільтрація вакансій з покращеним SmartFilter"""
    try:
        # Конвертуємо Pydantic моделі в dict
        jobs = [job.dict() for job in request.jobs]
        user_profile = request.user_profile.dict() if request.user_profile else {}
        filters = request.filters or {}
        
        # Використовуємо покращений SmartFilter
        result = await smart_filter.filter_jobs(jobs, user_profile, filters)
        
        if result["success"]:
            logger.info(f"✅ Відфільтровано {result.get('filtered_count', 0)} вакансій з {len(jobs)}")
        else:
            logger.warning(f"❌ Помилка фільтрації вакансій: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Помилка фільтрації вакансій: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка фільтрації вакансій"
        )


@app.post("/ai/optimize/proposal")
async def optimize_proposal(request: ProposalOptimizationRequest):
    """Оптимізація пропозиції з покращеним ProposalGenerator"""
    try:
        # Створюємо тимчасові дані для оптимізації
        temp_job_data = request.job_data.dict() if request.job_data else {
            "title": "Project",
            "description": "Project description",
            "budget": "$1000-5000"
        }
        
        user_profile = request.user_profile.dict() if request.user_profile else {}
        
        # Використовуємо ProposalGenerator для оптимізації
        result = await proposal_generator.generate_proposal(temp_job_data, user_profile, request.proposal_text)
        
        if result["success"]:
            logger.info(f"✅ Оптимізовано пропозицію довжиною {len(request.proposal_text)} символів")
        else:
            logger.warning(f"❌ Помилка оптимізації пропозиції: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Помилка оптимізації пропозиції: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка оптимізації пропозиції"
        )


@app.get("/ai/status")
async def get_ai_status():
    """Отримання статусу AI сервісів"""
    try:
        status = ai_service.get_service_status()
        return status
    except Exception as e:
        logger.error(f"❌ Помилка отримання статусу AI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання статусу AI"
        )


@app.post("/ai/test")
async def test_ai_connection():
    """Тестування з'єднання з AI сервісами"""
    try:
        result = await ai_service.test_connection()
        return result
    except Exception as e:
        logger.error(f"❌ Помилка тестування AI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка тестування AI"
        )


@app.post("/ai/analyze/multiple")
async def analyze_multiple_jobs(jobs: list):
    """Аналіз кількох вакансій"""
    try:
        result = await ai_service.analyze_multiple_jobs(jobs)
        return result
    except Exception as e:
        logger.error(f"❌ Помилка аналізу кількох вакансій: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка аналізу кількох вакансій"
        )


@app.post("/ai/generate/proposal/advanced")
async def generate_advanced_proposal(request: ProposalRequest):
    """Розширена генерація пропозиції з детальним аналізом"""
    try:
        # Конвертуємо Pydantic моделі в dict
        job_data = request.job_data.dict()
        user_profile = request.user_profile.dict() if request.user_profile else {}
        
        # Спочатку аналізуємо вакансію
        analysis_result = await job_analyzer.analyze_job(job_data, user_profile)
        
        if not analysis_result["success"]:
            return analysis_result
        
        # Генеруємо пропозицію з аналізом
        proposal_result = await proposal_generator.generate_proposal(
            job_data, user_profile, request.template
        )
        
        if not proposal_result["success"]:
            return proposal_result
        
        # Об'єднуємо результати
        combined_result = {
            "success": True,
            "analysis": analysis_result["analysis"],
            "proposal": proposal_result["proposal"],
            "template_type": proposal_result.get("template_type", "default"),
            "model": proposal_result.get("model", "fallback"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Згенеровано розширену пропозицію для: {job_data.get('title', 'unknown')}")
        return combined_result
        
    except Exception as e:
        logger.error(f"❌ Помилка розширеної генерації: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка розширеної генерації пропозиції"
        )


@app.post("/ai/filter/jobs/advanced")
async def filter_jobs_advanced(
    request: JobFilterRequest,
    include_analysis: bool = False
):
    """Розширена фільтрація вакансій з аналізом"""
    try:
        # Конвертуємо Pydantic моделі в dict
        jobs = [job.dict() for job in request.jobs]
        user_profile = request.user_profile.dict() if request.user_profile else {}
        filters = request.filters or {}
        
        # Фільтруємо вакансії
        filter_result = await smart_filter.filter_jobs(jobs, user_profile, filters)
        
        if not filter_result["success"]:
            return filter_result
        
        # Якщо потрібен аналіз, додаємо його для кожної вакансії
        if include_analysis:
            analyzed_jobs = []
            for job in filter_result["filtered_jobs"]:
                analysis_result = await job_analyzer.analyze_job(job, user_profile)
                if analysis_result["success"]:
                    job["analysis"] = analysis_result["analysis"]
                analyzed_jobs.append(job)
            
            filter_result["filtered_jobs"] = analyzed_jobs
        
        logger.info(f"✅ Виконано розширену фільтрацію: {filter_result.get('filtered_count', 0)} вакансій")
        return filter_result
        
    except Exception as e:
        logger.error(f"❌ Помилка розширеної фільтрації: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка розширеної фільтрації"
        )


@app.get("/ai/components/status")
async def get_components_status():
    """Отримання статусу всіх компонентів"""
    try:
        ai_status = ai_service.get_service_status()
        
        return {
            "ai_service": ai_status,
            "proposal_generator": "available",
            "job_analyzer": "available", 
            "smart_filter": "available",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Помилка отримання статусу компонентів: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання статусу компонентів"
        ) 