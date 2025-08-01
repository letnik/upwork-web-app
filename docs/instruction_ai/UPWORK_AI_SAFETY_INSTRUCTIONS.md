# 🤖 ІНСТРУКЦІЇ ДЛЯ AI: БЕЗПЕЧНА РОБОТА З UPWORK

**⚠️ КРИТИЧНІ ПРАВИЛА ДЛЯ AI**  
**🚨 ОБОВ'ЯЗКОВО ДО ВИКОНАННЯ**  
**📋 КОНТРОЛЬ НА КОЖНОМУ ЕТАПІ**

---

## 🎯 **МЕТА**

**Забезпечити безпечну роботу AI з Upwork API, уникнути порушень ToS та блокування акаунту.**

---

## 🚨 **КРИТИЧНІ ЗАБОРОНИ ДЛЯ AI**

### **1. АВТОМАТИЧНІ ВІДГУКИ - ЗАБОРОНЕНО**
```python
# ❌ ЗАБОРОНЕНО - AI не може автоматично відправляти відгуки
def auto_apply_to_jobs(self, search_queries, freelancer_profile):
    # AI НЕ МОЖЕ виконувати цю функцію
    pass

# ✅ ДОЗВОЛЕНО - AI може тільки створювати чернетки
def create_proposal_draft(self, job_data, freelancer_profile):
    """AI створює тільки чернетку відгуку"""
    draft = self.ai_generator.generate_proposal_template(job_data, freelancer_profile)
    return {
        "draft": draft,
        "warning": "Це чернетка. Перегляньте та відредагуйте перед відправкою."
    }
```

### **2. МАСОВІ ОПЕРАЦІЇ - ЗАБОРОНЕНО**
```python
# ❌ ЗАБОРОНЕНО - AI не може виконувати масові операції
def mass_apply_to_jobs(self, job_list):
    # AI НЕ МОЖЕ виконувати цю функцію
    pass

# ✅ ДОЗВОЛЕНО - AI може тільки аналізувати та рекомендувати
def analyze_jobs_for_recommendations(self, job_list):
    """AI аналізує вакансії та дає рекомендації"""
    recommendations = []
    for job in job_list[:5]:  # Максимум 5 рекомендацій
        analysis = self.analyze_job_suitability(job)
        if analysis['recommendation'] == 'Yes':
            recommendations.append({
                'job': job,
                'analysis': analysis,
                'note': 'Рекомендується для ручного розгляду'
            })
    return recommendations
```

### **3. AI ГЕНЕРАЦІЯ БЕЗ ПОПЕРЕДЖЕННЯ - ЗАБОРОНЕНО**
```python
# ❌ ЗАБОРОНЕНО - AI не може генерувати контент без попередження
def generate_proposal(self, job_data, freelancer_profile):
    return ai_generated_content  # Без попередження

# ✅ ДОЗВОЛЕНО - AI з попередженням
def generate_proposal_with_warning(self, job_data, freelancer_profile):
    """AI генерує контент з попередженням"""
    content = self.ai_generator.generate_proposal_template(job_data, freelancer_profile)
    
    warning = """
    ⚠️ УВАГА: Цей контент згенерований за допомогою AI!
    
    ОБОВ'ЯЗКОВО:
    1. Перегляньте весь текст
    2. Відредагуйте під конкретну вакансію
    3. Додайте особистий досвід
    4. Перевірте на помилки
    5. Тільки після цього відправляйте
    
    AI - це тільки допомога, не заміна людської творчості!
    """
    
    return {
        "content": content,
        "warning": warning,
        "requires_review": True,
        "ai_generated": True
    }
```

---

## 🔧 **ДОЗВОЛЕНІ ФУНКЦІЇ AI**

### **1. АНАЛІЗ ТА РЕКОМЕНДАЦІЇ**
```python
# ✅ ДОЗВОЛЕНО - AI може аналізувати
def analyze_job_suitability(self, job_data, freelancer_profile):
    """AI аналізує підходящість вакансії"""
    
    analysis = {
        "skill_match": self.calculate_skill_match(job_data, freelancer_profile),
        "budget_match": self.calculate_budget_match(job_data, freelancer_profile),
        "client_rating": job_data.get("client", {}).get("rating", 0),
        "project_complexity": self.assess_complexity(job_data),
        "recommendation": "Yes" if self.is_suitable(job_data, freelancer_profile) else "No",
        "reasoning": self.generate_reasoning(job_data, freelancer_profile),
        "risk_factors": self.identify_risks(job_data),
        "ai_confidence": self.calculate_confidence(job_data, freelancer_profile)
    }
    
    return analysis

def calculate_skill_match(self, job_data, freelancer_profile):
    """Розрахунок відповідності навичок"""
    job_skills = set(job_data.get("skills", []))
    freelancer_skills = set([skill["skill"] for skill in freelancer_profile.get("skills", [])])
    
    if not job_skills:
        return 0
    
    match_percentage = len(job_skills.intersection(freelancer_skills)) / len(job_skills) * 100
    return min(match_percentage, 100)  # Максимум 100%
```

### **2. ШАБЛОНИ ТА ЧЕРНЕТКИ**
```python
# ✅ ДОЗВОЛЕНО - AI може створювати шаблони
def create_proposal_template(self, job_data, freelancer_profile):
    """Створення шаблону відгуку"""
    
    template = {
        "greeting": self.generate_greeting(job_data),
        "introduction": self.generate_introduction(freelancer_profile),
        "understanding": self.generate_understanding(job_data),
        "proposal": self.generate_proposal_section(job_data, freelancer_profile),
        "experience": self.generate_experience_section(freelancer_profile),
        "closing": self.generate_closing(job_data),
        "ai_notes": self.generate_ai_notes(job_data, freelancer_profile)
    }
    
    return {
        "template": template,
        "ai_generated": True,
        "requires_review": True,
        "warning": "Це шаблон. Адаптуйте під конкретну вакансію!"
    }

def generate_ai_notes(self, job_data, freelancer_profile):
    """AI нотатки для користувача"""
    notes = []
    
    # Аналіз бюджету
    budget = job_data.get("budget", {})
    if budget.get("type") == "fixed":
        if budget.get("max", 0) < 1000:
            notes.append("⚠️ Низький бюджет - перевірте вимоги")
    
    # Аналіз клієнта
    client = job_data.get("client", {})
    if client.get("rating", 0) < 4.0:
        notes.append("⚠️ Низький рейтинг клієнта - будьте обережні")
    
    # Аналіз навичок
    skill_match = self.calculate_skill_match(job_data, freelancer_profile)
    if skill_match < 70:
        notes.append("⚠️ Часткова відповідність навичок - підкресліть адаптивність")
    
    return notes
```

### **3. АНАЛІЗ РИНКУ**
```python
# ✅ ДОЗВОЛЕНО - AI може аналізувати ринок
def analyze_market_trends(self, job_data_list):
    """Аналіз ринкових трендів"""
    
    analysis = {
        "popular_skills": self.identify_popular_skills(job_data_list),
        "average_budgets": self.calculate_average_budgets(job_data_list),
        "demand_trends": self.analyze_demand_trends(job_data_list),
        "geographic_distribution": self.analyze_geographic_distribution(job_data_list),
        "recommendations": self.generate_market_recommendations(job_data_list)
    }
    
    return analysis

def identify_popular_skills(self, job_data_list):
    """Визначення популярних навичок"""
    skill_frequency = {}
    
    for job in job_data_list:
        skills = job.get("skills", [])
        for skill in skills:
            skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
    
    # Сортування за частотою
    popular_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)
    
    return popular_skills[:10]  # Топ 10 навичок
```

---

## 📋 **ПРАВИЛА ГЕНЕРАЦІЇ КОНТЕНТУ**

### **1. ОБОВ'ЯЗКОВІ ПОПЕРЕДЖЕННЯ**
```python
def add_ai_warning(self, content, content_type="proposal"):
    """Додавання попередження про AI"""
    
    warnings = {
        "proposal": """
        ⚠️ AI-ГЕНЕРАЦІЯ ВІДГУКУ
        
        Цей відгук створений за допомогою штучного інтелекту.
        
        ОБОВ'ЯЗКОВО ПЕРЕД ВІДПРАВКОЮ:
        ✅ Перегляньте та відредагуйте текст
        ✅ Додайте особистий досвід та приклади
        ✅ Адаптуйте під конкретну вакансію
        ✅ Перевірте граматику та стиль
        ✅ Переконайтеся в унікальності контенту
        
        AI - це тільки допомога, не заміна вашої творчості!
        """,
        
        "message": """
        ⚠️ AI-ГЕНЕРАЦІЯ ПОВІДОМЛЕННЯ
        
        Це повідомлення створене за допомогою AI.
        
        ПЕРЕД ВІДПРАВКОЮ:
        ✅ Перегляньте та відредагуйте
        ✅ Додайте особистий підхід
        ✅ Перевірте відповідність контексту
        """,
        
        "analysis": """
        ℹ️ AI-АНАЛІЗ
        
        Цей аналіз виконаний за допомогою AI.
        Використовуйте для інформації, але приймайте рішення самостійно.
        """
    }
    
    return content + warnings.get(content_type, warnings["analysis"])
```

### **2. ВАЛІДАЦІЯ КОНТЕНТУ**
```python
def validate_ai_content(self, content, content_type="proposal"):
    """Валідація AI контенту"""
    
    validation_rules = {
        "proposal": {
            "min_length": 200,
            "max_length": 2000,
            "forbidden_phrases": [
                "AI-generated", "automated", "bot", "script",
                "generated by", "created by AI", "artificial intelligence"
            ],
            "required_sections": ["greeting", "introduction", "proposal", "closing"]
        },
        
        "message": {
            "min_length": 50,
            "max_length": 500,
            "forbidden_phrases": [
                "AI-generated", "automated", "bot"
            ]
        }
    }
    
    rules = validation_rules.get(content_type, {})
    
    # Перевірка довжини
    if len(content) < rules.get("min_length", 0):
        raise ValueError(f"Контент занадто короткий (мінімум {rules['min_length']} символів)")
    
    if len(content) > rules.get("max_length", 9999):
        raise ValueError(f"Контент занадто довгий (максимум {rules['max_length']} символів)")
    
    # Перевірка заборонених фраз
    content_lower = content.lower()
    forbidden_phrases = rules.get("forbidden_phrases", [])
    found_forbidden = [phrase for phrase in forbidden_phrases if phrase in content_lower]
    
    if found_forbidden:
        raise ValueError(f"Знайдено заборонені фрази: {found_forbidden}")
    
    return True
```

### **3. ПЕРСОНАЛІЗАЦІЯ**
```python
def personalize_content(self, content, freelancer_profile, job_data):
    """Персоналізація контенту"""
    
    # Заміна плейсхолдерів
    personalization_data = {
        "{freelancer_name}": freelancer_profile.get("name", "Фрілансер"),
        "{freelancer_title}": freelancer_profile.get("title", "Розробник"),
        "{years_experience}": str(freelancer_profile.get("experience_years", 3)),
        "{client_name}": job_data.get("client", {}).get("name", "Клієнт"),
        "{job_title}": job_data.get("title", "Вакансія"),
        "{project_budget}": str(job_data.get("budget", {}).get("max", 0))
    }
    
    personalized_content = content
    for placeholder, value in personalization_data.items():
        personalized_content = personalized_content.replace(placeholder, value)
    
    return personalized_content
```

---

## 🚨 **ОБМЕЖЕННЯ ДЛЯ AI**

### **1. НЕ МОЖЕ ВИКОНУВАТИ**
- ❌ Автоматичне відправлення відгуків
- ❌ Масові операції
- ❌ Генерація контенту без попередження
- ❌ Прийняття рішень за користувача
- ❌ Прямий доступ до API без контролю

### **2. МОЖЕ ВИКОНУВАТИ**
- ✅ Аналіз та рекомендації
- ✅ Створення шаблонів
- ✅ Валідація контенту
- ✅ Персоналізація
- ✅ Аналіз ринку

---

## 📊 **МОНІТОРИНГ AI АКТИВНОСТІ**

### **1. ЛОГУВАННЯ AI ДІЙ**
```python
def log_ai_activity(self, action, details, user_id):
    """Логування AI активності"""
    
    ai_log = AILog(
        user_id=user_id,
        action=action,
        details=details,
        ai_model="gpt-4",
        timestamp=datetime.utcnow(),
        content_length=len(str(details)),
        requires_review=True
    )
    
    self.db.add(ai_log)
    self.db.commit()
    
    logger.info(f"AI ACTIVITY: {action} - User: {user_id} - {details}")
```

### **2. СТАТИСТИКА AI ВИКОРИСТАННЯ**
```python
def get_ai_statistics(self, user_id, date_range=None):
    """Статистика використання AI"""
    
    query = self.db.query(AILog).filter(AILog.user_id == user_id)
    
    if date_range:
        query = query.filter(AILog.timestamp >= date_range[0])
        query = query.filter(AILog.timestamp <= date_range[1])
    
    ai_logs = query.all()
    
    statistics = {
        "total_ai_actions": len(ai_logs),
        "proposals_generated": len([log for log in ai_logs if log.action == "proposal_generation"]),
        "analyses_performed": len([log for log in ai_logs if log.action == "job_analysis"]),
        "templates_created": len([log for log in ai_logs if log.action == "template_creation"]),
        "average_content_length": sum(log.content_length for log in ai_logs) / len(ai_logs) if ai_logs else 0,
        "review_required_count": len([log for log in ai_logs if log.requires_review])
    }
    
    return statistics
```

---

## 📋 **КОНТРОЛЬНИЙ СПИСОК ДЛЯ AI**

### **Перед генерацією контенту:**
- [ ] Перевірити дозволеність операції
- [ ] Валідувати вхідні дані
- [ ] Перевірити ліміти користувача
- [ ] Підготувати попередження про AI

### **При генерації контенту:**
- [ ] Додати попередження про AI
- [ ] Валідувати довжину контенту
- [ ] Перевірити на заборонені фрази
- [ ] Персоналізувати контент
- [ ] Позначити як потребує перегляду

### **Після генерації:**
- [ ] Залогувати AI активність
- [ ] Зберегти в базу даних
- [ ] Повідомити користувача про необхідність перегляду
- [ ] Оновити статистику

---

## 🚨 **КРИТИЧНІ ПОПЕРЕДЖЕННЯ ДЛЯ AI**

### **1. НЕ ЗАМІНЯТИ ЛЮДСЬКУ ТВОРЧІСТЬ**
- AI - це тільки допомога
- Користувач ПОВИНЕН переглядати весь контент
- AI не може приймати рішення за людину

### **2. ДОТРИМУВАТИСЯ ЛІМІТІВ**
- Не генерувати занадто багато контенту
- Поважати rate limiting
- Не перевантажувати API

### **3. БУТИ ПРОЗОРИМ**
- Завжди позначати AI контент
- Додавати попередження
- Логувати всі дії

---

**⚠️ ЦІ ІНСТРУКЦІЇ Є КРИТИЧНИМИ ДЛЯ AI!**

**🚨 AI НЕ МОЖЕ ПОРУШУВАТИ ЦІ ПРАВИЛА!**

**📋 КОНТРОЛЬ AI НА КОЖНОМУ ЕТАПІ!** 