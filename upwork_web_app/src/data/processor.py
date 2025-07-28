"""
Модуль для обробки даних парсингу
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from loguru import logger
from pydantic import BaseModel, ValidationError, validator
from dataclasses import dataclass

from ..database.models import Job, ParsingSession, ParsingLog


class JobDataValidator(BaseModel):
    """Валідатор для даних роботи"""
    
    upwork_id: str
    title: str
    description: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    hourly_rate_min: Optional[float] = None
    hourly_rate_max: Optional[float] = None
    skills: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    client_country: Optional[str] = None
    client_rating: Optional[float] = None
    client_reviews_count: Optional[int] = None
    posted_time: Optional[datetime] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    project_length: Optional[str] = None
    hours_per_week: Optional[str] = None
    team_size: Optional[str] = None
    url: Optional[str] = None
    
    @validator('upwork_id')
    def validate_upwork_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('upwork_id не може бути порожнім')
        return v.strip()
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('title не може бути порожнім')
        return v.strip()
    
    @validator('budget_min', 'budget_max', 'hourly_rate_min', 'hourly_rate_max')
    def validate_budget(cls, v):
        if v is not None and v < 0:
            raise ValueError('Бюджет не може бути від\'ємним')
        return v
    
    @validator('client_rating')
    def validate_rating(cls, v):
        if v is not None and (v < 0 or v > 5):
            raise ValueError('Рейтинг має бути від 0 до 5')
        return v
    
    @validator('client_reviews_count')
    def validate_reviews_count(cls, v):
        if v is not None and v < 0:
            raise ValueError('Кількість відгуків не може бути від\'ємною')
        return v


@dataclass
class ProcessingResult:
    """Результат обробки даних"""
    is_valid: bool
    cleaned_data: Optional[Dict] = None
    errors: List[str] = None
    is_duplicate: bool = False
    existing_job_id: Optional[int] = None


class DataProcessor:
    """Клас для обробки даних парсингу"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.validator = JobDataValidator
    
    def process_job_data(self, raw_data: Dict[str, Any], session_id: str = None) -> ProcessingResult:
        """
        Обробка даних роботи
        
        Args:
            raw_data: Сирі дані з парсера
            session_id: ID сесії парсингу
            
        Returns:
            ProcessingResult з результатом обробки
        """
        try:
            # 1. Очищення даних
            cleaned_data = self._clean_data(raw_data)
            
            # 2. Валідація даних
            validation_result = self._validate_data(cleaned_data)
            if not validation_result['is_valid']:
                return ProcessingResult(
                    is_valid=False,
                    errors=validation_result['errors']
                )
            
            # 3. Перевірка на дублікати
            duplicate_check = self._check_duplicate(cleaned_data['upwork_id'])
            if duplicate_check['is_duplicate']:
                return ProcessingResult(
                    is_valid=True,
                    cleaned_data=cleaned_data,
                    is_duplicate=True,
                    existing_job_id=duplicate_check['existing_job_id']
                )
            
            # 4. Додаткове очищення та нормалізація
            final_data = self._normalize_data(cleaned_data)
            
            return ProcessingResult(
                is_valid=True,
                cleaned_data=final_data
            )
            
        except Exception as e:
            logger.error(f"Помилка обробки даних: {e}")
            return ProcessingResult(
                is_valid=False,
                errors=[f"Критична помилка обробки: {str(e)}"]
            )
    
    def _clean_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Очищення сирих даних"""
        cleaned = {}
        
        for key, value in raw_data.items():
            if value is None:
                continue
                
            if isinstance(value, str):
                # Видалення зайвих пробілів та символів
                cleaned_value = self._clean_string(value)
                if cleaned_value:  # Додаємо тільки непорожні значення
                    cleaned[key] = cleaned_value
            elif isinstance(value, (int, float)):
                cleaned[key] = value
            elif isinstance(value, datetime):
                cleaned[key] = value
            else:
                # Конвертуємо інші типи в строку
                cleaned_value = str(value).strip()
                if cleaned_value:
                    cleaned[key] = cleaned_value
        
        return cleaned
    
    def _clean_string(self, text: str) -> Optional[str]:
        """Очищення текстового значення"""
        if not text:
            return None
            
        # Видалення зайвих пробілів
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Видалення HTML тегів
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Видалення спеціальних символів
        cleaned = re.sub(r'[^\w\s\-.,!?()$€£¥%]', '', cleaned)
        
        # Нормалізація пробілів
        cleaned = ' '.join(cleaned.split())
        
        return cleaned if cleaned else None
    
    def _validate_data(self, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        """Валідація очищених даних"""
        try:
            # Створюємо валідатор з очищеними даними
            validated_data = self.validator(**cleaned_data)
            
            return {
                'is_valid': True,
                'validated_data': validated_data.dict()
            }
            
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = error['loc'][0] if error['loc'] else 'unknown'
                message = error['msg']
                errors.append(f"{field}: {message}")
            
            return {
                'is_valid': False,
                'errors': errors
            }
    
    def _check_duplicate(self, upwork_id: str) -> Dict[str, Any]:
        """Перевірка на дублікати"""
        try:
            existing_job = self.db.query(Job).filter(
                Job.upwork_id == upwork_id
            ).first()
            
            if existing_job:
                return {
                    'is_duplicate': True,
                    'existing_job_id': existing_job.id
                }
            
            return {
                'is_duplicate': False,
                'existing_job_id': None
            }
            
        except Exception as e:
            logger.error(f"Помилка перевірки дублікатів: {e}")
            return {
                'is_duplicate': False,
                'existing_job_id': None
            }
    
    def _normalize_data(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Нормалізація валідованих даних"""
        normalized = validated_data.copy()
        
        # Нормалізація навичок
        if 'skills' in normalized and normalized['skills']:
            skills = self._normalize_skills(normalized['skills'])
            normalized['skills'] = json.dumps(skills) if skills else None
        
        # Нормалізація категорій
        if 'category' in normalized and normalized['category']:
            normalized['category'] = self._normalize_category(normalized['category'])
        
        # Нормалізація типу роботи
        if 'job_type' in normalized and normalized['job_type']:
            normalized['job_type'] = self._normalize_job_type(normalized['job_type'])
        
        # Нормалізація рівня досвіду
        if 'experience_level' in normalized and normalized['experience_level']:
            normalized['experience_level'] = self._normalize_experience_level(normalized['experience_level'])
        
        return normalized
    
    def _normalize_skills(self, skills_text: str) -> List[str]:
        """Нормалізація навичок"""
        if not skills_text:
            return []
        
        # Розбиваємо на окремі навички
        skills = re.split(r'[,;|]', skills_text)
        
        # Очищаємо кожну навичку
        normalized_skills = []
        for skill in skills:
            cleaned_skill = self._clean_string(skill)
            if cleaned_skill and len(cleaned_skill) > 1:
                normalized_skills.append(cleaned_skill.lower())
        
        # Видаляємо дублікати
        return list(set(normalized_skills))
    
    def _normalize_category(self, category: str) -> str:
        """Нормалізація категорії"""
        if not category:
            return None
        
        # Приводимо до нижнього регістру
        normalized = category.lower().strip()
        
        # Мапінг категорій
        category_mapping = {
            'web development': 'Web Development',
            'mobile development': 'Mobile Development',
            'data science': 'Data Science',
            'design': 'Design',
            'writing': 'Writing',
            'marketing': 'Marketing',
            'admin support': 'Admin Support',
            'customer service': 'Customer Service',
            'sales': 'Sales',
            'accounting': 'Accounting',
            'legal': 'Legal',
            'translation': 'Translation',
            'engineering': 'Engineering',
            'architecture': 'Architecture',
            'consulting': 'Consulting'
        }
        
        return category_mapping.get(normalized, category.title())
    
    def _normalize_job_type(self, job_type: str) -> str:
        """Нормалізація типу роботи"""
        if not job_type:
            return None
        
        normalized = job_type.lower().strip()
        
        type_mapping = {
            'hourly': 'Hourly',
            'fixed': 'Fixed',
            'recurring': 'Recurring',
            'hourly project': 'Hourly',
            'fixed-price project': 'Fixed'
        }
        
        return type_mapping.get(normalized, job_type.title())
    
    def _normalize_experience_level(self, level: str) -> str:
        """Нормалізація рівня досвіду"""
        if not level:
            return None
        
        normalized = level.lower().strip()
        
        level_mapping = {
            'entry level': 'Entry Level',
            'intermediate': 'Intermediate',
            'expert': 'Expert',
            'beginner': 'Entry Level',
            'advanced': 'Expert'
        }
        
        return level_mapping.get(normalized, level.title())
    
    def save_job(self, job_data: Dict[str, Any], session_id: str = None) -> Tuple[bool, Optional[int], List[str]]:
        """
        Збереження роботи в базу даних
        
        Args:
            job_data: Дані роботи
            session_id: ID сесії парсингу
            
        Returns:
            Tuple[успіх, ID роботи, список помилок]
        """
        try:
            # Створюємо нову роботу
            job = Job(**job_data)
            
            if session_id:
                # Знаходимо сесію парсингу
                session = self.db.query(ParsingSession).filter(
                    ParsingSession.session_id == session_id
                ).first()
                
                if session:
                    job.parsing_session_id = session.id
            
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            
            logger.info(f"Збережено роботу: {job.upwork_id}")
            return True, job.id, []
            
        except Exception as e:
            self.db.rollback()
            error_msg = f"Помилка збереження роботи: {str(e)}"
            logger.error(error_msg)
            return False, None, [error_msg]
    
    def process_batch(self, jobs_data: List[Dict[str, Any]], session_id: str = None) -> Dict[str, Any]:
        """
        Обробка партії робіт
        
        Args:
            jobs_data: Список сирих даних робіт
            session_id: ID сесії парсингу
            
        Returns:
            Статистика обробки
        """
        stats = {
            'total': len(jobs_data),
            'processed': 0,
            'saved': 0,
            'duplicates': 0,
            'errors': 0,
            'error_details': []
        }
        
        for job_data in jobs_data:
            try:
                # Обробка даних
                result = self.process_job_data(job_data, session_id)
                stats['processed'] += 1
                
                if not result.is_valid:
                    stats['errors'] += 1
                    stats['error_details'].extend(result.errors)
                    continue
                
                if result.is_duplicate:
                    stats['duplicates'] += 1
                    continue
                
                # Збереження в базу
                success, job_id, errors = self.save_job(result.cleaned_data, session_id)
                
                if success:
                    stats['saved'] += 1
                else:
                    stats['errors'] += 1
                    stats['error_details'].extend(errors)
                    
            except Exception as e:
                stats['errors'] += 1
                stats['error_details'].append(f"Критична помилка: {str(e)}")
                logger.error(f"Помилка обробки роботи: {e}")
        
        logger.info(f"Оброблено партію: {stats}")
        return stats 