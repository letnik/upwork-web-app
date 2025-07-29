# Архітектура бази даних

> **Архітектура бази даних для багатокористувацької системи з максимальною безпекою**

---

## Зміст

1. [Огляд архітектури](#огляд-архітектури)
2. [Схема бази даних](#схема-бази-даних)
3. [Моделі даних](#моделі-даних)
4. [Індекси та оптимізація](#індекси-та-оптимізація)
5. [Міграції](#міграції)
6. [Безпека](#безпека)

---

## Огляд архітектури

### Технології
- **PostgreSQL 15+** - основна база даних
- **Redis** - кешування та сесії
- **SQLAlchemy 2.0** - ORM
- **Alembic** - міграції
- **psycopg2** - драйвер PostgreSQL

### Принципи
- **Повна ізоляція даних** - кожен користувач бачить тільки свої дані
- **Шифрування чутливих даних** - всі токени та секрети зашифровані
- **Аудит всіх змін** - логування всіх операцій
- **Масштабованість** - підтримка необмеженої кількості користувачів

---

## Схема бази даних

### Основні таблиці
```sql
-- Користувачі
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    encrypted_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MFA налаштування
CREATE TABLE user_mfa (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    encrypted_totp_secret VARCHAR(255),
    totp_enabled BOOLEAN DEFAULT FALSE,
    backup_codes_hash TEXT[],
    backup_codes_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Upwork токени
CREATE TABLE user_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    encrypted_access_token TEXT NOT NULL,
    encrypted_refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вакансії
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    upwork_job_id VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    hourly_rate_min DECIMAL(10,2),
    hourly_rate_max DECIMAL(10,2),
    skills TEXT[],
    category VARCHAR(100),
    subcategory VARCHAR(100),
    country VARCHAR(100),
    client_info JSONB,
    job_type VARCHAR(50), -- 'fixed', 'hourly'
    experience_level VARCHAR(50), -- 'entry', 'intermediate', 'expert'
    duration VARCHAR(100),
    workload VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'archived', 'deleted'
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Пропозиції
CREATE TABLE proposals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    upwork_proposal_id VARCHAR(100) UNIQUE,
    cover_letter TEXT,
    bid_amount DECIMAL(10,2),
    bid_type VARCHAR(20), -- 'fixed', 'hourly'
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'submitted', 'accepted', 'rejected'
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Повідомлення
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    upwork_message_id VARCHAR(100) UNIQUE,
    sender_type VARCHAR(20), -- 'client', 'freelancer'
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI генерації
CREATE TABLE ai_generations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    generation_type VARCHAR(50), -- 'proposal', 'cover_letter', 'message'
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    model_used VARCHAR(50), -- 'gpt-4', 'claude', 'gemini'
    tokens_used INTEGER,
    cost DECIMAL(10,6),
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Аналітика
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2),
    metric_data JSONB,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Логи безпеки
CREATE TABLE security_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    event_type VARCHAR(100) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Аудит змін
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER,
    action VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Моделі даних

### SQLAlchemy моделі
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, DECIMAL, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    encrypted_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
# Relationships
    mfa_settings = relationship("UserMFA", back_populates="user", uselist=False)
    tokens = relationship("UserTokens", back_populates="user")
    jobs = relationship("Job", back_populates="user")
    proposals = relationship("Proposal", back_populates="user")
    messages = relationship("Message", back_populates="user")
    ai_generations = relationship("AIGeneration", back_populates="user")
    analytics = relationship("Analytics", back_populates="user")

class UserMFA(Base):
    __tablename__ = 'user_mfa'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    encrypted_totp_secret = Column(String(255))
    totp_enabled = Column(Boolean, default=False)
    backup_codes_hash = Column(JSON)
    backup_codes_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
# Relationships
    user = relationship("User", back_populates="mfa_settings")

class UserTokens(Base):
    __tablename__ = 'user_tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
# Relationships
    user = relationship("User", back_populates="tokens")

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    upwork_job_id = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    budget_min = Column(DECIMAL(10, 2))
    budget_max = Column(DECIMAL(10, 2))
    hourly_rate_min = Column(DECIMAL(10, 2))
    hourly_rate_max = Column(DECIMAL(10, 2))
    skills = Column(JSON)
    category = Column(String(100))
    subcategory = Column(String(100))
    country = Column(String(100))
    client_info = Column(JSON)
    job_type = Column(String(50))
    experience_level = Column(String(50))
    duration = Column(String(100))
    workload = Column(String(100))
    status = Column(String(50), default='active')
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
# Relationships
    user = relationship("User", back_populates="jobs")
    proposals = relationship("Proposal", back_populates="job")
    messages = relationship("Message", back_populates="job")
    ai_generations = relationship("AIGeneration", back_populates="job")

class Proposal(Base):
    __tablename__ = 'proposals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    upwork_proposal_id = Column(String(100), unique=True)
    cover_letter = Column(Text)
    bid_amount = Column(DECIMAL(10, 2))
    bid_type = Column(String(20))
    status = Column(String(50), default='draft')
    submitted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
# Relationships
    user = relationship("User", back_populates="proposals")
    job = relationship("Job", back_populates="proposals")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    upwork_message_id = Column(String(100), unique=True)
    sender_type = Column(String(20))
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
# Relationships
    user = relationship("User", back_populates="messages")
    job = relationship("Job", back_populates="messages")

class AIGeneration(Base):
    __tablename__ = 'ai_generations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    generation_type = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model_used = Column(String(50))
    tokens_used = Column(Integer)
    cost = Column(DECIMAL(10, 6))
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
# Relationships
    user = relationship("User", back_populates="ai_generations")
    job = relationship("Job", back_populates="ai_generations")

class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 2))
    metric_data = Column(JSON)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
# Relationships
    user = relationship("User", back_populates="analytics")

class SecurityLog(Base):
    __tablename__ = 'security_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    event_type = Column(String(100), nullable=False)
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(Text)
    success = Column(Boolean, nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer)
    action = Column(String(20), nullable=False)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## Індекси та оптимізація

### Основні індекси
```sql
-- Індекси для користувачів
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Індекси для вакансій
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_upwork_job_id ON jobs(upwork_job_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_budget_range ON jobs(budget_min, budget_max);
CREATE INDEX idx_jobs_skills ON jobs USING GIN(skills);

-- Індекси для пропозицій
CREATE INDEX idx_proposals_user_id ON proposals(user_id);
CREATE INDEX idx_proposals_job_id ON proposals(job_id);
CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_proposals_submitted_at ON proposals(submitted_at);

-- Індекси для повідомлень
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_job_id ON messages(job_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_is_read ON messages(is_read);

-- Індекси для AI генерацій
CREATE INDEX idx_ai_generations_user_id ON ai_generations(user_id);
CREATE INDEX idx_ai_generations_job_id ON ai_generations(job_id);
CREATE INDEX idx_ai_generations_type ON ai_generations(generation_type);
CREATE INDEX idx_ai_generations_created_at ON ai_generations(created_at);

-- Індекси для аналітики
CREATE INDEX idx_analytics_user_id ON analytics(user_id);
CREATE INDEX idx_analytics_metric_name ON analytics(metric_name);
CREATE INDEX idx_analytics_date ON analytics(date);
CREATE INDEX idx_analytics_user_metric_date ON analytics(user_id, metric_name, date);

-- Індекси для логів безпеки
CREATE INDEX idx_security_logs_user_id ON security_logs(user_id);
CREATE INDEX idx_security_logs_event_type ON security_logs(event_type);
CREATE INDEX idx_security_logs_created_at ON security_logs(created_at);
CREATE INDEX idx_security_logs_ip_address ON security_logs(ip_address);

-- Індекси для аудит логів
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_table_name ON audit_logs(table_name);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

### Партиціонування
```sql
-- Партиціонування логів за датою
CREATE TABLE security_logs_2024 PARTITION OF security_logs
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE security_logs_2025 PARTITION OF security_logs
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Партиціонування аналітики за датою
CREATE TABLE analytics_2024 PARTITION OF analytics
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE analytics_2025 PARTITION OF analytics
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### Оптимізація запитів
```sql
-- Матеріалізовані представлення для аналітики
CREATE MATERIALIZED VIEW user_job_stats AS
SELECT 
    user_id,
    COUNT(*) as total_jobs,
    COUNT(*) FILTER (WHERE status = 'active') as active_jobs,
    COUNT(*) FILTER (WHERE is_favorite = true) as favorite_jobs,
    AVG(budget_max - budget_min) as avg_budget_range,
    MAX(created_at) as last_job_date
FROM jobs
GROUP BY user_id;

-- Індекс для матеріалізованого представлення
CREATE INDEX idx_user_job_stats_user_id ON user_job_stats(user_id);

-- Автоматичне оновлення матеріалізованого представлення
CREATE OR REPLACE FUNCTION refresh_user_job_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY user_job_stats;
END;
$$ LANGUAGE plpgsql;
```

---

## Міграції

### Alembic конфігурація
```python
# alembic.ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql://user:password@localhost/upwork_app

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### Приклад міграції
```python
# migrations/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-12-19 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
# Створення таблиці користувачів
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('encrypted_password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
# Створення індексів
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])

def downgrade():
# Видалення індексів
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    
# Видалення таблиці
    op.drop_table('users')
```

---

## Безпека

### Шифрування даних
```python
class DatabaseEncryption:
    def __init__(self, encryption_manager):
        self.encryption_manager = encryption_manager
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Шифрує чутливі дані"""
        return self.encryption_manager.encrypt(data)
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Розшифровує чутливі дані"""
        return self.encryption_manager.decrypt(encrypted_data)
    
    def hash_password(self, password: str) -> str:
        """Хешує пароль"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Перевіряє пароль"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
```

### Row Level Security (RLS)
```sql
-- Включення RLS для всіх таблиць
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

-- Політики для користувачів
CREATE POLICY users_own_data ON users
    FOR ALL USING (auth.uid() = id);

-- Політики для вакансій
CREATE POLICY jobs_own_data ON jobs
    FOR ALL USING (auth.uid() = user_id);

-- Політики для пропозицій
CREATE POLICY proposals_own_data ON proposals
    FOR ALL USING (auth.uid() = user_id);

-- Політики для повідомлень
CREATE POLICY messages_own_data ON messages
    FOR ALL USING (auth.uid() = user_id);

-- Політики для AI генерацій
CREATE POLICY ai_generations_own_data ON ai_generations
    FOR ALL USING (auth.uid() = user_id);

-- Політики для аналітики
CREATE POLICY analytics_own_data ON analytics
    FOR ALL USING (auth.uid() = user_id);
```

### Аудит змін
```python
class AuditManager:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def log_change(self, user_id: int, table_name: str, record_id: int,
                   action: str, old_values: dict = None, new_values: dict = None,
                   ip_address: str = None):
        """Логує зміни в базі даних"""
        audit_log = AuditLog(
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        
        self.db.add(audit_log)
        self.db.commit()
    
    def get_audit_trail(self, table_name: str, record_id: int) -> List[AuditLog]:
        """Отримує історію змін для запису"""
        return self.db.query(AuditLog).filter(
            AuditLog.table_name == table_name,
            AuditLog.record_id == record_id
        ).order_by(AuditLog.created_at.desc()).all()
```

---

## Моніторинг

### Метрики бази даних
```python
class DatabaseMetrics:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_table_sizes(self) -> dict:
        """Отримує розміри таблиць"""
        query = """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
        """
        
        result = self.db.execute(query)
        return [dict(row) for row in result]
    
    def get_slow_queries(self) -> List[dict]:
        """Отримує повільні запити"""
        query = """
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            rows
        FROM pg_stat_statements 
        ORDER BY mean_time DESC 
        LIMIT 10;
        """
        
        result = self.db.execute(query)
        return [dict(row) for row in result]
    
    def get_connection_stats(self) -> dict:
        """Отримує статистику з'єднань"""
        query = """
        SELECT 
            count(*) as total_connections,
            count(*) FILTER (WHERE state = 'active') as active_connections,
            count(*) FILTER (WHERE state = 'idle') as idle_connections
        FROM pg_stat_activity;
        """
        
        result = self.db.execute(query)
        return dict(result.fetchone())
```

---

## Контрольні списки

### Реалізація
- [ ] Створення всіх таблиць
- [ ] Налаштування індексів
- [ ] Налаштування RLS
- [ ] Налаштування аудиту
- [ ] Налаштування міграцій
- [ ] Тестування продуктивності

### Безпека
- [ ] Шифрування чутливих даних
- [ ] Row Level Security
- [ ] Аудит всіх змін
- [ ] Регулярні backup
- [ ] Моніторинг доступу

### Оптимізація
- [ ] Аналіз повільних запитів
- [ ] Налаштування індексів
- [ ] Партиціонування великих таблиць
- [ ] Матеріалізовані представлення
- [ ] Кешування запитів

---

## Посилання

- [Системна архітектура](system_architecture.md)
- [Архітектура безпеки](security_architecture.md)
- [План міграцій](database/migrations_plan.md)
- [Стратегія оптимізації](database/optimization_strategy.md)

---

**Версія**: 1.0.0 