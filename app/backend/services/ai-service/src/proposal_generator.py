"""
Покращений ProposalGenerator з AI інтеграцією
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.logging import get_logger
from .ai_service import AIService

logger = get_logger("proposal-generator")


class ProposalGenerator:
    """Покращений генератор пропозицій з AI інтеграцією"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.templates = self._load_templates()
        self.keywords_db = self._load_keywords()
    
    def _load_templates(self) -> Dict[str, str]:
        """Завантаження базових шаблонів"""
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

## Креативні рішення
{creative_solutions}

## Результати
{expected_results}

Готовий створити щось унікальне!
            """,
            
            "budget_friendly": """
# Економічна пропозиція

## Оптимізація витрат
{budget_optimization}

## Ефективні рішення
{efficient_solutions}

## Якість за доступну ціну
{quality_approach}

## Гарантії
{guarantees}

Готовий працювати ефективно!
            """
        }
    
    def _load_keywords(self) -> Dict[str, List[str]]:
        """Завантаження ключових слів по категоріях"""
        return {
            "web_development": [
                "react", "vue", "angular", "javascript", "typescript",
                "node.js", "express", "django", "flask", "fastapi",
                "html", "css", "sass", "bootstrap", "tailwind"
            ],
            "mobile_development": [
                "react native", "flutter", "swift", "kotlin", "android",
                "ios", "mobile app", "cross-platform"
            ],
            "backend_development": [
                "python", "java", "c#", "php", "ruby", "go",
                "postgresql", "mysql", "mongodb", "redis", "docker",
                "kubernetes", "aws", "azure", "gcp"
            ],
            "design": [
                "ui/ux", "figma", "adobe", "photoshop", "illustrator",
                "sketch", "wireframe", "prototype", "user experience"
            ],
            "data_science": [
                "python", "r", "machine learning", "ai", "deep learning",
                "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"
            ]
        }
    
    async def generate_proposal(self, job_data: Dict[str, Any], user_profile: Dict[str, Any], 
                              template_name: Optional[str] = None) -> Dict[str, Any]:
        """Генерація пропозиції з AI"""
        try:
            # Аналізуємо вакансію
            job_analysis = await self._analyze_job(job_data)
            
            # Визначаємо тип шаблону
            template_type = template_name or self._determine_template_type(job_data, job_analysis)
            
            # Генеруємо пропозицію через AI
            ai_result = await self.ai_service.generate_proposal(job_data, user_profile, template_type)
            
            if ai_result["success"]:
                # Обробляємо AI результат
                proposal = self._process_ai_proposal(ai_result["proposal"], job_data, user_profile)
                
                return {
                    "success": True,
                    "proposal": proposal,
                    "template_type": template_type,
                    "analysis": job_analysis,
                    "model": ai_result["model"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Fallback до базового генератора
                logger.warning(f"AI генерація не вдалася: {ai_result.get('error')}, використовуємо fallback")
                return await self._generate_fallback_proposal(job_data, user_profile, template_type)
                
        except Exception as e:
            logger.error(f"Помилка генерації пропозиції: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _analyze_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Аналіз вакансії"""
        try:
            result = await self.ai_service.analyze_job(job_data)
            if result["success"]:
                return result["analysis"]
            else:
                return self._basic_job_analysis(job_data)
        except Exception as e:
            logger.error(f"Помилка аналізу вакансії: {e}")
            return self._basic_job_analysis(job_data)
    
    def _basic_job_analysis(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Базовий аналіз вакансії без AI"""
        description = job_data.get('description', '')
        budget = job_data.get('budget', '')
        skills = job_data.get('skills', [])
        
        # Простий аналіз
        complexity_score = self._assess_complexity(description)
        budget_adequacy = self._assess_budget(budget)
        skill_match = self._assess_skill_match(skills)
        
        return {
            "complexity_score": complexity_score,
            "budget_adequacy": budget_adequacy,
            "skill_match": skill_match,
            "estimated_hours": self._estimate_duration(description),
            "recommended_rate": self._calculate_rate(budget, complexity_score)
        }
    
    def _determine_template_type(self, job_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Визначення типу шаблону"""
        description = job_data.get('description', '').lower()
        budget = job_data.get('budget', '')
        complexity = analysis.get('complexity_score', 5)
        
        # Технічні проекти
        if any(word in description for word in ['api', 'backend', 'database', 'server']):
            return 'technical'
        
        # Креативні проекти
        if any(word in description for word in ['design', 'creative', 'ui/ux', 'branding']):
            return 'creative'
        
        # Бюджетні проекти
        if 'budget' in description or 'cheap' in description or 'affordable' in description:
            return 'budget_friendly'
        
        # За замовчуванням
        return 'default'
    
    def _process_ai_proposal(self, ai_proposal: Dict[str, Any], job_data: Dict[str, Any], 
                           user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Обробка AI пропозиції"""
        proposal_text = ai_proposal.get('proposal_text', '')
        
        # Додаємо метадані
        processed_proposal = {
            "content": proposal_text,
            "estimated_hours": ai_proposal.get('estimated_hours', 'Не вказано'),
            "proposed_rate": ai_proposal.get('proposed_rate', 'Не вказано'),
            "timeline": ai_proposal.get('timeline', 'Не вказано'),
            "key_points": ai_proposal.get('key_points', []),
            "questions": ai_proposal.get('questions', []),
            "job_title": job_data.get('title', ''),
            "client_name": job_data.get('client_name', ''),
            "budget": job_data.get('budget', ''),
            "user_skills": user_profile.get('skills', []),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return processed_proposal
    
    async def _generate_fallback_proposal(self, job_data: Dict[str, Any], user_profile: Dict[str, Any], 
                                        template_type: str) -> Dict[str, Any]:
        """Fallback генерація пропозиції без AI"""
        try:
            template = self.templates.get(template_type, self.templates['default'])
            
            # Персоналізуємо шаблон
            personalized_content = self._personalize_template(template, job_data, user_profile)
            
            # Створюємо пропозицію
            proposal = {
                "content": personalized_content,
                "estimated_hours": self._estimate_duration(job_data.get('description', '')),
                "proposed_rate": self._calculate_rate(job_data.get('budget', ''), 5),
                "timeline": self._estimate_timeline(job_data.get('description', '')),
                "key_points": self._extract_key_points(job_data),
                "questions": self._generate_questions(job_data),
                "job_title": job_data.get('title', ''),
                "client_name": job_data.get('client_name', ''),
                "budget": job_data.get('budget', ''),
                "user_skills": user_profile.get('skills', []),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "proposal": proposal,
                "template_type": template_type,
                "fallback": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка fallback генерації: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _personalize_template(self, template: str, job_data: Dict[str, Any], 
                            user_profile: Dict[str, Any]) -> str:
        """Персоналізація шаблону"""
        personalized = template
        
        # Замінюємо плейсхолдери
        replacements = {
            "{user_profile}": self._format_user_profile(user_profile),
            "{technical_approach}": self._generate_technical_approach(job_data),
            "{architecture}": self._generate_architecture(job_data),
            "{tech_stack}": self._generate_tech_stack(job_data, user_profile),
            "{implementation_plan}": self._generate_implementation_plan(job_data),
            "{creative_approach}": self._generate_creative_approach(job_data),
            "{unique_advantages}": self._generate_unique_advantages(user_profile),
            "{creative_solutions}": self._generate_creative_solutions(job_data),
            "{expected_results}": self._generate_expected_results(job_data),
            "{budget_optimization}": self._generate_budget_optimization(job_data),
            "{efficient_solutions}": self._generate_efficient_solutions(job_data),
            "{quality_approach}": self._generate_quality_approach(),
            "{guarantees}": self._generate_guarantees()
        }
        
        for placeholder, value in replacements.items():
            personalized = personalized.replace(placeholder, value)
        
        return personalized
    
    def _format_user_profile(self, user_profile: Dict[str, Any]) -> str:
        """Форматування профілю користувача"""
        skills = user_profile.get('skills', [])
        experience = user_profile.get('experience', '')
        rate = user_profile.get('hourly_rate', '')
        
        profile = f"Досвідчений розробник з {experience} досвіду роботи.\n"
        profile += f"Навички: {', '.join(skills[:5])}\n"
        profile += f"Ставка: {rate}\n"
        
        return profile
    
    def _generate_technical_approach(self, job_data: Dict[str, Any]) -> str:
        """Генерація технічного підходу"""
        description = job_data.get('description', '')
        
        if 'api' in description.lower():
            return "RESTful API з документацією та тестуванням"
        elif 'database' in description.lower():
            return "Оптимізована база даних з індексацією"
        elif 'frontend' in description.lower():
            return "Responsive UI з сучасними фреймворками"
        else:
            return "Сучасний технічний підхід з найкращими практиками"
    
    def _generate_architecture(self, job_data: Dict[str, Any]) -> str:
        """Генерація архітектури"""
        return "Модульна архітектура з можливістю масштабування"
    
    def _generate_tech_stack(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Генерація технологічного стеку"""
        user_skills = user_profile.get('skills', [])
        job_skills = job_data.get('skills', [])
        
        # Об'єднуємо навички
        all_skills = list(set(user_skills + job_skills))
        return ", ".join(all_skills[:5])
    
    def _generate_implementation_plan(self, job_data: Dict[str, Any]) -> str:
        """Генерація плану реалізації"""
        return "1. Аналіз вимог\n2. Проектування\n3. Розробка\n4. Тестування\n5. Деплой"
    
    def _generate_creative_approach(self, job_data: Dict[str, Any]) -> str:
        """Генерація креативного підходу"""
        return "Унікальний дизайн з фокусом на користувацький досвід"
    
    def _generate_unique_advantages(self, user_profile: Dict[str, Any]) -> str:
        """Генерація унікальних переваг"""
        skills = user_profile.get('skills', [])
        return f"Досвід у технологіях: {', '.join(skills[:3])}"
    
    def _generate_creative_solutions(self, job_data: Dict[str, Any]) -> str:
        """Генерація креативних рішень"""
        return "Інноваційні підходи до вирішення задач"
    
    def _generate_expected_results(self, job_data: Dict[str, Any]) -> str:
        """Генерація очікуваних результатів"""
        return "Високоякісний продукт, що відповідає всім вимогам"
    
    def _generate_budget_optimization(self, job_data: Dict[str, Any]) -> str:
        """Генерація оптимізації бюджету"""
        return "Ефективне використання ресурсів для зниження витрат"
    
    def _generate_efficient_solutions(self, job_data: Dict[str, Any]) -> str:
        """Генерація ефективних рішень"""
        return "Оптимізовані рішення для швидкої реалізації"
    
    def _generate_quality_approach(self) -> str:
        """Генерація підходу до якості"""
        return "Високі стандарти якості за доступну ціну"
    
    def _generate_guarantees(self) -> str:
        """Генерація гарантій"""
        return "Гарантія якості та підтримка після завершення"
    
    def _assess_complexity(self, description: str) -> int:
        """Оцінка складності проекту"""
        complexity_indicators = [
            "складний", "complex", "advanced", "enterprise", "large-scale",
            "мікросервіси", "microservices", "архітектура", "architecture"
        ]
        
        text_lower = description.lower()
        score = sum(1 for indicator in complexity_indicators if indicator in text_lower)
        
        return min(score + 3, 10)  # Мінімум 3, максимум 10
    
    def _assess_budget(self, budget: str) -> str:
        """Оцінка бюджету"""
        if not budget:
            return "unknown"
        
        budget_lower = budget.lower()
        if any(word in budget_lower for word in ['high', 'великий', 'дорого']):
            return "good"
        elif any(word in budget_lower for word in ['low', 'малий', 'дешево']):
            return "bad"
        else:
            return "unknown"
    
    def _assess_skill_match(self, skills: List[str]) -> float:
        """Оцінка відповідності навичок"""
        if not skills:
            return 0.5
        
        # Простий алгоритм оцінки
        return min(len(skills) / 10, 1.0)
    
    def _estimate_duration(self, description: str) -> str:
        """Оцінка тривалості"""
        word_count = len(description.split())
        
        if word_count < 50:
            return "1-2 тижні"
        elif word_count < 100:
            return "2-4 тижні"
        elif word_count < 200:
            return "1-2 місяці"
        else:
            return "2-3 місяці"
    
    def _calculate_rate(self, budget: str, complexity: int) -> str:
        """Розрахунок ставки"""
        if not budget:
            return "$25-50/год"
        
        # Простий розрахунок на основі складності
        base_rate = 25 + (complexity - 3) * 5
        return f"${base_rate}-{base_rate + 25}/год"
    
    def _estimate_timeline(self, description: str) -> str:
        """Оцінка термінів"""
        return self._estimate_duration(description)
    
    def _extract_key_points(self, job_data: Dict[str, Any]) -> List[str]:
        """Витягування ключових моментів"""
        description = job_data.get('description', '')
        skills = job_data.get('skills', [])
        
        points = []
        if skills:
            points.append(f"Досвід у технологіях: {', '.join(skills[:3])}")
        
        if 'api' in description.lower():
            points.append("Розробка RESTful API")
        
        if 'database' in description.lower():
            points.append("Робота з базами даних")
        
        if 'frontend' in description.lower():
            points.append("Сучасний UI/UX дизайн")
        
        return points[:5]
    
    def _generate_questions(self, job_data: Dict[str, Any]) -> List[str]:
        """Генерація питань до клієнта"""
        return [
            "Чи є додаткові вимоги до проекту?",
            "Які терміни реалізації очікуються?",
            "Чи потрібна підтримка після завершення?",
            "Чи є приклади подібних проектів?"
        ] 