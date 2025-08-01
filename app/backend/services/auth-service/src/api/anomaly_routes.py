"""
API endpoints для роботи з аномаліями та сповіщеннями
SECURITY-009: Детекція аномалій та система сповіщень
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SecurityLog
from ...shared.utils.anomaly_detector import AnomalyDetector, AnomalySeverity
from ...shared.utils.alert_system import AlertSystem, AlertPriority
from ...shared.utils.security_logger import SecurityLogger

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("/")
async def get_anomalies(
    user_id: Optional[int] = Query(None, description="ID користувача"),
    ip_address: Optional[str] = Query(None, description="IP адреса"),
    severity: Optional[str] = Query(None, description="Рівень серйозності"),
    anomaly_type: Optional[str] = Query(None, description="Тип аномалії"),
    start_date: Optional[datetime] = Query(None, description="Початкова дата"),
    end_date: Optional[datetime] = Query(None, description="Кінцева дата"),
    limit: int = Query(100, description="Кількість записів"),
    offset: int = Query(0, description="Зміщення"),
    db: Session = Depends(get_db)
):
    """
    Отримує список аномалій з фільтрацією
    """
    try:
        # Створюємо детектор аномалій
        security_logger = SecurityLogger()
        anomaly_detector = AnomalyDetector(security_logger)
        
        # Отримуємо логи безпеки
        query = db.query(SecurityLog)
        
        # Застосовуємо фільтри
        if user_id:
            query = query.filter(SecurityLog.user_id == user_id)
        if ip_address:
            query = query.filter(SecurityLog.ip_address == ip_address)
        if start_date:
            query = query.filter(SecurityLog.created_at >= start_date)
        if end_date:
            query = query.filter(SecurityLog.created_at <= end_date)
        
        # Отримуємо записи
        security_logs = query.offset(offset).limit(limit).all()
        
        # Аналізуємо кожен запис на аномалії
        anomalies = []
        for log in security_logs:
            anomaly_score, anomaly_details = await anomaly_detector.detect_anomaly(log)
            
            if anomaly_score > 0:
                # Фільтруємо за серйозністю
                if severity:
                    log_severity = anomaly_detector._calculate_severity(anomaly_score).value
                    if log_severity != severity:
                        continue
                
                # Фільтруємо за типом аномалії
                if anomaly_type:
                    has_type = any(detail["type"] == anomaly_type for detail in anomaly_details)
                    if not has_type:
                        continue
                
                anomalies.append({
                    "id": log.id,
                    "user_id": log.user_id,
                    "ip_address": log.ip_address,
                    "event_type": log.event_type,
                    "anomaly_score": anomaly_score,
                    "anomaly_details": anomaly_details,
                    "severity": anomaly_detector._calculate_severity(anomaly_score).value,
                    "created_at": log.created_at
                })
        
        return {
            "anomalies": anomalies,
            "total": len(anomalies),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання аномалій: {str(e)}")


@router.get("/statistics")
async def get_anomaly_statistics(
    days: int = Query(7, description="Кількість днів для аналізу"),
    db: Session = Depends(get_db)
):
    """
    Отримує статистику аномалій
    """
    try:
        security_logger = SecurityLogger()
        anomaly_detector = AnomalyDetector(security_logger)
        
        # Отримуємо статистику
        statistics = await anomaly_detector.get_anomaly_statistics(days)
        
        return statistics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання статистики: {str(e)}")


@router.get("/types")
async def get_anomaly_types():
    """
    Отримує список типів аномалій
    """
    try:
        return {
            "anomaly_types": [
                {
                    "type": "unusual_login_time",
                    "description": "Незвичайний час входу",
                    "weight": 0.3,
                    "threshold": 0.7
                },
                {
                    "type": "unusual_location",
                    "description": "Незвичайна локація",
                    "weight": 0.5,
                    "threshold": 0.8
                },
                {
                    "type": "rapid_requests",
                    "description": "Швидкі запити",
                    "weight": 0.4,
                    "threshold": 0.6
                },
                {
                    "type": "failed_attempts",
                    "description": "Невдалі спроби",
                    "weight": 0.6,
                    "threshold": 0.5
                },
                {
                    "type": "suspicious_patterns",
                    "description": "Підозрілі паттерни",
                    "weight": 0.7,
                    "threshold": 0.8
                },
                {
                    "type": "behavior_change",
                    "description": "Зміна поведінки",
                    "weight": 0.5,
                    "threshold": 0.6
                },
                {
                    "type": "burst_activity",
                    "description": "Спалах активності",
                    "weight": 0.4,
                    "threshold": 0.7
                },
                {
                    "type": "geographic_anomaly",
                    "description": "Географічна аномалія",
                    "weight": 0.6,
                    "threshold": 0.8
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання типів аномалій: {str(e)}")


@router.post("/analyze")
async def analyze_security_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """
    Аналізує конкретний запис логу безпеки на аномалії
    """
    try:
        # Отримуємо запис логу
        security_log = db.query(SecurityLog).filter(SecurityLog.id == log_id).first()
        if not security_log:
            raise HTTPException(status_code=404, detail="Запис логу не знайдено")
        
        # Створюємо детектор аномалій
        security_logger = SecurityLogger()
        anomaly_detector = AnomalyDetector(security_logger)
        
        # Аналізуємо на аномалії
        anomaly_score, anomaly_details = await anomaly_detector.detect_anomaly(security_log)
        
        return {
            "log_id": log_id,
            "anomaly_score": anomaly_score,
            "anomaly_details": anomaly_details,
            "severity": anomaly_detector._calculate_severity(anomaly_score).value,
            "has_anomaly": anomaly_score > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка аналізу: {str(e)}")


@router.get("/alerts")
async def get_alerts(
    alert_type: Optional[str] = Query(None, description="Тип сповіщення"),
    priority: Optional[str] = Query(None, description="Пріоритет"),
    channel: Optional[str] = Query(None, description="Канал сповіщення"),
    start_date: Optional[datetime] = Query(None, description="Початкова дата"),
    end_date: Optional[datetime] = Query(None, description="Кінцева дата"),
    limit: int = Query(100, description="Кількість записів"),
    offset: int = Query(0, description="Зміщення"),
    db: Session = Depends(get_db)
):
    """
    Отримує список сповіщень з фільтрацією
    """
    try:
        # Створюємо систему сповіщень
        security_logger = SecurityLogger()
        anomaly_detector = AnomalyDetector(security_logger)
        alert_system = AlertSystem(security_logger, anomaly_detector)
        
        # Отримуємо історію сповіщень
        alerts = alert_system.alert_history
        
        # Застосовуємо фільтри
        filtered_alerts = []
        for alert in alerts:
            # Фільтр за типом
            if alert_type and alert["type"] != alert_type:
                continue
            
            # Фільтр за пріоритетом
            if priority and alert["priority"].value != priority:
                continue
            
            # Фільтр за каналом
            if channel:
                has_channel = any(ch.value == channel for ch in alert["channels"])
                if not has_channel:
                    continue
            
            # Фільтр за датою
            if start_date and alert["timestamp"] < start_date:
                continue
            if end_date and alert["timestamp"] > end_date:
                continue
            
            filtered_alerts.append(alert)
        
        # Пагінація
        total = len(filtered_alerts)
        paginated_alerts = filtered_alerts[offset:offset + limit]
        
        return {
            "alerts": paginated_alerts,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання сповіщень: {str(e)}")


@router.get("/alerts/statistics")
async def get_alert_statistics(
    days: int = Query(7, description="Кількість днів для аналізу"),
    db: Session = Depends(get_db)
):
    """
    Отримує статистику сповіщень
    """
    try:
        security_logger = SecurityLogger()
        anomaly_detector = AnomalyDetector(security_logger)
        alert_system = AlertSystem(security_logger, anomaly_detector)
        
        # Отримуємо статистику
        statistics = await alert_system.get_alert_statistics(days)
        
        return statistics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання статистики сповіщень: {str(e)}")


@router.get("/alerts/channels")
async def get_alert_channels():
    """
    Отримує список каналів сповіщень
    """
    try:
        return {
            "channels": [
                {
                    "channel": "email",
                    "description": "Email сповіщення",
                    "enabled": True
                },
                {
                    "channel": "sms",
                    "description": "SMS сповіщення",
                    "enabled": False
                },
                {
                    "channel": "telegram",
                    "description": "Telegram сповіщення",
                    "enabled": False
                },
                {
                    "channel": "slack",
                    "description": "Slack сповіщення",
                    "enabled": False
                },
                {
                    "channel": "webhook",
                    "description": "Webhook сповіщення",
                    "enabled": False
                },
                {
                    "channel": "dashboard",
                    "description": "Dashboard сповіщення",
                    "enabled": True
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання каналів: {str(e)}")


@router.post("/alerts/test")
async def test_alert(
    alert_type: str = Query(..., description="Тип сповіщення для тестування"),
    channel: str = Query(..., description="Канал для тестування"),
    db: Session = Depends(get_db)
):
    """
    Тестує відправку сповіщення
    """
    try:
        # Створюємо тестове сповіщення
        test_alert = {
            "type": alert_type,
            "priority": AlertPriority.MEDIUM,
            "channels": [channel],
            "message": f"Test alert: {alert_type}",
            "details": {
                "test": True,
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow()
        }
        
        # Створюємо систему сповіщень
        security_logger = SecurityLogger()
        anomaly_detector = AnomalyDetector(security_logger)
        alert_system = AlertSystem(security_logger, anomaly_detector)
        
        # Відправляємо тестове сповіщення
        success = await alert_system._send_alert(test_alert)
        
        return {
            "success": success,
            "alert": test_alert,
            "message": "Тестове сповіщення відправлено" if success else "Помилка відправки"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка тестування сповіщення: {str(e)}")


@router.get("/realtime")
async def get_realtime_anomalies():
    """
    Отримує аномалії в реальному часі (WebSocket endpoint)
    """
    try:
        # В реальному проекті тут був би WebSocket
        return {
            "message": "Real-time anomalies endpoint",
            "note": "This would be implemented as WebSocket endpoint for real-time monitoring"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка real-time endpoint: {str(e)}")


@router.post("/export")
async def export_anomalies(
    format: str = Query("json", description="Формат експорту (json/csv)"),
    start_date: Optional[datetime] = Query(None, description="Початкова дата"),
    end_date: Optional[datetime] = Query(None, description="Кінцева дата"),
    db: Session = Depends(get_db)
):
    """
    Експортує аномалії в файл
    """
    try:
        # Отримуємо аномалії
        security_logger = SecurityLogger()
        anomaly_detector = AnomalyDetector(security_logger)
        
        # Отримуємо логи безпеки
        query = db.query(SecurityLog)
        
        if start_date:
            query = query.filter(SecurityLog.created_at >= start_date)
        if end_date:
            query = query.filter(SecurityLog.created_at <= end_date)
        
        security_logs = query.all()
        
        # Аналізуємо аномалії
        anomalies = []
        for log in security_logs:
            anomaly_score, anomaly_details = await anomaly_detector.detect_anomaly(log)
            if anomaly_score > 0:
                anomalies.append({
                    "id": log.id,
                    "user_id": log.user_id,
                    "ip_address": log.ip_address,
                    "event_type": log.event_type,
                    "anomaly_score": anomaly_score,
                    "severity": anomaly_detector._calculate_severity(anomaly_score).value,
                    "created_at": log.created_at.isoformat(),
                    "anomaly_details": anomaly_details
                })
        
        if format.lower() == "csv":
            # Створюємо CSV
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Заголовки
            writer.writerow([
                "ID", "User ID", "IP Address", "Event Type", 
                "Anomaly Score", "Severity", "Created At"
            ])
            
            # Дані
            for anomaly in anomalies:
                writer.writerow([
                    anomaly["id"],
                    anomaly["user_id"],
                    anomaly["ip_address"],
                    anomaly["event_type"],
                    anomaly["anomaly_score"],
                    anomaly["severity"],
                    anomaly["created_at"]
                ])
            
            content = output.getvalue()
            output.close()
            
            return JSONResponse(
                content=content,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=anomalies.csv"}
            )
        else:
            # JSON формат
            return {
                "anomalies": anomalies,
                "total": len(anomalies),
                "export_format": "json",
                "export_date": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка експорту: {str(e)}") 