"""
Тестовий OAuth роутер
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """Тестовий endpoint"""
    return {
        "message": "Test OAuth router is working",
        "status": "ok"
    }

@router.get("/upwork/authorize")
async def upwork_authorize():
    """Початок OAuth flow для Upwork"""
    return {
        "authorization_url": "https://www.upwork.com/services/api/auth?response_type=code&client_id=test&redirect_uri=http://localhost:8000/auth/upwork/callback&scope=jobs:read%20jobs:write%20freelancers:read%20clients:read%20messages:read%20messages:write",
        "message": "Test URL for Upwork authorization",
        "status": "test_mode"
    } 