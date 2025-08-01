"""
AI Engine - Основний двигун для AI функціональності
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

try:
    from shared.config.logging import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger("ai-engine")


class ProposalGenerator:
    """Генератор персоналізованих пропозицій"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.keywords_db = self._load_keywords()
    
    def _load_templates(self) -> Dict[str, str]:
        """Завантаження шаблонів пропозицій"""
        return {
            "default": """
# Пропозиція для проекту

## Про мене
{user_profile}

## Підхід до проекту
На основі вашого опису, я пропоную наступний підхід:

### Технічне рішення
- Детальний аналіз вимог
- Архітектурне планування
- Поетапна реалізація

### Комунікація
- Регулярні оновлення прогресу
- Прозорість робочого процесу
- Готовність до обговорень

### Якість
- Тестування на кожному етапі
- Документація коду
- Підтримка після завершення

## Чому обирати мене
- ✅ Досвід у подібних проектах
- ✅ Якісний код та документація
- ✅ Вчасне виконання
- ✅ Підтримка після завершення

Готовий обговорити деталі та почати роботу!
            """,
            
            "technical": """
# Технічна пропозиція

## Технічний підхід
{technical_approach}

## Архітектура рішення
{architecture}

## Технологічний стек
{tech_stack}

## План реалізації
{implementation_plan}

## Гарантії якості
- Unit тести для всіх компонентів
- Code review та документація
- CI/CD pipeline
- Моніторинг та логування

Готовий почати роботу!
            """,
            
            "creative": """
# Креативна пропозиція

## Мій підхід
{creative_approach}

## Унікальні переваги
{unique_advantages}

## Портфоліо
{portfolio_highlights}

## Процес роботи
{work_process}

## Результат
{expected_result}

Давайте створимо щось дивовижне разом!
            """
        }
    
    def _load_keywords(self) -> Dict[str, List[str]]:
        """Завантаження бази ключових слів"""
        return {
            "frontend": ["react", "vue", "angular", "javascript", "typescript", "html", "css", "sass", "webpack"],
            "backend": ["python", "node.js", "java", "c#", "php", "go", "rust", "django", "fastapi", "express"],
            "database": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sql", "nosql"],
            "devops": ["docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "jenkins", "gitlab"],
            "mobile": ["react native", "flutter", "ios", "android", "swift", "kotlin"],
            "ai_ml": ["machine learning", "deep learning", "tensorflow", "pytorch", "opencv", "nlp"]
        }
    
    def generate_proposal(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Генерація персоналізованої пропозиції"""
        try:
            # Аналізуємо вакансію
            job_analysis = self._analyze_job(job_data)
            
            # Визначаємо тип шаблону
            template_type = self._determine_template_type(job_data, job_analysis)
            
            # Отримуємо базовий шаблон
            template = self.templates.get(template_type, self.templates["default"])
            
            # Персоналізуємо пропозицію
            personalized_proposal = self._personalize_proposal(
                template, job_data, user_profile, job_analysis
            )
            
            # Розраховуємо рекомендовану ставку
            recommended_rate = self._calculate_recommended_rate(job_data, user_profile)
            
            return {
                "proposal": personalized_proposal,
                "job_analysis": job_analysis,
                "recommended_rate": recommended_rate,
                "template_type": template_type,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка генерації пропозиції: {e}")
            raise
    
    def _analyze_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Аналіз вакансії"""
        description = job_data.get("description", "").lower()
        title = job_data.get("title", "").lower()
        
        # Витягуємо ключові слова
        keywords = []
        for category, words in self.keywords_db.items():
            for word in words:
                if word in description or word in title:
                    keywords.append(word)
        
        # Визначаємо складність
        complexity = self._assess_complexity(description)
        
        # Оцінюємо тривалість
        duration = self._estimate_duration(description)
        
        return {
            "keywords": list(set(keywords)),
            "complexity": complexity,
            "estimated_duration": duration,
            "category": self._categorize_job(description),
            "skill_requirements": self._extract_skill_requirements(description)
        }
    
    def _determine_template_type(self, job_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Визначення типу шаблону"""
        description = job_data.get("description", "").lower()
        
        if any(word in description for word in ["creative", "design", "ui/ux", "branding"]):
            return "creative"
        elif any(word in description for word in ["architecture", "system", "api", "database"]):
            return "technical"
        else:
            return "default"
    
    def _personalize_proposal(self, template: str, job_data: Dict[str, Any], 
                            user_profile: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Персоналізація пропозиції"""
        # Базові дані
        user_name = user_profile.get("name", "Досвідчений фрілансер")
        user_skills = ", ".join(user_profile.get("skills", []))
        user_experience = user_profile.get("experience", "багаторічним")
        
        # Технічні деталі
        tech_stack = ", ".join(analysis.get("keywords", []))
        complexity = analysis.get("complexity", "середньої")
        duration = analysis.get("estimated_duration", "2-4 тижні")
        
        # Замінюємо плейсхолдери
        proposal = template.format(
            user_profile=f"{user_name} з {user_experience} досвідом роботи в технологіях: {user_skills}.",
            technical_approach=f"Використовуючи {tech_stack} для створення надійного та масштабованого рішення.",
            architecture="Модульна архітектура з чітким розділенням відповідальності.",
            tech_stack=tech_stack,
            implementation_plan=f"Поетапна реалізація протягом {duration} з регулярними демо.",
            creative_approach="Креативний підхід до вирішення задач з фокусом на користувацький досвід.",
            unique_advantages="Унікальна комбінація технічних навичок та креативного мислення.",
            portfolio_highlights="Портфоліо включає подібні проекти з високими оцінками клієнтів.",
            work_process="Ітеративний процес з постійним зворотним зв'язком.",
            expected_result=f"Якісний результат {complexity} складності в обумовлені терміни."
        )
        
        return proposal
    
    def _calculate_recommended_rate(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Розрахунок рекомендованої ставки"""
        budget = job_data.get("budget", {})
        min_budget = budget.get("min", 1000)
        max_budget = budget.get("max", 5000)
        
        user_rate = user_profile.get("hourly_rate", 25)
        complexity = self._assess_complexity(job_data.get("description", ""))
        
        # Корекція на основі складності
        complexity_multiplier = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.3,
            "expert": 1.6
        }.get(complexity, 1.0)
        
        recommended_hourly = user_rate * complexity_multiplier
        estimated_hours = (min_budget + max_budget) / 2 / recommended_hourly
        
        return {
            "hourly_rate": round(recommended_hourly, 2),
            "estimated_hours": round(estimated_hours, 1),
            "total_budget": round(recommended_hourly * estimated_hours, 2),
            "complexity_multiplier": complexity_multiplier
        }
    
    def _assess_complexity(self, description: str) -> str:
        """Оцінка складності проекту"""
        description_lower = description.lower()
        
        expert_keywords = ["enterprise", "scalable", "microservices", "ai", "ml", "blockchain"]
        high_keywords = ["api", "database", "authentication", "payment", "real-time"]
        medium_keywords = ["website", "app", "frontend", "backend", "integration"]
        
        if any(word in description_lower for word in expert_keywords):
            return "expert"
        elif any(word in description_lower for word in high_keywords):
            return "high"
        elif any(word in description_lower for word in medium_keywords):
            return "medium"
        else:
            return "low"
    
    def _estimate_duration(self, description: str) -> str:
        """Оцінка тривалості проекту"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["simple", "basic", "landing"]):
            return "1-2 тижні"
        elif any(word in description_lower for word in ["website", "app", "integration"]):
            return "2-4 тижні"
        elif any(word in description_lower for word in ["platform", "system", "api"]):
            return "4-8 тижнів"
        else:
            return "2-4 тижні"
    
    def _categorize_job(self, description: str) -> str:
        """Категорізація вакансії"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["frontend", "ui", "ux", "design"]):
            return "frontend"
        elif any(word in description_lower for word in ["backend", "api", "server", "database"]):
            return "backend"
        elif any(word in description_lower for word in ["fullstack", "full-stack"]):
            return "fullstack"
        elif any(word in description_lower for word in ["mobile", "ios", "android"]):
            return "mobile"
        else:
            return "general"
    
    def _extract_skill_requirements(self, description: str) -> List[str]:
        """Витягування необхідних навичок"""
        description_lower = description.lower()
        required_skills = []
        
        for category, skills in self.keywords_db.items():
            for skill in skills:
                if skill in description_lower:
                    required_skills.append(skill)
        
        return list(set(required_skills))


class SmartFilter:
    """Розумний фільтр для вакансій"""
    
    def __init__(self):
        self.user_preferences = {}
        self.job_history = {}
    
    def filter_jobs(self, jobs: List[Dict[str, Any]], user_profile: Dict[str, Any], 
                   filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Фільтрація вакансій"""
        try:
            scored_jobs = []
            
            for job in jobs:
                score = self._calculate_job_score(job, user_profile, filters)
                job_with_score = {**job, "ai_score": score}
                scored_jobs.append(job_with_score)
            
            # Сортуємо за оцінкою
            scored_jobs.sort(key=lambda x: x["ai_score"], reverse=True)
            
            # Застосовуємо фільтри
            if filters:
                scored_jobs = self._apply_filters(scored_jobs, filters)
            
            return scored_jobs
            
        except Exception as e:
            logger.error(f"Помилка фільтрації вакансій: {e}")
            return jobs
    
    def _calculate_job_score(self, job: Dict[str, Any], user_profile: Dict[str, Any], 
                           filters: Optional[Dict[str, Any]] = None) -> float:
        """Розрахунок оцінки вакансії"""
        score = 0.0
        
        # Оцінка відповідності навичок
        skill_score = self._calculate_skill_match(job, user_profile)
        score += skill_score * 0.4
        
        # Оцінка бюджету
        budget_score = self._calculate_budget_match(job, user_profile)
        score += budget_score * 0.3
        
        # Оцінка клієнта
        client_score = self._calculate_client_score(job)
        score += client_score * 0.2
        
        # Оцінка складності
        complexity_score = self._calculate_complexity_match(job, user_profile)
        score += complexity_score * 0.1
        
        return round(score, 2)
    
    def _calculate_skill_match(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Розрахунок відповідності навичок"""
        job_skills = set(job.get("skills", []))
        user_skills = set(user_profile.get("skills", []))
        
        if not job_skills:
            return 0.5
        
        # Розраховуємо Jaccard similarity
        intersection = len(job_skills.intersection(user_skills))
        union = len(job_skills.union(user_skills))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _calculate_budget_match(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Розрахунок відповідності бюджету"""
        budget = job.get("budget", {})
        min_budget = budget.get("min", 0)
        max_budget = budget.get("max", 10000)
        avg_budget = (min_budget + max_budget) / 2
        
        user_rate = user_profile.get("hourly_rate", 25)
        user_preferred_budget = user_rate * 40  # 40 годин на тиждень
        
        if avg_budget == 0:
            return 0.5
        
        # Нормалізуємо різницю
        difference = abs(avg_budget - user_preferred_budget) / user_preferred_budget
        
        if difference <= 0.2:
            return 1.0
        elif difference <= 0.5:
            return 0.7
        elif difference <= 1.0:
            return 0.4
        else:
            return 0.1
    
    def _calculate_client_score(self, job: Dict[str, Any]) -> float:
        """Розрахунок оцінки клієнта"""
        client = job.get("client", {})
        rating = client.get("rating", 0)
        total_spent = client.get("total_spent", 0)
        
        # Оцінка на основі рейтингу
        rating_score = min(rating / 5.0, 1.0)
        
        # Оцінка на основі витрат
        spent_score = min(total_spent / 10000, 1.0) if total_spent > 0 else 0.5
        
        return (rating_score + spent_score) / 2
    
    def _calculate_complexity_match(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Розрахунок відповідності складності"""
        description = job.get("description", "").lower()
        user_experience = user_profile.get("experience_level", "intermediate")
        
        # Визначаємо складність вакансії
        if any(word in description for word in ["expert", "senior", "advanced", "complex"]):
            job_complexity = "expert"
        elif any(word in description for word in ["intermediate", "mid-level"]):
            job_complexity = "intermediate"
        else:
            job_complexity = "beginner"
        
        # Матриця відповідності
        complexity_matrix = {
            "beginner": {"beginner": 1.0, "intermediate": 0.7, "expert": 0.3},
            "intermediate": {"beginner": 0.8, "intermediate": 1.0, "expert": 0.6},
            "expert": {"beginner": 0.5, "intermediate": 0.8, "expert": 1.0}
        }
        
        return complexity_matrix.get(user_experience, {}).get(job_complexity, 0.5)
    
    def _apply_filters(self, jobs: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Застосування фільтрів"""
        filtered_jobs = jobs
        
        # Фільтр по бюджету
        if "min_budget" in filters:
            filtered_jobs = [job for job in filtered_jobs 
                           if job.get("budget", {}).get("min", 0) >= filters["min_budget"]]
        
        if "max_budget" in filters:
            filtered_jobs = [job for job in filtered_jobs 
                           if job.get("budget", {}).get("max", 10000) <= filters["max_budget"]]
        
        # Фільтр по навичках
        if "required_skills" in filters:
            required_skills = set(filters["required_skills"])
            filtered_jobs = [job for job in filtered_jobs 
                           if required_skills.issubset(set(job.get("skills", [])))]
        
        # Фільтр по локації
        if "location" in filters:
            filtered_jobs = [job for job in filtered_jobs 
                           if filters["location"].lower() in job.get("location", "").lower()]
        
        return filtered_jobs


class JobAnalyzer:
    """Аналізатор вакансій"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Повний аналіз вакансії"""
        try:
            job_id = job_data.get("id", "unknown")
            
            # Перевіряємо кеш
            if job_id in self.analysis_cache:
                return self.analysis_cache[job_id]
            
            analysis = {
                "job_id": job_id,
                "suitability_score": self._calculate_suitability_score(job_data),
                "competition_level": self._assess_competition(job_data),
                "success_probability": self._calculate_success_probability(job_data),
                "recommended_bid": self._calculate_recommended_bid(job_data),
                "red_flags": self._identify_red_flags(job_data),
                "opportunities": self._identify_opportunities(job_data),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Зберігаємо в кеш
            self.analysis_cache[job_id] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Помилка аналізу вакансії: {e}")
            return {"error": str(e)}
    
    def _calculate_suitability_score(self, job_data: Dict[str, Any]) -> float:
        """Розрахунок оцінки підходящості"""
        score = 0.5  # Базова оцінка
        
        # Аналіз опису
        description = job_data.get("description", "")
        if len(description) > 100:
            score += 0.1  # Детальний опис
        
        # Аналіз бюджету
        budget = job_data.get("budget", {})
        if budget.get("min", 0) > 500:
            score += 0.1  # Хороший бюджет
        
        # Аналіз клієнта
        client = job_data.get("client", {})
        if client.get("rating", 0) > 4.0:
            score += 0.2  # Хороший клієнт
        
        if client.get("total_spent", 0) > 1000:
            score += 0.1  # Досвідчений клієнт
        
        return min(score, 1.0)
    
    def _assess_competition(self, job_data: Dict[str, Any]) -> str:
        """Оцінка рівня конкуренції"""
        proposals_count = job_data.get("proposals_count", 0)
        
        if proposals_count <= 5:
            return "low"
        elif proposals_count <= 15:
            return "medium"
        else:
            return "high"
    
    def _calculate_success_probability(self, job_data: Dict[str, Any]) -> float:
        """Розрахунок ймовірності успіху"""
        base_probability = 0.3
        
        # Фактори, що збільшують ймовірність
        if job_data.get("client", {}).get("rating", 0) > 4.5:
            base_probability += 0.2
        
        if job_data.get("budget", {}).get("min", 0) > 1000:
            base_probability += 0.1
        
        if job_data.get("proposals_count", 0) < 10:
            base_probability += 0.1
        
        return min(base_probability, 0.9)
    
    def _calculate_recommended_bid(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Розрахунок рекомендованої ставки"""
        budget = job_data.get("budget", {})
        min_budget = budget.get("min", 1000)
        max_budget = budget.get("max", 5000)
        
        # Рекомендована ставка на основі конкуренції
        competition = self._assess_competition(job_data)
        competition_multiplier = {
            "low": 1.1,
            "medium": 1.0,
            "high": 0.9
        }.get(competition, 1.0)
        
        recommended_bid = (min_budget + max_budget) / 2 * competition_multiplier
        
        return {
            "amount": round(recommended_bid, 2),
            "range": f"${min_budget} - ${max_budget}",
            "competition_factor": competition_multiplier
        }
    
    def _identify_red_flags(self, job_data: Dict[str, Any]) -> List[str]:
        """Визначення червоних прапорців"""
        red_flags = []
        
        description = job_data.get("description", "").lower()
        client = job_data.get("client", {})
        
        # Перевіряємо опис
        if len(description) < 50:
            red_flags.append("Короткий опис проекту")
        
        if "urgent" in description or "asap" in description:
            red_flags.append("Терміновість може вказувати на погане планування")
        
        # Перевіряємо клієнта
        if client.get("rating", 0) < 3.0:
            red_flags.append("Низький рейтинг клієнта")
        
        if client.get("total_spent", 0) < 100:
            red_flags.append("Новий клієнт без історії")
        
        # Перевіряємо бюджет
        budget = job_data.get("budget", {})
        if budget.get("min", 0) < 100:
            red_flags.append("Дуже низький бюджет")
        
        return red_flags
    
    def _identify_opportunities(self, job_data: Dict[str, Any]) -> List[str]:
        """Визначення можливостей"""
        opportunities = []
        
        description = job_data.get("description", "").lower()
        client = job_data.get("client", {})
        
        # Аналізуємо опис
        if "long-term" in description or "ongoing" in description:
            opportunities.append("Потенціал для довгострокової співпраці")
        
        if "portfolio" in description or "showcase" in description:
            opportunities.append("Можливість поповнити портфоліо")
        
        # Аналізуємо клієнта
        if client.get("rating", 0) > 4.8:
            opportunities.append("Високорейтинговий клієнт")
        
        if client.get("total_spent", 0) > 10000:
            opportunities.append("Досвідчений клієнт з бюджетом")
        
        # Аналізуємо конкуренцію
        if job_data.get("proposals_count", 0) < 5:
            opportunities.append("Низька конкуренція")
        
        return opportunities


# Глобальні екземпляри
proposal_generator = ProposalGenerator()
smart_filter = SmartFilter()
job_analyzer = JobAnalyzer() 