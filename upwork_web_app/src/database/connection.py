"""
Підключення до бази даних
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from ..config.settings import settings
from .models import Base


class DatabaseManager:
    """Менеджер підключення до бази даних"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Налаштування двигуна бази даних"""
        try:
            # Створюємо двигун з пулом з'єднань
            self.engine = create_engine(
                settings.database_url,
                poolclass=StaticPool,
                pool_pre_ping=True,
                echo=settings.debug
            )
            
            # Створюємо фабрику сесій
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
        except Exception as e:
            print(f"Помилка підключення до бази даних: {e}")
            raise
    
    def create_tables(self):
        """Створення всіх таблиць"""
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Таблиці бази даних створені успішно")
        except Exception as e:
            print(f"❌ Помилка створення таблиць: {e}")
            raise
    
    def drop_tables(self):
        """Видалення всіх таблиць"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            print("✅ Таблиці бази даних видалені успішно")
        except Exception as e:
            print(f"❌ Помилка видалення таблиць: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """Контекстний менеджер для отримання сесії БД"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Тестування підключення до бази даних"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            print("✅ Підключення до бази даних успішне")
            return True
        except Exception as e:
            print(f"❌ Помилка підключення до бази даних: {e}")
            return False


# Глобальний екземпляр менеджера БД
db_manager = DatabaseManager()


def get_db() -> Session:
    """Функція для отримання сесії БД (для FastAPI dependency injection)"""
    with db_manager.get_session() as session:
        yield session 