-- Міграція 001: Створення таблиць MVP компонентів
-- Дата: 2024-12-19

-- Профілі фільтрів
CREATE TABLE IF NOT EXISTS filter_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    keywords TEXT[], -- ключові слова для пошуку
    exclude_keywords TEXT[], -- мінус-слова
    ai_instructions TEXT, -- AI інструкції природною мовою
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    hourly_rate_min DECIMAL(10,2),
    hourly_rate_max DECIMAL(10,2),
    experience_level VARCHAR(50), -- 'entry', 'intermediate', 'expert'
    job_type VARCHAR(50), -- 'fixed', 'hourly'
    categories TEXT[], -- категорії роботи
    countries TEXT[], -- країни
    working_hours JSONB, -- години роботи
    timezone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_paused BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Шаблони відгуків
CREATE TABLE IF NOT EXISTS proposal_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50), -- 'general', 'web_dev', 'mobile', 'design', etc.
    content TEXT NOT NULL, -- шаблон відгуку
    variables JSONB, -- змінні в шаблоні: {client_name}, {project_type}, {budget}
    style VARCHAR(50) DEFAULT 'formal', -- 'formal', 'friendly', 'technical'
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2), -- відсоток успішності
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Чернетки відгуків
CREATE TABLE IF NOT EXISTS proposal_drafts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES proposal_templates(id) ON DELETE SET NULL,
    job_id VARCHAR(255), -- ID вакансії з Upwork
    job_title VARCHAR(255),
    job_description TEXT,
    client_name VARCHAR(255),
    budget VARCHAR(100),
    content TEXT NOT NULL, -- згенерований відгук
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'sent', 'rejected', 'accepted'
    ai_generated BOOLEAN DEFAULT TRUE,
    sent_at TIMESTAMP,
    response_received BOOLEAN DEFAULT FALSE,
    response_date TIMESTAMP,
    notes TEXT, -- нотатки користувача
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI інструкції
CREATE TABLE IF NOT EXISTS ai_instructions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    instruction_type VARCHAR(50) NOT NULL, -- 'filter', 'proposal', 'analysis'
    content TEXT NOT NULL, -- текст інструкції
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    effectiveness_score DECIMAL(5,2), -- оцінка ефективності
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Знайдені вакансії
CREATE TABLE IF NOT EXISTS job_matches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filter_profile_id INTEGER REFERENCES filter_profiles(id) ON DELETE SET NULL,
    job_id VARCHAR(255) NOT NULL, -- ID вакансії з Upwork
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT,
    client_name VARCHAR(255),
    client_rating DECIMAL(3,2),
    budget VARCHAR(100),
    hourly_rate DECIMAL(10,2),
    job_type VARCHAR(50), -- 'fixed', 'hourly'
    experience_level VARCHAR(50),
    skills TEXT[],
    country VARCHAR(100),
    posted_date TIMESTAMP,
    match_score DECIMAL(5,2), -- оцінка підходящості
    status VARCHAR(50) DEFAULT 'new', -- 'new', 'viewed', 'applied', 'rejected'
    viewed_at TIMESTAMP,
    applied_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- A/B тестування шаблонів
CREATE TABLE IF NOT EXISTS ab_tests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    template_a_id INTEGER NOT NULL REFERENCES proposal_templates(id) ON DELETE CASCADE,
    template_b_id INTEGER NOT NULL REFERENCES proposal_templates(id) ON DELETE CASCADE,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'stopped'
    min_duration_days INTEGER DEFAULT 7, -- мінімальна тривалість тесту
    template_a_sent INTEGER DEFAULT 0,
    template_b_sent INTEGER DEFAULT 0,
    template_a_responses INTEGER DEFAULT 0,
    template_b_responses INTEGER DEFAULT 0,
    template_a_hired INTEGER DEFAULT 0,
    template_b_hired INTEGER DEFAULT 0,
    winner_template_id INTEGER REFERENCES proposal_templates(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Аналітика користувача
CREATE TABLE IF NOT EXISTS user_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    jobs_found INTEGER DEFAULT 0,
    proposals_sent INTEGER DEFAULT 0,
    responses_received INTEGER DEFAULT 0,
    interviews_scheduled INTEGER DEFAULT 0,
    jobs_won INTEGER DEFAULT 0,
    total_earned DECIMAL(10,2) DEFAULT 0,
    active_profiles INTEGER DEFAULT 0,
    active_templates INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Індекси для оптимізації
CREATE INDEX IF NOT EXISTS idx_filter_profiles_user_id ON filter_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_filter_profiles_active ON filter_profiles(is_active);
CREATE INDEX IF NOT EXISTS idx_proposal_templates_user_id ON proposal_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_proposal_templates_active ON proposal_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_proposal_drafts_user_id ON proposal_drafts(user_id);
CREATE INDEX IF NOT EXISTS idx_proposal_drafts_status ON proposal_drafts(status);
CREATE INDEX IF NOT EXISTS idx_proposal_drafts_created_at ON proposal_drafts(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_instructions_user_id ON ai_instructions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_instructions_type ON ai_instructions(instruction_type);
CREATE INDEX IF NOT EXISTS idx_job_matches_user_id ON job_matches(user_id);
CREATE INDEX IF NOT EXISTS idx_job_matches_status ON job_matches(status);
CREATE INDEX IF NOT EXISTS idx_job_matches_job_id ON job_matches(job_id);
CREATE INDEX IF NOT EXISTS idx_ab_tests_user_id ON ab_tests(user_id);
CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON ab_tests(status);
CREATE INDEX IF NOT EXISTS idx_user_analytics_user_date ON user_analytics(user_id, date);

-- Обмеження для MVP
ALTER TABLE filter_profiles ADD CONSTRAINT check_max_profiles_per_user 
    CHECK (user_id IN (
        SELECT user_id FROM filter_profiles 
        GROUP BY user_id 
        HAVING COUNT(*) <= 10
    ));

ALTER TABLE proposal_templates ADD CONSTRAINT check_max_templates_per_user 
    CHECK (user_id IN (
        SELECT user_id FROM proposal_templates 
        GROUP BY user_id 
        HAVING COUNT(*) <= 10
    ));

-- Тригер для оновлення updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Застосовуємо тригер до всіх таблиць
CREATE TRIGGER update_filter_profiles_updated_at BEFORE UPDATE ON filter_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_proposal_templates_updated_at BEFORE UPDATE ON proposal_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_proposal_drafts_updated_at BEFORE UPDATE ON proposal_drafts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_instructions_updated_at BEFORE UPDATE ON ai_instructions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_job_matches_updated_at BEFORE UPDATE ON job_matches FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ab_tests_updated_at BEFORE UPDATE ON ab_tests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_analytics_updated_at BEFORE UPDATE ON user_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 