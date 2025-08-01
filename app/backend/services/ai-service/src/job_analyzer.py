"""
Покращений JobAnalyzer з AI інтеграцією
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.logging import get_logger
from .ai_service import AIService

logger = get_logger("job-analyzer")


class JobAnalyzer:
    """Покращений аналізатор вакансій з AI інтеграцією"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.red_flags = self._load_red_flags()
        self.green_flags = self._load_green_flags()
        self.skill_weights = self._load_skill_weights()
    
    def _load_red_flags(self) -> List[str]:
        """Завантаження червоних прапорців"""
        return [
            "urgent", "asap", "immediately", "quick", "fast",
            "cheap", "low budget", "minimum price", "affordable",
            "simple", "easy", "basic", "entry level",
            "no experience needed", "beginners welcome",
            "payment after completion", "milestone payment",
            "fixed price only", "no hourly",
            "long term", "ongoing", "permanent",
            "work for equity", "partnership opportunity",
            "revolutionary", "next big thing", "disruptive"
        ]
    
    def _load_green_flags(self) -> List[str]:
        """Завантаження зелених прапорців"""
        return [
            "professional", "experienced", "expert", "senior",
            "competitive rate", "market rate", "fair compensation",
            "detailed requirements", "clear scope", "well-defined",
            "quality focused", "best practices", "standards",
            "reasonable timeline", "flexible schedule",
            "good communication", "regular updates",
            "testing required", "documentation needed",
            "maintenance included", "support provided"
        ]
    
    def _load_skill_weights(self) -> Dict[str, float]:
        """Завантаження ваг навичок"""
        return {
            "python": 1.2,
            "javascript": 1.1,
            "react": 1.3,
            "node.js": 1.2,
            "django": 1.1,
            "postgresql": 1.0,
            "docker": 1.1,
            "aws": 1.2,
            "machine learning": 1.4,
            "ai": 1.4,
            "api": 1.1,
            "frontend": 1.0,
            "backend": 1.1,
            "fullstack": 1.2
        }
    
    async def analyze_job(self, job_data: Dict[str, Any], user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Повний аналіз вакансії з AI"""
        try:
            # Аналіз через AI
            ai_result = await self.ai_service.analyze_job(job_data)
            
            if ai_result["success"]:
                # Обробляємо AI результат
                analysis = self._process_ai_analysis(ai_result["analysis"], job_data, user_profile)
                analysis["ai_model"] = ai_result["model"]
            else:
                # Fallback до базового аналізу
                logger.warning(f"AI аналіз не вдався: {ai_result.get('error')}, використовуємо fallback")
                analysis = self._basic_job_analysis(job_data, user_profile)
                analysis["ai_model"] = "fallback"
            
            # Додаємо додатковий аналіз
            analysis.update(self._additional_analysis(job_data, user_profile))
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка аналізу вакансії: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _process_ai_analysis(self, ai_analysis: Dict[str, Any], job_data: Dict[str, Any], 
                           user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Обробка AI аналізу"""
        # Додаємо метадані
        processed_analysis = {
            "complexity_score": ai_analysis.get('complexity_score', 5),
            "budget_adequacy": ai_analysis.get('budget_adequacy', 'unknown'),
            "requirements_clarity": ai_analysis.get('requirements_clarity', 'unclear'),
            "competition_level": ai_analysis.get('competition_level', 'medium'),
            "risks": ai_analysis.get('risks', []),
            "opportunities": ai_analysis.get('opportunities', []),
            "recommended_rate": ai_analysis.get('recommended_rate', 'Не вказано'),
            "estimated_hours": ai_analysis.get('estimated_hours', 'Не вказано'),
            "success_probability": ai_analysis.get('success_probability', 0.5),
            "red_flags": ai_analysis.get('red_flags', []),
            "green_flags": ai_analysis.get('green_flags', []),
            "job_title": job_data.get('title', ''),
            "client_rating": job_data.get('client_rating', 0),
            "budget": job_data.get('budget', ''),
            "skills_required": job_data.get('skills', [])
        }
        
        return processed_analysis
    
    def _basic_job_analysis(self, job_data: Dict[str, Any], user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Базовий аналіз вакансії без AI"""
        description = job_data.get('description', '')
        title = job_data.get('title', '')
        budget = job_data.get('budget', '')
        skills = job_data.get('skills', [])
        client_rating = job_data.get('client_rating', 0)
        
        # Аналіз складності
        complexity_score = self._assess_complexity(description, title)
        
        # Аналіз бюджету
        budget_adequacy = self._assess_budget_adequacy(budget, complexity_score)
        
        # Аналіз чіткості вимог
        requirements_clarity = self._assess_requirements_clarity(description)
        
        # Аналіз конкурентності
        competition_level = self._assess_competition_level(description, budget)
        
        # Аналіз ризиків та можливостей
        risks = self._identify_risks(description, budget, client_rating)
        opportunities = self._identify_opportunities(description, skills, user_profile)
        
        # Розрахунок ймовірності успіху
        success_probability = self._calculate_success_probability(
            complexity_score, budget_adequacy, requirements_clarity, 
            competition_level, client_rating, risks, opportunities
        )
        
        # Рекомендована ставка
        recommended_rate = self._calculate_recommended_rate(budget, complexity_score, client_rating)
        
        # Оцінка годин
        estimated_hours = self._estimate_hours(description, complexity_score)
        
        # Червоні та зелені прапорці
        red_flags = self._detect_red_flags(description)
        green_flags = self._detect_green_flags(description)
        
        return {
            "complexity_score": complexity_score,
            "budget_adequacy": budget_adequacy,
            "requirements_clarity": requirements_clarity,
            "competition_level": competition_level,
            "risks": risks,
            "opportunities": opportunities,
            "success_probability": success_probability,
            "recommended_rate": recommended_rate,
            "estimated_hours": estimated_hours,
            "red_flags": red_flags,
            "green_flags": green_flags
        }
    
    def _additional_analysis(self, job_data: Dict[str, Any], user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Додатковий аналіз"""
        description = job_data.get('description', '')
        skills = job_data.get('skills', [])
        
        # Аналіз навичок
        skill_analysis = self._analyze_skills(skills, user_profile)
        
        # Аналіз тексту
        text_analysis = self._analyze_text(description)
        
        # Аналіз термінів
        timeline_analysis = self._analyze_timeline(description)
        
        # Аналіз комунікації
        communication_analysis = self._analyze_communication(description)
        
        return {
            "skill_analysis": skill_analysis,
            "text_analysis": text_analysis,
            "timeline_analysis": timeline_analysis,
            "communication_analysis": communication_analysis
        }
    
    def _assess_complexity(self, description: str, title: str) -> int:
        """Оцінка складності проекту"""
        complexity_indicators = [
            "складний", "complex", "advanced", "enterprise", "large-scale",
            "мікросервіси", "microservices", "архітектура", "architecture",
            "система", "system", "платформа", "platform", "інтеграція", "integration"
        ]
        
        text_lower = (description + " " + title).lower()
        score = sum(1 for indicator in complexity_indicators if indicator in text_lower)
        
        # Додаткові фактори
        if len(description.split()) > 200:
            score += 2
        if any(word in text_lower for word in ['api', 'database', 'backend']):
            score += 1
        
        return min(score + 3, 10)  # Мінімум 3, максимум 10
    
    def _assess_budget_adequacy(self, budget: str, complexity: int) -> str:
        """Оцінка адекватності бюджету"""
        if not budget:
            return "unknown"
        
        budget_lower = budget.lower()
        
        # Аналізуємо бюджет
        if any(word in budget_lower for word in ['high', 'великий', 'дорого', 'premium']):
            return "good"
        elif any(word in budget_lower for word in ['low', 'малий', 'дешево', 'cheap', 'affordable']):
            return "bad"
        elif any(word in budget_lower for word in ['medium', 'середній', 'reasonable']):
            return "medium"
        else:
            return "unknown"
    
    def _assess_requirements_clarity(self, description: str) -> str:
        """Оцінка чіткості вимог"""
        clarity_indicators = [
            "детальний", "detailed", "конкретний", "specific",
            "вимоги", "requirements", "функціональність", "functionality",
            "технічні", "technical", "специфікація", "specification"
        ]
        
        unclear_indicators = [
            "простий", "simple", "базовий", "basic", "легкий", "easy",
            "щось", "something", "подібний", "similar", "як", "like"
        ]
        
        text_lower = description.lower()
        clarity_score = sum(1 for indicator in clarity_indicators if indicator in text_lower)
        unclear_score = sum(1 for indicator in unclear_indicators if indicator in text_lower)
        
        if clarity_score > unclear_score:
            return "clear"
        elif unclear_score > clarity_score:
            return "unclear"
        else:
            return "medium"
    
    def _assess_competition_level(self, description: str, budget: str) -> str:
        """Оцінка рівня конкуренції"""
        competition_indicators = [
            "простий", "simple", "базовий", "basic", "entry level",
            "початківець", "beginner", "студент", "student"
        ]
        
        high_competition_indicators = [
            "складний", "complex", "експерт", "expert", "senior",
            "спеціаліст", "specialist", "досвідчений", "experienced"
        ]
        
        text_lower = description.lower()
        budget_lower = budget.lower()
        
        competition_score = sum(1 for indicator in competition_indicators if indicator in text_lower)
        high_competition_score = sum(1 for indicator in high_competition_indicators if indicator in text_lower)
        
        # Бюджет також впливає на конкуренцію
        if any(word in budget_lower for word in ['high', 'великий']):
            high_competition_score += 1
        elif any(word in budget_lower for word in ['low', 'малий']):
            competition_score += 1
        
        if high_competition_score > competition_score:
            return "low"
        elif competition_score > high_competition_score:
            return "high"
        else:
            return "medium"
    
    def _identify_risks(self, description: str, budget: str, client_rating: float) -> List[str]:
        """Ідентифікація ризиків"""
        risks = []
        
        # Аналіз тексту на ризики
        risk_indicators = {
            "Низький бюджет": ["cheap", "low budget", "affordable", "дешево"],
            "Нечіткі вимоги": ["simple", "basic", "easy", "простий"],
            "Терміновість": ["urgent", "asap", "immediately", "швидко"],
            "Складність проекту": ["complex", "advanced", "enterprise", "складний"],
            "Низький рейтинг клієнта": []  # Перевіряємо окремо
        }
        
        text_lower = description.lower()
        budget_lower = budget.lower()
        
        for risk, indicators in risk_indicators.items():
            if any(indicator in text_lower or indicator in budget_lower for indicator in indicators):
                risks.append(risk)
        
        # Перевіряємо рейтинг клієнта
        if client_rating < 4.0:
            risks.append("Низький рейтинг клієнта")
        
        return risks
    
    def _identify_opportunities(self, description: str, skills: List[str], user_profile: Optional[Dict[str, Any]] = None) -> List[str]:
        """Ідентифікація можливостей"""
        opportunities = []
        
        # Аналіз навичок
        if user_profile:
            user_skills = user_profile.get('skills', [])
            skill_match = self._calculate_skill_match(skills, user_skills)
            if skill_match > 0.7:
                opportunities.append("Висока відповідність навичок")
        
        # Аналіз тексту на можливості
        opportunity_indicators = {
            "Довгострокова співпраця": ["long term", "ongoing", "permanent", "тривалий"],
            "Технічний виклик": ["complex", "advanced", "challenging", "складний"],
            "Високий бюджет": ["high budget", "premium", "дорого"],
            "Якісний проект": ["quality", "professional", "expert", "якісний"]
        }
        
        text_lower = description.lower()
        
        for opportunity, indicators in opportunity_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                opportunities.append(opportunity)
        
        return opportunities
    
    def _calculate_success_probability(self, complexity: int, budget_adequacy: str, 
                                     requirements_clarity: str, competition_level: str,
                                     client_rating: float, risks: List[str], opportunities: List[str]) -> float:
        """Розрахунок ймовірності успіху"""
        probability = 0.5  # Базова ймовірність
        
        # Фактори, що збільшують ймовірність
        if budget_adequacy == "good":
            probability += 0.1
        if requirements_clarity == "clear":
            probability += 0.1
        if competition_level == "low":
            probability += 0.1
        if client_rating >= 4.5:
            probability += 0.1
        if len(opportunities) > len(risks):
            probability += 0.1
        
        # Фактори, що зменшують ймовірність
        if budget_adequacy == "bad":
            probability -= 0.1
        if requirements_clarity == "unclear":
            probability -= 0.1
        if competition_level == "high":
            probability -= 0.1
        if client_rating < 3.5:
            probability -= 0.1
        if len(risks) > len(opportunities):
            probability -= 0.1
        
        return max(0.0, min(1.0, probability))
    
    def _calculate_recommended_rate(self, budget: str, complexity: int, client_rating: float) -> str:
        """Розрахунок рекомендованої ставки"""
        # Базова ставка залежно від складності
        base_rate = 25 + (complexity - 3) * 5
        
        # Коригування за рейтингом клієнта
        if client_rating >= 4.5:
            base_rate += 10
        elif client_rating < 3.5:
            base_rate -= 5
        
        # Коригування за бюджетом
        budget_lower = budget.lower()
        if any(word in budget_lower for word in ['high', 'великий']):
            base_rate += 15
        elif any(word in budget_lower for word in ['low', 'малий']):
            base_rate -= 10
        
        return f"${max(15, base_rate)}-{max(15, base_rate + 25)}/год"
    
    def _estimate_hours(self, description: str, complexity: int) -> str:
        """Оцінка годин роботи"""
        word_count = len(description.split())
        
        # Базова оцінка за кількістю слів
        base_hours = word_count * 0.5
        
        # Коригування за складністю
        complexity_multiplier = 1 + (complexity - 5) * 0.2
        
        estimated_hours = base_hours * complexity_multiplier
        
        if estimated_hours < 10:
            return "5-15 годин"
        elif estimated_hours < 40:
            return "15-40 годин"
        elif estimated_hours < 100:
            return "40-100 годин"
        else:
            return "100+ годин"
    
    def _detect_red_flags(self, description: str) -> List[str]:
        """Виявлення червоних прапорців"""
        text_lower = description.lower()
        detected_flags = []
        
        for flag in self.red_flags:
            if flag in text_lower:
                detected_flags.append(flag)
        
        return detected_flags
    
    def _detect_green_flags(self, description: str) -> List[str]:
        """Виявлення зелених прапорців"""
        text_lower = description.lower()
        detected_flags = []
        
        for flag in self.green_flags:
            if flag in text_lower:
                detected_flags.append(flag)
        
        return detected_flags
    
    def _analyze_skills(self, job_skills: List[str], user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Аналіз навичок"""
        if not user_profile:
            return {
                "skill_match": 0.0,
                "missing_skills": job_skills,
                "matching_skills": [],
                "skill_weights": {}
            }
        
        user_skills = user_profile.get('skills', [])
        
        # Розрахунок відповідності навичок
        matching_skills = [skill for skill in job_skills if skill.lower() in [s.lower() for s in user_skills]]
        missing_skills = [skill for skill in job_skills if skill.lower() not in [s.lower() for s in user_skills]]
        
        # Розрахунок вагованої відповідності
        total_weight = 0
        matched_weight = 0
        
        for skill in job_skills:
            weight = self.skill_weights.get(skill.lower(), 1.0)
            total_weight += weight
            
            if skill.lower() in [s.lower() for s in user_skills]:
                matched_weight += weight
        
        skill_match = matched_weight / total_weight if total_weight > 0 else 0.0
        
        return {
            "skill_match": skill_match,
            "missing_skills": missing_skills,
            "matching_skills": matching_skills,
            "skill_weights": {skill: self.skill_weights.get(skill.lower(), 1.0) for skill in job_skills}
        }
    
    def _analyze_text(self, description: str) -> Dict[str, Any]:
        """Аналіз тексту"""
        words = description.split()
        
        return {
            "word_count": len(words),
            "character_count": len(description),
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "has_technical_terms": any(word.lower() in self.skill_weights for word in words),
            "readability_score": self._calculate_readability(description)
        }
    
    def _calculate_readability(self, text: str) -> float:
        """Розрахунок читабельності"""
        sentences = re.split(r'[.!?]+', text)
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Простий алгоритм читабельності (менше = легше читати)
        if avg_sentence_length < 10:
            return 0.9
        elif avg_sentence_length < 15:
            return 0.7
        elif avg_sentence_length < 20:
            return 0.5
        else:
            return 0.3
    
    def _analyze_timeline(self, description: str) -> Dict[str, Any]:
        """Аналіз термінів"""
        text_lower = description.lower()
        
        timeline_indicators = {
            "urgent": ["urgent", "asap", "immediately", "швидко", "терміново"],
            "flexible": ["flexible", "reasonable", "realistic", "гнучкий"],
            "long_term": ["long term", "ongoing", "permanent", "тривалий"],
            "short_term": ["short term", "quick", "fast", "короткий"]
        }
        
        detected_timelines = {}
        for timeline_type, indicators in timeline_indicators.items():
            detected_timelines[timeline_type] = any(indicator in text_lower for indicator in indicators)
        
        return detected_timelines
    
    def _analyze_communication(self, description: str) -> Dict[str, Any]:
        """Аналіз комунікації"""
        text_lower = description.lower()
        
        communication_indicators = {
            "good_communication": ["communication", "updates", "regular", "комунікація"],
            "detailed_requirements": ["detailed", "specific", "requirements", "детальний"],
            "professional": ["professional", "expert", "experienced", "професійний"],
            "collaborative": ["collaboration", "team", "partnership", "співпраця"]
        }
        
        detected_communication = {}
        for comm_type, indicators in communication_indicators.items():
            detected_communication[comm_type] = any(indicator in text_lower for indicator in indicators)
        
        return detected_communication
    
    def _calculate_skill_match(self, job_skills: List[str], user_skills: List[str]) -> float:
        """Розрахунок відповідності навичок"""
        if not job_skills or not user_skills:
            return 0.0
        
        matching_skills = [skill for skill in job_skills if skill.lower() in [s.lower() for s in user_skills]]
        return len(matching_skills) / len(job_skills) 