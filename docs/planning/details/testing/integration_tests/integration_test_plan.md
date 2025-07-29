# План Integration тестів

> **Детальний план integration тестів для перевірки взаємодії між модулями**

---

## Зміст

1. [Загальні принципи](#загальні-принципи)
2. [API Integration Tests](#api-integration-tests)
3. [Database Integration Tests](#database-integration-tests)
4. [External Services Integration Tests](#external-services-integration-tests)
5. [Module Interaction Tests](#module-interaction-tests)
6. [Чек-лист Integration тестів](#чек-лист-integration-тестів)

---

## Загальні принципи

### Підходи до integration тестування
- **API Testing**: Тестування всіх REST API endpoints
- **Database Integration**: Тестування взаємодії з базою даних
- **External Services**: Тестування інтеграції з зовнішніми сервісами
- **Module Interaction**: Тестування взаємодії між модулями
- **Error Handling**: Тестування обробки помилок

### Структура тестів
```
tests/
├── integration/
│   ├── api/
│   │   ├── test_auth_api.py
│   │   ├── test_ai_api.py
│   │   └── test_analytics_api.py
│   ├── database/
│   │   ├── test_user_data.py
│   │   └── test_analytics_data.py
│   ├── external/
│   │   ├── test_upwork_integration.py
│   │   └── test_openai_integration.py
│   └── modules/
│       ├── test_auth_analytics.py
│       └── test_ai_security.py
```

---

## API Integration Tests

### Тести Auth API

```python
# tests/integration/api/test_auth_api.py
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app

class TestAuthAPI:
    @pytest.mark.asyncio
    async def test_oauth_init_endpoint(self):
        """Тест endpoint ініціалізації OAuth"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/auth/upwork/init", json={
                "redirect_uri": "https://app.com/callback"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "authorization_url" in data
            assert "state" in data
            assert "code_verifier" in data
            assert "upwork.com" in data["authorization_url"]
    
    @pytest.mark.asyncio
    async def test_oauth_callback_endpoint(self):
        """Тест endpoint callback OAuth"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Мокаємо успішну відповідь від Upwork
            with patch('src.modules.auth.oauth_security.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    'access_token': 'test_access_token',
                    'refresh_token': 'test_refresh_token',
                    'expires_in': 3600
                }
                mock_post.return_value = mock_response
                
                response = await client.get("/auth/upwork/callback?code=test_code&state=test_state")
                
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_refresh_token_endpoint(self):
        """Тест endpoint оновлення токенів"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Створюємо тестовий refresh токен
            test_refresh_token = create_test_refresh_token()
            
            response = await client.post("/auth/refresh", json={
                "refresh_token": test_refresh_token
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_mfa_setup_endpoint(self):
        """Тест endpoint налаштування MFA"""
        async with AsyncClient(app=app, base_url="http://test") as client:
# Авторизуємо користувача
            auth_headers = await get_auth_headers(client)
            
            response = await client.post("/auth/mfa/setup", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "totp_secret" in data
            assert "qr_code" in data
            assert "backup_codes" in data
    
    @pytest.mark.asyncio
    async def test_mfa_verify_endpoint(self):
        """Тест endpoint валідації MFA"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
# Генеруємо TOTP код
            totp_code = generate_test_totp_code()
            
            response = await client.post("/auth/mfa/verify", 
                headers=auth_headers,
                json={"totp_code": totp_code}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["verified"] == True
```

### Тести AI API

```python
# tests/integration/api/test_ai_api.py
import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import Mock, patch
from src.main import app

class TestAIAPI:
    @pytest.mark.asyncio
    async def test_proposal_analysis_endpoint(self):
        """Тест endpoint аналізу пропозицій"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            response = await client.post("/api/ai/analyze/proposal",
                headers=auth_headers,
                json={
                    "proposal_text": "Professional web developer with 5 years experience",
                    "category": "web_development",
                    "budget_range": "1000-5000"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "score" in data
            assert "suggestions" in data
            assert "keywords" in data
            assert "confidence" in data
            assert 0 <= data["score"] <= 1
    
    @pytest.mark.asyncio
    async def test_proposal_generation_endpoint(self):
        """Тест endpoint генерації пропозицій"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
# Мокаємо OpenAI API
            with patch('src.modules.ai.openai_integration.openai.ChatCompletion.create') as mock_openai:
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = '{"proposal_text": "Professional proposal...", "cover_letter": "Thank you..."}'
                mock_openai.return_value = mock_response
                
                response = await client.post("/api/ai/generate/proposal",
                    headers=auth_headers,
                    json={
                        "project_description": "E-commerce website development",
                        "budget": 5000,
                        "timeline": "2 months",
                        "skills": ["React", "Node.js", "MongoDB"]
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "proposal_text" in data
                assert "cover_letter" in data
                assert "portfolio_items" in data
                assert "pricing_breakdown" in data
    
    @pytest.mark.asyncio
    async def test_competition_analysis_endpoint(self):
        """Тест endpoint аналізу конкурентів"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            response = await client.post("/api/ai/analyze/competition",
                headers=auth_headers,
                json={
                    "category": "web_development",
                    "budget_range": "1000-5000",
                    "skills": ["React", "Node.js"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "competitor_count" in data
            assert "average_rate" in data
            assert "rate_distribution" in data
            assert "top_competitors" in data
            assert "market_position" in data
    
    @pytest.mark.asyncio
    async def test_success_prediction_endpoint(self):
        """Тест endpoint прогнозування успішності"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            response = await client.post("/api/ai/predict/success",
                headers=auth_headers,
                json={
                    "project_category": "web_development",
                    "budget": 5000,
                    "client_rating": 4.8,
                    "project_complexity": "medium"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "success_probability" in data
            assert "risk_factors" in data
            assert "recommendations" in data
            assert "confidence" in data
            assert 0 <= data["success_probability"] <= 1
```

### Тести Analytics API

```python
# tests/integration/api/test_analytics_api.py
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app

class TestAnalyticsAPI:
    @pytest.mark.asyncio
    async def test_user_metrics_endpoint(self):
        """Тест endpoint метрик користувача"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            response = await client.get("/api/analytics/metrics/user/test_user",
                headers=auth_headers,
                params={"period": "monthly"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "period" in data
            assert "metrics" in data
            assert "trends" in data
            assert "proposals_sent" in data["metrics"]
            assert "win_rate" in data["metrics"]
            assert "total_earnings" in data["metrics"]
    
    @pytest.mark.asyncio
    async def test_dashboard_endpoint(self):
        """Тест endpoint дашборду"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            response = await client.get("/api/dashboard/main", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "widgets" in data
            assert "summary" in data
            assert len(data["widgets"]) > 0
            assert "total_earnings" in data["summary"]
            assert "active_contracts" in data["summary"]
    
    @pytest.mark.asyncio
    async def test_proposals_analytics_endpoint(self):
        """Тест endpoint аналітики пропозицій"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            response = await client.get("/api/analytics/proposals/test_user",
                headers=auth_headers,
                params={
                    "status": "all",
                    "category": "web_development",
                    "date_from": "2024-01-01",
                    "date_to": "2024-12-31"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "total_proposals" in data
            assert "by_status" in data
            assert "by_category" in data
            assert "timeline" in data
    
    @pytest.mark.asyncio
    async def test_report_generation_endpoint(self):
        """Тест endpoint генерації звітів"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            response = await client.post("/api/analytics/reports/generate",
                headers=auth_headers,
                json={
                    "report_type": "monthly_performance",
                    "user_id": "test_user",
                    "period": "2024-01",
                    "include_charts": True
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "report_id" in data
            assert "download_url" in data
            assert "summary" in data
            assert "charts" in data
    
    @pytest.mark.asyncio
    async def test_audit_logs_endpoint(self):
        """Тест endpoint аудит логів"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            auth_headers = await get_auth_headers(client)
            
            response = await client.get("/api/security/audit-logs",
                headers=auth_headers,
                params={
                    "user_id": "test_user",
                    "action": "login",
                    "date_from": "2024-01-01",
                    "date_to": "2024-12-31",
                    "limit": 50
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "logs" in data
            assert "pagination" in data
            assert len(data["logs"]) <= 50
```

---

## Database Integration Tests

### Тести даних користувачів

```python
# tests/integration/database/test_user_data.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import get_db_session
from src.modules.auth.models import User
from src.modules.analytics.models import UserAnalytics

class TestUserDataIntegration:
    @pytest.mark.asyncio
    async def test_user_profile_storage(self):
        """Тест збереження профілю користувача"""
        async with get_db_session() as session:
# Створюємо тестового користувача
            user_data = {
                "user_id": "test_user_123",
                "email": "test@example.com",
                "upwork_profile": {
                    "profile_id": "~0123456789",
                    "hourly_rate": 85,
                    "total_earnings": 15000,
                    "success_rate": 0.85
                }
            }
            
# Зберігаємо користувача
            user = User(**user_data)
            session.add(user)
            await session.commit()
            
# Отримуємо користувача
            retrieved_user = await session.get(User, user_data["user_id"])
            
            assert retrieved_user is not None
            assert retrieved_user.email == user_data["email"]
            assert retrieved_user.upwork_profile["profile_id"] == user_data["upwork_profile"]["profile_id"]
    
    @pytest.mark.asyncio
    async def test_user_analytics_storage(self):
        """Тест збереження аналітичних даних користувача"""
        async with get_db_session() as session:
# Створюємо аналітичні дані
            analytics_data = {
                "user_id": "test_user_123",
                "metrics": {
                    "proposals_sent": 50,
                    "proposals_won": 15,
                    "win_rate": 0.3,
                    "total_earnings": 10000,
                    "average_rate": 85,
                    "active_contracts": 3
                },
                "updated_at": datetime.utcnow()
            }
            
# Зберігаємо аналітику
            analytics = UserAnalytics(**analytics_data)
            session.add(analytics)
            await session.commit()
            
# Отримуємо аналітику
            retrieved_analytics = await session.get(UserAnalytics, analytics_data["user_id"])
            
            assert retrieved_analytics is not None
            assert retrieved_analytics.metrics["proposals_sent"] == 50
            assert retrieved_analytics.metrics["win_rate"] == 0.3
    
    @pytest.mark.asyncio
    async def test_user_data_encryption(self):
        """Тест шифрування чутливих даних"""
        async with get_db_session() as session:
# Створюємо користувача з чутливими даними
            sensitive_data = {
                "user_id": "test_user_123",
                "email": "test@example.com",
                "access_token": "sensitive_access_token",
                "refresh_token": "sensitive_refresh_token"
            }
            
            user = User(**sensitive_data)
            session.add(user)
            await session.commit()
            
# Отримуємо користувача
            retrieved_user = await session.get(User, sensitive_data["user_id"])
            
# Перевіряємо що токени зашифровані в базі
            raw_data = await session.execute(
                "SELECT access_token, refresh_token FROM users WHERE user_id = $1",
                sensitive_data["user_id"]
            )
            raw_result = raw_data.fetchone()
            
            assert raw_result["access_token"] != sensitive_data["access_token"]
            assert raw_result["refresh_token"] != sensitive_data["refresh_token"]
            
# Перевіряємо що розшифровані дані правильні
            assert retrieved_user.access_token == sensitive_data["access_token"]
            assert retrieved_user.refresh_token == sensitive_data["refresh_token"]
    
    @pytest.mark.asyncio
    async def test_user_data_relationships(self):
        """Тест зв'язків між таблицями даних користувача"""
        async with get_db_session() as session:
# Створюємо користувача
            user = User(user_id="test_user_123", email="test@example.com")
            session.add(user)
            await session.commit()
            
# Створюємо аналітичні дані
            analytics = UserAnalytics(
                user_id="test_user_123",
                metrics={"proposals_sent": 50},
                updated_at=datetime.utcnow()
            )
            session.add(analytics)
            await session.commit()
            
# Перевіряємо зв'язок
            user_with_analytics = await session.execute(
                """
                SELECT u.user_id, u.email, a.metrics
                FROM users u
                JOIN user_analytics a ON u.user_id = a.user_id
                WHERE u.user_id = $1
                """,
                "test_user_123"
            )
            result = user_with_analytics.fetchone()
            
            assert result is not None
            assert result["email"] == "test@example.com"
            assert result["metrics"]["proposals_sent"] == 50
```

### Тести аналітичних даних

```python
# tests/integration/database/test_analytics_data.py
import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import get_db_session
from src.modules.analytics.models import UserAnalytics, ProposalAnalytics

class TestAnalyticsDataIntegration:
    @pytest.mark.asyncio
    async def test_analytics_data_aggregation(self):
        """Тест агрегації аналітичних даних"""
        async with get_db_session() as session:
# Створюємо тестові дані
            test_data = [
                {
                    "user_id": "test_user_123",
                    "metrics": {"proposals_sent": 10, "earnings": 1000},
                    "updated_at": datetime.utcnow() - timedelta(days=30)
                },
                {
                    "user_id": "test_user_123",
                    "metrics": {"proposals_sent": 15, "earnings": 1500},
                    "updated_at": datetime.utcnow() - timedelta(days=15)
                },
                {
                    "user_id": "test_user_123",
                    "metrics": {"proposals_sent": 20, "earnings": 2000},
                    "updated_at": datetime.utcnow()
                }
            ]
            
            for data in test_data:
                analytics = UserAnalytics(**data)
                session.add(analytics)
            await session.commit()
            
# Агрегуємо дані
            result = await session.execute(
                """
                SELECT 
                    user_id,
                    AVG(metrics->>'proposals_sent') as avg_proposals,
                    SUM(CAST(metrics->>'earnings' AS INTEGER)) as total_earnings
                FROM user_analytics
                WHERE user_id = $1
                GROUP BY user_id
                """,
                "test_user_123"
            )
            aggregated = result.fetchone()
            
            assert aggregated is not None
            assert float(aggregated["avg_proposals"]) == 15.0
            assert aggregated["total_earnings"] == 4500
    
    @pytest.mark.asyncio
    async def test_proposal_analytics_storage(self):
        """Тест збереження аналітики пропозицій"""
        async with get_db_session() as session:
# Створюємо аналітику пропозиції
            proposal_analytics = ProposalAnalytics(
                proposal_id="proposal_123",
                user_id="test_user_123",
                analysis_data={
                    "score": 0.85,
                    "suggestions": ["Add more details"],
                    "keywords": ["React", "Node.js"],
                    "confidence": 0.92
                },
                created_at=datetime.utcnow()
            )
            session.add(proposal_analytics)
            await session.commit()
            
# Отримуємо аналітику
            retrieved = await session.get(ProposalAnalytics, "proposal_123")
            
            assert retrieved is not None
            assert retrieved.analysis_data["score"] == 0.85
            assert "React" in retrieved.analysis_data["keywords"]
    
    @pytest.mark.asyncio
    async def test_analytics_data_performance(self):
        """Тест продуктивності запитів аналітики"""
        async with get_db_session() as session:
# Створюємо велику кількість тестових даних
            for i in range(1000):
                analytics = UserAnalytics(
                    user_id=f"user_{i}",
                    metrics={"proposals_sent": i, "earnings": i * 100},
                    updated_at=datetime.utcnow()
                )
                session.add(analytics)
            await session.commit()
            
# Тестуємо швидкий запит
            start_time = datetime.utcnow()
            result = await session.execute(
                "SELECT COUNT(*) FROM user_analytics WHERE user_id = $1",
                "user_500"
            )
            end_time = datetime.utcnow()
            
            count = result.fetchone()[0]
            query_time = (end_time - start_time).total_seconds()
            
            assert count == 1
            assert query_time < 0.1  # Не більше 100ms
    
    @pytest.mark.asyncio
    async def test_analytics_data_backup(self):
        """Тест резервного копіювання аналітичних даних"""
        async with get_db_session() as session:
# Створюємо тестові дані
            analytics = UserAnalytics(
                user_id="test_user_123",
                metrics={"proposals_sent": 50},
                updated_at=datetime.utcnow()
            )
            session.add(analytics)
            await session.commit()
            
# Створюємо резервну копію
            backup_result = await session.execute(
                """
                CREATE TABLE user_analytics_backup AS 
                SELECT * FROM user_analytics 
                WHERE user_id = $1
                """,
                "test_user_123"
            )
            
# Перевіряємо резервну копію
            backup_data = await session.execute(
                "SELECT * FROM user_analytics_backup WHERE user_id = $1",
                "test_user_123"
            )
            backup_row = backup_data.fetchone()
            
            assert backup_row is not None
            assert backup_row.metrics["proposals_sent"] == 50
```

---

## External Services Integration Tests

### Тести інтеграції з Upwork

```python
# tests/integration/external/test_upwork_integration.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.modules.upwork_integration.upwork_client import UpworkAPIClient

class TestUpworkIntegration:
    @pytest.mark.asyncio
    async def test_upwork_oauth_flow(self):
        """Тест OAuth flow з Upwork"""
        client = UpworkAPIClient()
        
# Тест ініціалізації OAuth
        with patch('src.modules.upwork_integration.oauth_security.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'authorization_url': 'https://www.upwork.com/oauth/authorize?client_id=test&response_type=code&scope=test'
            }
            mock_get.return_value = mock_response
            
            oauth_data = await client.initiate_oauth_flow("https://app.com/callback")
            
            assert "authorization_url" in oauth_data
            assert "state" in oauth_data
            assert "code_verifier" in oauth_data
    
    @pytest.mark.asyncio
    async def test_upwork_token_exchange(self):
        """Тест обміну коду на токени"""
        client = UpworkAPIClient()
        
        with patch('src.modules.upwork_integration.oauth_security.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token',
                'expires_in': 3600
            }
            mock_post.return_value = mock_response
            
            tokens = await client.exchange_code_for_tokens("test_code", "test_verifier")
            
            assert tokens["access_token"] == "test_access_token"
            assert tokens["refresh_token"] == "test_refresh_token"
    
    @pytest.mark.asyncio
    async def test_upwork_user_profile_fetch(self):
        """Тест отримання профілю користувача"""
        client = UpworkAPIClient()
        
        with patch('src.modules.upwork_integration.api_client.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'user': {
                    'id': '~0123456789',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'hourly_rate': 85,
                    'total_earnings': 15000
                }
            }
            mock_get.return_value = mock_response
            
            profile = await client.get_user_profile("test_access_token")
            
            assert profile["user"]["id"] == "~0123456789"
            assert profile["user"]["hourly_rate"] == 85
    
    @pytest.mark.asyncio
    async def test_upwork_proposals_fetch(self):
        """Тест отримання пропозицій"""
        client = UpworkAPIClient()
        
        with patch('src.modules.upwork_integration.api_client.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'proposals': [
                    {
                        'id': 'proposal_123',
                        'title': 'E-commerce Website',
                        'status': 'interviewing',
                        'budget': 5000
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            proposals = await client.get_user_proposals("test_access_token")
            
            assert len(proposals["proposals"]) == 1
            assert proposals["proposals"][0]["id"] == "proposal_123"
    
    @pytest.mark.asyncio
    async def test_upwork_rate_limiting(self):
        """Тест обробки rate limits від Upwork"""
        client = UpworkAPIClient()
        
        with patch('src.modules.upwork_integration.api_client.requests.get') as mock_get:
# Симулюємо rate limit
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {'Retry-After': '60'}
            mock_get.return_value = mock_response
            
# Перевіряємо обробку rate limit
            with pytest.raises(RateLimitExceeded):
                await client.get_user_profile("test_access_token")
    
    @pytest.mark.asyncio
    async def test_upwork_webhook_processing(self):
        """Тест обробки webhook від Upwork"""
        client = UpworkAPIClient()
        
        webhook_data = {
            "event": "proposal.updated",
            "data": {
                "proposal_id": "proposal_123",
                "status": "hired"
            }
        }
        
# Перевіряємо валідацію підпису
        signature = client._generate_webhook_signature(webhook_data)
        
        is_valid = client.validate_webhook_signature(webhook_data, signature)
        assert is_valid
        
# Перевіряємо обробку webhook
        processed = await client.process_webhook(webhook_data)
        assert processed["status"] == "processed"
```

### Тести інтеграції з OpenAI

```python
# tests/integration/external/test_openai_integration.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.modules.ai.openai_integration import OpenAIIntegration

class TestOpenAIIntegration:
    @pytest.mark.asyncio
    async def test_openai_proposal_analysis(self):
        """Тест аналізу пропозицій через OpenAI"""
        ai_client = OpenAIIntegration()
        
        with patch('src.modules.ai.openai_integration.openai.ChatCompletion.create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '''
            {
                "score": 0.85,
                "suggestions": ["Add more details about technologies"],
                "keywords": ["React", "Node.js"],
                "confidence": 0.92
            }
            '''
            mock_create.return_value = mock_response
            
            analysis = await ai_client.analyze_proposal(
                "Professional web developer with React experience"
            )
            
            assert analysis["score"] == 0.85
            assert "React" in analysis["keywords"]
            assert len(analysis["suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_openai_content_generation(self):
        """Тест генерації контенту через OpenAI"""
        ai_client = OpenAIIntegration()
        
        with patch('src.modules.ai.openai_integration.openai.ChatCompletion.create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '''
            {
                "proposal_text": "Professional web developer with 5 years experience...",
                "cover_letter": "Thank you for considering my proposal...",
                "portfolio_items": ["project1.com", "project2.com"]
            }
            '''
            mock_create.return_value = mock_response
            
            content = await ai_client.generate_proposal({
                "project_description": "E-commerce website",
                "budget": 5000
            })
            
            assert "proposal_text" in content
            assert "cover_letter" in content
            assert "portfolio_items" in content
    
    @pytest.mark.asyncio
    async def test_openai_error_handling(self):
        """Тест обробки помилок OpenAI"""
        ai_client = OpenAIIntegration()
        
        with patch('src.modules.ai.openai_integration.openai.ChatCompletion.create') as mock_create:
# Симулюємо помилку API
            mock_create.side_effect = Exception("OpenAI API error")
            
            with pytest.raises(AIProcessingError):
                await ai_client.analyze_proposal("test proposal")
    
    @pytest.mark.asyncio
    async def test_openai_rate_limiting(self):
        """Тест обробки rate limits OpenAI"""
        ai_client = OpenAIIntegration()
        
        with patch('src.modules.ai.openai_integration.openai.ChatCompletion.create') as mock_create:
# Симулюємо rate limit
            mock_create.side_effect = RateLimitError("Rate limit exceeded")
            
            with pytest.raises(RateLimitExceeded):
                await ai_client.generate_proposal({"project_description": "test"})
    
    @pytest.mark.asyncio
    async def test_openai_token_usage_tracking(self):
        """Тест відстеження використання токенів"""
        ai_client = OpenAIIntegration()
        
        with patch('src.modules.ai.openai_integration.openai.ChatCompletion.create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"result": "test"}'
            mock_response.usage = Mock()
            mock_response.usage.total_tokens = 150
            mock_create.return_value = mock_response
            
            await ai_client.analyze_proposal("test proposal")
            
# Перевіряємо що використання токенів відстежується
            assert ai_client.total_tokens_used > 0
```

---

## Module Interaction Tests

### Тести взаємодії Auth та Analytics

```python
# tests/integration/modules/test_auth_analytics.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.modules.auth.auth_manager import AuthManager
from src.modules.analytics.analytics_manager import AnalyticsManager

class TestAuthAnalyticsIntegration:
    @pytest.mark.asyncio
    async def test_user_login_analytics_tracking(self):
        """Тест відстеження аналітики при вході користувача"""
        auth_manager = AuthManager()
        analytics_manager = AnalyticsManager()
        
# Симулюємо вхід користувача
        login_event = {
            "user_id": "test_user_123",
            "action": "login",
            "ip_address": "192.168.1.50",
            "user_agent": "Mozilla/5.0...",
            "timestamp": datetime.utcnow()
        }
        
# Обробляємо вхід
        auth_result = await auth_manager.process_login(login_event)
        
# Перевіряємо що аналітика відстежується
        analytics_data = await analytics_manager.get_user_activity("test_user_123")
        
        assert analytics_data["last_login"] == login_event["timestamp"]
        assert analytics_data["login_count"] > 0
    
    @pytest.mark.asyncio
    async def test_user_logout_analytics_tracking(self):
        """Тест відстеження аналітики при виході користувача"""
        auth_manager = AuthManager()
        analytics_manager = AnalyticsManager()
        
# Симулюємо вихід користувача
        logout_event = {
            "user_id": "test_user_123",
            "action": "logout",
            "session_duration": 3600,  # 1 година
            "timestamp": datetime.utcnow()
        }
        
# Обробляємо вихід
        auth_result = await auth_manager.process_logout(logout_event)
        
# Перевіряємо що аналітика оновлюється
        analytics_data = await analytics_manager.get_user_activity("test_user_123")
        
        assert analytics_data["last_logout"] == logout_event["timestamp"]
        assert analytics_data["avg_session_duration"] > 0
    
    @pytest.mark.asyncio
    async def test_failed_login_analytics_tracking(self):
        """Тест відстеження невдалих спроб входу"""
        auth_manager = AuthManager()
        analytics_manager = AnalyticsManager()
        
# Симулюємо невдалі спроби входу
        for i in range(3):
            failed_login = {
                "user_id": "test_user_123",
                "action": "login_failed",
                "ip_address": "192.168.1.50",
                "timestamp": datetime.utcnow()
            }
            
            await auth_manager.process_failed_login(failed_login)
        
# Перевіряємо що аналітика відстежує невдалі спроби
        security_analytics = await analytics_manager.get_security_analytics("test_user_123")
        
        assert security_analytics["failed_login_attempts"] >= 3
        assert security_analytics["account_locked"] == True
```

### Тести взаємодії AI та Security

```python
# tests/integration/modules/test_ai_security.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.modules.ai.ai_manager import AIManager
from src.modules.security.security_manager import SecurityManager

class TestAISecurityIntegration:
    @pytest.mark.asyncio
    async def test_ai_content_security_validation(self):
        """Тест валідації безпеки AI контенту"""
        ai_manager = AIManager()
        security_manager = SecurityManager()
        
# Генеруємо контент через AI
        generated_content = await ai_manager.generate_proposal({
            "project_description": "E-commerce website development"
        })
        
# Перевіряємо безпеку контенту
        security_check = await security_manager.validate_content_security(generated_content)
        
        assert security_check["is_safe"] == True
        assert security_check["toxicity_score"] < 0.1
        assert "personal_data" not in security_check["issues"]
    
    @pytest.mark.asyncio
    async def test_ai_input_security_validation(self):
        """Тест валідації безпеки вхідних даних для AI"""
        ai_manager = AIManager()
        security_manager = SecurityManager()
        
# Тестуємо безпечні вхідні дані
        safe_input = "Professional web developer with React experience"
        safe_check = await security_manager.validate_input_security(safe_input)
        assert safe_check["is_safe"] == True
        
# Тестуємо небезпечні вхідні дані
        malicious_input = "'; DROP TABLE users; --"
        malicious_check = await security_manager.validate_input_security(malicious_input)
        assert malicious_check["is_safe"] == False
        assert "sql_injection" in malicious_check["threats"]
    
    @pytest.mark.asyncio
    async def test_ai_rate_limiting_integration(self):
        """Тест інтеграції rate limiting з AI"""
        ai_manager = AIManager()
        security_manager = SecurityManager()
        
# Симулюємо багато запитів до AI
        for i in range(50):
            try:
                await ai_manager.analyze_proposal(f"Test proposal {i}")
            except RateLimitExceeded:
                break
        
# Перевіряємо що rate limiting спрацював
        rate_limit_status = await security_manager.get_rate_limit_status("ai_operations")
        assert rate_limit_status["limit_exceeded"] == True
    
    @pytest.mark.asyncio
    async def test_ai_threat_detection_integration(self):
        """Тест інтеграції виявлення загроз з AI"""
        ai_manager = AIManager()
        security_manager = SecurityManager()
        
# Симулюємо підозрілу активність
        suspicious_activity = {
            "user_id": "test_user_123",
            "action": "ai_generation",
            "input": "malicious input",
            "output": "suspicious output",
            "timestamp": datetime.utcnow()
        }
        
# Обробляємо через AI
        ai_result = await ai_manager.process_request(suspicious_activity)
        
# Перевіряємо виявлення загрози
        threats = await security_manager.detect_threats([suspicious_activity])
        
        assert len(threats) > 0
        assert any(t.severity in ["medium", "high"] for t in threats)
```

---

## Чек-лист Integration тестів

### API Integration Tests
- [ ] Тести всіх REST API endpoints
- [ ] Тести авторизації та аутентифікації
- [ ] Тести валідації вхідних даних
- [ ] Тести обробки помилок
- [ ] Тести rate limiting

### Database Integration Tests
- [ ] Тести збереження та отримання даних
- [ ] Тести шифрування чутливих даних
- [ ] Тести зв'язків між таблицями
- [ ] Тести продуктивності запитів
- [ ] Тести резервного копіювання

### External Services Integration Tests
- [ ] Тести інтеграції з Upwork API
- [ ] Тести інтеграції з OpenAI API
- [ ] Тести обробки rate limits
- [ ] Тести обробки помилок зовнішніх сервісів
- [ ] Тести webhook обробки

### Module Interaction Tests
- [ ] Тести взаємодії між модулями
- [ ] Тести передачі даних між компонентами
- [ ] Тести обробки подій
- [ ] Тести конфлікт-резолюції
- [ ] Тести синхронізації даних

### Загальні вимоги
- [ ] Автоматичне виконання в CI/CD
- [ ] Мокавання зовнішніх залежностей
- [ ] Тести в ізольованому середовищі
- [ ] Документація тестів
- [ ] Моніторинг часу виконання

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 16:30 