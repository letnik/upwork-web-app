"""
API endpoints для управління безпекою
SECURITY-008: Логування безпеки та моніторинг
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import get_logger
from shared.database.connection import get_db
from shared.utils.security_logger import SecurityLogger, SecurityEventType, SecurityLevel
from .models import SecurityLog, User
from .jwt_manager import get_current_user

# Налаштування логування
logger = get_logger("security-routes")

# Створюємо роутер
router = APIRouter(prefix="/security", tags=["security"])


@router.get("/logs")
async def get_security_logs(
    user_id: Optional[int] = Query(None, description="ID користувача"),
    event_type: Optional[str] = Query(None, description="Тип події"),
    level: Optional[str] = Query(None, description="Рівень безпеки"),
    ip_address: Optional[str] = Query(None, description="IP адреса"),
    start_date: Optional[datetime] = Query(None, description="Початкова дата"),
    end_date: Optional[datetime] = Query(None, description="Кінцева дата"),
    limit: int = Query(100, ge=1, le=1000, description="Кількість записів"),
    offset: int = Query(0, ge=0, description="Зміщення"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отримання логів безпеки з фільтрацією
    
    Args:
        user_id: ID користувача для фільтрації
        event_type: Тип події для фільтрації
        level: Рівень безпеки для фільтрації
        ip_address: IP адреса для фільтрації
        start_date: Початкова дата
        end_date: Кінцева дата
        limit: Кількість записів
        offset: Зміщення
        current_user: Поточний користувач
        db: Сесія БД
        
    Returns:
        Список логів безпеки
    """
    try:
        # Базовий запит
        query = db.query(SecurityLog)
        
        # Застосовуємо фільтри
        if user_id:
            query = query.filter(SecurityLog.user_id == user_id)
        
        if event_type:
            query = query.filter(SecurityLog.event_type == event_type)
        
        if level:
            query = query.filter(SecurityLog.level == level)
        
        if ip_address:
            query = query.filter(SecurityLog.ip_address == ip_address)
        
        if start_date:
            query = query.filter(SecurityLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(SecurityLog.created_at <= end_date)
        
        # Сортуємо за датою (новіші спочатку)
        query = query.order_by(desc(SecurityLog.created_at))
        
        # Додаємо пагінацію
        total = query.count()
        logs = query.offset(offset).limit(limit).all()
        
        # Конвертуємо в словники
        logs_data = []
        for log in logs:
            logs_data.append({
                "id": log.id,
                "user_id": log.user_id,
                "event_type": log.event_type,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "details": log.details,
                "success": log.success,
                "level": log.level,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        return {
            "logs": logs_data,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Помилка отримання логів безпеки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання логів безпеки"
        )


@router.get("/logs/statistics")
async def get_security_statistics(
    days: int = Query(7, ge=1, le=365, description="Кількість днів"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отримання статистики безпеки
    
    Args:
        days: Кількість днів для аналізу
        current_user: Поточний користувач
        db: Сесія БД
        
    Returns:
        Статистика безпеки
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Статистика по типах подій
        event_stats = db.query(
            SecurityLog.event_type,
            func.count(SecurityLog.id).label('count'),
            func.sum(func.case([(SecurityLog.success == True, 1)], else_=0)).label('success_count')
        ).filter(
            SecurityLog.created_at >= start_date
        ).group_by(SecurityLog.event_type).all()
        
        # Статистика по рівнях безпеки
        level_stats = db.query(
            SecurityLog.level,
            func.count(SecurityLog.id).label('count')
        ).filter(
            SecurityLog.created_at >= start_date
        ).group_by(SecurityLog.level).all()
        
        # Статистика по IP адресах
        ip_stats = db.query(
            SecurityLog.ip_address,
            func.count(SecurityLog.id).label('count')
        ).filter(
            SecurityLog.created_at >= start_date,
            SecurityLog.ip_address.isnot(None)
        ).group_by(SecurityLog.ip_address).order_by(
            desc(func.count(SecurityLog.id))
        ).limit(10).all()
        
        # Загальна статистика
        total_events = db.query(func.count(SecurityLog.id)).filter(
            SecurityLog.created_at >= start_date
        ).scalar()
        
        failed_events = db.query(func.count(SecurityLog.id)).filter(
            SecurityLog.created_at >= start_date,
            SecurityLog.success == False
        ).scalar()
        
        return {
            "period_days": days,
            "total_events": total_events,
            "failed_events": failed_events,
            "success_rate": (total_events - failed_events) / total_events if total_events > 0 else 0,
            "event_types": [
                {
                    "event_type": stat.event_type,
                    "count": stat.count,
                    "success_count": stat.success_count,
                    "success_rate": stat.success_count / stat.count if stat.count > 0 else 0
                }
                for stat in event_stats
            ],
            "levels": [
                {
                    "level": stat.level,
                    "count": stat.count
                }
                for stat in level_stats
            ],
            "top_ips": [
                {
                    "ip_address": stat.ip_address,
                    "count": stat.count
                }
                for stat in ip_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Помилка отримання статистики безпеки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання статистики безпеки"
        )


@router.get("/logs/anomalies")
async def get_security_anomalies(
    days: int = Query(1, ge=1, le=30, description="Кількість днів"),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Поріг аномалії"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отримання аномалій безпеки
    
    Args:
        days: Кількість днів для аналізу
        threshold: Поріг для виявлення аномалій
        current_user: Поточний користувач
        db: Сесія БД
        
    Returns:
        Список аномалій
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Знаходимо підозрілу активність
        suspicious_activity = db.query(SecurityLog).filter(
            SecurityLog.created_at >= start_date,
            SecurityLog.event_type == SecurityEventType.SUSPICIOUS_ACTIVITY.value
        ).order_by(desc(SecurityLog.created_at)).all()
        
        # Знаходимо невдалі спроби входу
        failed_logins = db.query(SecurityLog).filter(
            SecurityLog.created_at >= start_date,
            SecurityLog.event_type == SecurityEventType.LOGIN_FAILED.value
        ).order_by(desc(SecurityLog.created_at)).all()
        
        # Знаходимо перевищення rate limit
        rate_limit_violations = db.query(SecurityLog).filter(
            SecurityLog.created_at >= start_date,
            SecurityLog.event_type == SecurityEventType.API_RATE_LIMIT.value
        ).order_by(desc(SecurityLog.created_at)).all()
        
        return {
            "period_days": days,
            "threshold": threshold,
            "suspicious_activity": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "ip_address": log.ip_address,
                    "details": log.details,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in suspicious_activity
            ],
            "failed_logins": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "ip_address": log.ip_address,
                    "details": log.details,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in failed_logins
            ],
            "rate_limit_violations": [
                {
                    "id": log.id,
                    "ip_address": log.ip_address,
                    "details": log.details,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in rate_limit_violations
            ]
        }
        
    except Exception as e:
        logger.error(f"Помилка отримання аномалій безпеки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання аномалій безпеки"
        )


@router.post("/logs/export")
async def export_security_logs(
    format: str = Query("json", description="Формат експорту (json, csv)"),
    start_date: Optional[datetime] = Query(None, description="Початкова дата"),
    end_date: Optional[datetime] = Query(None, description="Кінцева дата"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Експорт логів безпеки
    
    Args:
        format: Формат експорту
        start_date: Початкова дата
        end_date: Кінцева дата
        current_user: Поточний користувач
        db: Сесія БД
        
    Returns:
        Експортовані дані
    """
    try:
        # Базовий запит
        query = db.query(SecurityLog)
        
        # Застосовуємо фільтри по даті
        if start_date:
            query = query.filter(SecurityLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(SecurityLog.created_at <= end_date)
        
        # Отримуємо всі записи
        logs = query.order_by(desc(SecurityLog.created_at)).all()
        
        # Конвертуємо в словники
        logs_data = []
        for log in logs:
            logs_data.append({
                "id": log.id,
                "user_id": log.user_id,
                "event_type": log.event_type,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "details": log.details,
                "success": log.success,
                "level": log.level,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        if format.lower() == "csv":
            # Генеруємо CSV
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "id", "user_id", "event_type", "ip_address", "user_agent",
                "success", "level", "created_at"
            ])
            
            writer.writeheader()
            for log in logs_data:
                writer.writerow(log)
            
            return {
                "format": "csv",
                "data": output.getvalue(),
                "filename": f"security_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        else:
            # Повертаємо JSON
            return {
                "format": "json",
                "data": logs_data,
                "total_records": len(logs_data)
            }
        
    except Exception as e:
        logger.error(f"Помилка експорту логів безпеки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка експорту логів безпеки"
        )


@router.delete("/logs/cleanup")
async def cleanup_old_logs(
    days: int = Query(90, ge=1, le=365, description="Видалити логи старіше N днів"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Очищення старих логів безпеки
    
    Args:
        days: Видалити логи старіше N днів
        current_user: Поточний користувач
        db: Сесія БД
        
    Returns:
        Результат очищення
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Підраховуємо кількість записів для видалення
        count_to_delete = db.query(func.count(SecurityLog.id)).filter(
            SecurityLog.created_at < cutoff_date
        ).scalar()
        
        # Видаляємо старі записи
        deleted = db.query(SecurityLog).filter(
            SecurityLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        logger.info(f"Видалено {deleted} старих логів безпеки (старіше {days} днів)")
        
        return {
            "message": f"Видалено {deleted} старих логів безпеки",
            "deleted_count": deleted,
            "cutoff_date": cutoff_date.isoformat(),
            "days_old": days
        }
        
    except Exception as e:
        logger.error(f"Помилка очищення логів безпеки: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка очищення логів безпеки"
        ) 