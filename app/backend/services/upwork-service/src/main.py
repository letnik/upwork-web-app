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
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.insert(0, shared_path)

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
    skills: str = None,
    budget_min: float = None,
    budget_max: float = None,
    location: str = None,
    db: Session = Depends(get_db)
):
    """Отримання списку вакансій"""
    try:
        # Імпортуємо UpworkAPIClient
        from src.upwork_client import MockUpworkAPIClient
        
        # Використовуємо mock клієнт для тестування
        client = MockUpworkAPIClient()
        
        # Формуємо фільтри
        filters = {}
        if skills:
            filters["skills"] = skills
        if budget_min:
            filters["budget_min"] = budget_min
        if budget_max:
            filters["budget_max"] = budget_max
        if location:
            filters["location"] = location
        
        # Отримуємо вакансії
        result = client.search_jobs("", filters)
        jobs = result.get("jobs", [])
        
        # Застосовуємо пагінацію
        jobs = jobs[skip:skip + limit]
        
        logger.info(f"✅ Отримано {len(jobs)} вакансій")
        
        return {
            "jobs": jobs,
            "total": len(jobs),
            "skip": skip,
            "limit": limit,
            "filters_applied": filters
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання вакансій: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка отримання вакансій: {str(e)}"
        )


@app.get("/upwork/jobs/search")
async def search_jobs(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Пошук вакансій"""
    try:
        # Імпортуємо UpworkAPIClient
        from src.upwork_client import MockUpworkAPIClient
        
        # Використовуємо mock клієнт для тестування
        client = MockUpworkAPIClient()
        
        # Шукаємо вакансії
        result = client.search_jobs(query)
        jobs = result.get("jobs", [])
        
        # Застосовуємо пагінацію
        jobs = jobs[skip:skip + limit]
        
        logger.info(f"✅ Знайдено {len(jobs)} вакансій для запиту: {query}")
        
        return {
            "jobs": jobs,
            "total": len(jobs),
            "query": query,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка пошуку вакансій: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка пошуку вакансій"
        )


@app.get("/upwork/jobs/{job_id}")
async def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Отримання деталей вакансії"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        # Використовуємо mock клієнт
        client = MockUpworkAPIClient()
        
        # Отримуємо деталі вакансії
        job = client.get_job_details(job_id)
        
        logger.info(f"✅ Отримано деталі вакансії: {job_id}")
        
        return {
            "job": job
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Помилка отримання вакансії: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання вакансії"
        )


@app.get("/upwork/applications")
async def get_applications(
    skip: int = 0,
    limit: int = 50,
    job_id: str = None,
    db: Session = Depends(get_db)
):
    """Отримання пропозицій користувача"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        # Використовуємо mock клієнт
        client = MockUpworkAPIClient()
        
        # Створюємо mock пропозиції
        mock_proposals = [
            {
                "id": "proposal_1",
                "job_id": "~0123456789012345",
                "proposal_text": "I am interested in this project and have relevant experience...",
                "bid_amount": 2500,
                "delivery_time": "2-3 weeks",
                "status": "pending",
                "submitted_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "proposal_2", 
                "job_id": "~0123456789012347",
                "proposal_text": "I have extensive experience with React Native...",
                "bid_amount": 4000,
                "delivery_time": "1-2 months",
                "status": "accepted",
                "submitted_at": "2024-01-14T15:30:00Z"
            }
        ]
        
        # Фільтруємо за job_id якщо вказано
        if job_id:
            mock_proposals = [p for p in mock_proposals if p["job_id"] == job_id]
        
        # Застосовуємо пагінацію
        proposals = mock_proposals[skip:skip + limit]
        
        logger.info(f"✅ Отримано {len(proposals)} пропозицій")
        
        return {
            "applications": proposals,
            "total": len(mock_proposals),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання пропозицій: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання пропозицій"
        )


@app.post("/upwork/applications")
async def create_application(
    job_id: str,
    proposal_text: str,
    bid_amount: float,
    delivery_time: str,
    db: Session = Depends(get_db)
):
    """Створення нової пропозиції"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        # Використовуємо mock клієнт
        client = MockUpworkAPIClient()
        
        # Перевіряємо чи існує вакансія
        job = client.get_job_details(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вакансію не знайдено"
            )
        
        # Створюємо пропозицію
        proposal = {
            "id": f"proposal_{job_id}_{int(datetime.utcnow().timestamp())}",
            "job_id": job_id,
            "proposal_text": proposal_text,
            "bid_amount": bid_amount,
            "delivery_time": delivery_time,
            "status": "pending",
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Створено пропозицію для вакансії: {job_id}")
        
        return {
            "proposal": proposal,
            "job": job,
            "message": "Пропозицію успішно створено"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Помилка створення пропозиції: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка створення пропозиції"
        )


@app.get("/upwork/clients/{client_id}")
async def get_client(
    client_id: str,
    db: Session = Depends(get_db)
):
    """Отримання інформації про клієнта"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        client_data = client.get_client_info(client_id)
        if not client_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Клієнта не знайдено"
            )
        
        logger.info(f"✅ Отримано інформацію про клієнта: {client_id}")
        
        return {
            "client": client_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Помилка отримання клієнта: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання клієнта"
        )


@app.get("/upwork/freelancers/{freelancer_id}")
async def get_freelancer(
    freelancer_id: str,
    db: Session = Depends(get_db)
):
    """Отримання інформації про фрілансера"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        freelancer = client.get_freelancer_profile(freelancer_id)
        if not freelancer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Фрілансера не знайдено"
            )
        
        logger.info(f"✅ Отримано інформацію про фрілансера: {freelancer_id}")
        
        return {
            "freelancer": freelancer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Помилка отримання фрілансера: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання фрілансера"
        )


@app.get("/upwork/analytics/overview")
async def get_analytics_overview(
    db: Session = Depends(get_db)
):
    """Отримання аналітики по Upwork"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        jobs = client.search_jobs("")
        
        # Розраховуємо статистику
        total_jobs = len(jobs)
        total_proposals = 0  # Mock клієнт не повертає пропозиції
        
        # Безпечний розрахунок середнього бюджету
        total_budget = 0
        budget_count = 0
        for job in jobs:
            if isinstance(job.get("budget"), dict):
                min_budget = job["budget"].get("min", 0)
                max_budget = job["budget"].get("max", 0)
                if isinstance(min_budget, (int, float)) and isinstance(max_budget, (int, float)):
                    total_budget += min_budget + max_budget
                    budget_count += 2
        
        avg_budget = total_budget / budget_count if budget_count > 0 else 0
        
        # Топ навички
        all_skills = []
        for job in jobs:
            all_skills.extend(job["skills"])
        
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        logger.info("✅ Отримано аналітику Upwork")
        
        return {
            "overview": {
                "total_jobs": total_jobs,
                "total_proposals": total_proposals,
                "average_budget": round(avg_budget, 2),
                "top_skills": top_skills
            },
            "recent_jobs": MOCK_JOBS[:3],
            "recent_proposals": MOCK_PROPOSALS[:3]
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання аналітики: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання аналітики"
        )


# Нові endpoints для роботи з OAuth та реальним API

@app.get("/upwork/profile")
async def get_user_profile(
    db: Session = Depends(get_db)
):
    """Отримання профілю користувача"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        profile = client.get_user_profile()
        
        logger.info("✅ Отримано профіль користувача")
        
        return {
            "profile": profile
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання профілю: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання профілю"
        )


@app.post("/upwork/jobs/{job_id}/proposals")
async def submit_proposal(
    job_id: str,
    proposal_data: dict,
    db: Session = Depends(get_db)
):
    """Відправка відгуку на вакансію"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        result = client.submit_proposal(job_id, proposal_data)
        
        logger.info(f"✅ Відправлено відгук на вакансію: {job_id}")
        
        return {
            "success": True,
            "proposal": result,
            "job_id": job_id
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка відправки відгуку: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка відправки відгуку"
        )


@app.get("/upwork/messages")
async def get_messages(
    thread_id: str = None,
    db: Session = Depends(get_db)
):
    """Отримання повідомлень"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        messages = client.get_messages(thread_id)
        
        logger.info("✅ Отримано повідомлення")
        
        return {
            "messages": messages
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання повідомлень: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання повідомлень"
        )


@app.post("/upwork/messages")
async def send_message(
    thread_id: str,
    message: str,
    db: Session = Depends(get_db)
):
    """Відправка повідомлення"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        result = client.send_message(thread_id, message)
        
        logger.info(f"✅ Відправлено повідомлення в thread: {thread_id}")
        
        return {
            "success": True,
            "message": result
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка відправки повідомлення: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка відправки повідомлення"
        )


@app.get("/upwork/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Отримання категорій вакансій"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        result = client.get_categories()
        
        logger.info("✅ Категорії вакансій отримано успішно")
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання категорій: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання категорій"
        )


@app.get("/upwork/skills")
async def get_skills(db: Session = Depends(get_db)):
    """Отримання навичок"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        result = client.get_skills()
        
        logger.info("✅ Навички отримано успішно")
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання навичок: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання навичок"
        )


@app.get("/upwork/contracts")
async def get_contracts(db: Session = Depends(get_db)):
    """Отримання контрактів"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        result = client.get_contracts()
        
        logger.info("✅ Контракти отримано успішно")
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання контрактів: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання контрактів"
        )


@app.get("/upwork/earnings")
async def get_earnings(
    from_date: str = None,
    to_date: str = None,
    db: Session = Depends(get_db)
):
    """Отримання заробітку"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        # Використовуємо ID поточного користувача (в реальному API це буде з токена)
        freelancer_id = "~0123456789012345"
        result = client.get_earnings(freelancer_id, from_date, to_date)
        
        logger.info("✅ Заробіток отримано успішно")
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання заробітку: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання заробітку"
        )


@app.get("/upwork/workdiary")
async def get_workdiary(
    date: str = None,
    db: Session = Depends(get_db)
):
    """Отримання робочого щоденника"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        # Використовуємо ID поточного користувача
        freelancer_id = "~0123456789012345"
        result = client.get_workdiary(freelancer_id, date)
        
        logger.info("✅ Робочий щоденник отримано успішно")
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання робочого щоденника: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання робочого щоденника"
        )


@app.get("/upwork/portfolio")
async def get_portfolio(db: Session = Depends(get_db)):
    """Отримання портфоліо користувача"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        profile = client.get_user_profile()
        
        # Виділяємо портфоліо з профілю
        portfolio = profile.get("portfolio_items", [])
        
        logger.info("✅ Портфоліо отримано успішно")
        return {
            "success": True,
            "data": {
                "portfolio_items": portfolio
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання портфоліо: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання портфоліо"
        )


@app.get("/upwork/certifications")
async def get_certifications(db: Session = Depends(get_db)):
    """Отримання сертифікатів користувача"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        profile = client.get_user_profile()
        
        # Виділяємо сертифікати з профілю
        certifications = profile.get("certifications", [])
        
        logger.info("✅ Сертифікати отримано успішно")
        return {
            "success": True,
            "data": {
                "certifications": certifications
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання сертифікатів: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання сертифікатів"
        )


@app.get("/upwork/education")
async def get_education(db: Session = Depends(get_db)):
    """Отримання освіти користувача"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        profile = client.get_user_profile()
        
        # Виділяємо освіту з профілю
        education = profile.get("education", [])
        
        logger.info("✅ Освіта отримано успішно")
        return {
            "success": True,
            "data": {
                "education": education
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання освіти: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання освіти"
        )


@app.get("/upwork/languages")
async def get_languages(db: Session = Depends(get_db)):
    """Отримання мов користувача"""
    try:
        from src.upwork_client import MockUpworkAPIClient
        
        client = MockUpworkAPIClient()
        profile = client.get_user_profile()
        
        # Виділяємо мови з профілю
        languages = profile.get("languages", [])
        
        logger.info("✅ Мови отримано успішно")
        return {
            "success": True,
            "data": {
                "languages": languages
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка отримання мов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання мов"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) # Updated at Fri Aug  1 14:59:09 EEST 2025
