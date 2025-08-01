# ⚡ Performance Tests

> **Тестування продуктивності та навантаження системи**

---

## 📋 **Огляд**

Performance тести перевіряють:
- Швидкість відповіді API
- Обробку навантаження
- Використання пам'яті
- Масштабованість системи
- Database продуктивність

---

## 🏗️ **Архітектура**

```
tests/performance/
├── load_tests/                    # Навантажувальні тести
│   ├── test_api_load.py          # API навантаження
│   ├── test_database_load.py     # Database навантаження
│   ├── test_concurrent_users.py  # Конкурентні користувачі
│   └── test_stress_scenarios.py  # Стрес-сценарії
├── stress_tests/                  # Стрес-тести
│   ├── test_memory_stress.py     # Стрес пам'яті
│   ├── test_cpu_stress.py        # Стрес CPU
│   ├── test_network_stress.py    # Стрес мережі
│   └── test_disk_stress.py       # Стрес диску
├── memory_tests/                  # Тести пам'яті
│   ├── test_memory_leaks.py      # Витоки пам'яті
│   ├── test_memory_usage.py      # Використання пам'яті
│   └── test_garbage_collection.py # Garbage collection
├── database_performance/          # Database продуктивність
│   ├── test_query_performance.py # Продуктивність запитів
│   ├── test_connection_pool.py   # Connection pool
│   └── test_index_performance.py # Продуктивність індексів
└── api_performance/               # API продуктивність
    ├── test_response_times.py     # Час відповіді
    ├── test_throughput.py         # Пропускна здатність
    └── test_latency.py           # Затримки
```

---

## 🚀 **Запуск тестів**

```bash
# Всі performance тести
./tools/scripts/testing/run_tests.sh performance

# Конкретні performance тести
pytest tests/performance/load_tests/ -v
pytest tests/performance/stress_tests/ -v
pytest tests/performance/memory_tests/ -v

# З різними параметрами
pytest tests/performance/ --users=100 --duration=300
pytest tests/performance/ --ramp-up=60 --hold-time=300
```

---

## 📊 **Метрики**

### **Ключові показники:**
- **Response Time**: < 200ms (95th percentile)
- **Throughput**: > 1000 RPS
- **Error Rate**: < 1%
- **Memory Usage**: < 2GB
- **CPU Usage**: < 80%
- **Database Connections**: < 100

### **Цільові показники:**
- **Load Tests**: 1000+ одночасних користувачів
- **Stress Tests**: 200% від нормального навантаження
- **Memory Tests**: Без витоків пам'яті
- **Database Tests**: < 100ms середній час запиту

---

## 🔧 **Налаштування**

### **Locust конфігурація:**
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class UpworkUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def test_job_search(self):
        self.client.get("/api/jobs/search?q=react")
    
    @task(2)
    def test_proposal_creation(self):
        self.client.post("/api/proposals", json={
            "job_id": "test_job",
            "cover_letter": "Test proposal"
        })
    
    @task(1)
    def test_analytics_dashboard(self):
        self.client.get("/api/analytics/dashboard")
```

### **JMeter конфігурація:**
```xml
<!-- tests/performance/jmeter/upwork_test_plan.jmx -->
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Upwork Performance Test">
      <elementProp name="TestPlan.arguments" elementType="Arguments">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <stringProp name="TestPlan.comments"></stringProp>
    </TestPlan>
  </hashTree>
</jmeterTestPlan>
```

---

## 📋 **Чекліст**

### **Перед створенням performance тесту:**
- [ ] Визначити метрики продуктивності
- [ ] Налаштувати monitoring
- [ ] Створити тестові дані
- [ ] Визначити baseline
- [ ] Планувати cleanup

### **Під час написання тесту:**
- [ ] Використовувати реальні сценарії
- [ ] Моніторити ресурси
- [ ] Збирати метрики
- [ ] Обробляти помилки
- [ ] Документувати результати

### **Після написання тесту:**
- [ ] Аналізувати результати
- [ ] Створити звіт
- [ ] Порівняти з baseline
- [ ] Документувати висновки
- [ ] Додати до CI/CD pipeline

---

## 🎯 **Приклади тестів**

### **API Load Test:**
```python
def test_api_load_performance():
    """Тест продуктивності API під навантаженням"""
    import requests
    import time
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/jobs/search",
        "/api/analytics/dashboard",
        "/api/proposals/list"
    ]
    
    results = []
    
    # Тестуємо кожен endpoint
    for endpoint in endpoints:
        start_time = time.time()
        response = requests.get(f"{base_url}{endpoint}")
        end_time = time.time()
        
        results.append({
            "endpoint": endpoint,
            "response_time": (end_time - start_time) * 1000,
            "status_code": response.status_code
        })
    
    # Перевіряємо результати
    for result in results:
        assert result["response_time"] < 200  # < 200ms
        assert result["status_code"] == 200
```

### **Database Performance Test:**
```python
def test_database_query_performance():
    """Тест продуктивності database запитів"""
    import time
    from app.backend.shared.database.connection import get_db
    
    db = get_db()
    
    # Тестуємо складний запит
    start_time = time.time()
    
    result = db.execute("""
        SELECT u.email, COUNT(p.id) as proposal_count
        FROM users u
        LEFT JOIN proposals p ON u.id = p.user_id
        WHERE u.created_at >= NOW() - INTERVAL '30 days'
        GROUP BY u.id, u.email
        ORDER BY proposal_count DESC
        LIMIT 100
    """)
    
    end_time = time.time()
    query_time = (end_time - start_time) * 1000
    
    # Перевіряємо результат
    assert query_time < 100  # < 100ms
    assert len(result.fetchall()) <= 100
```

---

## 🚨 **Важливі правила**

### **✅ Дозволено:**
- Тестування в staging середовищі
- Моніторинг системних ресурсів
- Збір метрик продуктивності
- Стрес-тестування
- Аналіз bottleneck'ів

### **❌ Заборонено:**
- Тестування в production середовищі
- Зміна production даних
- Надмірне навантаження на інфраструктуру
- Ігнорування результатів тестів
- Відсутність monitoring

---

## 📈 **Моніторинг**

### **Системні метрики:**
- CPU використання
- Memory використання
- Disk I/O
- Network I/O
- Database connections

### **Application метрики:**
- Response time
- Throughput
- Error rate
- Active connections
- Queue length

---

**Статус**: 🚧 В розробці  
**Пріоритет**: Середній  
**Останнє оновлення**: 2024-12-19 