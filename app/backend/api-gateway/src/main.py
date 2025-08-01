"""
API Gateway - Головний файл для маршрутизації запитів між мікросервісами
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import sys
import os
from datetime import datetime

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config.settings import settings
from shared.config.logging import setup_logging, get_logger
from shared.utils.rate_limiter import rate_limit_middleware
from shared.utils.validation_middleware import validation_middleware_handler
from shared.utils.auth_middleware import auth_middleware_handler

# Налаштування логування
setup_logging(service_name="api-gateway")
logger = get_logger("api-gateway")

# Створюємо FastAPI додаток
app = FastAPI(
    title="API Gateway",
    description="API Gateway для маршрутизації запитів між мікросервісами",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Middleware для додавання security headers"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Додаємо middleware для безпеки (тимчасово відключено для тестування)
# @app.middleware("http")
# async def security_middleware(request: Request, call_next):
#     """Middleware для безпеки (rate limiting, validation, auth)"""
#     try:
#         # 1. Rate limiting
#         await rate_limit_middleware(request, call_next)
#         
#         # 2. Validation
#         await validation_middleware_handler(request, call_next)
#         
#         # 3. Authentication
#         await auth_middleware_handler(request, call_next)
#         
#         # Виконуємо запит
#         response = await call_next(request)
#         return response
#         
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Помилка middleware безпеки: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="Помилка обробки запиту"
#         )

# HTTP клієнт для запитів до мікросервісів
http_client = httpx.AsyncClient(timeout=30.0)

# Додаємо роутери
from .routers import mvp_router

# MVP endpoints
app.include_router(mvp_router.router, prefix="/api/mvp")

@app.get("/api/mvp/test")
async def test_mvp():
    """Тестовий endpoint для MVP"""
    return {"message": "MVP API is working"}


@app.on_event("startup")
async def startup_event():
    """Подія запуску API Gateway"""
    logger.info("🚀 Запуск API Gateway...")


@app.on_event("shutdown")
async def shutdown_event():
    """Подія зупинки API Gateway"""
    await http_client.aclose()
    logger.info("🛑 API Gateway зупинено")


@app.get("/")
async def root():
    """Головна сторінка API Gateway"""
    return {
        "service": "API Gateway",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "auth": settings.AUTH_SERVICE_URL,
            "upwork": settings.UPWORK_SERVICE_URL,
            "ai": settings.AI_SERVICE_URL,
            "analytics": settings.ANALYTICS_SERVICE_URL,
            "notification": settings.NOTIFICATION_SERVICE_URL
        }
    }


@app.get("/health")
async def health_check():
    """Перевірка здоров'я API Gateway"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/test-auth")
async def test_auth_service():
    """Тест підключення до Auth Service"""
    try:
        response = await http_client.get(f"{settings.AUTH_SERVICE_URL}/health")
        return {
            "status": "success",
            "auth_service_url": settings.AUTH_SERVICE_URL,
            "auth_service_response": response.json()
        }
    except Exception as e:
        return {
            "status": "error",
            "auth_service_url": settings.AUTH_SERVICE_URL,
            "error": str(e)
        }


# ===== AUTH SERVICE ROUTES =====

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_service_route(request: Request, path: str):
    """Маршрутизація запитів до Auth Service"""
    try:
        # Формуємо URL для Auth Service
        url = f"{settings.AUTH_SERVICE_URL}/auth/{path}"
        
        # Отримуємо тіло запиту
        body = await request.body()
        
        # Формуємо заголовки
        headers = dict(request.headers)
        headers.pop("host", None)  # Видаляємо host заголовок
        
        # Виконуємо запит до Auth Service
        response = await http_client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params
        )
        
        # Повертаємо відповідь
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Помилка маршрутизації до Auth Service: {e}")
        logger.error(f"URL: {settings.AUTH_SERVICE_URL}/auth/{path}")
        raise HTTPException(status_code=500, detail="Помилка Auth Service")


# ===== UPWORK SERVICE ROUTES =====

@app.get("/upwork/analytics/overview")
async def analytics_overview():
    """Простий analytics endpoint для дашборду"""
    return {
        "total_jobs": 150,
        "total_proposals": 45,
        "success_rate": 0.78,
        "average_earnings": 2500,
        "top_skills": ["Python", "JavaScript", "React", "Node.js", "Docker"],
        "recent_activity": [
            {"date": "2024-01-15", "action": "Proposal submitted", "job": "Python Developer"},
            {"date": "2024-01-14", "action": "Job applied", "job": "React Developer"},
            {"date": "2024-01-13", "action": "Contract won", "job": "Full Stack Developer"}
        ],
        "earnings_chart": [
            {"month": "Jan", "earnings": 2000},
            {"month": "Feb", "earnings": 3500},
            {"month": "Mar", "earnings": 2800},
            {"month": "Apr", "earnings": 4200}
        ],
        "status": "success"
    }


@app.api_route("/upwork/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def upwork_service_route(request: Request, path: str):
    """Маршрутизація запитів до Upwork Service"""
    try:
        # Формуємо URL для Upwork Service
        url = f"{settings.UPWORK_SERVICE_URL}/upwork/{path}"
        
        # Отримуємо тіло запиту
        body = await request.body()
        
        # Формуємо заголовки
        headers = dict(request.headers)
        headers.pop("host", None)
        
        # Виконуємо запит до Upwork Service
        response = await http_client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Помилка маршрутизації до Upwork Service: {e}")
        raise HTTPException(status_code=500, detail="Помилка Upwork Service")


# ===== AI SERVICE ROUTES =====

@app.api_route("/ai/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def ai_service_route(request: Request, path: str):
    """Маршрутизація запитів до AI Service"""
    try:
        # Формуємо URL для AI Service
        url = f"{settings.AI_SERVICE_URL}/ai/{path}"
        
        # Отримуємо тіло запиту
        body = await request.body()
        
        # Формуємо заголовки
        headers = dict(request.headers)
        headers.pop("host", None)
        
        # Виконуємо запит до AI Service
        response = await http_client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Помилка маршрутизації до AI Service: {e}")
        raise HTTPException(status_code=500, detail="Помилка AI Service")


# ===== ANALYTICS SERVICE ROUTES =====

@app.api_route("/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def analytics_service_route(request: Request, path: str):
    """Маршрутизація запитів до Analytics Service"""
    try:
        # Формуємо URL для Analytics Service
        url = f"{settings.ANALYTICS_SERVICE_URL}/analytics/{path}"
        
        # Отримуємо тіло запиту
        body = await request.body()
        
        # Формуємо заголовки
        headers = dict(request.headers)
        headers.pop("host", None)
        
        # Виконуємо запит до Analytics Service
        response = await http_client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Помилка маршрутизації до Analytics Service: {e}")
        raise HTTPException(status_code=500, detail="Помилка Analytics Service")


# ===== NOTIFICATION SERVICE ROUTES =====

@app.api_route("/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def notification_service_route(request: Request, path: str):
    """Маршрутизація запитів до Notification Service"""
    try:
        # Формуємо URL для Notification Service
        url = f"{settings.NOTIFICATION_SERVICE_URL}/notifications/{path}"
        
        # Отримуємо тіло запиту
        body = await request.body()
        
        # Формуємо заголовки
        headers = dict(request.headers)
        headers.pop("host", None)
        
        # Виконуємо запит до Notification Service
        response = await http_client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Помилка маршрутизації до Notification Service: {e}")
        raise HTTPException(status_code=500, detail="Помилка Notification Service")


# ===== LEGACY ROUTES (для сумісності) =====

@app.api_route("/jobs/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def jobs_legacy_route(request: Request, path: str):
    """Legacy маршрути для вакансій (перенаправляємо на Upwork Service)"""
    try:
        url = f"{settings.UPWORK_SERVICE_URL}/upwork/jobs/{path}"
        body = await request.body()
        headers = dict(request.headers)
        headers.pop("host", None)
        
        response = await http_client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Помилка legacy маршрутизації jobs: {e}")
        raise HTTPException(status_code=500, detail="Помилка Upwork Service")


@app.api_route("/applications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def applications_legacy_route(request: Request, path: str):
    """Legacy маршрути для заявок (перенаправляємо на Upwork Service)"""
    try:
        url = f"{settings.UPWORK_SERVICE_URL}/upwork/applications/{path}"
        body = await request.body()
        headers = dict(request.headers)
        headers.pop("host", None)
        
        response = await http_client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Помилка legacy маршрутизації applications: {e}")
        raise HTTPException(status_code=500, detail="Помилка Upwork Service")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 