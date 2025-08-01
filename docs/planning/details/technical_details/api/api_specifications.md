# API Специфікації

## Огляд

Цей документ містить детальні специфікації всіх API endpoints проекту Upwork AI Assistant.

## Базові принципи

### Аутентифікація
Всі API endpoints (крім публічних) вимагають JWT токен в заголовку:
```
Authorization: Bearer <jwt_token>
```

### Формат відповіді
Всі відповіді повертаються в JSON форматі:
```json
{
  "success": true,
  "data": {...},
  "message": "Success message",
  "timestamp": "2024-12-19T18:00:00Z"
}
```

### Обробка помилок
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {...}
  },
  "timestamp": "2024-12-19T18:00:00Z"
}
```

## AI Service API

### Налаштування AI

#### Отримання налаштувань AI
```http
GET /api/ai/settings
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "ai_disclosure": {
      "enabled": true,
      "position": "end",
      "template": "default",
      "custom_text": "",
      "auto_add": true
    },
    "editing": {
      "auto_save": true,
      "save_interval": 30,
      "draft_retention": 7,
      "validation": {
        "min_length": 100,
        "max_length": 2000,
        "check_spam": true,
        "require_review": true
      }
    }
  }
}
```

#### Оновлення налаштувань AI
```http
PUT /api/ai/settings
```

**Тіло запиту:**
```json
{
  "ai_disclosure": {
    "enabled": true,
    "position": "end",
    "template": "detailed",
    "custom_text": "Custom disclosure text",
    "auto_add": true
  },
  "editing": {
    "auto_save": true,
    "save_interval": 60,
    "draft_retention": 14,
    "validation": {
      "min_length": 150,
      "max_length": 2500,
      "check_spam": true,
      "require_review": true
    }
  }
}
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "message": "Settings updated successfully",
    "settings": {...}
  }
}
```

#### Скидання налаштувань до за замовчуванням
```http
POST /api/ai/settings/reset
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "message": "Settings reset to default",
    "settings": {...}
  }
}
```

### Генерація відгуків

#### Генерація відгуку
```http
POST /api/ai/generate-proposal
```

**Тіло запиту:**
```json
{
  "job_id": "~0123456789012345",
  "user_profile": {
    "skills": ["python", "django"],
    "experience_years": 5,
    "hourly_rate": 35
  },
  "template_type": "professional",
  "tone": "friendly",
  "include_disclosure": true
}
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "proposal_id": "prop_123",
    "content": "Generated proposal content...",
    "ai_disclosure": "AI disclosure text...",
    "full_content": "Complete proposal with disclosure",
    "word_count": 250,
    "estimated_cost": 0.045,
    "generated_at": "2024-12-19T18:00:00Z"
  }
}
```

### Управління чернетками

#### Збереження чернетки
```http
POST /api/ai/drafts
```

**Тіло запиту:**
```json
{
  "job_id": "~0123456789012345",
  "content": "Proposal content...",
  "ai_generated_content": "Original AI content...",
  "user_edited_content": "User modifications...",
  "ai_disclosure_included": true
}
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "draft_id": "draft_456",
    "saved_at": "2024-12-19T18:00:00Z",
    "word_count": 300
  }
}
```

#### Отримання чернетки
```http
GET /api/ai/drafts/{draft_id}
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "draft_id": "draft_456",
    "job_id": "~0123456789012345",
    "content": "Current proposal content...",
    "ai_generated_content": "Original AI content...",
    "user_edited_content": "User modifications...",
    "ai_disclosure_included": true,
    "validation_status": "valid",
    "validation_errors": [],
    "created_at": "2024-12-19T17:30:00Z",
    "updated_at": "2024-12-19T18:00:00Z",
    "last_edited_at": "2024-12-19T18:00:00Z"
  }
}
```

#### Оновлення чернетки
```http
PUT /api/ai/drafts/{draft_id}
```

**Тіло запиту:**
```json
{
  "content": "Updated proposal content...",
  "user_edited_content": "New user modifications...",
  "ai_disclosure_included": true
}
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "draft_id": "draft_456",
    "updated_at": "2024-12-19T18:15:00Z",
    "word_count": 350
  }
}
```

#### Список чернеток користувача
```http
GET /api/ai/drafts
```

**Параметри запиту:**
- `page` (int): Номер сторінки (за замовчуванням: 1)
- `limit` (int): Кількість записів на сторінку (за замовчуванням: 10)
- `status` (string): Фільтр за статусом ("draft", "ready", "sent")

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "drafts": [
      {
        "draft_id": "draft_456",
        "job_id": "~0123456789012345",
        "job_title": "Python Developer Needed",
        "content_preview": "First 100 characters...",
        "word_count": 350,
        "validation_status": "valid",
        "created_at": "2024-12-19T17:30:00Z",
        "updated_at": "2024-12-19T18:15:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "pages": 3
    }
  }
}
```

### Валідація відгуків

#### Валідація відгуку
```http
POST /api/ai/validate-proposal
```

**Тіло запиту:**
```json
{
  "content": "Proposal content to validate...",
  "job_id": "~0123456789012345",
  "ai_disclosure_included": true
}
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "validation_status": "valid",
    "errors": [],
    "warnings": [
      "Content is quite short, consider adding more details"
    ],
    "suggestions": [
      "Add specific examples of your work",
      "Mention relevant experience with similar projects"
    ],
    "word_count": 250,
    "readability_score": 85,
    "spam_score": 0.02
  }
}
```

### Відправка відгуків

#### Відправка відгуку
```http
POST /api/ai/send-proposal
```

**Тіло запиту:**
```json
{
  "draft_id": "draft_456",
  "job_id": "~0123456789012345",
  "final_content": "Final proposal content...",
  "bid_amount": 1500,
  "estimated_duration": "2-3 weeks",
  "cover_letter": "Cover letter content...",
  "attachments": []
}
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "proposal_id": "prop_789",
    "upwork_proposal_id": "~0123456789012346",
    "sent_at": "2024-12-19T18:30:00Z",
    "status": "submitted",
    "estimated_response_time": "2-3 days"
  }
}
```

## Upwork Service API

### Пошук вакансій

#### Пошук вакансій
```http
GET /api/upwork/jobs/search
```

**Параметри запиту:**
- `q` (string): Пошуковий запит
- `category` (string): Категорія вакансій
- `job_type` (string): Тип роботи ("hourly", "fixed")
- `budget_min` (int): Мінімальний бюджет
- `budget_max` (int): Максимальний бюджет
- `experience_level` (string): Рівень досвіду
- `page` (int): Номер сторінки
- `limit` (int): Кількість результатів

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": "~0123456789012345",
        "title": "Python Developer Needed",
        "description": "Job description...",
        "budget": {
          "min": 1000,
          "max": 5000,
          "type": "fixed"
        },
        "client": {
          "id": "~0123456789012346",
          "name": "Tech Solutions Inc",
          "rating": 4.8,
          "reviews_count": 15
        },
        "skills": ["python", "django", "postgresql"],
        "posted_time": "2024-12-19T10:30:00Z",
        "proposals_count": 8,
        "url": "https://www.upwork.com/jobs/~0123456789012345"
      }
    ],
    "pagination": {
      "total": 1500,
      "page": 1,
      "limit": 20,
      "pages": 75
    }
  }
}
```

#### Отримання деталей вакансії
```http
GET /api/upwork/jobs/{job_id}
```

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "id": "~0123456789012345",
    "title": "Python Developer Needed",
    "description": "Detailed job description...",
    "budget": {
      "min": 1000,
      "max": 5000,
      "type": "fixed"
    },
    "client": {
      "id": "~0123456789012346",
      "name": "Tech Solutions Inc",
      "rating": 4.8,
      "reviews_count": 15,
      "total_spent": 50000,
      "location": "United States"
    },
    "skills": ["python", "django", "postgresql"],
    "posted_time": "2024-12-19T10:30:00Z",
    "category": "Web Development",
    "subcategory": "Web Programming",
    "experience_level": "intermediate",
    "project_length": "3-6 months",
    "hours_per_week": "10-30 hrs/week",
    "proposals_count": 8,
    "client_hires": 5,
    "payment_verified": true,
    "url": "https://www.upwork.com/jobs/~0123456789012345"
  }
}
```

## Analytics Service API

### Аналіз ефективності

#### Аналіз ефективності відгуків
```http
GET /api/analytics/proposals/effectiveness
```

**Параметри запиту:**
- `date_from` (string): Початкова дата (YYYY-MM-DD)
- `date_to` (string): Кінцева дата (YYYY-MM-DD)
- `group_by` (string): Групування ("day", "week", "month")

**Відповідь:**
```json
{
  "success": true,
  "data": {
    "total_proposals": 45,
    "responses_received": 12,
    "response_rate": 26.67,
    "hires_received": 3,
    "hire_rate": 6.67,
    "average_response_time": "2.5 days",
    "top_performing_templates": [
      {
        "template": "professional",
        "response_rate": 35.0,
        "hire_rate": 10.0
      }
    ],
    "ai_disclosure_impact": {
      "with_disclosure": {
        "response_rate": 28.0,
        "hire_rate": 7.0
      },
      "without_disclosure": {
        "response_rate": 25.0,
        "hire_rate": 6.0
      }
    }
  }
}
```

## Коди помилок

### Загальні помилки
- `AUTHENTICATION_FAILED` - Помилка аутентифікації
- `AUTHORIZATION_FAILED` - Помилка авторизації
- `VALIDATION_ERROR` - Помилка валідації
- `RATE_LIMIT_EXCEEDED` - Перевищення ліміту запитів
- `INTERNAL_SERVER_ERROR` - Внутрішня помилка сервера

### AI Service помилки
- `AI_GENERATION_FAILED` - Помилка генерації AI
- `AI_SETTINGS_INVALID` - Невірні налаштування AI
- `DRAFT_NOT_FOUND` - Чернетка не знайдена
- `PROPOSAL_VALIDATION_FAILED` - Помилка валідації відгуку
- `UPWORK_API_ERROR` - Помилка API Upwork

### Upwork Service помилки
- `UPWORK_AUTH_FAILED` - Помилка авторизації Upwork
- `UPWORK_RATE_LIMIT` - Перевищення ліміту Upwork
- `JOB_NOT_FOUND` - Вакансія не знайдена
- `PROPOSAL_SUBMISSION_FAILED` - Помилка відправки відгуку

## Rate Limiting

### Ліміти запитів
- **AI генерація**: 100 запитів/годину
- **Upwork API**: 1000 запитів/день
- **Валідація**: 500 запитів/годину
- **Аналітика**: 200 запитів/годину

### Заголовки rate limiting
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## Версіонування API

### Поточна версія
- **Версія**: v1
- **Статус**: Beta
- **Дата релізу**: 2024-12-19

### Плани версіонування
- **v1.1**: Додавання нових AI моделей
- **v1.2**: Розширення аналітики
- **v2.0**: Повна переробка API

## Документація

### Swagger/OpenAPI
API документація доступна за адресою:
```
GET /api/docs
```

### Postman Collection
Колекція Postman доступна для імпорту:
```
GET /api/postman-collection.json
``` 