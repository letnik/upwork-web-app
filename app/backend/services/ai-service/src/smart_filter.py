"""
Покращений SmartFilter з AI інтеграцією
"""

import math
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.logging import get_logger
from .ai_service import AIService
from .job_analyzer import JobAnalyzer

logger = get_logger("smart-filter")


class SmartFilter:
    """Покращений розумний фільтр вакансій з AI інтеграцією"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.job_analyzer = JobAnalyzer()
        self.filter_weights = self._load_filter_weights()
        self.category_keywords = self._load_category_keywords()
    
    def _load_filter_weights(self) -> Dict[str, float]:
        """Завантаження ваг фільтрів"""
        return {
            "skill_match": 0.25,
            "budget_match": 0.20,
            "complexity_match": 0.15,
            "client_rating": 0.15,
            "timeline_match": 0.10,
            "location_match": 0.05,
            "category_match": 0.10
        }
    
    def _load_category_keywords(self) -> Dict[str, List[str]]:
        """Завантаження ключових слів по категоріях"""
        return {
            "web_development": [
                "web", "website", "frontend", "backend", "fullstack",
                "react", "vue", "angular", "javascript", "html", "css"
            ],
            "mobile_development": [
                "mobile", "app", "ios", "android", "react native",
                "flutter", "swift", "kotlin"
            ],
            "backend_development": [
                "api", "server", "database", "backend", "python",
                "java", "node.js", "postgresql", "mysql"
            ],
            "design": [
                "design", "ui", "ux", "graphic", "logo", "branding",
                "figma", "photoshop", "illustrator"
            ],
            "data_science": [
                "data", "analytics", "machine learning", "ai",
                "python", "r", "statistics", "visualization"
            ],
            "devops": [
                "devops", "docker", "kubernetes", "aws", "azure",
                "ci/cd", "deployment", "infrastructure"
            ]
        }
    
    async def filter_jobs(self, jobs: List[Dict[str, Any]], user_profile: Dict[str, Any], 
                         filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Розумна фільтрація вакансій з AI"""
        try:
            if not jobs:
                return {
                    "success": True,
                    "filtered_jobs": [],
                    "total_jobs": 0,
                    "filtered_count": 0,
                    "filters_applied": filters or {}
                }
            
            # Спочатку пробуємо AI фільтрацію
            ai_result = await self.ai_service.filter_jobs(jobs, user_profile, filters)
            
            if ai_result["success"]:
                # Обробляємо AI результат
                filtered_jobs = self._process_ai_filtered_jobs(ai_result["filtered_jobs"], user_profile)
                
                return {
                    "success": True,
                    "filtered_jobs": filtered_jobs,
                    "total_jobs": len(jobs),
                    "filtered_count": len(filtered_jobs),
                    "filters_applied": filters or {},
                    "ai_model": ai_result["model"]
                }
            else:
                # Fallback до базового фільтра
                logger.warning(f"AI фільтрація не вдалася: {ai_result.get('error')}, використовуємо fallback")
                return await self._basic_filter_jobs(jobs, user_profile, filters)
                
        except Exception as e:
            logger.error(f"Помилка фільтрації вакансій: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _process_ai_filtered_jobs(self, ai_filtered_jobs: List[Dict[str, Any]], 
                                user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Обробка AI відфільтрованих вакансій"""
        processed_jobs = []
        
        for job in ai_filtered_jobs:
            # Додаємо додатковий аналіз
            enhanced_job = job.copy()
            
            # Розрахунок додаткових метрик
            enhanced_job["skill_match_score"] = self._calculate_skill_match_score(job, user_profile)
            enhanced_job["budget_score"] = self._calculate_budget_score(job, user_profile)
            enhanced_job["complexity_score"] = self._calculate_complexity_score(job, user_profile)
            enhanced_job["client_score"] = self._calculate_client_score(job)
            enhanced_job["timeline_score"] = self._calculate_timeline_score(job, user_profile)
            enhanced_job["location_score"] = self._calculate_location_score(job, user_profile)
            enhanced_job["category_score"] = self._calculate_category_score(job, user_profile)
            
            # Загальний скор
            enhanced_job["total_score"] = self._calculate_total_score(enhanced_job)
            
            processed_jobs.append(enhanced_job)
        
        # Сортуємо за загальним скором
        processed_jobs.sort(key=lambda x: x["total_score"], reverse=True)
        
        return processed_jobs
    
    async def _basic_filter_jobs(self, jobs: List[Dict[str, Any]], user_profile: Dict[str, Any], 
                               filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Базова фільтрація вакансій без AI"""
        try:
            filtered_jobs = []
            
            for job in jobs:
                # Розрахунок скорів для кожної вакансії
                job_score = self._calculate_job_score(job, user_profile, filters)
                
                if job_score > 0.3:  # Мінімальний поріг
                    enhanced_job = job.copy()
                    enhanced_job["ai_score"] = job_score
                    enhanced_job["ai_reason"] = self._generate_score_reason(job, user_profile, job_score)
                    
                    # Додаємо додаткові метрики
                    enhanced_job.update(self._calculate_additional_metrics(job, user_profile))
                    
                    filtered_jobs.append(enhanced_job)
            
            # Сортуємо за скором
            filtered_jobs.sort(key=lambda x: x["ai_score"], reverse=True)
            
            # Обмежуємо кількість результатів
            max_results = filters.get("max_results", 10) if filters else 10
            filtered_jobs = filtered_jobs[:max_results]
            
            return {
                "success": True,
                "filtered_jobs": filtered_jobs,
                "total_jobs": len(jobs),
                "filtered_count": len(filtered_jobs),
                "filters_applied": filters or {},
                "ai_model": "fallback"
            }
            
        except Exception as e:
            logger.error(f"Помилка базової фільтрації: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _calculate_job_score(self, job: Dict[str, Any], user_profile: Dict[str, Any], 
                           filters: Optional[Dict[str, Any]] = None) -> float:
        """Розрахунок загального скору вакансії"""
        # Отримуємо окремі скори
        skill_score = self._calculate_skill_match_score(job, user_profile)
        budget_score = self._calculate_budget_score(job, user_profile)
        complexity_score = self._calculate_complexity_score(job, user_profile)
        client_score = self._calculate_client_score(job)
        timeline_score = self._calculate_timeline_score(job, user_profile)
        location_score = self._calculate_location_score(job, user_profile)
        category_score = self._calculate_category_score(job, user_profile)
        
        # Зважений середній скор
        total_score = (
            skill_score * self.filter_weights["skill_match"] +
            budget_score * self.filter_weights["budget_match"] +
            complexity_score * self.filter_weights["complexity_match"] +
            client_score * self.filter_weights["client_rating"] +
            timeline_score * self.filter_weights["timeline_match"] +
            location_score * self.filter_weights["location_match"] +
            category_score * self.filter_weights["category_match"]
        )
        
        # Застосовуємо фільтри
        if filters:
            total_score = self._apply_filters(total_score, job, filters)
        
        return max(0.0, min(1.0, total_score))
    
    def _calculate_skill_match_score(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Розрахунок скору відповідності навичок"""
        job_skills = job.get('skills', []) or []
        user_skills = user_profile.get('skills', []) or []
        
        if not job_skills or not user_skills:
            return 0.0
        
        # Розрахунок відповідності
        matching_skills = [skill for skill in job_skills if skill.lower() in [s.lower() for s in user_skills]]
        skill_match = len(matching_skills) / len(job_skills)
        
        # Вагований скор за важливістю навичок
        weighted_score = 0.0
        for skill in job_skills:
            if skill.lower() in [s.lower() for s in user_skills]:
                # Вага залежить від популярності навички
                weight = self._get_skill_weight(skill)
                weighted_score += weight
        
        # Нормалізуємо
        max_possible_weight = sum(self._get_skill_weight(skill) for skill in job_skills)
        weighted_score = weighted_score / max_possible_weight if max_possible_weight > 0 else 0.0
        
        # Комбінуємо простий та вагований скор
        return (skill_match + weighted_score) / 2
    
    def _calculate_budget_score(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Розрахунок скору бюджету"""
        job_budget = job.get('budget', '') or ''
        user_rate = user_profile.get('hourly_rate', '') or ''
        
        if not job_budget or not user_rate:
            return 0.5  # Нейтральний скор
        
        # Екстракція чисел з бюджету та ставки
        budget_value = self._extract_budget_value(job_budget)
        rate_value = self._extract_rate_value(user_rate)
        
        if budget_value == 0 or rate_value == 0:
            return 0.5
        
        # Розрахунок співвідношення
        ratio = budget_value / rate_value
        
        # Нормалізація скору
        if ratio >= 100:  # Дуже високий бюджет
            return 1.0
        elif ratio >= 50:  # Високий бюджет
            return 0.8
        elif ratio >= 20:  # Середній бюджет
            return 0.6
        elif ratio >= 10:  # Низький бюджет
            return 0.4
        else:  # Дуже низький бюджет
            return 0.2
    
    def _calculate_complexity_score(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Розрахунок скору складності"""
        description = job.get('description', '') or ''
        title = job.get('title', '') or ''
        user_experience = user_profile.get('experience', '') or ''
        
        # Оцінка складності проекту
        complexity_indicators = [
            "complex", "advanced", "enterprise", "large-scale",
            "microservices", "architecture", "system", "platform"
        ]
        
        text_lower = (description + " " + title).lower()
        complexity_count = sum(1 for indicator in complexity_indicators if indicator in text_lower)
        
        # Нормалізація складності (0-1)
        complexity_score = min(complexity_count / 5, 1.0)
        
        # Коригування за досвідом користувача
        experience_years = self._extract_experience_years(user_experience)
        
        if experience_years >= 5:  # Досвідчений розробник
            return complexity_score  # Високі складні проекти
        elif experience_years >= 2:  # Середній досвід
            return max(0.3, complexity_score * 0.8)  # Трохи менша складність
        else:  # Початківець
            return max(0.1, complexity_score * 0.5)  # Низька складність
    
    def _calculate_client_score(self, job: Dict[str, Any]) -> float:
        """Розрахунок скору клієнта"""
        client_rating = job.get('client_rating', 0)
        client_reviews = job.get('client_reviews', 0)
        client_spent = job.get('client_spent', 0)
        
        # Базовий скор за рейтингом
        rating_score = client_rating / 5.0 if client_rating > 0 else 0.5
        
        # Бонус за кількість відгуків
        review_bonus = min(client_reviews / 100, 0.2) if client_reviews > 0 else 0
        
        # Бонус за витрати клієнта
        spent_bonus = min(client_spent / 10000, 0.2) if client_spent > 0 else 0
        
        total_score = rating_score + review_bonus + spent_bonus
        return min(1.0, total_score)
    
    def _calculate_timeline_score(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Розрахунок скору термінів"""
        description = job.get('description', '') or ''
        user_availability = user_profile.get('availability', 'flexible') or 'flexible'
        
        # Аналіз терміновості
        urgent_indicators = ["urgent", "asap", "immediately", "quick", "fast"]
        flexible_indicators = ["flexible", "reasonable", "realistic", "no rush"]
        
        text_lower = description.lower()
        urgent_count = sum(1 for indicator in urgent_indicators if indicator in text_lower)
        flexible_count = sum(1 for indicator in flexible_indicators if indicator in text_lower)
        
        # Розрахунок скору
        if urgent_count > flexible_count:
            timeline_score = 0.3  # Термінові проекти менш бажані
        elif flexible_count > urgent_count:
            timeline_score = 0.8  # Гнучкі терміни бажані
        else:
            timeline_score = 0.6  # Нейтральні терміни
        
        # Коригування за доступністю користувача
        if user_availability == 'urgent':
            timeline_score = 1.0 if urgent_count > 0 else 0.5
        elif user_availability == 'flexible':
            timeline_score = 0.8 if flexible_count > 0 else 0.6
        
        return timeline_score
    
    def _calculate_location_score(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Розрахунок скору локації"""
        job_location = job.get('location', '') or ''
        user_location = user_profile.get('location', '') or ''
        user_timezone = user_profile.get('timezone', '') or ''
        
        if not job_location:
            return 0.5  # Нейтральний скор
        
        # Простий аналіз часових зон
        timezone_matches = {
            'UTC': ['UTC', 'GMT', 'Europe', 'UK'],
            'EST': ['EST', 'Eastern', 'US', 'America'],
            'PST': ['PST', 'Pacific', 'West Coast'],
            'CET': ['CET', 'Central Europe', 'Germany', 'France']
        }
        
        # Перевіряємо відповідність часових зон
        for user_tz, job_tz_list in timezone_matches.items():
            if user_timezone in user_tz:
                if any(tz in job_location for tz in job_tz_list):
                    return 0.9
                else:
                    return 0.3
        
        return 0.5  # Нейтральний скор
    
    def _calculate_category_score(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Розрахунок скору категорії"""
        description = job.get('description', '') or ''
        title = job.get('title', '') or ''
        user_preferences = user_profile.get('preferred_categories', []) or []
        
        text_lower = (description + " " + title).lower()
        
        # Перевіряємо відповідність категорій
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = keyword_matches / len(keywords) if keywords else 0
        
        # Знаходимо найкращу категорію
        best_category = max(category_scores.items(), key=lambda x: x[1])
        
        # Бонус за відповідність уподобанням
        preference_bonus = 0.2 if best_category[0] in user_preferences else 0
        
        return min(1.0, best_category[1] + preference_bonus)
    
    def _calculate_total_score(self, job: Dict[str, Any]) -> float:
        """Розрахунок загального скору"""
        scores = [
            job.get("skill_match_score", 0),
            job.get("budget_score", 0),
            job.get("complexity_score", 0),
            job.get("client_score", 0),
            job.get("timeline_score", 0),
            job.get("location_score", 0),
            job.get("category_score", 0)
        ]
        
        # Зважений середній
        weights = list(self.filter_weights.values())
        total_score = sum(score * weight for score, weight in zip(scores, weights))
        
        return total_score
    
    def _apply_filters(self, score: float, job: Dict[str, Any], filters: Dict[str, Any]) -> float:
        """Застосування додаткових фільтрів"""
        # Фільтр за бюджетом
        if 'min_budget' in filters:
            budget_value = self._extract_budget_value(job.get('budget', ''))
            if budget_value < filters['min_budget']:
                return 0.0
        
        # Фільтр за рейтингом клієнта
        if 'min_client_rating' in filters:
            client_rating = job.get('client_rating', 0)
            if client_rating < filters['min_client_rating']:
                return 0.0
        
        # Фільтр за навичками
        if 'required_skills' in filters:
            job_skills = [skill.lower() for skill in job.get('skills', [])]
            required_skills = [skill.lower() for skill in filters['required_skills']]
            if not any(skill in job_skills for skill in required_skills):
                return 0.0
        
        return score
    
    def _calculate_additional_metrics(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Розрахунок додаткових метрик"""
        return {
            "skill_match_score": self._calculate_skill_match_score(job, user_profile),
            "budget_score": self._calculate_budget_score(job, user_profile),
            "complexity_score": self._calculate_complexity_score(job, user_profile),
            "client_score": self._calculate_client_score(job),
            "timeline_score": self._calculate_timeline_score(job, user_profile),
            "location_score": self._calculate_location_score(job, user_profile),
            "category_score": self._calculate_category_score(job, user_profile),
            "total_score": 0.0  # Буде розраховано пізніше
        }
    
    def _generate_score_reason(self, job: Dict[str, Any], user_profile: Dict[str, Any], score: float) -> str:
        """Генерація причини скору"""
        reasons = []
        
        skill_score = self._calculate_skill_match_score(job, user_profile)
        if skill_score > 0.8:
            reasons.append("Висока відповідність навичок")
        elif skill_score < 0.3:
            reasons.append("Низька відповідність навичок")
        
        budget_score = self._calculate_budget_score(job, user_profile)
        if budget_score > 0.8:
            reasons.append("Високий бюджет")
        elif budget_score < 0.3:
            reasons.append("Низький бюджет")
        
        client_score = self._calculate_client_score(job)
        if client_score > 0.8:
            reasons.append("Високий рейтинг клієнта")
        elif client_score < 0.3:
            reasons.append("Низький рейтинг клієнта")
        
        if not reasons:
            reasons.append("Середня відповідність")
        
        return "; ".join(reasons)
    
    def _get_skill_weight(self, skill: str) -> float:
        """Отримання ваги навички"""
        skill_weights = {
            "python": 1.2, "javascript": 1.1, "react": 1.3,
            "node.js": 1.2, "django": 1.1, "postgresql": 1.0,
            "docker": 1.1, "aws": 1.2, "machine learning": 1.4,
            "ai": 1.4, "api": 1.1, "frontend": 1.0,
            "backend": 1.1, "fullstack": 1.2
        }
        return skill_weights.get(skill.lower(), 1.0)
    
    def _extract_budget_value(self, budget: str) -> float:
        """Екстракція числового значення з бюджету"""
        import re
        
        if not budget:
            return 0.0
        
        # Шукаємо числа в бюджеті
        numbers = re.findall(r'\d+(?:\.\d+)?', budget.replace(',', ''))
        if numbers:
            return float(numbers[0])
        
        return 0.0
    
    def _extract_rate_value(self, rate: str) -> float:
        """Екстракція числового значення з ставки"""
        import re
        
        if not rate:
            return 0.0
        
        # Шукаємо числа в ставці
        numbers = re.findall(r'\d+(?:\.\d+)?', rate.replace(',', ''))
        if numbers:
            return float(numbers[0])
        
        return 0.0
    
    def _extract_experience_years(self, experience: str) -> int:
        """Екстракція років досвіду"""
        import re
        
        if not experience:
            return 0
        
        # Шукаємо роки в тексті досвіду
        years = re.findall(r'(\d+)\s*(?:років?|years?)', experience.lower())
        if years:
            return int(years[0])
        
        return 0 