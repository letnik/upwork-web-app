"""
Моделі бази даних для Auth Service
Покращена версія з шифруванням токенів (SECURITY-007)
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
    """Модель безпеки користувача з шифруванням"""
    
    __tablename__ = "user_security"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(Text, nullable=True)  # Зашифрований секрет
    mfa_backup_codes = Column(JSON, nullable=True)  # Список резервних кодів
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_password_change = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(Text, nullable=True)  # Зашифрований токен
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    email_verification_token = Column(Text, nullable=True)  # Зашифрований токен
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
    """Модель сесій користувачів з шифруванням токенів"""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(Text, unique=True, nullable=False)  # Зашифрований токен
    refresh_token = Column(Text, unique=True, nullable=False)  # Зашифрований токен
    ip_address = Column(String(45), nullable=True)  # IPv4 або IPv6
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"


class SecurityLog(Base):
    """Модель логів безпеки з розширеними полями"""
    
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False)  # login, logout, mfa_enabled, etc.
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)  # Додаткові деталі події
    success = Column(Boolean, default=True)
    level = Column(String(20), default="info")  # info, warning, error, critical
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Індекси для швидкого пошуку
    __table_args__ = (
        Index('idx_security_logs_event_type', 'event_type'),
        Index('idx_security_logs_user_id', 'user_id'),
        Index('idx_security_logs_ip_address', 'ip_address'),
        Index('idx_security_logs_created_at', 'created_at'),
        Index('idx_security_logs_level', 'level'),
    )
    
    def __repr__(self):
        return f"<SecurityLog(id={self.id}, event_type='{self.event_type}', success={self.success})>"


class OAuthConnection(Base):
    """Модель OAuth з'єднань з шифруванням токенів"""
    
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
        return f"<OAuthConnection(id={self.id}, provider='{self.provider}', user_id={self.user_id})>"


class PasswordResetToken(Base):
    """Модель токенів скидання паролю з шифруванням"""
    
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hashed_token = Column(String(255), nullable=False)  # Хеш токена для швидкого пошуку
    encrypted_token = Column(Text, nullable=False)  # Зашифрований токен
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, used={self.used})>"


class EncryptedData(Base):
    """Модель для зберігання зашифрованих даних"""
    
    __tablename__ = "encrypted_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    data_type = Column(String(50), nullable=False)  # api_key, personal_info, etc.
    encrypted_data = Column(Text, nullable=False)  # Зашифровані дані
    metadata = Column(JSON, nullable=True)  # Додаткові метадані
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<EncryptedData(id={self.id}, data_type='{self.data_type}', user_id={self.user_id})>"


def create_default_roles():
    """Створення стандартних ролей"""
    from shared.database.connection import get_db
    
    db = next(get_db())
    
    # Перевіряємо чи існують ролі
    existing_roles = db.query(Role).all()
    if existing_roles:
        return
    
    # Створюємо стандартні ролі
    roles = [
        Role(
            name="user",
            description="Звичайний користувач",
            permissions=["read_profile", "edit_profile", "use_ai_features"],
            is_active=True
        ),
        Role(
            name="premium",
            description="Преміум користувач",
            permissions=["read_profile", "edit_profile", "use_ai_features", "advanced_analytics", "priority_support"],
            is_active=True
        ),
        Role(
            name="admin",
            description="Адміністратор",
            permissions=["*"],  # Всі дозволи
            is_active=True
        )
    ]
    
    for role in roles:
        db.add(role)
    
    db.commit()
    db.close() 