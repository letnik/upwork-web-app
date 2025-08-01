"""
API Router для MVP компонентів
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database.connection import get_db
from shared.database.mvp_models import (
    FilterProfile, ProposalTemplate, ProposalDraft, 
    AIInstruction, JobMatch, ABTest, UserAnalytics
)
from shared.utils.encryption import encrypt_data, decrypt_data
from .auth_router import get_current_user
from .models import User

router = APIRouter(prefix="/mvp", tags=["MVP Components"])


# ============================================================================
# ПРОФІЛІ ФІЛЬТРІВ
# ============================================================================

@router.post("/filter-profiles", response_model=dict)
async def create_filter_profile(
    name: str,
    keywords: Optional[List[str]] = None,
    exclude_keywords: Optional[List[str]] = None,
    ai_instructions: Optional[str] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    hourly_rate_min: Optional[float] = None,
    hourly_rate_max: Optional[float] = None,
    experience_level: Optional[str] = None,
    job_type: Optional[str] = None,
    categories: Optional[List[str]] = None,
    countries: Optional[List[str]] = None,
    working_hours: Optional[dict] = None,
    timezone: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Створення профілю фільтрів"""
    try:
        # Перевіряємо ліміт (до 10 профілів на користувача)
        existing_profiles = db.query(FilterProfile).filter(
            FilterProfile.user_id == current_user.id
        ).count()
        
        if existing_profiles >= 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Досягнуто ліміт профілів фільтрів (10)"
            )
        
        # Створюємо профіль
        profile = FilterProfile(
            user_id=current_user.id,
            name=name,
            keywords=keywords or [],
            exclude_keywords=exclude_keywords or [],
            ai_instructions=ai_instructions,
            budget_min=budget_min,
            budget_max=budget_max,
            hourly_rate_min=hourly_rate_min,
            hourly_rate_max=hourly_rate_max,
            experience_level=experience_level,
            job_type=job_type,
            categories=categories or [],
            countries=countries or [],
            working_hours=working_hours,
            timezone=timezone,
            is_active=True
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        return {
            "message": "Профіль фільтрів створено",
            "profile_id": profile.id,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка створення профілю: {str(e)}"
        )


@router.get("/filter-profiles", response_model=List[dict])
async def get_filter_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отримання профілів фільтрів користувача"""
    try:
        profiles = db.query(FilterProfile).filter(
            FilterProfile.user_id == current_user.id
        ).all()
        
        return [{
            "id": profile.id,
            "name": profile.name,
            "keywords": profile.keywords,
            "exclude_keywords": profile.exclude_keywords,
            "ai_instructions": profile.ai_instructions,
            "budget_min": float(profile.budget_min) if profile.budget_min else None,
            "budget_max": float(profile.budget_max) if profile.budget_max else None,
            "hourly_rate_min": float(profile.hourly_rate_min) if profile.hourly_rate_min else None,
            "hourly_rate_max": float(profile.hourly_rate_max) if profile.hourly_rate_max else None,
            "experience_level": profile.experience_level,
            "job_type": profile.job_type,
            "categories": profile.categories,
            "countries": profile.countries,
            "working_hours": profile.working_hours,
            "timezone": profile.timezone,
            "is_active": profile.is_active,
            "is_paused": profile.is_paused,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat()
        } for profile in profiles]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка отримання профілів: {str(e)}"
        )


@router.put("/filter-profiles/{profile_id}", response_model=dict)
async def update_filter_profile(
    profile_id: int,
    name: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    exclude_keywords: Optional[List[str]] = None,
    ai_instructions: Optional[str] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    hourly_rate_min: Optional[float] = None,
    hourly_rate_max: Optional[float] = None,
    experience_level: Optional[str] = None,
    job_type: Optional[str] = None,
    categories: Optional[List[str]] = None,
    countries: Optional[List[str]] = None,
    working_hours: Optional[dict] = None,
    timezone: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_paused: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Оновлення профілю фільтрів"""
    try:
        profile = db.query(FilterProfile).filter(
            FilterProfile.id == profile_id,
            FilterProfile.user_id == current_user.id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профіль не знайдено"
            )
        
        # Оновлюємо поля
        if name is not None:
            profile.name = name
        if keywords is not None:
            profile.keywords = keywords
        if exclude_keywords is not None:
            profile.exclude_keywords = exclude_keywords
        if ai_instructions is not None:
            profile.ai_instructions = ai_instructions
        if budget_min is not None:
            profile.budget_min = budget_min
        if budget_max is not None:
            profile.budget_max = budget_max
        if hourly_rate_min is not None:
            profile.hourly_rate_min = hourly_rate_min
        if hourly_rate_max is not None:
            profile.hourly_rate_max = hourly_rate_max
        if experience_level is not None:
            profile.experience_level = experience_level
        if job_type is not None:
            profile.job_type = job_type
        if categories is not None:
            profile.categories = categories
        if countries is not None:
            profile.countries = countries
        if working_hours is not None:
            profile.working_hours = working_hours
        if timezone is not None:
            profile.timezone = timezone
        if is_active is not None:
            profile.is_active = is_active
        if is_paused is not None:
            profile.is_paused = is_paused
        
        profile.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": "Профіль фільтрів оновлено",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка оновлення профілю: {str(e)}"
        )


@router.delete("/filter-profiles/{profile_id}", response_model=dict)
async def delete_filter_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Видалення профілю фільтрів"""
    try:
        profile = db.query(FilterProfile).filter(
            FilterProfile.id == profile_id,
            FilterProfile.user_id == current_user.id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профіль не знайдено"
            )
        
        db.delete(profile)
        db.commit()
        
        return {
            "message": "Профіль фільтрів видалено",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка видалення профілю: {str(e)}"
        )


# ============================================================================
# ШАБЛОНИ ВІДГУКІВ
# ============================================================================

@router.post("/proposal-templates", response_model=dict)
async def create_proposal_template(
    name: str,
    content: str,
    category: Optional[str] = None,
    variables: Optional[dict] = None,
    style: str = "formal",
    is_default: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Створення шаблону відгуку"""
    try:
        # Перевіряємо ліміт (до 10 шаблонів на користувача)
        existing_templates = db.query(ProposalTemplate).filter(
            ProposalTemplate.user_id == current_user.id
        ).count()
        
        if existing_templates >= 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Досягнуто ліміт шаблонів відгуків (10)"
            )
        
        # Створюємо шаблон
        template = ProposalTemplate(
            user_id=current_user.id,
            name=name,
            content=content,
            category=category,
            variables=variables or {},
            style=style,
            is_default=is_default,
            is_active=True
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "message": "Шаблон відгуку створено",
            "template_id": template.id,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка створення шаблону: {str(e)}"
        )


@router.get("/proposal-templates", response_model=List[dict])
async def get_proposal_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отримання шаблонів відгуків користувача"""
    try:
        templates = db.query(ProposalTemplate).filter(
            ProposalTemplate.user_id == current_user.id
        ).all()
        
        return [{
            "id": template.id,
            "name": template.name,
            "content": template.content,
            "category": template.category,
            "variables": template.variables,
            "style": template.style,
            "is_default": template.is_default,
            "is_active": template.is_active,
            "usage_count": template.usage_count,
            "success_rate": float(template.success_rate) if template.success_rate else None,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat()
        } for template in templates]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка отримання шаблонів: {str(e)}"
        )


# ============================================================================
# ЧЕРНЕТКИ ВІДГУКІВ
# ============================================================================

@router.post("/proposal-drafts", response_model=dict)
async def create_proposal_draft(
    content: str,
    job_id: Optional[str] = None,
    job_title: Optional[str] = None,
    job_description: Optional[str] = None,
    client_name: Optional[str] = None,
    budget: Optional[str] = None,
    template_id: Optional[int] = None,
    ai_generated: bool = True,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Створення чернетки відгуку"""
    try:
        # Перевіряємо ліміт (100 останніх чернеток)
        existing_drafts = db.query(ProposalDraft).filter(
            ProposalDraft.user_id == current_user.id
        ).count()
        
        if existing_drafts >= 100:
            # Видаляємо найстарішу чернетку
            oldest_draft = db.query(ProposalDraft).filter(
                ProposalDraft.user_id == current_user.id
            ).order_by(ProposalDraft.created_at.asc()).first()
            
            if oldest_draft:
                db.delete(oldest_draft)
        
        # Створюємо чернетку
        draft = ProposalDraft(
            user_id=current_user.id,
            content=content,
            job_id=job_id,
            job_title=job_title,
            job_description=job_description,
            client_name=client_name,
            budget=budget,
            template_id=template_id,
            ai_generated=ai_generated,
            notes=notes,
            status="draft"
        )
        
        db.add(draft)
        db.commit()
        db.refresh(draft)
        
        return {
            "message": "Чернетку відгуку створено",
            "draft_id": draft.id,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка створення чернетки: {str(e)}"
        )


@router.get("/proposal-drafts", response_model=List[dict])
async def get_proposal_drafts(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отримання чернеток відгуків користувача"""
    try:
        query = db.query(ProposalDraft).filter(
            ProposalDraft.user_id == current_user.id
        )
        
        if status:
            query = query.filter(ProposalDraft.status == status)
        
        drafts = query.order_by(ProposalDraft.created_at.desc()).limit(limit).all()
        
        return [{
            "id": draft.id,
            "content": draft.content,
            "job_id": draft.job_id,
            "job_title": draft.job_title,
            "job_description": draft.job_description,
            "client_name": draft.client_name,
            "budget": draft.budget,
            "template_id": draft.template_id,
            "ai_generated": draft.ai_generated,
            "status": draft.status,
            "sent_at": draft.sent_at.isoformat() if draft.sent_at else None,
            "response_received": draft.response_received,
            "response_date": draft.response_date.isoformat() if draft.response_date else None,
            "notes": draft.notes,
            "created_at": draft.created_at.isoformat(),
            "updated_at": draft.updated_at.isoformat()
        } for draft in drafts]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка отримання чернеток: {str(e)}"
        )


# ============================================================================
# AI ІНСТРУКЦІЇ
# ============================================================================

@router.post("/ai-instructions", response_model=dict)
async def create_ai_instruction(
    name: str,
    content: str,
    instruction_type: str,
    is_default: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Створення AI інструкції"""
    try:
        instruction = AIInstruction(
            user_id=current_user.id,
            name=name,
            content=content,
            instruction_type=instruction_type,
            is_default=is_default,
            is_active=True
        )
        
        db.add(instruction)
        db.commit()
        db.refresh(instruction)
        
        return {
            "message": "AI інструкцію створено",
            "instruction_id": instruction.id,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка створення AI інструкції: {str(e)}"
        )


@router.get("/ai-instructions", response_model=List[dict])
async def get_ai_instructions(
    instruction_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отримання AI інструкцій користувача"""
    try:
        query = db.query(AIInstruction).filter(
            AIInstruction.user_id == current_user.id
        )
        
        if instruction_type:
            query = query.filter(AIInstruction.instruction_type == instruction_type)
        
        instructions = query.all()
        
        return [{
            "id": instruction.id,
            "name": instruction.name,
            "content": instruction.content,
            "instruction_type": instruction.instruction_type,
            "is_default": instruction.is_default,
            "is_active": instruction.is_active,
            "usage_count": instruction.usage_count,
            "effectiveness_score": float(instruction.effectiveness_score) if instruction.effectiveness_score else None,
            "created_at": instruction.created_at.isoformat(),
            "updated_at": instruction.updated_at.isoformat()
        } for instruction in instructions]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка отримання AI інструкцій: {str(e)}"
        ) 