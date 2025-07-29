# Схеми бази даних

> **Детальні схеми таблиць, індекси та міграції для Upwork Web App**

---

## Зміст

1. [Призначення](#-призначення)
2. [Архітектура бази даних](#-архітектура-бази-даних)
3. [Основні таблиці](#основні-таблиці)
4. [Індекси для оптимізації](#індекси-для-оптимізації)
5. [Шифрування даних](#шифрування-даних)
6. [Міграції](#міграції)
7. [Backup та відновлення](#backup-та-відновлення)

---

## Призначення

Схеми бази даних визначають:
- Структуру таблиць PostgreSQL
- Індекси для оптимізації
- Зв'язки між таблицями
- Міграції для версіонування
- Шифрування чутливих даних

---

## Архітектура бази даних

### Основні таблиці

```sql
-- Користувачі
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Профілі Upwork
CREATE TABLE upwork_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    upwork_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100),
    title VARCHAR(255),
    hourly_rate DECIMAL(10,2),
    total_earnings DECIMAL(12,2),
    total_hours INTEGER,
    success_rate DECIMAL(5,2),
    skills TEXT[],
    location VARCHAR(255),
    member_since DATE,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Вакансії
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upwork_job_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    budget_type VARCHAR(20), -- 'fixed', 'hourly'
    client_id VARCHAR(50),
    client_name VARCHAR(255),
    client_rating DECIMAL(3,2),
    client_total_spent DECIMAL(12,2),
    skills TEXT[],
    category VARCHAR(100),
    subcategory VARCHAR(100),
    posted_date TIMESTAMP WITH TIME ZONE,
    proposals_count INTEGER DEFAULT 0,
    interview_count INTEGER DEFAULT 0,
    hired_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Пропозиції
CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    upwork_proposal_id VARCHAR(50) UNIQUE,
    cover_letter TEXT,
    bid_amount DECIMAL(10,2),
    delivery_time INTEGER, -- дні
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'submitted', 'viewed', 'interviewed', 'hired', 'rejected'
    submitted_at TIMESTAMP WITH TIME ZONE,
    viewed_at TIMESTAMP WITH TIME ZONE,
    interviewed_at TIMESTAMP WITH TIME ZONE,
    hired_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Контракти
CREATE TABLE contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    upwork_contract_id VARCHAR(50) UNIQUE NOT NULL,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    client_id VARCHAR(50),
    client_name VARCHAR(255),
    title VARCHAR(500),
    description TEXT,
    hourly_rate DECIMAL(10,2),
    total_hours INTEGER,
    total_amount DECIMAL(12,2),
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'closed'
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Платежі
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    upwork_payment_id VARCHAR(50) UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    hours_worked DECIMAL(5,2),
    hourly_rate DECIMAL(10,2),
    payment_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Безпека та аутентифікація

```sql
-- JWT токени
CREATE TABLE jwt_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    token_type VARCHAR(20) NOT NULL, -- 'access', 'refresh'
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- MFA налаштування
CREATE TABLE mfa_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    method VARCHAR(20) NOT NULL, -- 'totp', 'sms', 'email'
    secret_key VARCHAR(255), -- для TOTP
    phone_number VARCHAR(20), -- для SMS
    backup_codes TEXT[], -- резервні коди
    is_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Сесії
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Логи безпеки
CREATE TABLE security_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL, -- 'login', 'logout', 'failed_login', 'password_change'
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    severity VARCHAR(10) DEFAULT 'info', -- 'info', 'warning', 'error', 'critical'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Аналітика та метрики

```sql
-- Метрики користувачів
CREATE TABLE user_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    proposals_sent INTEGER DEFAULT 0,
    proposals_viewed INTEGER DEFAULT 0,
    proposals_interviewed INTEGER DEFAULT 0,
    proposals_hired INTEGER DEFAULT 0,
    total_earnings DECIMAL(12,2) DEFAULT 0,
    total_hours DECIMAL(8,2) DEFAULT 0,
    response_rate DECIMAL(5,2) DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Аналітика вакансій
CREATE TABLE job_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    skill_match DECIMAL(5,2),
    salary_estimate_min DECIMAL(10,2),
    salary_estimate_max DECIMAL(10,2),
    success_probability DECIMAL(5,2),
    competition_level VARCHAR(20), -- 'low', 'medium', 'high'
    recommendations TEXT[],
    risk_factors TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI аналітика
CREATE TABLE ai_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50), -- 'job_analysis', 'proposal_generation', 'optimization'
    input_data JSONB,
    output_data JSONB,
    confidence_score DECIMAL(5,2),
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Індекси для оптимізації

### Основні індекси

```sql
-- Індекси для користувачів
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Індекси для Upwork профілів
CREATE INDEX idx_upwork_profiles_user_id ON upwork_profiles(user_id);
CREATE INDEX idx_upwork_profiles_upwork_id ON upwork_profiles(upwork_id);
CREATE INDEX idx_upwork_profiles_last_sync ON upwork_profiles(last_sync_at);

-- Індекси для вакансій
CREATE INDEX idx_jobs_upwork_job_id ON jobs(upwork_job_id);
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_jobs_budget_type ON jobs(budget_type);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX idx_jobs_is_active ON jobs(is_active);
CREATE INDEX idx_jobs_skills ON jobs USING GIN(skills);

-- Індекси для пропозицій
CREATE INDEX idx_proposals_user_id ON proposals(user_id);
CREATE INDEX idx_proposals_job_id ON proposals(job_id);
CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_proposals_submitted_at ON proposals(submitted_at);
CREATE INDEX idx_proposals_upwork_proposal_id ON proposals(upwork_proposal_id);

-- Індекси для контрактів
CREATE INDEX idx_contracts_user_id ON contracts(user_id);
CREATE INDEX idx_contracts_job_id ON contracts(job_id);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contracts_upwork_contract_id ON contracts(upwork_contract_id);

-- Індекси для платежів
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_contract_id ON payments(contract_id);
CREATE INDEX idx_payments_payment_date ON payments(payment_date);
CREATE INDEX idx_payments_status ON payments(status);

-- Індекси для безпеки
CREATE INDEX idx_jwt_tokens_user_id ON jwt_tokens(user_id);
CREATE INDEX idx_jwt_tokens_expires_at ON jwt_tokens(expires_at);
CREATE INDEX idx_jwt_tokens_is_revoked ON jwt_tokens(is_revoked);

CREATE INDEX idx_security_logs_user_id ON security_logs(user_id);
CREATE INDEX idx_security_logs_event_type ON security_logs(event_type);
CREATE INDEX idx_security_logs_created_at ON security_logs(created_at);
CREATE INDEX idx_security_logs_severity ON security_logs(severity);

-- Індекси для аналітики
CREATE INDEX idx_user_metrics_user_id_date ON user_metrics(user_id, date);
CREATE INDEX idx_job_analytics_job_id ON job_analytics(job_id);
CREATE INDEX idx_job_analytics_user_id ON job_analytics(user_id);
CREATE INDEX idx_ai_analysis_user_id ON ai_analysis(user_id);
CREATE INDEX idx_ai_analysis_created_at ON ai_analysis(created_at);
```

### Складні індекси

```sql
-- Складний індекс для пошуку вакансій
CREATE INDEX idx_jobs_search ON jobs USING GIN(
    to_tsvector('english', title || ' ' || COALESCE(description, ''))
);

-- Складний індекс для метрик користувачів
CREATE INDEX idx_user_metrics_period ON user_metrics(user_id, date DESC);

-- Складний індекс для аналітики безпеки
CREATE INDEX idx_security_logs_analysis ON security_logs(user_id, event_type, created_at DESC);
```

---

## Шифрування даних

### Чутливі дані

```sql
-- Розширення для шифрування
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Функція для шифрування
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(encrypt(data::bytea, key::bytea, 'aes'), 'base64');
END;
$$ LANGUAGE plpgsql;

-- Функція для дешифрування
CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data TEXT, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN convert_from(decrypt(decode(encrypted_data, 'base64'), key::bytea, 'aes'), 'utf8');
END;
$$ LANGUAGE plpgsql;

-- Тригер для автоматичного шифрування
CREATE OR REPLACE FUNCTION encrypt_user_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Шифрування чутливих даних
    NEW.email = encrypt_sensitive_data(NEW.email, current_setting('app.encryption_key'));
    NEW.phone_number = encrypt_sensitive_data(NEW.phone_number, current_setting('app.encryption_key'));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_encrypt_user_data
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION encrypt_user_data();
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
Create Date: 2024-12-19 17:15:00.000000

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
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
# Створення індексів
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)

def downgrade():
# Видалення індексів
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    
# Видалення таблиці
    op.drop_table('users')
```

---

## Backup та відновлення

### Backup стратегія

```bash
#!/bin/bash
# scripts/backup_database.sh

# Конфігурація
DB_NAME="upwork_app"
DB_USER="postgres"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Створення backup
echo "Creating database backup..."
pg_dump -U $DB_USER -h localhost -d $DB_NAME \
    --format=custom \
    --compress=9 \
    --file="$BACKUP_DIR/backup_$DATE.dump"

# Видалення старих backup (старше 30 днів)
find $BACKUP_DIR -name "backup_*.dump" -mtime +30 -delete

echo "Backup completed: backup_$DATE.dump"
```

### Відновлення

```bash
#!/bin/bash
# scripts/restore_database.sh

# Конфігурація
DB_NAME="upwork_app"
DB_USER="postgres"
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Зупинка додатку
echo "Stopping application..."
docker-compose stop app

# Відновлення бази даних
echo "Restoring database from $BACKUP_FILE..."
pg_restore -U $DB_USER -h localhost -d $DB_NAME \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    "$BACKUP_FILE"

# Запуск додатку
echo "Starting application..."
docker-compose start app

echo "Database restore completed"
```

---

## Моніторинг продуктивності

### Запити для моніторингу

```sql
-- Медленні запити
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Використання індексів
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;

-- Розмір таблиць
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Активні з'єднання
SELECT 
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query_start
FROM pg_stat_activity 
WHERE state = 'active';
```

---

**Версія**: 1.0.0 