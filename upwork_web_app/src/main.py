"""
Головний файл FastAPI додатку для Upwork Web App
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from typing import Optional, List

from .config.settings import settings
from .database.connection import get_db, db_manager
from .database.models import Job, Application, Message, Template, Client, Analytics, Notification, SystemLog
from .utils.logger import structured_logger
from .utils.telegram_bot import TelegramNotifier, TelegramConfig

app = FastAPI(
    title="Upwork Web App API",
    description="API для роботи з Upwork через офіційне API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Подія запуску додатку"""
    print("🚀 Запуск Upwork Web App...")
    
    # Тестуємо підключення до БД
    if not db_manager.test_connection():
        print("⚠️ Попередження: Проблеми з підключенням до БД")
    else:
        # Створюємо таблиці якщо їх немає
        try:
            db_manager.create_tables()
        except Exception as e:
            print(f"⚠️ Попередження: Не вдалося створити таблиці: {e}")

@app.get("/")
async def root():
    """Головна сторінка API"""
    return {
        "message": "Upwork Web App API",
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
        "service": "upwork_web_app",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/status")
async def get_status(db: Session = Depends(get_db)):
    """Статус додатку"""
    try:
        # Отримуємо статистику з БД
        total_jobs = db.query(Job).count()
        total_applications = db.query(Application).count()
        total_messages = db.query(Message).count()
        total_templates = db.query(Template).count()
        
        return {
            "app_status": "running",
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "total_messages": total_messages,
            "total_templates": total_templates,
            "last_sync": None  # Буде додано після реалізації API синхронізації
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання статусу: {str(e)}")

# ===== JOBS ENDPOINTS =====

@app.get("/jobs")
async def get_jobs(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    job_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Отримання списку вакансій"""
    try:
        query = db.query(Job).filter(Job.is_active == True)
        
        if category:
            query = query.filter(Job.category == category)
        if job_type:
            query = query.filter(Job.job_type == job_type)
            
        jobs = query.offset(skip).limit(limit).all()
        
        return {
            "jobs": [
                {
                    "id": job.id,
                    "upwork_id": job.upwork_id,
                    "title": job.title,
                    "description": job.description,
                    "budget_min": job.budget_min,
                    "budget_max": job.budget_max,
                    "hourly_rate_min": job.hourly_rate_min,
                    "hourly_rate_max": job.hourly_rate_max,
                    "skills": job.skills,
                    "category": job.category,
                    "client_rating": job.client_rating,
                    "job_type": job.job_type,
                    "experience_level": job.experience_level,
                    "url": job.url,
                    "smart_filter_score": job.smart_filter_score,
                    "created_at": job.created_at.isoformat() if job.created_at else None
                }
                for job in jobs
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання вакансій: {str(e)}")

@app.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Отримання деталей вакансії"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Вакансію не знайдено")
            
        return {
            "id": job.id,
            "upwork_id": job.upwork_id,
            "title": job.title,
            "description": job.description,
            "budget_min": job.budget_min,
            "budget_max": job.budget_max,
            "hourly_rate_min": job.hourly_rate_min,
            "hourly_rate_max": job.hourly_rate_max,
            "skills": job.skills,
            "category": job.category,
            "subcategory": job.subcategory,
            "client_country": job.client_country,
            "client_rating": job.client_rating,
            "client_reviews_count": job.client_reviews_count,
            "posted_time": job.posted_time.isoformat() if job.posted_time else None,
            "job_type": job.job_type,
            "experience_level": job.experience_level,
            "project_length": job.project_length,
            "hours_per_week": job.hours_per_week,
            "team_size": job.team_size,
            "url": job.url,
            "ai_analysis": job.ai_analysis,
            "smart_filter_score": job.smart_filter_score,
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання вакансії: {str(e)}")

@app.post("/jobs/search")
async def search_jobs(
    query: str,
    filters: Optional[dict] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Пошук вакансій"""
    try:
        # Базований пошук - буде розширено з AI
        search_query = db.query(Job).filter(
            Job.is_active == True,
            Job.title.contains(query) | Job.description.contains(query)
        )
        
        # Застосування фільтрів
        if filters:
            if filters.get("category"):
                search_query = search_query.filter(Job.category == filters["category"])
            if filters.get("job_type"):
                search_query = search_query.filter(Job.job_type == filters["job_type"])
            if filters.get("budget_min"):
                search_query = search_query.filter(Job.budget_min >= filters["budget_min"])
            if filters.get("budget_max"):
                search_query = search_query.filter(Job.budget_max <= filters["budget_max"])
        
        jobs = search_query.offset(skip).limit(limit).all()
        
        return {
            "jobs": [
                {
                    "id": job.id,
                    "upwork_id": job.upwork_id,
                    "title": job.title,
                    "budget_min": job.budget_min,
                    "budget_max": job.budget_max,
                    "category": job.category,
                    "client_rating": job.client_rating,
                    "smart_filter_score": job.smart_filter_score,
                    "url": job.url
                }
                for job in jobs
            ],
            "total": search_query.count(),
            "query": query,
            "filters": filters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка пошуку: {str(e)}")

# ===== APPLICATIONS ENDPOINTS =====

@app.get("/applications")
async def get_applications(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Отримання списку відгуків"""
    try:
        query = db.query(Application)
        
        if status:
            query = query.filter(Application.status == status)
            
        applications = query.offset(skip).limit(limit).all()
        
        return {
            "applications": [
                {
                    "id": app.id,
                    "job_id": app.job_id,
                    "upwork_job_id": app.upwork_job_id,
                    "proposal_text": app.proposal_text,
                    "cover_letter": app.cover_letter,
                    "bid_amount": app.bid_amount,
                    "estimated_hours": app.estimated_hours,
                    "status": app.status,
                    "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
                    "viewed_at": app.viewed_at.isoformat() if app.viewed_at else None,
                    "ai_generated": app.ai_generated,
                    "template_used": app.template_used,
                    "effectiveness_score": app.effectiveness_score,
                    "created_at": app.created_at.isoformat() if app.created_at else None
                }
                for app in applications
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання відгуків: {str(e)}")

@app.post("/applications")
async def create_application(
    job_id: str,
    upwork_job_id: str,
    proposal_text: str,
    cover_letter: Optional[str] = None,
    bid_amount: Optional[float] = None,
    estimated_hours: Optional[int] = None,
    ai_generated: bool = False,
    template_used: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Створення нового відгуку"""
    try:
        application = Application(
            job_id=job_id,
            upwork_job_id=upwork_job_id,
            proposal_text=proposal_text,
            cover_letter=cover_letter,
            bid_amount=bid_amount,
            estimated_hours=estimated_hours,
            ai_generated=ai_generated,
            template_used=template_used,
            status="draft"
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        return {
            "id": application.id,
            "job_id": application.job_id,
            "upwork_job_id": application.upwork_job_id,
            "status": application.status,
            "created_at": application.created_at.isoformat() if application.created_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка створення відгуку: {str(e)}")

@app.post("/applications/{application_id}/submit")
async def submit_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Відправка відгуку через Upwork API"""
    try:
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise HTTPException(status_code=404, detail="Відгук не знайдено")
            
        # TODO: Інтеграція з Upwork API для відправки
        application.status = "submitted"
        application.submitted_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "id": application.id,
            "status": application.status,
            "submitted_at": application.submitted_at.isoformat() if application.submitted_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка відправки відгуку: {str(e)}")

# ===== TEMPLATES ENDPOINTS =====

@app.get("/templates")
async def get_templates(
    template_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Отримання списку шаблонів"""
    try:
        query = db.query(Template).filter(Template.is_active == True)
        
        if template_type:
            query = query.filter(Template.template_type == template_type)
            
        templates = query.offset(skip).limit(limit).all()
        
        return {
            "templates": [
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "template_type": template.template_type,
                    "usage_count": template.usage_count,
                    "success_rate": template.success_rate,
                    "is_active": template.is_active,
                    "created_at": template.created_at.isoformat() if template.created_at else None
                }
                for template in templates
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання шаблонів: {str(e)}")

@app.post("/templates")
async def create_template(
    name: str,
    template_text: str,
    template_type: str = "cover_letter",
    description: Optional[str] = None,
    ai_prompt: Optional[str] = None,
    variables: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Створення нового шаблону"""
    try:
        template = Template(
            name=name,
            template_text=template_text,
            template_type=template_type,
            description=description,
            ai_prompt=ai_prompt,
            variables=variables
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "id": template.id,
            "name": template.name,
            "template_type": template.template_type,
            "created_at": template.created_at.isoformat() if template.created_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка створення шаблону: {str(e)}")

# ===== MESSAGES ENDPOINTS =====

@app.get("/messages")
async def get_messages(
    job_id: Optional[str] = None,
    application_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Отримання списку повідомлень"""
    try:
        query = db.query(Message)
        
        if job_id:
            query = query.filter(Message.job_id == job_id)
        if application_id:
            query = query.filter(Message.application_id == application_id)
            
        messages = query.offset(skip).limit(limit).all()
        
        return {
            "messages": [
                {
                    "id": msg.id,
                    "upwork_message_id": msg.upwork_message_id,
                    "job_id": msg.job_id,
                    "application_id": msg.application_id,
                    "content": msg.content,
                    "message_type": msg.message_type,
                    "direction": msg.direction,
                    "ai_generated": msg.ai_generated,
                    "sentiment_score": msg.sentiment_score,
                    "urgency_score": msg.urgency_score,
                    "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання повідомлень: {str(e)}")

@app.post("/messages")
async def send_message(
    content: str,
    job_id: Optional[str] = None,
    application_id: Optional[int] = None,
    message_type: str = "text",
    ai_generated: bool = False,
    db: Session = Depends(get_db)
):
    """Відправка повідомлення"""
    try:
        message = Message(
            upwork_message_id=str(uuid.uuid4()),  # TODO: Отримати з Upwork API
            job_id=job_id,
            application_id=application_id,
            content=content,
            message_type=message_type,
            direction="outgoing",
            ai_generated=ai_generated
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return {
            "id": message.id,
            "upwork_message_id": message.upwork_message_id,
            "content": message.content,
            "direction": message.direction,
            "created_at": message.created_at.isoformat() if message.created_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка відправки повідомлення: {str(e)}")

# ===== ANALYTICS ENDPOINTS =====

@app.get("/analytics")
async def get_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metric_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Отримання аналітичних даних"""
    try:
        query = db.query(Analytics)
        
        if start_date:
            query = query.filter(Analytics.date >= start_date)
        if end_date:
            query = query.filter(Analytics.date <= end_date)
        if metric_type:
            query = query.filter(Analytics.metric_type == metric_type)
            
        analytics = query.all()
        
        return {
            "analytics": [
                {
                    "id": item.id,
                    "date": item.date.isoformat() if item.date else None,
                    "metric_type": item.metric_type,
                    "metric_value": item.metric_value,
                    "category": item.category,
                    "subcategory": item.subcategory,
                    "template_id": item.template_id
                }
                for item in analytics
            ],
            "total": query.count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання аналітики: {str(e)}")

# ===== NOTIFICATIONS ENDPOINTS =====

@app.get("/notifications")
async def get_notifications(
    is_read: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Отримання списку сповіщень"""
    try:
        query = db.query(Notification)
        
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
            
        notifications = query.offset(skip).limit(limit).all()
        
        return {
            "notifications": [
                {
                    "id": notif.id,
                    "notification_type": notif.notification_type,
                    "title": notif.title,
                    "message": notif.message,
                    "is_read": notif.is_read,
                    "is_sent": notif.is_sent,
                    "job_id": notif.job_id,
                    "application_id": notif.application_id,
                    "message_id": notif.message_id,
                    "created_at": notif.created_at.isoformat() if notif.created_at else None
                }
                for notif in notifications
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання сповіщень: {str(e)}")

@app.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Позначення сповіщення як прочитане"""
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Сповіщення не знайдено")
            
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Сповіщення позначено як прочитане"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка оновлення сповіщення: {str(e)}")

# ===== SYSTEM ENDPOINTS =====

@app.get("/logs")
async def get_logs(
    level: Optional[str] = None,
    module: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Отримання системних логів"""
    try:
        query = db.query(SystemLog)
        
        if level:
            query = query.filter(SystemLog.level == level)
        if module:
            query = query.filter(SystemLog.module == module)
            
        logs = query.order_by(SystemLog.timestamp.desc()).offset(skip).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "level": log.level,
                    "message": log.message,
                    "module": log.module,
                    "function": log.function,
                    "job_id": log.job_id,
                    "application_id": log.application_id,
                    "error_details": log.error_details,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                }
                for log in logs
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання логів: {str(e)}")

@app.post("/telegram/setup")
async def setup_telegram(
    bot_token: str,
    chat_ids: str  # JSON string або кома-розділений список
):
    """Налаштування Telegram бота"""
    try:
        # TODO: Зберегти налаштування в конфігурації
        return {
            "message": "Telegram бот налаштовано",
            "bot_token": bot_token[:10] + "...",  # Показуємо тільки частину токена
            "chat_ids": chat_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка налаштування Telegram: {str(e)}")

@app.post("/telegram/test")
async def test_telegram():
    """Тестування Telegram сповіщень"""
    try:
        # TODO: Відправити тестове повідомлення
        return {"message": "Тестове повідомлення відправлено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка тестування Telegram: {str(e)}")

@app.post("/telegram/send")
async def send_telegram_message(
    message: str,
    chat_id: Optional[str] = None
):
    """Відправка повідомлення через Telegram"""
    try:
        # TODO: Відправити повідомлення через Telegram API
        return {"message": "Повідомлення відправлено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка відправки повідомлення: {str(e)}") 