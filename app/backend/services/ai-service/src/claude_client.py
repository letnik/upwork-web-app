"""
Claude Client для fallback інтеграції з Anthropic Claude
"""

import anthropic
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.settings import settings
from shared.config.logging import get_logger

logger = get_logger("claude-client")


class ClaudeClient:
    """Клієнт для роботи з Anthropic Claude API"""
    
    def __init__(self):
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Налаштування Claude клієнта"""
        try:
            api_key = settings.CLAUDE_API_KEY
            if not api_key:
                logger.warning("Claude API ключ не налаштований")
                return
            
            self.client = anthropic.Anthropic(api_key=api_key)
            logger.info("Claude клієнт успішно налаштований")
            
        except Exception as e:
            logger.error(f"Помилка налаштування Claude клієнта: {e}")
            self.client = None
    
    async def generate_proposal(self, job_data: Dict[str, Any], user_profile: Dict[str, Any], 
                              template: Optional[str] = None) -> Dict[str, Any]:
        """Генерація пропозиції за допомогою Claude"""
        try:
            if not self.client:
                raise Exception("Claude клієнт не налаштований")
            
            # Формуємо промпт
            prompt = self._create_proposal_prompt(job_data, user_profile, template)
            
            # Викликаємо Claude
            response = await self._call_claude(prompt)
            
            # Парсимо відповідь
            proposal = self._parse_proposal_response(response)
            
            return {
                "success": True,
                "proposal": proposal,
                "model": "claude-3-sonnet",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка генерації пропозиції через Claude: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": "claude-3-sonnet",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def analyze_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Аналіз вакансії за допомогою Claude"""
        try:
            if not self.client:
                raise Exception("Claude клієнт не налаштований")
            
            # Формуємо промпт для аналізу
            prompt = self._create_job_analysis_prompt(job_data)
            
            # Викликаємо Claude
            response = await self._call_claude(prompt)
            
            # Парсимо відповідь
            analysis = self._parse_analysis_response(response)
            
            return {
                "success": True,
                "analysis": analysis,
                "model": "claude-3-sonnet",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка аналізу вакансії через Claude: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": "claude-3-sonnet",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def filter_jobs(self, jobs: List[Dict[str, Any]], user_profile: Dict[str, Any], 
                         filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Фільтрація вакансій за допомогою Claude"""
        try:
            if not self.client:
                raise Exception("Claude клієнт не налаштований")
            
            # Формуємо промпт для фільтрації
            prompt = self._create_filtering_prompt(jobs, user_profile, filters)
            
            # Викликаємо Claude
            response = await self._call_claude(prompt)
            
            # Парсимо відповідь
            filtered_jobs = self._parse_filtering_response(response, jobs)
            
            return {
                "success": True,
                "filtered_jobs": filtered_jobs,
                "model": "claude-3-sonnet",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка фільтрації вакансій через Claude: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": "claude-3-sonnet",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _create_proposal_prompt(self, job_data: Dict[str, Any], user_profile: Dict[str, Any], 
                               template: Optional[str] = None) -> str:
        """Створення промпту для генерації пропозиції"""
        job_title = job_data.get('title', 'Unknown')
        job_description = job_data.get('description', '')
        budget = job_data.get('budget', 'Not specified')
        skills = job_data.get('skills', [])
        
        user_skills = user_profile.get('skills', [])
        user_experience = user_profile.get('experience', '')
        user_rate = user_profile.get('hourly_rate', '')
        
        prompt = f"""
Ти - експерт з написання пропозицій на Upwork. Створи професійну та переконливу пропозицію для наступної вакансії.

ВАКАНСІЯ:
Назва: {job_title}
Опис: {job_description}
Бюджет: {budget}
Потрібні навички: {', '.join(skills) if skills else 'Не вказано'}

ПРОФІЛЬ ФРІЛАНСЕРА:
Навички: {', '.join(user_skills) if user_skills else 'Не вказано'}
Досвід: {user_experience}
Ставка: {user_rate}

ВИМОГИ ДО ПРОПОЗИЦІЇ:
1. Персоналізована під конкретну вакансію
2. Показує розуміння проекту
3. Демонструє відповідність навичок
4. Професійний тон
5. Конкретні приклади досвіду
6. Чіткий план роботи
7. Максимум 500 слів

Створи пропозицію в JSON форматі:
{{
    "proposal_text": "текст пропозиції",
    "estimated_hours": "оцінка годин",
    "proposed_rate": "запропонована ставка",
    "timeline": "термін виконання",
    "key_points": ["ключові моменти"],
    "questions": ["питання до клієнта"]
}}
"""
        return prompt
    
    def _create_job_analysis_prompt(self, job_data: Dict[str, Any]) -> str:
        """Створення промпту для аналізу вакансії"""
        job_title = job_data.get('title', 'Unknown')
        job_description = job_data.get('description', '')
        budget = job_data.get('budget', 'Not specified')
        skills = job_data.get('skills', [])
        
        prompt = f"""
Проаналізуй наступну вакансію на Upwork та надай детальну оцінку.

ВАКАНСІЯ:
Назва: {job_title}
Опис: {job_description}
Бюджет: {budget}
Навички: {', '.join(skills) if skills else 'Не вказано'}

ПРОВЕДИ АНАЛІЗ:
1. Складність проекту (1-10)
2. Відповідність бюджету
3. Чіткість вимог
4. Конкурентність
5. Ризики
6. Можливості

Поверни результат в JSON форматі:
{{
    "complexity_score": 7,
    "budget_adequacy": "good/bad/unknown",
    "requirements_clarity": "clear/unclear",
    "competition_level": "low/medium/high",
    "risks": ["список ризиків"],
    "opportunities": ["список можливостей"],
    "recommended_rate": "рекомендована ставка",
    "estimated_hours": "оцінка годин",
    "success_probability": 0.85,
    "red_flags": ["червоні прапорці"],
    "green_flags": ["позитивні моменти"]
}}
"""
        return prompt
    
    def _create_filtering_prompt(self, jobs: List[Dict[str, Any]], user_profile: Dict[str, Any], 
                                filters: Optional[Dict[str, Any]] = None) -> str:
        """Створення промпту для фільтрації вакансій"""
        user_skills = user_profile.get('skills', [])
        user_rate = user_profile.get('hourly_rate', '')
        
        jobs_text = ""
        for i, job in enumerate(jobs[:10]):  # Обмежуємо до 10 вакансій
            jobs_text += f"""
{i+1}. {job.get('title', 'Unknown')}
   Бюджет: {job.get('budget', 'Not specified')}
   Навички: {', '.join(job.get('skills', []))}
   Опис: {job.get('description', '')[:200]}...
"""
        
        prompt = f"""
Проаналізуй список вакансій та відбери найкращі для фрілансера.

ПРОФІЛЬ ФРІЛАНСЕРА:
Навички: {', '.join(user_skills) if user_skills else 'Не вказано'}
Ставка: {user_rate}

ФІЛЬТРИ:
{filters if filters else 'Без додаткових фільтрів'}

ВАКАНСІЇ:
{jobs_text}

ВИБЕРИ НАЙКРАЩІ ВАКАНСІЇ (максимум 5) та поверни в JSON форматі:
{{
    "selected_jobs": [1, 3, 5],
    "reasons": {{
        "1": "причина вибору вакансії 1",
        "3": "причина вибору вакансії 3",
        "5": "причина вибору вакансії 5"
    }},
    "scores": {{
        "1": 0.85,
        "3": 0.92,
        "5": 0.78
    }}
}}
"""
        return prompt
    
    async def _call_claude(self, prompt: str) -> str:
        """Виклик Claude API"""
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": f"Ти - експерт з Upwork та фрілансингу. Надавай корисні та практичні поради.\n\n{prompt}"
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Помилка виклику Claude: {e}")
            raise
    
    def _parse_proposal_response(self, response: str) -> Dict[str, Any]:
        """Парсинг відповіді з пропозицією"""
        try:
            # Спробуємо знайти JSON в відповіді
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Якщо JSON не знайдено, повертаємо текст як є
                return {
                    "proposal_text": response,
                    "estimated_hours": "Не вказано",
                    "proposed_rate": "Не вказано",
                    "timeline": "Не вказано",
                    "key_points": [],
                    "questions": []
                }
                
        except json.JSONDecodeError:
            logger.warning("Не вдалося розпарсити JSON відповідь Claude")
            return {
                "proposal_text": response,
                "estimated_hours": "Не вказано",
                "proposed_rate": "Не вказано",
                "timeline": "Не вказано",
                "key_points": [],
                "questions": []
            }
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Парсинг відповіді з аналізом"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {
                    "complexity_score": 5,
                    "budget_adequacy": "unknown",
                    "requirements_clarity": "unclear",
                    "competition_level": "medium",
                    "risks": ["Не вдалося проаналізувати"],
                    "opportunities": ["Не вдалося проаналізувати"],
                    "recommended_rate": "Не вказано",
                    "estimated_hours": "Не вказано",
                    "success_probability": 0.5,
                    "red_flags": [],
                    "green_flags": []
                }
                
        except json.JSONDecodeError:
            logger.warning("Не вдалося розпарсити JSON відповідь аналізу Claude")
            return {
                "complexity_score": 5,
                "budget_adequacy": "unknown",
                "requirements_clarity": "unclear",
                "competition_level": "medium",
                "risks": ["Помилка парсингу"],
                "opportunities": ["Помилка парсингу"],
                "recommended_rate": "Не вказано",
                "estimated_hours": "Не вказано",
                "success_probability": 0.5,
                "red_flags": [],
                "green_flags": []
            }
    
    def _parse_filtering_response(self, response: str, original_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Парсинг відповіді з фільтрацією"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                selected_indices = result.get('selected_jobs', [])
                filtered_jobs = []
                
                for idx in selected_indices:
                    if 1 <= idx <= len(original_jobs):
                        job = original_jobs[idx - 1].copy()
                        job['ai_score'] = result.get('scores', {}).get(str(idx), 0.5)
                        job['ai_reason'] = result.get('reasons', {}).get(str(idx), 'Відібрано AI')
                        filtered_jobs.append(job)
                
                return filtered_jobs
            else:
                return original_jobs[:5]  # Повертаємо перші 5 якщо не вдалося розпарсити
                
        except json.JSONDecodeError:
            logger.warning("Не вдалося розпарсити JSON відповідь фільтрації Claude")
            return original_jobs[:5]
    
    def is_available(self) -> bool:
        """Перевірка доступності Claude API"""
        return self.client is not None and settings.CLAUDE_API_KEY is not None 