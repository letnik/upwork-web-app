# План реалізації AI модуля

> **Детальний план реалізації штучного інтелекту для генерації відгуків, аналізу вакансій та розумної фільтрації**

---

## Зміст

1. [Огляд реалізації](#огляд-реалізації)
2. [Етапи розробки](#етапи-розробки)
3. [Детальні таски](#детальні-таски)
4. [Інструкції виконання](#інструкції-виконання)
5. [Критерії приймання](#критерії-приймання)
6. [Тестування](#тестування)
7. [Розгортання](#розгортання)

---

## Огляд реалізації

### **Мета**
Створити повнофункціональний AI модуль для автоматизації процесів створення відгуків, аналізу вакансій та розумної фільтрації на Upwork.

### **Ключові компоненти**
- **ProposalGenerator**: Генерація персоналізованих відгуків
- **JobAnalyzer**: Аналіз вакансій та оцінка відповідності
- **SmartFilter**: Розумна фільтрація та ранжування
- **CostManager**: Управління витратами на AI API
- **CacheManager**: Кешування відповідей для оптимізації

### **Технічний стек**
- **LLM**: OpenAI GPT-4 (основний), Claude (fallback)
- **ML**: Scikit-learn для класифікації
- **NLP**: spaCy, NLTK для обробки тексту
- **Кешування**: Redis для кешування відповідей
- **Моніторинг**: Prometheus + Grafana

---

## Етапи розробки

### **Етап 1: Базова архітектура (5 днів)**
- Створення базової структури модуля
- Налаштування інтеграції з OpenAI API
- Створення базових класів та інтерфейсів
- Налаштування кешування

### **Етап 2: Core функціональність (8 днів)**
- Реалізація ProposalGenerator
- Реалізація JobAnalyzer
- Створення prompt templates
- Налаштування fallback механізмів

### **Етап 3: Розширена функціональність (6 днів)**
- Реалізація SmartFilter
- Додавання ML моделей
- Реалізація A/B тестування
- Оптимізація продуктивності

### **Етап 4: Інтеграція та тестування (4 дні)**
- Інтеграція з іншими модулями
- Комплексне тестування
- Оптимізація та налагодження
- Документація API

---

## Детальні таски

### **AI-001: Створити базову структуру AI модуля**

#### Опис
Створити основні класи та інтерфейси для AI модуля з базовою архітектурою.

#### Критерії приймання
- [ ] Створено базову структуру папок
- [ ] Створено абстрактні класи для AI сервісів
- [ ] Налаштовано конфігурацію модуля
- [ ] Створено базові exception класи
- [ ] Налаштовано логування

#### Інструкції виконання
1. **Створити структуру папок**:
   ```bash
   mkdir -p src/ai/{services,models,utils,templates}
   mkdir -p tests/ai/{unit,integration}
   mkdir -p config/ai
   ```

2. **Створити базові класи**:
   ```python
# src/ai/base.py
   from abc import ABC, abstractmethod
   from typing import Dict, Any, Optional
   
   class AIServiceBase(ABC):
       @abstractmethod
       async def generate(self, prompt: str, **kwargs) -> str:
           pass
       
       @abstractmethod
       async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
           pass
   ```

3. **Створити конфігурацію**:
   ```python
# config/ai/config.py
   from dataclasses import dataclass
   
   @dataclass
   class AIConfig:
       openai_api_key: str
       claude_api_key: str
       max_tokens: int = 2000
       temperature: float = 0.7
       cache_ttl: int = 3600
   ```

#### Залежності
- Немає

#### Оцінка
- **Розробка**: 2 дні
- **Тестування**: 1 день
- **Документація**: 0.5 дня
- **Всього**: 3.5 дні

### **AI-002: OpenAI інтеграція**

#### Опис
Інтегрувати OpenAI GPT-4 API для генерації відгуків та аналізу вакансій.

#### Критерії приймання
- [ ] Створено OpenAIService клас
- [ ] Реалізовано метод generate_proposal()
- [ ] Реалізовано метод analyze_job()
- [ ] Налаштовано rate limiting
- [ ] Додано error handling
- [ ] Створено unit тести

#### Інструкції виконання
1. **Встановити залежності**:
   ```bash
   pip install openai redis
   ```

2. **Створити OpenAIService**:
   ```python
# src/ai/services/openai_service.py
   import openai
   from typing import Dict, Any, Optional
   from ..base import AIServiceBase
   
   class OpenAIService(AIServiceBase):
       def __init__(self, api_key: str, max_tokens: int = 2000):
           self.client = openai.AsyncOpenAI(api_key=api_key)
           self.max_tokens = max_tokens
       
       async def generate_proposal(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
           prompt = self._build_proposal_prompt(job_data, user_profile)
           
           response = await self.client.chat.completions.create(
               model="gpt-4",
               messages=[{"role": "user", "content": prompt}],
               max_tokens=self.max_tokens,
               temperature=0.7
           )
           
           return response.choices[0].message.content
   ```

3. **Створити prompt templates**:
   ```python
# src/ai/templates/proposal_templates.py
   PROPOSAL_TEMPLATE = """
   You are an expert freelancer writing a cover letter for an Upwork job.
   
   Job Title: {job_title}
   Job Description: {job_description}
   Client Budget: {budget}
   Required Skills: {skills}
   
   User Profile:
   - Experience: {user_experience}
   - Skills: {user_skills}
   - Portfolio: {user_portfolio}
   
   Write a compelling cover letter that:
   1. Addresses the client's specific needs
   2. Highlights relevant experience
   3. Shows understanding of the project
   4. Includes a clear call to action
   5. Stays within 300-500 words
   
   Tone: Professional, confident, and solution-oriented
   """
   ```

#### Залежності
- AI-001: Базова структура

#### Оцінка
- **Розробка**: 3 дні
- **Тестування**: 1.5 дні
- **Документація**: 0.5 дня
- **Всього**: 5 днів

### **AI-003: Claude fallback інтеграція**

#### Опис
Додати Claude як fallback сервіс для випадків, коли OpenAI недоступний.

#### Критерії приймання
- [ ] Створено ClaudeService клас
- [ ] Реалізовано fallback логіку
- [ ] Налаштовано автоматичне перемикання
- [ ] Додано метрики для відстеження fallback
- [ ] Створено unit тести

#### Інструкції виконання
1. **Встановити залежності**:
   ```bash
   pip install anthropic
   ```

2. **Створити ClaudeService**:
   ```python
# src/ai/services/claude_service.py
   import anthropic
   from typing import Dict, Any
   from ..base import AIServiceBase
   
   class ClaudeService(AIServiceBase):
       def __init__(self, api_key: str, max_tokens: int = 2000):
           self.client = anthropic.AsyncAnthropic(api_key=api_key)
           self.max_tokens = max_tokens
       
       async def generate_proposal(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
           prompt = self._build_proposal_prompt(job_data, user_profile)
           
           response = await self.client.messages.create(
               model="claude-3-sonnet-20240229",
               max_tokens=self.max_tokens,
               messages=[{"role": "user", "content": prompt}]
           )
           
           return response.content[0].text
   ```

3. **Створити fallback логіку**:
   ```python
# src/ai/services/ai_orchestrator.py
   from typing import Dict, Any
   from .openai_service import OpenAIService
   from .claude_service import ClaudeService
   
   class AIOrchestrator:
       def __init__(self, openai_service: OpenAIService, claude_service: ClaudeService):
           self.primary_service = openai_service
           self.fallback_service = claude_service
       
       async def generate_proposal(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
           try:
               return await self.primary_service.generate_proposal(job_data, user_profile)
           except Exception as e:
# Log fallback usage
               self._log_fallback_usage("openai_error", str(e))
               return await self.fallback_service.generate_proposal(job_data, user_profile)
   ```

#### Залежності
- AI-002: OpenAI інтеграція

#### Оцінка
- **Розробка**: 2 дні
- **Тестування**: 1 день
- **Документація**: 0.5 дня
- **Всього**: 3.5 дні

### **AI-004: Кешування відповідей**

#### Опис
Реалізувати кешування AI відповідей для оптимізації витрат та швидкості.

#### Критерії приймання
- [ ] Створено CacheManager клас
- [ ] Реалізовано similarity matching
- [ ] Налаштовано TTL для кешу
- [ ] Додано cache invalidation
- [ ] Створено метрики кешування
- [ ] Створено unit тести

#### Інструкції виконання
1. **Створити CacheManager**:
   ```python
# src/ai/utils/cache_manager.py
   import redis
   import hashlib
   import json
   from typing import Optional, Dict, Any
   
   class CacheManager:
       def __init__(self, redis_url: str, ttl: int = 3600):
           self.redis = redis.from_url(redis_url)
           self.ttl = ttl
       
       def _generate_cache_key(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
# Create a hash based on job and user data
           data_str = json.dumps({
               "job": {k: v for k, v in job_data.items() if k in ["title", "description", "skills"]},
               "user": {k: v for k, v in user_profile.items() if k in ["skills", "experience"]}
           }, sort_keys=True)
           
           return f"ai_cache:{hashlib.md5(data_str.encode()).hexdigest()}"
       
       async def get_cached_response(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Optional[str]:
           cache_key = self._generate_cache_key(job_data, user_profile)
           cached = self.redis.get(cache_key)
           return cached.decode() if cached else None
       
       async def cache_response(self, job_data: Dict[str, Any], user_profile: Dict[str, Any], response: str):
           cache_key = self._generate_cache_key(job_data, user_profile)
           self.redis.setex(cache_key, self.ttl, response)
   ```

2. **Інтегрувати з AI сервісами**:
   ```python
# src/ai/services/ai_orchestrator.py
   async def generate_proposal(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
# Check cache first
       cached_response = await self.cache_manager.get_cached_response(job_data, user_profile)
       if cached_response:
           return cached_response
       
# Generate new response
       try:
           response = await self.primary_service.generate_proposal(job_data, user_profile)
       except Exception as e:
           response = await self.fallback_service.generate_proposal(job_data, user_profile)
       
# Cache the response
       await self.cache_manager.cache_response(job_data, user_profile, response)
       
       return response
   ```

#### Залежності
- AI-003: Claude fallback

#### Оцінка
- **Розробка**: 2 дні
- **Тестування**: 1 день
- **Документація**: 0.5 дня
- **Всього**: 3.5 дні

### **AI-005: JobAnalyzer реалізація**

#### Опис
Створити систему аналізу вакансій з ML-based оцінкою складності, конкуренції та відповідності.

#### Критерії приймання
- [ ] Створено JobAnalyzer клас
- [ ] Реалізовано аналіз складності
- [ ] Реалізовано аналіз конкуренції
- [ ] Реалізовано аналіз відповідності
- [ ] Додано ML моделі для класифікації
- [ ] Створено unit тести

#### Інструкції виконання
1. **Створити JobAnalyzer**:
   ```python
# src/ai/services/job_analyzer.py
   from typing import Dict, Any, List
   import numpy as np
   from sklearn.feature_extraction.text import TfidfVectorizer
   from sklearn.ensemble import RandomForestClassifier
   
   class JobAnalyzer:
       def __init__(self):
           self.difficulty_classifier = RandomForestClassifier()
           self.competition_classifier = RandomForestClassifier()
           self.vectorizer = TfidfVectorizer(max_features=1000)
       
       async def analyze_job(self, job_data: Dict[str, Any], user_skills: List[str]) -> Dict[str, Any]:
# Extract features
           features = self._extract_features(job_data)
           
# Analyze difficulty
           difficulty_score = await self._analyze_difficulty(features)
           
# Analyze competition
           competition_score = await self._analyze_competition(features)
           
# Analyze skill match
           skill_match_score = await self._analyze_skill_match(job_data, user_skills)
           
# Calculate success probability
           success_probability = self._calculate_success_probability(
               difficulty_score, competition_score, skill_match_score
           )
           
           return {
               "difficulty_score": difficulty_score,
               "competition_score": competition_score,
               "skill_match_score": skill_match_score,
               "success_probability": success_probability,
               "recommended_bid": self._calculate_recommended_bid(job_data, success_probability)
           }
       
       def _extract_features(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
           return {
               "budget": job_data.get("budget", 0),
               "experience_level": job_data.get("experience_level", "entry"),
               "job_type": job_data.get("job_type", "fixed"),
               "skills_count": len(job_data.get("skills", [])),
               "description_length": len(job_data.get("description", "")),
               "client_rating": job_data.get("client_rating", 0),
               "client_total_spent": job_data.get("client_total_spent", 0)
           }
   ```

#### Залежності
- AI-004: Кешування відповідей

#### Оцінка
- **Розробка**: 3 дні
- **Тестування**: 1.5 дні
- **Документація**: 0.5 дня
- **Всього**: 5 днів

### **AI-006: SmartFilter реалізація**

#### Опис
Створити розумну систему фільтрації вакансій з ML-based ранжуванням та адаптивним навчанням.

#### Критерії приймання
- [ ] Створено SmartFilter клас
- [ ] Реалізовано ML-based ранжування
- [ ] Додано user preference learning
- [ ] Реалізовано feedback loop
- [ ] Створено real-time оновлення
- [ ] Створено unit тести

#### Інструкції виконання
1. **Створити SmartFilter**:
   ```python
# src/ai/services/smart_filter.py
   from typing import List, Dict, Any
   import numpy as np
   from sklearn.ensemble import GradientBoostingRegressor
   
   class SmartFilter:
       def __init__(self):
           self.ranking_model = GradientBoostingRegressor()
           self.user_preferences = {}
       
       async def filter_jobs(self, jobs: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
# Get user preferences
           user_prefs = self.user_preferences.get(user_id, {})
           
# Calculate scores for each job
           scored_jobs = []
           for job in jobs:
               score = await self._calculate_job_score(job, user_prefs)
               scored_jobs.append({**job, "score": score})
           
# Sort by score
           scored_jobs.sort(key=lambda x: x["score"], reverse=True)
           
           return scored_jobs
       
       async def _calculate_job_score(self, job: Dict[str, Any], user_prefs: Dict[str, Any]) -> float:
# Base score from job analysis
           base_score = job.get("success_probability", 0.5)
           
# User preference adjustments
           preference_score = 0
           if user_prefs.get("preferred_budget_range"):
               budget_score = self._calculate_budget_preference_score(job, user_prefs["preferred_budget_range"])
               preference_score += budget_score
           
           if user_prefs.get("preferred_skills"):
               skill_score = self._calculate_skill_preference_score(job, user_prefs["preferred_skills"])
               preference_score += skill_score
           
# Combine scores
           final_score = 0.7 * base_score + 0.3 * preference_score
           
           return final_score
       
       async def update_user_preferences(self, user_id: str, job_id: str, action: str):
           """Update user preferences based on actions (view, apply, ignore)"""
           if user_id not in self.user_preferences:
               self.user_preferences[user_id] = {}
           
# Update preferences based on action
           if action == "apply":
# User liked this type of job
               pass
           elif action == "ignore":
# User didn't like this type of job
               pass
   ```

#### Залежності
- AI-005: JobAnalyzer реалізація

#### Оцінка
- **Розробка**: 3 дні
- **Тестування**: 1.5 дні
- **Документація**: 0.5 дня
- **Всього**: 5 днів

### **AI-007: Cost management**

#### Опис
Реалізувати систему управління витратами на AI API з відстеженням та лімітами.

#### Критерії приймання
- [ ] Створено CostManager клас
- [ ] Реалізовано відстеження витрат
- [ ] Додано ліміти для користувачів
- [ ] Створено alerts при перевищенні лімітів
- [ ] Додано оптимізацію витрат
- [ ] Створено unit тести

#### Інструкції виконання
1. **Створити CostManager**:
   ```python
# src/ai/utils/cost_manager.py
   from typing import Dict, Any, Optional
   import redis
   from datetime import datetime, timedelta
   
   class CostManager:
       def __init__(self, redis_url: str):
           self.redis = redis.from_url(redis_url)
           self.cost_limits = {
               "free": {"daily": 0.10, "monthly": 2.00},
               "basic": {"daily": 0.50, "monthly": 10.00},
               "premium": {"daily": 2.00, "monthly": 50.00}
           }
       
       async def check_cost_limit(self, user_id: str, user_plan: str) -> bool:
           """Check if user has exceeded cost limits"""
           daily_key = f"cost:daily:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
           monthly_key = f"cost:monthly:{user_id}:{datetime.now().strftime('%Y-%m')}"
           
           daily_cost = float(self.redis.get(daily_key) or 0)
           monthly_cost = float(self.redis.get(monthly_key) or 0)
           
           limits = self.cost_limits.get(user_plan, self.cost_limits["free"])
           
           return daily_cost < limits["daily"] and monthly_cost < limits["monthly"]
       
       async def record_cost(self, user_id: str, cost: float, model: str):
           """Record cost for user"""
           daily_key = f"cost:daily:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
           monthly_key = f"cost:monthly:{user_id}:{datetime.now().strftime('%Y-%m')}"
           
# Increment daily cost
           self.redis.incrbyfloat(daily_key, cost)
           self.redis.expire(daily_key, 86400)  # 24 hours
           
# Increment monthly cost
           self.redis.incrbyfloat(monthly_key, cost)
           self.redis.expire(monthly_key, 2592000)  # 30 days
           
# Log cost details
           cost_log = {
               "user_id": user_id,
               "cost": cost,
               "model": model,
               "timestamp": datetime.now().isoformat()
           }
           self.redis.lpush("cost_log", str(cost_log))
   ```

#### Залежності
- AI-006: SmartFilter реалізація

#### Оцінка
- **Розробка**: 2 дні
- **Тестування**: 1 день
- **Документація**: 0.5 дня
- **Всього**: 3.5 дні

### **AI-008: A/B testing**

#### Опис
Реалізувати систему A/B тестування для оптимізації prompt templates та AI стратегій.

#### Критерії приймання
- [ ] Створено ABTestManager клас
- [ ] Реалізовано розподіл користувачів по групах
- [ ] Додано відстеження метрик
- [ ] Реалізовано статистичний аналіз
- [ ] Створено автоматичне перемикання
- [ ] Створено unit тести

#### Інструкції виконання
1. **Створити ABTestManager**:
   ```python
# src/ai/utils/ab_test_manager.py
   import random
   import hashlib
   from typing import Dict, Any, List
   from datetime import datetime, timedelta
   
   class ABTestManager:
       def __init__(self, redis_url: str):
           self.redis = redis.from_url(redis_url)
           self.tests = {}
       
       def assign_user_to_group(self, user_id: str, test_name: str) -> str:
           """Assign user to A/B test group"""
# Create consistent assignment based on user_id
           hash_value = hashlib.md5(f"{user_id}:{test_name}".encode()).hexdigest()
           group = "A" if int(hash_value[:8], 16) % 2 == 0 else "B"
           
# Store assignment
           assignment_key = f"ab_test:{test_name}:{user_id}"
           self.redis.setex(assignment_key, 86400, group)  # 24 hours
           
           return group
       
       def get_user_group(self, user_id: str, test_name: str) -> str:
           """Get user's assigned group for test"""
           assignment_key = f"ab_test:{test_name}:{user_id}"
           group = self.redis.get(assignment_key)
           
           if group:
               return group.decode()
           
# Assign new group if not exists
           return self.assign_user_to_group(user_id, test_name)
       
       async def record_metric(self, test_name: str, user_id: str, metric: str, value: float):
           """Record metric for A/B test"""
           group = self.get_user_group(user_id, test_name)
           metric_key = f"ab_metric:{test_name}:{group}:{metric}"
           
# Store metric
           self.redis.lpush(metric_key, value)
           self.redis.expire(metric_key, 604800)  # 7 days
       
       async def get_test_results(self, test_name: str) -> Dict[str, Any]:
           """Get A/B test results"""
           results = {}
           
           for group in ["A", "B"]:
               group_results = {}
               for metric in ["conversion_rate", "user_satisfaction", "cost_per_conversion"]:
                   metric_key = f"ab_metric:{test_name}:{group}:{metric}"
                   values = self.redis.lrange(metric_key, 0, -1)
                   
                   if values:
                       group_results[metric] = {
                           "mean": sum(float(v) for v in values) / len(values),
                           "count": len(values)
                       }
               
               results[group] = group_results
           
           return results
   ```

#### Залежності
- AI-007: Cost management

#### Оцінка
- **Розробка**: 2 дні
- **Тестування**: 1 день
- **Документація**: 0.5 дня
- **Всього**: 3.5 дні

---

## Інструкції виконання

### **Загальні інструкції**
1. **Налаштування середовища**:
   ```bash
# Встановити залежності
   pip install openai anthropic redis scikit-learn numpy pandas
   
# Налаштувати змінні середовища
   export OPENAI_API_KEY="your_openai_key"
   export CLAUDE_API_KEY="your_claude_key"
   export REDIS_URL="redis://localhost:6379"
   ```

2. **Створення структури проекту**:
   ```bash
# Створити папки
   mkdir -p src/ai/{services,models,utils,templates}
   mkdir -p tests/ai/{unit,integration}
   mkdir -p config/ai
   ```

3. **Налаштування тестування**:
   ```bash
# Встановити pytest
   pip install pytest pytest-asyncio pytest-mock
   
# Запустити тести
   pytest tests/ai/ -v
   ```

### **Специфічні інструкції**
- **AI-001**: Дотримуватися шаблону базових класів
- **AI-002**: Використовувати async/await для API викликів
- **AI-003**: Реалізувати proper error handling
- **AI-004**: Оптимізувати cache keys для швидкого пошуку
- **AI-005**: Використовувати ML моделі для класифікації
- **AI-006**: Реалізувати feedback loop для навчання
- **AI-007**: Додати alerts при перевищенні лімітів
- **AI-008**: Використовувати статистичні методи для аналізу

---

## Критерії приймання

### **Загальні критерії**
- [ ] Всі unit тести проходять (>90% покриття)
- [ ] Integration тести проходять
- [ ] API документація створена та актуальна
- [ ] Error handling реалізовано
- [ ] Logging налаштовано
- [ ] Performance метрики відстежуються

### **Специфічні критерії**
- **AI-001**: Базова архітектура готова до розширення
- **AI-002**: OpenAI інтеграція працює стабільно
- **AI-003**: Fallback механізм спрацьовує автоматично
- **AI-004**: Кешування зменшує витрати на 30%+
- **AI-005**: JobAnalyzer дає точні прогнози
- **AI-006**: SmartFilter покращує релевантність на 50%+
- **AI-007**: Cost management контролює витрати
- **AI-008**: A/B testing дає статистично значущі результати

---

## 🧪 Тестування

### **Unit тести**
```python
# tests/ai/unit/test_openai_service.py
import pytest
from unittest.mock import AsyncMock, patch
from src.ai.services.openai_service import OpenAIService

class TestOpenAIService:
    @pytest.fixture
    def service(self):
        return OpenAIService("test_key")
    
    @pytest.mark.asyncio
    async def test_generate_proposal(self, service):
        with patch('openai.AsyncOpenAI') as mock_client:
            mock_response = AsyncMock()
            mock_response.choices[0].message.content = "Test proposal"
            mock_client.return_value.chat.completions.create.return_value = mock_response
            
            result = await service.generate_proposal({}, {})
            assert result == "Test proposal"
```

### **Integration тести**
```python
# tests/ai/integration/test_ai_orchestrator.py
import pytest
from src.ai.services.ai_orchestrator import AIOrchestrator

class TestAIOrchestrator:
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self):
# Test fallback when primary service fails
        pass
```

### **Performance тести**
```python
# tests/ai/performance/test_cache_performance.py
import pytest
import time
from src.ai.utils.cache_manager import CacheManager

class TestCachePerformance:
    def test_cache_speed(self):
# Test cache response time
        pass
```

---

## Розгортання

### **Development**
```bash
# Запуск з Docker
docker-compose up ai-service

# Запуск локально
python -m uvicorn src.ai.main:app --reload
```

### **Production**
```bash
# Build Docker image
docker build -t upwork-ai-service .

# Deploy to Kubernetes
kubectl apply -f k8s/ai-service.yaml
```

### **Monitoring**
```bash
# Check logs
kubectl logs -f deployment/ai-service

# Check metrics
curl http://localhost:8000/metrics
```

---

## Пов'язані документи

### Основні документи
- [AI Module](ai_module.md)
- [План проекту](../PROJECT_OVERVIEW.md)
- [Всі завдання](../MASTER_TASKS.md)

### Технічні деталі
- [API специфікації](../technical_details/api/)
- [Database схеми](../technical_details/database/)
- [Security реалізація](../technical_details/security/)

### Гіди
- [Development Guides](../guides/development/)
- [Testing Guides](../guides/testing/)

---

**Статус**: Створено  
**Версія**: 1.0.0  
**Останнє оновлення**: 2024-12-19 20:00 