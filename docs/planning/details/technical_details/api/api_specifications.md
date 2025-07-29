# API специфікації

> **Детальні специфікації REST API для Upwork Web App**

---

## Зміст

1. [Огляд API](#-огляд-api)
2. [Аутентифікація](#аутентифікація)
3. [Endpoints](#-endpoints)
4. [Моделі даних](#-моделі-даних)
5. [Помилки](#помилки)
6. [Rate Limiting](#rate-limiting)
7. [Документація](#документація)

---

## Огляд API

### Принципи дизайну
- [ ] **API-DESIGN-001**: RESTful архітектура
- [ ] **API-DESIGN-002**: JSON як формат даних
- [ ] **API-DESIGN-003**: Версіонування через URL
- [ ] **API-DESIGN-004**: Стандартні HTTP коди відповіді
- [ ] **API-DESIGN-005**: Консистентна структура відповідей

### Базовий URL
```
Production: https://api.upwork-web-app.com/v1
Staging: https://staging-api.upwork-web-app.com/v1
Development: http://localhost:8000/v1
```

### Формат відповідей
```json
{
  "success": true,
  "data": {...},
  "message": "Success message",
  "timestamp": "2024-12-19T17:50:00Z",
  "version": "1.0"
}
```

---

## Аутентифікація

### JWT токени
- [ ] **API-AUTH-001**: Bearer токени в Authorization header
- [ ] **API-AUTH-002**: Access токени з терміном дії 15 хвилин
- [ ] **API-AUTH-003**: Refresh токени з терміном дії 7 днів
- [ ] **API-AUTH-004**: Автоматичне оновлення токенів
- [ ] **API-AUTH-005**: Валідація токенів на кожному запиті

### OAuth 2.0
- [ ] **API-OAUTH-001**: PKCE flow для безпеки
- [ ] **API-OAUTH-002**: State параметр для CSRF захисту
- [ ] **API-OAUTH-003**: Secure redirect URIs
- [ ] **API-OAUTH-004**: Обробка помилок автентифікації
- [ ] **API-OAUTH-005**: Логування OAuth подій

### MFA підтримка
- [ ] **API-MFA-001**: TOTP верифікація для критичних операцій
- [ ] **API-MFA-002**: Backup коди для відновлення
- [ ] **API-MFA-003**: SMS аутентифікація (опціонально)
- [ ] **API-MFA-004**: Налаштування MFA через API
- [ ] **API-MFA-005**: Вимкнення MFA через API

---

## Endpoints

### Аутентифікація
- [ ] **POST /auth/register** - реєстрація користувача
- [ ] **POST /auth/login** - вхід користувача
- [ ] **POST /auth/logout** - вихід користувача
- [ ] **POST /auth/refresh** - оновлення токенів
- [ ] **GET /auth/profile** - отримання профілю

### OAuth з Upwork
- [ ] **GET /auth/upwork/init** - ініціалізація OAuth flow
- [ ] **GET /auth/upwork/callback** - обробка OAuth callback
- [ ] **POST /auth/upwork/refresh** - оновлення Upwork токенів
- [ ] **DELETE /auth/upwork/revoke** - відкликання токенів

### MFA
- [ ] **POST /auth/mfa/setup** - налаштування MFA
- [ ] **POST /auth/mfa/verify** - верифікація MFA коду
- [ ] **POST /auth/mfa/disable** - вимкнення MFA
- [ ] **GET /auth/mfa/backup-codes** - генерація backup кодів

### Вакансії
- [ ] **GET /jobs** - список вакансій
- [ ] **GET /jobs/{id}** - деталі вакансії
- [ ] **POST /jobs/search** - пошук вакансій
- [ ] **GET /jobs/favorites** - улюблені вакансії
- [ ] **POST /jobs/{id}/favorite** - додати в улюблені

### Пропозиції
- [ ] **GET /proposals** - список пропозицій
- [ ] **POST /proposals** - створення пропозиції
- [ ] **GET /proposals/{id}** - деталі пропозиції
- [ ] **PUT /proposals/{id}** - оновлення пропозиції
- [ ] **DELETE /proposals/{id}** - видалення пропозиції

### AI функціональність
- [ ] **POST /ai/generate-proposal** - генерація пропозиції
- [ ] **POST /ai/analyze-job** - аналіз вакансії
- [ ] **POST /ai/filter-jobs** - розумна фільтрація
- [ ] **POST /ai/predict-success** - прогнозування успіху
- [ ] **GET /ai/templates** - шаблони пропозицій

### Контракти
- [ ] **GET /contracts** - список контрактів
- [ ] **GET /contracts/{id}** - деталі контракту
- [ ] **GET /contracts/{id}/payments** - платежі по контракту
- [ ] **GET /contracts/{id}/time** - час роботи по контракту

### Аналітика
- [ ] **GET /analytics/overview** - загальна аналітика
- [ ] **GET /analytics/proposals** - аналітика пропозицій
- [ ] **GET /analytics/earnings** - аналітика доходів
- [ ] **GET /analytics/performance** - метрики продуктивності
- [ ] **GET /analytics/reports** - звіти

### Налаштування
- [ ] **GET /settings** - отримання налаштувань
- [ ] **PUT /settings** - оновлення налаштувань
- [ ] **GET /settings/notifications** - налаштування сповіщень
- [ ] **PUT /settings/notifications** - оновлення сповіщень
- [ ] **GET /settings/security** - налаштування безпеки

---

## Моделі даних

### Користувач
```json
{
  "id": "string",
  "email": "string",
  "name": "string",
  "avatar": "string",
  "timezone": "string",
  "language": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "mfa_enabled": "boolean",
  "upwork_connected": "boolean"
}
```

### Вакансія
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "budget": {
    "min": "number",
    "max": "number",
    "type": "string"
  },
  "skills": ["string"],
  "client": {
    "id": "string",
    "name": "string",
    "rating": "number",
    "total_spent": "number"
  },
  "posted_at": "datetime",
  "deadline": "datetime",
  "proposals_count": "number",
  "is_favorite": "boolean"
}
```

### Пропозиція
```json
{
  "id": "string",
  "job_id": "string",
  "cover_letter": "string",
  "bid_amount": "number",
  "estimated_duration": "number",
  "status": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "ai_generated": "boolean"
}
```

### Контракт
```json
{
  "id": "string",
  "job_id": "string",
  "client_id": "string",
  "title": "string",
  "rate": "number",
  "rate_type": "string",
  "status": "string",
  "start_date": "datetime",
  "end_date": "datetime",
  "total_earnings": "number"
}
```

---

## Помилки

### Стандартні HTTP коди
- [ ] **200** - Успішна операція
- [ ] **201** - Ресурс створено
- [ ] **400** - Неправильний запит
- [ ] **401** - Не авторизовано
- [ ] **403** - Заборонено
- [ ] **404** - Не знайдено
- [ ] **429** - Забагато запитів
- [ ] **500** - Внутрішня помилка сервера

### Формат помилок
```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": "object",
    "timestamp": "datetime"
  }
}
```

### Коди помилок
- [ ] **AUTH_001** - Неправильні облікові дані
- [ ] **AUTH_002** - Токен закінчився
- [ ] **AUTH_003** - MFA потрібна
- [ ] **AUTH_004** - Недостатньо прав
- [ ] **VALIDATION_001** - Неправильні дані
- [ ] **RATE_LIMIT_001** - Перевищено ліміт запитів
- [ ] **UPWORK_001** - Помилка Upwork API
- [ ] **AI_001** - Помилка AI сервісу

---

## ⏱ Rate Limiting

### Обмеження
- [ ] **API-RATE-001**: 100 запитів/хвилину для авторизованих користувачів
- [ ] **API-RATE-002**: 10 запитів/хвилину для неавторизованих користувачів
- [ ] **API-RATE-003**: 1000 запитів/день на користувача
- [ ] **API-RATE-004**: 50 запитів/хвилину для AI endpoints
- [ ] **API-RATE-005**: 20 запитів/хвилину для OAuth endpoints

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Обробка перевищення ліміту
- [ ] **API-RATE-006**: HTTP 429 статус код
- [ ] **API-RATE-007**: Retry-After header
- [ ] **API-RATE-008**: Логування перевищень
- [ ] **API-RATE-009**: Сповіщення адміністраторів
- [ ] **API-RATE-010**: Автоматичне відновлення після блокування

---

## Документація

### OpenAPI/Swagger
- [ ] **API-DOC-001**: Автоматична генерація документації
- [ ] **API-DOC-002**: Інтерактивна документація
- [ ] **API-DOC-003**: Приклади запитів та відповідей
- [ ] **API-DOC-004**: Опис всіх моделей даних
- [ ] **API-DOC-005**: Коди помилок та їх значення

### Postman Collection
- [ ] **API-DOC-006**: Готові колекції для тестування
- [ ] **API-DOC-007**: Environment змінні
- [ ] **API-DOC-008**: Приклади для всіх endpoints
- [ ] **API-DOC-009**: Автоматичні тести
- [ ] **API-DOC-010**: Документація для розробників

### SDK та клієнти
- [ ] **API-DOC-011**: Python SDK
- [ ] **API-DOC-012**: JavaScript SDK
- [ ] **API-DOC-013**: PHP SDK
- [ ] **API-DOC-014**: Go SDK
- [ ] **API-DOC-015**: .NET SDK

---

**Версія**: 1.0.0 