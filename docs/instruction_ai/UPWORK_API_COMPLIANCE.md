# 🔥 КРИТИЧНІ ІНСТРУКЦІЇ: ДОТРИМАННЯ СТАНДАРТІВ UPWORK API

**⚠️ ОБОВ'ЯЗКОВО ДО ВИКОНАННЯ**  
**🚨 НЕ ДОЗВОЛЯТИ ВІДХИЛЕННЯ ВІД ЦИХ СТАНДАРТІВ**  
**📋 КОНТРОЛЬ ЯКОСТІ НА КОЖНОМУ ЕТАПІ**

---

## 🎯 **КРИТИЧНА МЕТА**

**Наш проект ПОВИНЕН повністю відповідати офіційній документації Upwork API.** Будь-які відхилення від стандартів Upwork API НЕДОПУСТИМІ та будуть відхилені.

---

## 📚 **ОФІЦІЙНІ ДЖЕРЕЛА UPWORK API**

### **Обов'язкові документи для вивчення:**
1. **Upwork API Documentation**: https://developers.upwork.com/
2. **Jobs API Reference**: https://developers.upwork.com/reference/jobs
3. **Freelancers API Reference**: https://developers.upwork.com/reference/freelancers
4. **Clients API Reference**: https://developers.upwork.com/reference/clients
5. **Messages API Reference**: https://developers.upwork.com/reference/messages
6. **Workdiary API Reference**: https://developers.upwork.com/reference/workdiary
7. **Contracts API Reference**: https://developers.upwork.com/reference/contracts
8. **Earnings API Reference**: https://developers.upwork.com/reference/earnings

### **Обов'язкові стандарти:**
- **OAuth 2.0** для авторизації
- **REST API** для всіх endpoint'ів
- **JSON** для всіх відповідей
- **HTTP Status Codes** відповідно до RFC
- **Rate Limiting** відповідно до Upwork обмежень

---

## 🔥 **КРИТИЧНІ ВИМОГИ ДО СТРУКТУРИ ДАНИХ**

### **1. ОБОВ'ЯЗКОВІ ПОЛЯ ДЛЯ ВАКАНСІЙ (JOBS)**

```json
{
    "id": "~0123456789012345",                    // ОБОВ'ЯЗКОВО: формат ~ + 16 цифр
    "title": "Job Title",                         // ОБОВ'ЯЗКОВО: string
    "description": "Job description",             // ОБОВ'ЯЗКОВО: string
    "budget": {                                   // ОБОВ'ЯЗКОВО: object
        "min": 1000,                             // ОБОВ'ЯЗКОВО: number
        "max": 5000,                             // ОБОВ'ЯЗКОВО: number
        "type": "fixed"                          // ОБОВ'ЯЗКОВО: "fixed" | "hourly"
    },
    "client": {                                   // ОБОВ'ЯЗКОВО: object
        "id": "~0123456789012346",               // ОБОВ'ЯЗКОВО: формат ~ + 16 цифр
        "name": "Client Name",                   // ОБОВ'ЯЗКОВО: string
        "rating": 4.8,                           // ОБОВ'ЯЗКОВО: number (0-5)
        "reviews_count": 15,                     // ОБОВ'ЯЗКОВО: number
        "total_spent": 50000,                    // ОБОВ'ЯЗКОВО: number
        "location": "United States"              // ОБОВ'ЯЗКОВО: string
    },
    "skills": ["python", "react"],               // ОБОВ'ЯЗКОВО: array of strings
    "posted_time": "2024-01-15T10:30:00Z",       // ОБОВ'ЯЗКОВО: ISO 8601
    "category": "Web Development",               // ОБОВ'ЯЗКОВО: string
    "subcategory": "Web Programming",            // ОБОВ'ЯЗКОВО: string
    "experience_level": "intermediate",          // ОБОВ'ЯЗКОВО: "beginner" | "intermediate" | "expert"
    "project_length": "3-6 months",              // ОБОВ'ЯЗКОВО: string
    "hours_per_week": "10-30 hrs/week",          // ОБОВ'ЯЗКОВО: string
    "job_type": "hourly",                        // ОБОВ'ЯЗКОВО: "hourly" | "fixed"
    "url": "https://www.upwork.com/jobs/~0123456789012345", // ОБОВ'ЯЗКОВО: string
    "proposals_count": 8,                        // ОБОВ'ЯЗКОВО: number
    "client_hires": 5,                           // ОБОВ'ЯЗКОВО: number
    "payment_verified": true,                    // ОБОВ'ЯЗКОВО: boolean
    "preferred_qualifications": ["AWS"],         // ОБОВ'ЯЗКОВО: array of strings
    "attachments": [],                           // ОБОВ'ЯЗКОВО: array
    "enterprise_job": false,                     // ОБОВ'ЯЗКОВО: boolean
    "job_status": "open"                         // ОБОВ'ЯЗКОВО: "open" | "closed" | "cancelled"
}
```

### **2. ОБОВ'ЯЗКОВІ ПОЛЯ ДЛЯ ФРІЛАНСЕРІВ (FREELANCERS)**

```json
{
    "id": "~0123456789012345",                   // ОБОВ'ЯЗКОВО: формат ~ + 16 цифр
    "name": "John Doe",                          // ОБОВ'ЯЗКОВО: string
    "title": "Full Stack Developer",             // ОБОВ'ЯЗКОВО: string
    "description": "Experienced developer...",   // ОБОВ'ЯЗКОВО: string
    "skills": [                                  // ОБОВ'ЯЗКОВО: array of objects
        {
            "skill": "python",                   // ОБОВ'ЯЗКОВО: string
            "level": "expert"                    // ОБОВ'ЯЗКОВО: "beginner" | "intermediate" | "expert"
        }
    ],
    "hourly_rate": 35.0,                         // ОБОВ'ЯЗКОВО: number
    "total_earnings": 45000.0,                   // ОБОВ'ЯЗКОВО: number
    "success_rate": 98.0,                        // ОБОВ'ЯЗКОВО: number (0-100)
    "member_since": "2020-01-15T00:00:00Z",      // ОБОВ'ЯЗКОВО: ISO 8601
    "location": "Ukraine",                       // ОБОВ'ЯЗКОВО: string
    "timezone": "UTC+2",                         // ОБОВ'ЯЗКОВО: string
    "availability": "full-time",                 // ОБОВ'ЯЗКОВО: "full-time" | "part-time" | "not-available"
    "verification_status": "verified",           // ОБОВ'ЯЗКОВО: "verified" | "unverified"
    "profile_completion": 95,                    // ОБОВ'ЯЗКОВО: number (0-100)
    "response_time": "2 hours",                  // ОБОВ'ЯЗКОВО: string
    "total_jobs": 25,                            // ОБОВ'ЯЗКОВО: number
    "total_hours": 1200,                         // ОБОВ'ЯЗКОВО: number
    "feedback_score": 4.9,                       // ОБОВ'ЯЗКОВО: number (0-5)
    "reviews_count": 18                          // ОБОВ'ЯЗКОВО: number
}
```

### **3. ОБОВ'ЯЗКОВІ ПОЛЯ ДЛЯ КЛІЄНТІВ (CLIENTS)**

```json
{
    "id": "~0123456789012346",                   // ОБОВ'ЯЗКОВО: формат ~ + 16 цифр
    "name": "Tech Solutions Inc",                // ОБОВ'ЯЗКОВО: string
    "rating": 4.8,                               // ОБОВ'ЯЗКОВО: number (0-5)
    "reviews_count": 15,                         // ОБОВ'ЯЗКОВО: number
    "total_spent": 50000,                        // ОБОВ'ЯЗКОВО: number
    "location": "United States",                 // ОБОВ'ЯЗКОВО: string
    "member_since": "2020-03-15T00:00:00Z",      // ОБОВ'ЯЗКОВО: ISO 8601
    "hire_rate": 85,                             // ОБОВ'ЯЗКОВО: number (0-100)
    "avg_hourly_rate": 45,                       // ОБОВ'ЯЗКОВО: number
    "total_hired": 12                            // ОБОВ'ЯЗКОВО: number
}
```

---

## 🚨 **КРИТИЧНІ ПРАВИЛА РОЗРОБКИ**

### **1. НЕ ДОЗВОЛЯТИ ВІДХИЛЕННЯ ВІД СТАНДАРТІВ**
- ❌ **ЗАБОРОНЕНО** використовувати власні поля
- ❌ **ЗАБОРОНЕНО** змінювати типи даних
- ❌ **ЗАБОРОНЕНО** пропускати обов'язкові поля
- ❌ **ЗАБОРОНЕНО** використовувати неправильні формати ID
- ❌ **ЗАБОРОНЕНО** ігнорувати офіційну документацію

### **2. ОБОВ'ЯЗКОВІ ПЕРЕВІРКИ**
- ✅ **ОБОВ'ЯЗКОВО** перевіряти кожне поле на відповідність документації
- ✅ **ОБОВ'ЯЗКОВО** тестувати з реальними прикладами з Upwork
- ✅ **ОБОВ'ЯЗКОВО** валідувати формати даних
- ✅ **ОБОВ'ЯЗКОВО** перевіряти HTTP статус коди
- ✅ **ОБОВ'ЯЗКОВО** тестувати обробку помилок

### **3. КОНТРОЛЬ ЯКОСТІ**
- 🔍 **ПЕРЕВІРЯТИ** кожен commit на відповідність стандартам
- 🔍 **ТЕСТУВАТИ** всі endpoint'и з реальними даними
- 🔍 **ВАЛІДУВАТИ** структуру відповідей
- 🔍 **ПЕРЕВІРЯТИ** обробку edge cases

---

## 📋 **ОБОВ'ЯЗКОВІ API ENDPOINTS**

### **Jobs API (ОБОВ'ЯЗКОВО РЕАЛІЗУВАТИ ВСІ)**
```python
# ОБОВ'ЯЗКОВІ ENDPOINTS
GET    /api/v3/jobs/search                    # Пошук вакансій
GET    /api/v3/jobs/{job_id}                  # Деталі вакансії
GET    /api/v3/jobs/{job_id}/proposals        # Пропозиції до вакансії
POST   /api/v3/jobs/{job_id}/proposals        # Створення пропозиції
GET    /api/v3/jobs/categories                # Категорії вакансій
GET    /api/v3/jobs/skills                    # Навички
```

### **Freelancers API (ОБОВ'ЯЗКОВО РЕАЛІЗУВАТИ ВСІ)**
```python
# ОБОВ'ЯЗКОВІ ENDPOINTS
GET    /api/v3/freelancers/search             # Пошук фрілансерів
GET    /api/v3/freelancers/{freelancer_id}    # Профіль фрілансера
GET    /api/v3/freelancers/{freelancer_id}/portfolio  # Портфоліо
GET    /api/v3/freelancers/{freelancer_id}/workdiary  # Робочий щоденник
```

### **Clients API (ОБОВ'ЯЗКОВО РЕАЛІЗУВАТИ ВСІ)**
```python
# ОБОВ'ЯЗКОВІ ENDPOINTS
GET    /api/v3/clients/{client_id}            # Інформація про клієнта
GET    /api/v3/clients/{client_id}/jobs       # Вакансії клієнта
GET    /api/v3/clients/{client_id}/reviews    # Відгуки про клієнта
```

### **Messages API (ОБОВ'ЯЗКОВО РЕАЛІЗУВАТИ ВСІ)**
```python
# ОБОВ'ЯЗКОВІ ENDPOINTS
GET    /api/v3/messages/rooms                 # Кімнати повідомлень
GET    /api/v3/messages/rooms/{room_id}       # Повідомлення в кімнаті
POST   /api/v3/messages/rooms/{room_id}       # Відправка повідомлення
```

### **Contracts API (ОБОВ'ЯЗКОВО РЕАЛІЗУВАТИ ВСІ)**
```python
# ОБОВ'ЯЗКОВІ ENDPOINTS
GET    /api/v3/contracts                      # Контракти
GET    /api/v3/contracts/{contract_id}        # Деталі контракту
GET    /api/v3/contracts/{contract_id}/hours  # Години роботи
```

### **Earnings API (ОБОВ'ЯЗКОВО РЕАЛІЗУВАТИ ВСІ)**
```python
# ОБОВ'ЯЗКОВІ ENDPOINTS
GET    /api/v3/earnings                       # Заробіток
GET    /api/v3/earnings/reports               # Звіти про заробіток
```

---

## 🔧 **ТЕХНІЧНІ ВИМОГИ**

### **1. ОБОВ'ЯЗКОВІ ЗАГОЛОВКИ**
```python
headers = {
    "Authorization": "Bearer {access_token}",   # ОБОВ'ЯЗКОВО
    "Content-Type": "application/json",        # ОБОВ'ЯЗКОВО
    "Accept": "application/json"               # ОБОВ'ЯЗКОВО
}
```

### **2. ОБОВ'ЯЗКОВІ HTTP СТАТУС КОДИ**
```python
200 OK                    # Успішна відповідь
201 Created              # Створено ресурс
400 Bad Request          # Помилка запиту
401 Unauthorized         # Не авторизовано
403 Forbidden            # Заборонено
404 Not Found            # Не знайдено
429 Too Many Requests    # Перевищено ліміт
500 Internal Server Error # Помилка сервера
```

### **3. ОБОВ'ЯЗКОВІ ФОРМАТИ ДАТ**
```python
# ОБОВ'ЯЗКОВО використовувати ISO 8601
"2024-01-15T10:30:00Z"   # UTC час
"2024-01-15T10:30:00+02:00"  # З часовим поясом
```

### **4. ОБОВ'ЯЗКОВІ ФОРМАТИ ID**
```python
# ОБОВ'ЯЗКОВО використовувати формат Upwork
"~0123456789012345"      # ~ + 16 цифр
```

---

## 🧪 **ОБОВ'ЯЗКОВІ ТЕСТИ**

### **1. ВАЛІДАЦІЯ СТРУКТУРИ**
```python
def test_job_structure():
    """ОБОВ'ЯЗКОВО: Перевірити структуру вакансії"""
    job = get_job_details("~0123456789012345")
    
    # ОБОВ'ЯЗКОВІ ПОЛЯ
    assert "id" in job
    assert "title" in job
    assert "description" in job
    assert "budget" in job
    assert "client" in job
    assert "skills" in job
    assert "posted_time" in job
    
    # ОБОВ'ЯЗКОВІ ТИПИ
    assert isinstance(job["id"], str)
    assert job["id"].startswith("~")
    assert len(job["id"]) == 17
    assert isinstance(job["budget"], dict)
    assert "min" in job["budget"]
    assert "max" in job["budget"]
    assert "type" in job["budget"]
```

### **2. ВАЛІДАЦІЯ ФОРМАТІВ**
```python
def test_data_formats():
    """ОБОВ'ЯЗКОВО: Перевірити формати даних"""
    import re
    from datetime import datetime
    
    # ОБОВ'ЯЗКОВО: Валідація ID
    id_pattern = r"^~[0-9]{16}$"
    assert re.match(id_pattern, job["id"])
    
    # ОБОВ'ЯЗКОВО: Валідація дати
    datetime.fromisoformat(job["posted_time"].replace("Z", "+00:00"))
    
    # ОБОВ'ЯЗКОВО: Валідація рейтингу
    assert 0 <= job["client"]["rating"] <= 5
```

### **3. ВАЛІДАЦІЯ ENDPOINTS**
```python
def test_api_endpoints():
    """ОБОВ'ЯЗКОВО: Перевірити всі endpoint'и"""
    endpoints = [
        "/api/v3/jobs/search",
        "/api/v3/jobs/{job_id}",
        "/api/v3/freelancers/search",
        "/api/v3/clients/{client_id}",
        "/api/v3/messages/rooms"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in [200, 201, 400, 401, 404]
        assert response.headers["Content-Type"] == "application/json"
```

---

## 📊 **КОНТРОЛЬ ЯКОСТІ**

### **1. ОБОВ'ЯЗКОВІ ПЕРЕВІРКИ ПЕРЕД COMMIT**
- [ ] Всі поля відповідають документації Upwork
- [ ] Всі типи даних правильні
- [ ] Всі формати відповідають стандартам
- [ ] Всі endpoint'и реалізовані
- [ ] Всі тести проходять
- [ ] Валідація структури успішна

### **2. ОБОВ'ЯЗКОВІ ПЕРЕВІРКИ ПЕРЕД DEPLOY**
- [ ] Інтеграційні тести з реальним API
- [ ] Перевірка всіх edge cases
- [ ] Валідація обробки помилок
- [ ] Перевірка rate limiting
- [ ] Тестування з реальними даними

### **3. ОБОВ'ЯЗКОВІ МОНІТОРИНГИ**
- [ ] Моніторинг відповідності API
- [ ] Логування помилок валідації
- [ ] Перевірка структури відповідей
- [ ] Моніторинг продуктивності

---

## 🚨 **КРИТИЧНІ ПОПЕРЕДЖЕННЯ**

### **1. НЕ ДОЗВОЛЯТИ ВІДХИЛЕННЯ**
- Будь-які відхилення від стандартів Upwork API НЕДОПУСТИМІ
- Всі зміни ПОВИННІ бути узгоджені з офіційною документацією
- Тестування ПОВИННО використовувати реальні приклади з Upwork

### **2. ОБОВ'ЯЗКОВА ВАЛІДАЦІЯ**
- Кожен endpoint ПОВИНЕН проходити валідацію
- Кожна відповідь ПОВИННА відповідати схемі
- Кожна помилка ПОВИННА оброблятися правильно

### **3. ПОСТІЙНИЙ КОНТРОЛЬ**
- Регулярно перевіряти відповідність документації
- Оновлювати тести при зміні API
- Моніторити зміни в документації Upwork

---

## 📞 **ВІДПОВІДАЛЬНІСТЬ**

### **Кожен розробник ПОВИНЕН:**
1. **ЗНАЙОМИТИСЯ** з офіційною документацією Upwork API
2. **ДОТРИМУВАТИСЯ** всіх стандартів та форматів
3. **ТЕСТУВАТИ** свою роботу на відповідність
4. **ПЕРЕВІРЯТИ** структуру даних перед commit
5. **ПОВІДОМЛЯТИ** про будь-які відхилення

### **Керівник проекту ПОВИНЕН:**
1. **КОНТРОЛЮВАТИ** дотримання стандартів
2. **ПЕРЕВІРЯТИ** якість коду
3. **ЗАБЕЗПЕЧУВАТИ** тестування
4. **МОНІТОРИТИ** відповідність API

---

**⚠️ ЦІ ІНСТРУКЦІЇ Є КРИТИЧНИМИ ТА ОБОВ'ЯЗКОВИМИ ДО ВИКОНАННЯ!**

**🚨 БУДЬ-ЯКІ ВІДХИЛЕННЯ ВІД ЦИХ СТАНДАРТІВ НЕДОПУСТИМІ!**

**📋 КОНТРОЛЬ ЯКОСТІ НА КОЖНОМУ ЕТАПІ РОЗРОБКИ!** 