"""
Спільне підключення до бази даних для всіх мікросервісів
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import redis
from ..config.settings import settings


class DatabaseManager:
    """Менеджер підключення до бази даних"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.redis_client = None
        self._setup_database()
        self._setup_redis()
    
    def _setup_database(self):
        """Налаштування підключення до PostgreSQL"""
        try:
            # Створюємо engine
            self.engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=10,
                max_overflow=20,
                echo=settings.DEBUG
            )
            
            # Створюємо SessionLocal
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
        except Exception as e:
            print(f"Помилка підключення до БД: {e}")
            # Fallback для тестування
            self.engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.DEBUG
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
    
    def _setup_redis(self):
        """Налаштування підключення до Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Тестуємо підключення
            self.redis_client.ping()
        except Exception as e:
            print(f"Помилка підключення до Redis: {e}")
            self.redis_client = None
    
    def get_db(self) -> Generator[Session, None, None]:
        """Отримання сесії бази даних"""
        if not self.SessionLocal:
            raise Exception("База даних не ініціалізована")
        
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def get_redis(self):
        """Отримання клієнта Redis"""
        if not self.redis_client:
            raise Exception("Redis не ініціалізований")
        return self.redis_client
    
    def test_connection(self) -> bool:
        """Тестування підключення до БД"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False
    
    def test_redis_connection(self) -> bool:
        """Тестування підключення до Redis"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
            return False
        except Exception as e:
            print(f"Redis connection test failed: {e}")
            return False
    
    def test_redis_connection(self) -> bool:
        """Тестування підключення до Redis"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
            return False
        except Exception:
            return False
    
    def create_tables(self):
        """Створення таблиць"""
        from .models import Base
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Видалення таблиць"""
        from .models import Base
        Base.metadata.drop_all(bind=self.engine)


# Глобальний екземпляр менеджера БД
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """Dependency для FastAPI"""
    return db_manager.get_db()


def get_redis():
    """Dependency для FastAPI Redis"""
    return db_manager.get_redis()


# Базовий клас для моделей
Base = declarative_base() 