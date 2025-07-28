"""
Моделі бази даних для Upwork Web App
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Job(Base):
    """Модель для зберігання інформації про вакансії з Upwork API"""
    
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    upwork_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    hourly_rate_min = Column(Float, nullable=True)
    hourly_rate_max = Column(Float, nullable=True)
    skills = Column(JSON, nullable=True)  # JSON array
    category = Column(String(200), nullable=True)
    subcategory = Column(String(200), nullable=True)
    client_country = Column(String(100), nullable=True)
    client_rating = Column(Float, nullable=True)
    client_reviews_count = Column(Integer, nullable=True)
    posted_time = Column(DateTime, nullable=True)
    job_type = Column(String(50), nullable=True)  # hourly, fixed, etc.
    experience_level = Column(String(50), nullable=True)
    project_length = Column(String(100), nullable=True)
    hours_per_week = Column(String(100), nullable=True)
    team_size = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)
    
    # AI аналіз
    ai_analysis = Column(JSON, nullable=True)  # Результати AI аналізу
    smart_filter_score = Column(Float, nullable=True)  # Оцінка розумного фільтра
    
    # Метадані
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Application(Base):
    """Модель для зберігання відгуків на вакансії"""
    
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), index=True, nullable=False)
    upwork_job_id = Column(String(100), index=True, nullable=False)
    
    # Відгук
    proposal_text = Column(Text, nullable=False)
    cover_letter = Column(Text, nullable=True)
    bid_amount = Column(Float, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    
    # Статус
    status = Column(String(50), default="draft")  # draft, submitted, viewed, interviewed, hired, rejected
    submitted_at = Column(DateTime, nullable=True)
    viewed_at = Column(DateTime, nullable=True)
    
    # AI генерація
    ai_generated = Column(Boolean, default=False)
    template_used = Column(String(200), nullable=True)
    effectiveness_score = Column(Float, nullable=True)  # Оцінка ефективності
    
    # Метадані
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Message(Base):
    """Модель для зберігання повідомлень з клієнтами"""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    upwork_message_id = Column(String(100), unique=True, index=True, nullable=False)
    job_id = Column(String(100), index=True, nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    
    # Повідомлення
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, file, interview_invitation
    direction = Column(String(20), default="incoming")  # incoming, outgoing
    
    # AI аналіз
    ai_generated = Column(Boolean, default=False)
    sentiment_score = Column(Float, nullable=True)  # Сентимент-аналіз
    urgency_score = Column(Float, nullable=True)  # Оцінка терміновості
    
    # Метадані
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Template(Base):
    """Модель для зберігання шаблонів відгуків"""
    
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Шаблон
    template_text = Column(Text, nullable=False)
    template_type = Column(String(50), default="cover_letter")  # cover_letter, proposal, message
    
    # AI налаштування
    ai_prompt = Column(Text, nullable=True)  # Промпт для AI генерації
    variables = Column(JSON, nullable=True)  # Змінні для шаблону
    
    # Статистика
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    
    # A/B тестування
    is_active = Column(Boolean, default=True)
    variant_id = Column(Integer, nullable=True)  # Для A/B тестування
    
    # Метадані
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Client(Base):
    """Модель для зберігання інформації про клієнтів"""
    
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    upwork_client_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Інформація про клієнта
    name = Column(String(200), nullable=True)
    country = Column(String(100), nullable=True)
    rating = Column(Float, nullable=True)
    reviews_count = Column(Integer, nullable=True)
    total_spent = Column(Float, nullable=True)
    hourly_rate_avg = Column(Float, nullable=True)
    
    # Аналіз
    hiring_frequency = Column(Float, nullable=True)  # Частота найму
    avg_project_size = Column(Float, nullable=True)  # Середній розмір проекту
    preferred_skills = Column(JSON, nullable=True)  # Улюблені скіли
    
    # Метадані
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Analytics(Base):
    """Модель для зберігання аналітичних даних"""
    
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    metric_type = Column(String(100), nullable=False)  # applications_sent, interviews_received, etc.
    metric_value = Column(Float, nullable=False)
    
    # Додаткові дані
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    
    # Метадані
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    """Модель для зберігання сповіщень"""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_type = Column(String(50), nullable=False)  # new_job, application_viewed, message_received
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Статус
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Додаткові дані
    job_id = Column(String(100), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # Метадані
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)


class SystemLog(Base):
    """Модель для зберігання системних логів"""
    
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    
    # Контекст
    module = Column(String(100), nullable=True)
    function = Column(String(100), nullable=True)
    job_id = Column(String(100), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    
    # Додаткові дані
    error_details = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Метадані
    timestamp = Column(DateTime, default=datetime.utcnow) 