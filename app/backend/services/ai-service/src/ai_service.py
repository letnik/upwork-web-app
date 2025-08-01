"""
AI Service - Основний сервіс для AI функціональності з fallback
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.config.logging import get_logger
from .openai_client import OpenAIClient
from .claude_client import ClaudeClient

logger = get_logger("ai-service")


class AIService:
    """Основний AI сервіс з fallback логікою"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.claude_client = ClaudeClient()
        self._setup_clients()
    
    def _setup_clients(self):
        """Налаштування AI клієнтів"""
        logger.info("Налаштування AI клієнтів...")
        
        if self.openai_client.is_available():
            logger.info("✅ OpenAI клієнт доступний")
        else:
            logger.warning("❌ OpenAI клієнт недоступний")
        
        if self.claude_client.is_available():
            logger.info("✅ Claude клієнт доступний")
        else:
            logger.warning("❌ Claude клієнт недоступний")
        
        if not self.openai_client.is_available() and not self.claude_client.is_available():
            logger.error("❌ Жоден AI клієнт не доступний!")
    
    async def generate_proposal(self, job_data: Dict[str, Any], user_profile: Dict[str, Any], 
                              template: Optional[str] = None) -> Dict[str, Any]:
        """Генерація пропозиції з fallback"""
        try:
            # Спочатку пробуємо OpenAI
            if self.openai_client.is_available():
                logger.info("Спроба генерації пропозиції через OpenAI...")
                result = await self.openai_client.generate_proposal(job_data, user_profile, template)
                
                if result["success"]:
                    logger.info("✅ Пропозицію згенеровано через OpenAI")
                    return result
                else:
                    logger.warning(f"OpenAI не вдався: {result.get('error', 'Unknown error')}")
            
            # Fallback до Claude
            if self.claude_client.is_available():
                logger.info("Fallback до Claude для генерації пропозиції...")
                result = await self.claude_client.generate_proposal(job_data, user_profile, template)
                
                if result["success"]:
                    logger.info("✅ Пропозицію згенеровано через Claude (fallback)")
                    return result
                else:
                    logger.warning(f"Claude не вдався: {result.get('error', 'Unknown error')}")
            
            # Якщо обидва не працюють, повертаємо помилку
            return {
                "success": False,
                "error": "Жоден AI сервіс не доступний",
                "model": "none",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка генерації пропозиції: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": "none",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def analyze_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Аналіз вакансії з fallback"""
        try:
            # Спочатку пробуємо OpenAI
            if self.openai_client.is_available():
                logger.info("Спроба аналізу вакансії через OpenAI...")
                result = await self.openai_client.analyze_job(job_data)
                
                if result["success"]:
                    logger.info("✅ Вакансію проаналізовано через OpenAI")
                    return result
                else:
                    logger.warning(f"OpenAI аналіз не вдався: {result.get('error', 'Unknown error')}")
            
            # Fallback до Claude
            if self.claude_client.is_available():
                logger.info("Fallback до Claude для аналізу вакансії...")
                result = await self.claude_client.analyze_job(job_data)
                
                if result["success"]:
                    logger.info("✅ Вакансію проаналізовано через Claude (fallback)")
                    return result
                else:
                    logger.warning(f"Claude аналіз не вдався: {result.get('error', 'Unknown error')}")
            
            # Якщо обидва не працюють, повертаємо помилку
            return {
                "success": False,
                "error": "Жоден AI сервіс не доступний",
                "model": "none",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка аналізу вакансії: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": "none",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def filter_jobs(self, jobs: List[Dict[str, Any]], user_profile: Dict[str, Any], 
                         filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Фільтрація вакансій з fallback"""
        try:
            # Спочатку пробуємо OpenAI
            if self.openai_client.is_available():
                logger.info("Спроба фільтрації вакансій через OpenAI...")
                result = await self.openai_client.filter_jobs(jobs, user_profile, filters)
                
                if result["success"]:
                    logger.info("✅ Вакансії відфільтровано через OpenAI")
                    return result
                else:
                    logger.warning(f"OpenAI фільтрація не вдалася: {result.get('error', 'Unknown error')}")
            
            # Fallback до Claude
            if self.claude_client.is_available():
                logger.info("Fallback до Claude для фільтрації вакансій...")
                result = await self.claude_client.filter_jobs(jobs, user_profile, filters)
                
                if result["success"]:
                    logger.info("✅ Вакансії відфільтровано через Claude (fallback)")
                    return result
                else:
                    logger.warning(f"Claude фільтрація не вдалася: {result.get('error', 'Unknown error')}")
            
            # Якщо обидва не працюють, повертаємо помилку
            return {
                "success": False,
                "error": "Жоден AI сервіс не доступний",
                "model": "none",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка фільтрації вакансій: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": "none",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def generate_proposal_with_template(self, job_data: Dict[str, Any], user_profile: Dict[str, Any], 
                                            template_content: str) -> Dict[str, Any]:
        """Генерація пропозиції з використанням шаблону"""
        try:
            # Додаємо шаблон до промпту
            enhanced_job_data = job_data.copy()
            enhanced_job_data['template'] = template_content
            
            return await self.generate_proposal(enhanced_job_data, user_profile, template_content)
            
        except Exception as e:
            logger.error(f"Помилка генерації пропозиції з шаблоном: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": "none",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def analyze_multiple_jobs(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Аналіз кількох вакансій"""
        try:
            results = []
            
            for i, job in enumerate(jobs):
                logger.info(f"Аналіз вакансії {i+1}/{len(jobs)}: {job.get('title', 'Unknown')}")
                
                result = await self.analyze_job(job)
                result['job_id'] = job.get('id', f'job_{i}')
                result['job_title'] = job.get('title', 'Unknown')
                
                results.append(result)
                
                # Невелика затримка між запитами
                await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "results": results,
                "total_jobs": len(jobs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка аналізу кількох вакансій: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Отримання статусу AI сервісів"""
        return {
            "openai_available": self.openai_client.is_available(),
            "claude_available": self.claude_client.is_available(),
            "any_available": self.openai_client.is_available() or self.claude_client.is_available(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Тестування з'єднання з AI сервісами"""
        try:
            test_job = {
                "title": "Test Job",
                "description": "This is a test job for connection testing",
                "budget": "$100",
                "skills": ["Python", "Testing"]
            }
            
            test_profile = {
                "skills": ["Python", "AI"],
                "experience": "5 years",
                "hourly_rate": "$50"
            }
            
            # Тестуємо OpenAI
            openai_test = None
            if self.openai_client.is_available():
                try:
                    openai_test = await self.openai_client.analyze_job(test_job)
                except Exception as e:
                    openai_test = {"success": False, "error": str(e)}
            else:
                openai_test = {"success": False, "error": "Not available"}
            
            # Тестуємо Claude
            claude_test = None
            if self.claude_client.is_available():
                try:
                    claude_test = await self.claude_client.analyze_job(test_job)
                except Exception as e:
                    claude_test = {"success": False, "error": str(e)}
            else:
                claude_test = {"success": False, "error": "Not available"}
            
            return {
                "openai_test": openai_test,
                "claude_test": claude_test,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка тестування з'єднання: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 