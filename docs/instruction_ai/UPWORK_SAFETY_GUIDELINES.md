# 🔒 ІНСТРУКЦІЇ БЕЗПЕКИ: РОБОТА З UPWORK API

**⚠️ КРИТИЧНІ ПРАВИЛА БЕЗПЕКИ**  
**🚨 ОБОВ'ЯЗКОВО ДО ВИКОНАННЯ**  
**📋 КОНТРОЛЬ НА КОЖНОМУ ЕТАПІ**

---

## 🎯 **МЕТА**

**Забезпечити безпечну та відповідну політикам Upwork роботу з API, уникнути блокування акаунту та проекту.**

---

## 🚨 **КРИТИЧНІ ЗАБОРОНИ**

### **1. АВТОМАТИЗАЦІЯ ВІДГУКІВ - ЗАБОРОНЕНО**
```python
# ❌ ЗАБОРОНЕНО - Автоматичне відправлення відгуків
def auto_apply_to_jobs(self, search_queries, freelancer_profile):
    for job in suitable_jobs:
        self.apply_to_job(job, freelancer_profile)  # ЗАБОРОНЕНО!

# ✅ ДОЗВОЛЕНО - Тільки рекомендації
def suggest_jobs(self, search_queries, freelancer_profile):
    suitable_jobs = self.smart_filter.filter_jobs(jobs, freelancer_profile)
    return suitable_jobs  # Тільки список підходящих вакансій
```

### **2. МАСОВІ ОПЕРАЦІЇ - ЗАБОРОНЕНО**
```python
# ❌ ЗАБОРОНЕНО - Масове відгукання
for job in suitable_jobs[:10]:  # Більше 5 відгуків за раз
    self.apply_to_job(job, freelancer_profile)

# ✅ ДОЗВОЛЕНО - Обмежена кількість
MAX_DAILY_APPLICATIONS = 5  # Максимум 5 відгуків на день
MAX_HOURLY_APPLICATIONS = 1  # Максимум 1 відгук на годину
```

### **3. AI ГЕНЕРАЦІЯ БЕЗ ПОПЕРЕДЖЕННЯ - ЗАБОРОНЕНО**
```python
# ❌ ЗАБОРОНЕНО - AI без попередження
def generate_proposal(self, job_data, freelancer_profile):
    return ai_generated_proposal  # Без попередження

# ✅ ДОЗВОЛЕНО - З попередженням
def generate_proposal(self, job_data, freelancer_profile):
    proposal = ai_generated_proposal
    
    ai_warning = """
    ⚠️ Цей відгук згенерований за допомогою AI.
    Будь ласка, перегляньте та відредагуйте перед відправкою.
    """
    
    return proposal + ai_warning
```

---

## 🔧 **ОБОВ'ЯЗКОВІ ЗАХОДИ БЕЗПЕКИ**

### **1. РЕЄСТРАЦІЯ НА DEVELOPERS.UPWORK.COM**

#### **Кроки реєстрації:**
```bash
# 1. Перейти на https://developers.upwork.com/
# 2. Створити акаунт розробника
# 3. Заповнити профіль компанії
# 4. Створити додаток з описом функціоналу
# 5. Отримати схвалення від Upwork
# 6. Отримати реальні API ключі
```

#### **Опис додатку для Upwork:**
```json
{
  "app_name": "Upwork Job Assistant",
  "description": "AI-powered tool for freelancers to find and analyze job opportunities on Upwork. Provides job recommendations, proposal templates, and market analysis. Does NOT automate job applications.",
  "website": "https://your-domain.com",
  "callback_url": "https://your-domain.com/auth/upwork/callback",
  "scopes": [
    "jobs:read",
    "freelancers:read", 
    "clients:read",
    "messages:read"
  ],
  "features": [
    "Job search and filtering",
    "Market analysis",
    "Proposal templates (manual use only)",
    "Client analysis",
    "Earnings tracking"
  ],
  "compliance": [
    "No automated job applications",
    "No mass messaging",
    "Manual review of all AI-generated content",
    "Respect for rate limits",
    "Compliance with Upwork ToS"
  ]
}
```

### **2. RATE LIMITING ТА ЗАТРИМКИ**

#### **Обов'язкові затримки:**
```python
import time
import random

class SafeUpworkClient:
    def __init__(self):
        self.last_request_time = None
        self.daily_requests = 0
        self.hourly_requests = 0
    
    def safe_api_call(self, func, *args, **kwargs):
        """Безпечний виклик API з затримками"""
        
        # Перевірка денних лімітів
        if self.daily_requests >= 1000:  # Upwork ліміт
            raise Exception("Денний ліміт запитів перевищено")
        
        # Перевірка погодинних лімітів
        if self.hourly_requests >= 100:  # Upwork ліміт
            time.sleep(3600)  # Чекаємо годину
            self.hourly_requests = 0
        
        # Затримка між запитами (2-5 секунд)
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < 2:
                time.sleep(random.uniform(2, 5))
        
        try:
            result = func(*args, **kwargs)
            
            # Оновлення лічильників
            self.last_request_time = time.time()
            self.daily_requests += 1
            self.hourly_requests += 1
            
            return result
            
        except RateLimitExceeded:
            # Затримка 60 секунд при перевищенні ліміту
            time.sleep(60)
            return func(*args, **kwargs)
```

### **3. МОНІТОРИНГ АКТИВНОСТІ**

#### **Система моніторингу:**
```python
class ActivityMonitor:
    def __init__(self, db_session):
        self.db = db_session
        self.daily_applications = 0
        self.daily_messages = 0
        self.daily_searches = 0
    
    def check_application_limit(self, user_id):
        """Перевірка ліміту відгуків"""
        today = datetime.utcnow().date()
        
        # Підрахунок відгуків за сьогодні
        applications_today = self.db.query(Application).filter(
            Application.user_id == user_id,
            Application.created_at >= today
        ).count()
        
        if applications_today >= 5:  # Максимум 5 відгуків на день
            raise Exception("Денний ліміт відгуків перевищено (5)")
        
        return True
    
    def check_message_limit(self, user_id):
        """Перевірка ліміту повідомлень"""
        today = datetime.utcnow().date()
        
        messages_today = self.db.query(Message).filter(
            Message.user_id == user_id,
            Message.created_at >= today
        ).count()
        
        if messages_today >= 50:  # Максимум 50 повідомлень на день
            raise Exception("Денний ліміт повідомлень перевищено (50)")
        
        return True
    
    def log_activity(self, user_id, action, details):
        """Логування активності"""
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            timestamp=datetime.utcnow(),
            ip_address=request.client.host
        )
        
        self.db.add(activity)
        self.db.commit()
        
        logger.info(f"ACTIVITY: {action} - User: {user_id} - {details}")
```

### **4. ВАЛІДАЦІЯ КОНТЕНТУ**

#### **Перевірка AI контенту:**
```python
class ContentValidator:
    def __init__(self):
        self.ai_keywords = [
            "AI-generated", "automated", "bot", "script",
            "generated by", "created by AI", "artificial intelligence"
        ]
    
    def validate_proposal(self, proposal_text):
        """Валідація відгуку"""
        
        # Перевірка на AI контент
        if any(keyword in proposal_text.lower() for keyword in self.ai_keywords):
            raise Exception("AI контент виявлено - потрібно редагування")
        
        # Перевірка довжини
        if len(proposal_text) < 100:
            raise Exception("Відгук занадто короткий (мінімум 100 символів)")
        
        if len(proposal_text) > 5000:
            raise Exception("Відгук занадто довгий (максимум 5000 символів)")
        
        # Перевірка на спам
        if self.detect_spam(proposal_text):
            raise Exception("Спам контент виявлено")
        
        return True
    
    def detect_spam(self, text):
        """Виявлення спаму"""
        spam_indicators = [
            "buy now", "click here", "limited time",
            "make money fast", "work from home",
            "earn $1000", "guaranteed income"
        ]
        
        text_lower = text.lower()
        spam_count = sum(1 for indicator in spam_indicators if indicator in text_lower)
        
        return spam_count > 2  # Більше 2 спам індикаторів
```

---

## 📋 **ПРАВИЛА ВИКОРИСТАННЯ**

### **1. ПОШУК ВАКАНСІЙ - ДОЗВОЛЕНО**
```python
# ✅ ДОЗВОЛЕНО
def search_jobs(self, query, filters=None):
    """Пошук вакансій з обмеженнями"""
    
    # Перевірка лімітів
    self.activity_monitor.check_search_limit(self.user_id)
    
    # Безпечний API виклик
    jobs = self.safe_api_call(
        self.client.search_jobs,
        query=query,
        filters=filters
    )
    
    # Логування активності
    self.activity_monitor.log_activity(
        self.user_id,
        "job_search",
        f"Query: {query}, Results: {len(jobs.get('jobs', []))}"
    )
    
    return jobs
```

### **2. АНАЛІЗ КЛІЄНТІВ - ДОЗВОЛЕНО**
```python
# ✅ ДОЗВОЛЕНО
def analyze_client(self, client_id):
    """Аналіз клієнта"""
    
    client_info = self.safe_api_call(
        self.client.get_client_info,
        client_id=client_id
    )
    
    # Аналіз без автоматичних дій
    analysis = {
        "rating": client_info.get("rating"),
        "total_spent": client_info.get("total_spent"),
        "hire_rate": client_info.get("hire_rate"),
        "recommendation": self.analyze_client_suitability(client_info)
    }
    
    return analysis
```

### **3. ШАБЛОНИ ВІДГУКІВ - ДОЗВОЛЕНО**
```python
# ✅ ДОЗВОЛЕНО
def create_proposal_template(self, job_data, freelancer_profile):
    """Створення шаблону відгуку (НЕ автоматична відправка)"""
    
    template = self.ai_generator.generate_proposal_template(
        job_data, 
        freelancer_profile
    )
    
    # Додавання попередження
    template = self.add_ai_warning(template)
    
    # Збереження як чернетку
    draft = ProposalDraft(
        user_id=self.user_id,
        job_id=job_data["id"],
        content=template,
        created_at=datetime.utcnow()
    )
    
    self.db.add(draft)
    self.db.commit()
    
    return {
        "draft_id": draft.id,
        "content": template,
        "warning": "Це чернетка. Перегляньте та відредагуйте перед відправкою."
    }
```

---

## 🚨 **ЗАБОРОНЕНІ ДІЇ**

### **1. АВТОМАТИЧНІ ВІДГУКИ**
```python
# ❌ ЗАБОРОНЕНО
def auto_apply_to_jobs(self, search_queries, freelancer_profile):
    for query in search_queries:
        jobs = self.search_jobs(query)
        for job in jobs[:5]:
            self.apply_to_job(job, freelancer_profile)  # ЗАБОРОНЕНО!
```

### **2. МАСОВІ ПОВІДОМЛЕННЯ**
```python
# ❌ ЗАБОРОНЕНО
def mass_message_clients(self, message_template, client_ids):
    for client_id in client_ids:
        self.send_message(client_id, message_template)  # ЗАБОРОНЕНО!
```

### **3. СКРАПІНГ ДАНИХ**
```python
# ❌ ЗАБОРОНЕНО
def scrape_job_data(self, job_urls):
    for url in job_urls:
        data = requests.get(url).text  # ЗАБОРОНЕНО!
        # Парсинг HTML замість API
```

---

## 📊 **МОНІТОРИНГ ТА ЗВІТНІСТЬ**

### **1. ЩОДЕННІ ЗВІТИ**
```python
class DailyReport:
    def generate_report(self, user_id, date):
        """Генерація щоденного звіту"""
        
        activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.timestamp >= date
        ).all()
        
        report = {
            "date": date,
            "total_searches": len([a for a in activities if a.action == "job_search"]),
            "total_applications": len([a for a in activities if a.action == "application"]),
            "total_messages": len([a for a in activities if a.action == "message"]),
            "api_requests": len([a for a in activities if a.action == "api_request"]),
            "warnings": self.get_warnings(activities),
            "recommendations": self.get_recommendations(activities)
        }
        
        return report
```

### **2. ПОПЕРЕДЖЕННЯ**
```python
def get_warnings(self, activities):
    """Отримання попереджень"""
    warnings = []
    
    # Перевірка кількості відгуків
    applications = [a for a in activities if a.action == "application"]
    if len(applications) >= 4:  # Близько до ліміту
        warnings.append("Наближаєтесь до денного ліміту відгуків (5)")
    
    # Перевірка швидкості дій
    if self.detect_fast_activity(activities):
        warnings.append("Занадто швидка активність - ризик блокування")
    
    return warnings
```

---

## 🔐 **БЕЗПЕКА ДАНИХ**

### **1. ШИФРУВАННЯ ТОКЕНІВ**
```python
# ✅ ОБОВ'ЯЗКОВО шифрувати токени
def store_access_token(self, user_id, access_token):
    """Безпечне збереження токена"""
    
    encrypted_token = encrypt_data(access_token)
    
    oauth_connection = OAuthConnection(
        user_id=user_id,
        provider="upwork",
        access_token=encrypted_token,  # Шифрований токен
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    
    self.db.add(oauth_connection)
    self.db.commit()
```

### **2. ЛОГУВАННЯ БЕЗПЕКИ**
```python
def log_security_event(self, event_type, details, user_id=None):
    """Логування подій безпеки"""
    
    security_log = SecurityLog(
        event_type=event_type,
        details=details,
        user_id=user_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        timestamp=datetime.utcnow()
    )
    
    self.db.add(security_log)
    self.db.commit()
    
    # Сповіщення адміністратора про критичні події
    if event_type in ["rate_limit_exceeded", "suspicious_activity", "api_error"]:
        self.notify_admin(security_log)
```

---

## 📞 **ПЛАН ДІЙ ПРИ ПРОБЛЕМАХ**

### **1. ПРИ БЛОКУВАННІ АКАУНТУ**
```python
def handle_account_suspension(self):
    """Обробка блокування акаунту"""
    
    # 1. Негайно зупинити всі автоматичні процеси
    self.stop_all_automation()
    
    # 2. Зібрати лог активності
    activity_log = self.get_recent_activity()
    
    # 3. Зв'язатися з підтримкою Upwork
    support_ticket = {
        "subject": "Account Suspension Appeal",
        "description": "Appeal for account suspension",
        "evidence": activity_log,
        "compliance_measures": self.get_compliance_measures()
    }
    
    # 4. Оновити систему безпеки
    self.update_security_measures()
    
    return support_ticket
```

### **2. ПРИ ПОПЕРЕДЖЕННІ**
```python
def handle_warning(self, warning_details):
    """Обробка попередження"""
    
    # 1. Аналіз причини попередження
    cause = self.analyze_warning_cause(warning_details)
    
    # 2. Впровадження виправлень
    if cause == "rate_limit":
        self.increase_delays()
    elif cause == "automation":
        self.disable_automation()
    elif cause == "content":
        self.improve_content_validation()
    
    # 3. Логування події
    self.log_security_event("warning_received", warning_details)
    
    # 4. Повідомлення користувача
    self.notify_user("warning_received", cause)
```

---

## 📋 **КОНТРОЛЬНИЙ СПИСОК БЕЗПЕКИ**

### **Перед запуском:**
- [ ] Реєстрація на developers.upwork.com
- [ ] Отримання схвалення додатку
- [ ] Налаштування реальних API ключів
- [ ] Видалення автоматизації відгуків
- [ ] Додавання попереджень про AI
- [ ] Налаштування rate limiting
- [ ] Реалізація моніторингу активності

### **При розробці:**
- [ ] Тестування з реальним API
- [ ] Валідація відповідності ToS
- [ ] Перевірка rate limiting
- [ ] Тестування обробки помилок
- [ ] Валідація контенту

### **Для продакшену:**
- [ ] Моніторинг активності
- [ ] Логування подій безпеки
- [ ] Регулярні звіти
- [ ] Оновлення заходів безпеки
- [ ] Тренування користувачів

---

## 🚨 **КРИТИЧНІ ПОПЕРЕДЖЕННЯ**

### **1. НЕ ВИКОРИСТОВУВАТИ БЕЗ РЕЄСТРАЦІЇ**
- Будь-яке використання API без реєстрації **ЗАБОРОНЕНО**
- Mock дані **НЕ ПРИЙНЯТНІ** для продакшену
- Тестування без схвалення **НЕБЕЗПЕЧНО**

### **2. ДОТРИМУВАТИСЯ ЛІМІТІВ**
- Максимум **5 відгуків на день**
- Максимум **50 повідомлень на день**
- Затримка **2-5 секунд** між запитами
- Повага до **rate limiting**

### **3. МОНІТОРИТИ АКТИВНІСТЬ**
- Відстежувати всі дії користувачів
- Логувати всі API запити
- Перевіряти відповідність ToS
- Реагувати на попередження

---

**⚠️ ЦІ ІНСТРУКЦІЇ Є КРИТИЧНИМИ ТА ОБОВ'ЯЗКОВИМИ ДО ВИКОНАННЯ!**

**🚨 БУДЬ-ЯКІ ВІДХИЛЕННЯ ВІД ЦИХ ПРАВИЛ НЕДОПУСТИМІ!**

**📋 КОНТРОЛЬ БЕЗПЕКИ НА КОЖНОМУ ЕТАПІ РОЗРОБКИ!** 