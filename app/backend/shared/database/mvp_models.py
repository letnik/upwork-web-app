"""
Моделі бази даних для MVP компонентів
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, DECIMAL, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .connection import Base


class FilterProfile(Base):
    """Модель профілів фільтрів"""
    
    __tablename__ = "filter_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    keywords = Column(ARRAY(String), nullable=True)  # ключові слова для пошуку
    exclude_keywords = Column(ARRAY(String), nullable=True)  # мінус-слова
    ai_instructions = Column(Text, nullable=True)  # AI інструкції природною мовою
    budget_min = Column(DECIMAL(10, 2), nullable=True)
    budget_max = Column(DECIMAL(10, 2), nullable=True)
    hourly_rate_min = Column(DECIMAL(10, 2), nullable=True)
    hourly_rate_max = Column(DECIMAL(10, 2), nullable=True)
    experience_level = Column(String(50), nullable=True)  # 'entry', 'intermediate', 'expert'
    job_type = Column(String(50), nullable=True)  # 'fixed', 'hourly'
    categories = Column(ARRAY(String), nullable=True)  # категорії роботи
    countries = Column(ARRAY(String), nullable=True)  # країни
    working_hours = Column(JSON, nullable=True)  # години роботи
    timezone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    is_paused = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="filter_profiles")
    job_matches = relationship("JobMatch", back_populates="filter_profile")
    
    def __repr__(self):
        return f"<FilterProfile(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class ProposalTemplate(Base):
    """Модель шаблонів відгуків"""
    
    __tablename__ = "proposal_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)  # 'general', 'web_dev', 'mobile', 'design', etc.
    content = Column(Text, nullable=False)  # шаблон відгуку
    variables = Column(JSON, nullable=True)  # змінні в шаблоні: {client_name}, {project_type}, {budget}
    style = Column(String(50), default='formal')  # 'formal', 'friendly', 'technical'
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    success_rate = Column(DECIMAL(5, 2), nullable=True)  # відсоток успішності
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="proposal_templates")
    proposals = relationship("ProposalDraft", back_populates="template")
    
    def __repr__(self):
        return f"<ProposalTemplate(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class ProposalDraft(Base):
    """Модель чернеток відгуків"""
    
    __tablename__ = "proposal_drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("proposal_templates.id"), nullable=True)
    job_id = Column(String(255), nullable=True)  # ID вакансії з Upwork
    job_title = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=True)
    client_name = Column(String(255), nullable=True)
    budget = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)  # згенерований відгук
    status = Column(String(50), default='draft')  # 'draft', 'sent', 'rejected', 'accepted'
    ai_generated = Column(Boolean, default=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)  # нотатки користувача
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="proposal_drafts")
    template = relationship("ProposalTemplate", back_populates="proposals")
    
    def __repr__(self):
        return f"<ProposalDraft(id={self.id}, job_title='{self.job_title}', user_id={self.user_id})>"


class AIInstruction(Base):
    """Модель AI інструкцій"""
    
    __tablename__ = "ai_instructions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    instruction_type = Column(String(50), nullable=False)  # 'filter', 'proposal', 'analysis'
    content = Column(Text, nullable=False)  # текст інструкції
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    effectiveness_score = Column(DECIMAL(5, 2), nullable=True)  # оцінка ефективності
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="ai_instructions")
    
    def __repr__(self):
        return f"<AIInstruction(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class JobMatch(Base):
    """Модель знайдених вакансій"""
    
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filter_profile_id = Column(Integer, ForeignKey("filter_profiles.id"), nullable=True)
    job_id = Column(String(255), nullable=False)  # ID вакансії з Upwork
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=True)
    client_name = Column(String(255), nullable=True)
    client_rating = Column(DECIMAL(3, 2), nullable=True)
    budget = Column(String(100), nullable=True)
    hourly_rate = Column(DECIMAL(10, 2), nullable=True)
    job_type = Column(String(50), nullable=True)  # 'fixed', 'hourly'
    experience_level = Column(String(50), nullable=True)
    skills = Column(ARRAY(String), nullable=True)
    country = Column(String(100), nullable=True)
    posted_date = Column(DateTime(timezone=True), nullable=True)
    match_score = Column(DECIMAL(5, 2), nullable=True)  # оцінка підходящості
    status = Column(String(50), default='new')  # 'new', 'viewed', 'applied', 'rejected'
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="job_matches")
    filter_profile = relationship("FilterProfile", back_populates="job_matches")
    
    def __repr__(self):
        return f"<JobMatch(id={self.id}, job_title='{self.job_title}', user_id={self.user_id})>"


class ABTest(Base):
    """Модель A/B тестування шаблонів"""
    
    __tablename__ = "ab_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    template_a_id = Column(Integer, ForeignKey("proposal_templates.id"), nullable=False)
    template_b_id = Column(Integer, ForeignKey("proposal_templates.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default='running')  # 'running', 'completed', 'stopped'
    min_duration_days = Column(Integer, default=7)  # мінімальна тривалість тесту
    template_a_sent = Column(Integer, default=0)
    template_b_sent = Column(Integer, default=0)
    template_a_responses = Column(Integer, default=0)
    template_b_responses = Column(Integer, default=0)
    template_a_hired = Column(Integer, default=0)
    template_b_hired = Column(Integer, default=0)
    winner_template_id = Column(Integer, ForeignKey("proposal_templates.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="ab_tests")
    template_a = relationship("ProposalTemplate", foreign_keys=[template_a_id])
    template_b = relationship("ProposalTemplate", foreign_keys=[template_b_id])
    winner_template = relationship("ProposalTemplate", foreign_keys=[winner_template_id])
    
    def __repr__(self):
        return f"<ABTest(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class UserAnalytics(Base):
    """Модель аналітики користувача"""
    
    __tablename__ = "user_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    jobs_found = Column(Integer, default=0)
    proposals_sent = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    interviews_scheduled = Column(Integer, default=0)
    jobs_won = Column(Integer, default=0)
    total_earned = Column(DECIMAL(10, 2), default=0)
    active_profiles = Column(Integer, default=0)
    active_templates = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="analytics")
    
    def __repr__(self):
        return f"<UserAnalytics(id={self.id}, user_id={self.user_id}, date={self.date})>"


# Додаємо зв'язки до існуючої моделі User
def add_user_relationships(User):
    """Додаємо зв'язки до моделі User"""
    User.filter_profiles = relationship("FilterProfile", back_populates="user")
    User.proposal_templates = relationship("ProposalTemplate", back_populates="user")
    User.proposal_drafts = relationship("ProposalDraft", back_populates="user")
    User.ai_instructions = relationship("AIInstruction", back_populates="user")
    User.job_matches = relationship("JobMatch", back_populates="user")
    User.ab_tests = relationship("ABTest", back_populates="user")
    User.analytics = relationship("UserAnalytics", back_populates="user") 