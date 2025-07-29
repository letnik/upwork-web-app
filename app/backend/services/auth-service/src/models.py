"""
Моделі бази даних для Auth Service
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.database.connection import Base


class User(Base):
    """Модель користувача"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("roles.id"), default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    security = relationship("UserSecurity", back_populates="user", uselist=False)
    role = relationship("Role", back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class UserSecurity(Base):
    """Модель безпеки користувача"""
    
    __tablename__ = "user_security"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    mfa_backup_codes = Column(JSON, nullable=True)  # Список резервних кодів
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_password_change = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    user = relationship("User", back_populates="security")
    
    def __repr__(self):
        return f"<UserSecurity(user_id={self.user_id}, mfa_enabled={self.mfa_enabled})>"


class Role(Base):
    """Модель ролей користувачів"""
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)  # Список дозволів
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Зв'язки
    users = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class Session(Base):
    """Модель сесій користувачів"""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4 або IPv6
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Session(user_id={self.user_id}, is_active={self.is_active})>"


class SecurityLog(Base):
    """Модель логів безпеки"""
    
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False)  # login, logout, mfa_enabled, etc.
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)  # Додаткові деталі події
    success = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SecurityLog(user_id={self.user_id}, event_type='{self.event_type}')>"


class OAuthConnection(Base):
    """Модель OAuth з'єднань"""
    
    __tablename__ = "oauth_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # upwork, google, github, etc.
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)  # Зашифрований токен
    refresh_token = Column(Text, nullable=True)  # Зашифрований токен
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scopes = Column(JSON, nullable=True)  # Список дозволів
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<OAuthConnection(user_id={self.user_id}, provider='{self.provider}')>"


# Функції для створення початкових даних
def create_default_roles():
    """Створення стандартних ролей"""
    return [
        {
            "id": 1,
            "name": "user",
            "description": "Звичайний користувач",
            "permissions": ["read_own_data", "write_own_data"]
        },
        {
            "id": 2,
            "name": "premium",
            "description": "Преміум користувач",
            "permissions": ["read_own_data", "write_own_data", "ai_features", "analytics"]
        },
        {
            "id": 3,
            "name": "admin",
            "description": "Адміністратор",
            "permissions": ["read_all", "write_all", "manage_users", "system_settings"]
        }
    ] 