# Схеми бази даних

## Огляд

Цей документ містить детальні схеми всіх таблиць бази даних проекту Upwork AI Assistant.

## Основні таблиці

### Users (Користувачі)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP,
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    profile_completed BOOLEAN DEFAULT false
);
```

### AI Settings (Налаштування AI)
```sql
CREATE TABLE ai_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    ai_disclosure_enabled BOOLEAN DEFAULT true,
    ai_disclosure_position VARCHAR(10) DEFAULT 'end' CHECK (ai_disclosure_position IN ('start', 'end', 'none')),
    ai_disclosure_template VARCHAR(20) DEFAULT 'default' CHECK (ai_disclosure_template IN ('default', 'minimal', 'detailed', 'custom')),
    ai_disclosure_custom_text TEXT,
    auto_add_disclosure BOOLEAN DEFAULT true,
    auto_save_drafts BOOLEAN DEFAULT true,
    save_interval INTEGER DEFAULT 30 CHECK (save_interval >= 10 AND save_interval <= 300),
    draft_retention_days INTEGER DEFAULT 7 CHECK (draft_retention_days >= 1 AND draft_retention_days <= 90),
    min_proposal_length INTEGER DEFAULT 100 CHECK (min_proposal_length >= 50),
    max_proposal_length INTEGER DEFAULT 2000 CHECK (max_proposal_length <= 5000),
    check_spam_content BOOLEAN DEFAULT true,
    require_review_before_sending BOOLEAN DEFAULT true,
    preferred_ai_model VARCHAR(50) DEFAULT 'gpt-4',
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);
```

### Proposal Drafts (Чернетки відгуків)
```sql
CREATE TABLE proposal_drafts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(50) NOT NULL,
    job_title VARCHAR(255),
    content TEXT NOT NULL,
    ai_generated_content TEXT,
    user_edited_content TEXT,
    ai_disclosure_included BOOLEAN DEFAULT false,
    ai_disclosure_text TEXT,
    validation_status VARCHAR(20) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'valid', 'invalid', 'warning')),
    validation_errors JSONB,
    word_count INTEGER DEFAULT 0,
    character_count INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10,4) DEFAULT 0,
    ai_model_used VARCHAR(50),
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_edited_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '30 days')
);

-- Індекси для швидкого пошуку
CREATE INDEX idx_proposal_drafts_user_id ON proposal_drafts(user_id);
CREATE INDEX idx_proposal_drafts_job_id ON proposal_drafts(job_id);
CREATE INDEX idx_proposal_drafts_status ON proposal_drafts(validation_status);
CREATE INDEX idx_proposal_drafts_created_at ON proposal_drafts(created_at);
```

### Proposal Draft History (Історія змін чернеток)
```sql
CREATE TABLE proposal_draft_history (
    id SERIAL PRIMARY KEY,
    draft_id INTEGER REFERENCES proposal_drafts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_snapshot TEXT NOT NULL,
    change_type VARCHAR(20) NOT NULL CHECK (change_type IN ('created', 'edited', 'ai_generated', 'validated', 'sent')),
    change_description TEXT,
    word_count INTEGER DEFAULT 0,
    character_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_draft_history_draft_id ON proposal_draft_history(draft_id);
CREATE INDEX idx_draft_history_created_at ON proposal_draft_history(created_at);
```

### Jobs (Вакансії)
```sql
CREATE TABLE jobs (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    budget_type VARCHAR(20) CHECK (budget_type IN ('hourly', 'fixed')),
    client_id VARCHAR(50),
    client_name VARCHAR(255),
    client_rating DECIMAL(3,2),
    client_reviews_count INTEGER DEFAULT 0,
    client_total_spent DECIMAL(12,2),
    client_location VARCHAR(100),
    skills TEXT[], -- PostgreSQL array
    category VARCHAR(100),
    subcategory VARCHAR(100),
    experience_level VARCHAR(20),
    project_length VARCHAR(50),
    hours_per_week VARCHAR(50),
    proposals_count INTEGER DEFAULT 0,
    client_hires INTEGER DEFAULT 0,
    payment_verified BOOLEAN DEFAULT false,
    posted_time TIMESTAMP,
    url VARCHAR(500),
    scraped_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_title ON jobs USING gin(to_tsvector('english', title));
CREATE INDEX idx_jobs_skills ON jobs USING gin(skills);
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_jobs_budget_type ON jobs(budget_type);
CREATE INDEX idx_jobs_posted_time ON jobs(posted_time);
```

### Applications (Відгуки)
```sql
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(50) REFERENCES jobs(id),
    upwork_proposal_id VARCHAR(50),
    draft_id INTEGER REFERENCES proposal_drafts(id),
    content TEXT NOT NULL,
    bid_amount DECIMAL(10,2),
    estimated_duration VARCHAR(100),
    cover_letter TEXT,
    attachments JSONB,
    ai_disclosure_included BOOLEAN DEFAULT false,
    ai_disclosure_text TEXT,
    status VARCHAR(20) DEFAULT 'submitted' CHECK (status IN ('draft', 'submitted', 'viewed', 'responded', 'hired', 'rejected')),
    submitted_at TIMESTAMP DEFAULT NOW(),
    viewed_at TIMESTAMP,
    responded_at TIMESTAMP,
    hired_at TIMESTAMP,
    rejected_at TIMESTAMP,
    response_time_hours INTEGER,
    client_feedback TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_submitted_at ON applications(submitted_at);
```

### Messages (Повідомлення)
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    upwork_message_id VARCHAR(50),
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('client', 'freelancer')),
    content TEXT NOT NULL,
    ai_generated BOOLEAN DEFAULT false,
    ai_disclosure_included BOOLEAN DEFAULT false,
    attachments JSONB,
    sent_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_application_id ON messages(application_id);
CREATE INDEX idx_messages_sent_at ON messages(sent_at);
```

### Proposal Templates (Шаблони відгуків)
```sql
CREATE TABLE proposal_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    template_type VARCHAR(50) DEFAULT 'general',
    category VARCHAR(100),
    tags TEXT[],
    is_default BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_templates_user_id ON proposal_templates(user_id);
CREATE INDEX idx_templates_type ON proposal_templates(template_type);
CREATE INDEX idx_templates_category ON proposal_templates(category);
```

### AI Activity Log (Лог активності AI)
```sql
CREATE TABLE ai_activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    details JSONB,
    ai_model VARCHAR(50),
    tokens_used INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10,4) DEFAULT 0,
    processing_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ai_activity_user_id ON ai_activity_log(user_id);
CREATE INDEX idx_ai_activity_action ON ai_activity_log(action);
CREATE INDEX idx_ai_activity_created_at ON ai_activity_log(created_at);
```

### User Profiles (Профілі користувачів)
```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    overview TEXT,
    skills TEXT[],
    experience_years INTEGER,
    hourly_rate DECIMAL(10,2),
    availability VARCHAR(50),
    timezone VARCHAR(50),
    languages TEXT[],
    portfolio_urls JSONB,
    certifications JSONB,
    education JSONB,
    work_history JSONB,
    profile_completion_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE INDEX idx_user_profiles_skills ON user_profiles USING gin(skills);
CREATE INDEX idx_user_profiles_hourly_rate ON user_profiles(hourly_rate);
```

### Analytics Data (Дані аналітики)
```sql
CREATE TABLE analytics_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_data JSONB,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analytics_user_id ON analytics_data(user_id);
CREATE INDEX idx_analytics_metric_name ON analytics_data(metric_name);
CREATE INDEX idx_analytics_date ON analytics_data(date);
```

## Зв'язки та обмеження

### Foreign Key Constraints
```sql
-- Додаткові обмеження для цілісності даних
ALTER TABLE ai_settings 
ADD CONSTRAINT fk_ai_settings_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE proposal_drafts 
ADD CONSTRAINT fk_proposal_drafts_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE applications 
ADD CONSTRAINT fk_applications_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE applications 
ADD CONSTRAINT fk_applications_job 
FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL;
```

### Check Constraints
```sql
-- Додаткові перевірки для валідації даних
ALTER TABLE ai_settings 
ADD CONSTRAINT check_save_interval 
CHECK (save_interval >= 10 AND save_interval <= 300);

ALTER TABLE proposal_drafts 
ADD CONSTRAINT check_word_count 
CHECK (word_count >= 0);

ALTER TABLE applications 
ADD CONSTRAINT check_bid_amount 
CHECK (bid_amount > 0);
```

## Індекси для продуктивності

### Складні індекси
```sql
-- Складений індекс для пошуку чернеток користувача
CREATE INDEX idx_drafts_user_status ON proposal_drafts(user_id, validation_status);

-- Складений індекс для аналітики відгуків
CREATE INDEX idx_applications_user_status_date ON applications(user_id, status, submitted_at);

-- Складений індекс для AI активності
CREATE INDEX idx_ai_activity_user_action_date ON ai_activity_log(user_id, action, created_at);

-- Повнотекстовий пошук по вакансіях
CREATE INDEX idx_jobs_fulltext ON jobs USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));
```

## Тригери для автоматизації

### Автоматичне оновлення часу
```sql
-- Тригер для автоматичного оновлення updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Застосування тригера до таблиць
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_settings_updated_at BEFORE UPDATE ON ai_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_proposal_drafts_updated_at BEFORE UPDATE ON proposal_drafts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Автоматичний підрахунок слів
```sql
-- Функція для підрахунку слів
CREATE OR REPLACE FUNCTION count_words(text_content TEXT)
RETURNS INTEGER AS $$
BEGIN
    RETURN array_length(regexp_split_to_array(trim(text_content), '\s+'), 1);
END;
$$ LANGUAGE plpgsql;

-- Тригер для автоматичного підрахунку слів
CREATE OR REPLACE FUNCTION update_word_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.word_count = count_words(NEW.content);
    NEW.character_count = length(NEW.content);
    NEW.last_edited_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_proposal_draft_word_count 
BEFORE INSERT OR UPDATE ON proposal_drafts 
FOR EACH ROW EXECUTE FUNCTION update_word_count();
```

## Міграції

### Створення таблиць
```sql
-- Міграція для створення AI налаштувань
CREATE TABLE IF NOT EXISTS ai_settings (
    -- ... (код вище)
);

-- Міграція для створення чернеток
CREATE TABLE IF NOT EXISTS proposal_drafts (
    -- ... (код вище)
);

-- Міграція для додавання AI полів до існуючих таблиць
ALTER TABLE applications 
ADD COLUMN IF NOT EXISTS ai_disclosure_included BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS ai_disclosure_text TEXT;
```

### Оновлення існуючих таблиць
```sql
-- Додавання нових полів до існуючих таблиць
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS profile_completed BOOLEAN DEFAULT false;

ALTER TABLE applications 
ADD COLUMN IF NOT EXISTS draft_id INTEGER REFERENCES proposal_drafts(id);

-- Додавання нових індексів
CREATE INDEX IF NOT EXISTS idx_applications_draft_id ON applications(draft_id);
```

## Резервне копіювання та відновлення

### Створення резервних копій
```sql
-- Створення резервної копії всієї бази даних
pg_dump -h localhost -U username -d upwork_ai_assistant > backup_$(date +%Y%m%d_%H%M%S).sql

-- Створення резервної копії тільки схеми
pg_dump -h localhost -U username -d upwork_ai_assistant --schema-only > schema_backup.sql

-- Створення резервної копії тільки даних
pg_dump -h localhost -U username -d upwork_ai_assistant --data-only > data_backup.sql
```

### Відновлення з резервної копії
```sql
-- Відновлення з повної резервної копії
psql -h localhost -U username -d upwork_ai_assistant < backup_20241219_180000.sql

-- Відновлення тільки схеми
psql -h localhost -U username -d upwork_ai_assistant < schema_backup.sql
```

## Моніторинг та оптимізація

### Запити для моніторингу
```sql
-- Розмір таблиць
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Найбільш активні користувачі AI
SELECT 
    u.email,
    COUNT(*) as ai_actions,
    SUM(aal.tokens_used) as total_tokens,
    SUM(aal.estimated_cost) as total_cost
FROM ai_activity_log aal
JOIN users u ON aal.user_id = u.id
WHERE aal.created_at >= NOW() - INTERVAL '30 days'
GROUP BY u.id, u.email
ORDER BY ai_actions DESC
LIMIT 10;

-- Статистика чернеток
SELECT 
    validation_status,
    COUNT(*) as count,
    AVG(word_count) as avg_words,
    AVG(character_count) as avg_chars
FROM proposal_drafts
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY validation_status;
``` 