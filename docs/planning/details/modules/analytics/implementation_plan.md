# План імплементації модуля аналітики

> **Детальний план розробки модуля аналітики з конкретними завданнями та інструкціями**

---

## Зміст

1. [Огляд плану](#огляд-плану)
2. [Етапи розробки](#етапи-розробки)
3. [Детальні завдання](#детальні-завдання)
4. [Критерії прийняття](#критерії-прийняття)
5. [Інструкції виконання](#інструкції-виконання)
6. [Тестування](#тестування)
7. [Моніторинг](#моніторинг)

---

## Огляд плану

### Мета
Створити повнофункціональний модуль аналітики для збору, обробки та візуалізації даних про роботу з Upwork.

### Тривалість
- **Загальна тривалість**: 6 тижнів
- **Кількість спринтів**: 3 спринти по 2 тижні

### Команда
- **Backend Developer**: 1 особа
- **Frontend Developer**: 1 особа  
- **DevOps Engineer**: 0.5 особи
- **QA Engineer**: 0.5 особи

---

## Етапи розробки

### Етап 1: Базова інфраструктура (Тижні 1-2)
- Створення базової структури модуля
- Налаштування бази даних для аналітики
- Інтеграція з Upwork API для збору даних
- Базові API endpoints

### Етап 2: Основний функціонал (Тижні 3-4)
- Реалізація збору метрик
- Створення системи обробки даних
- Розробка аналізу конкурентів
- Генерація звітів

### Етап 3: Візуалізація та оптимізація (Тижні 5-6)
- Створення дашбордів
- Оптимізація продуктивності
- Тестування та моніторинг
- Документація

---

## Детальні завдання

### ANALYTICS-001: Створити базову структуру модуля аналітики

**Опис**: Створити основну архітектуру модуля аналітики з необхідними компонентами.

**Критерії прийняття**:
- [ ] Створена структура папок для модуля
- [ ] Налаштовані базові класи та інтерфейси
- [ ] Створена конфігурація для аналітики
- [ ] Налаштоване логування для модуля

**Інструкції виконання**:

```python
# Структура папок
analytics/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── collector.py
│   ├── processor.py
│   └── reporter.py
├── models/
│   ├── __init__.py
│   ├── metrics.py
│   └── reports.py
├── services/
│   ├── __init__.py
│   ├── upwork_collector.py
│   └── competitor_analyzer.py
├── api/
│   ├── __init__.py
│   ├── routes.py
│   └── schemas.py
└── utils/
    ├── __init__.py
    ├── security.py
    └── rate_limiter.py
```

```python
# Базовий клас для збору даних
class BaseDataCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = DatabaseConnection()
    
    async def collect_data(self, user_id: str) -> dict:
        """Базовий метод для збору даних"""
        raise NotImplementedError
    
    async def validate_data(self, data: dict) -> bool:
        """Валідація зібраних даних"""
        raise NotImplementedError
```

**Оцінка**: 8 годин

---

### ANALYTICS-002: Налаштування бази даних для аналітики

**Опис**: Створити схему бази даних для зберігання аналітичних даних.

**Критерії прийняття**:
- [ ] Створені таблиці для метрик користувачів
- [ ] Створені таблиці для звітів
- [ ] Налаштовані індекси для швидкого пошуку
- [ ] Створені міграції бази даних

**Інструкції виконання**:

```sql
-- Таблиця для метрик користувачів
CREATE TABLE user_analytics (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    metrics_data TEXT NOT NULL, -- зашифровані дані
    period VARCHAR(20) NOT NULL, -- daily, weekly, monthly
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, period)
);

-- Таблиця для звітів
CREATE TABLE analytics_reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    report_type VARCHAR(100) NOT NULL,
    report_data TEXT NOT NULL, -- зашифровані дані
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Індекси для швидкого пошуку
CREATE INDEX idx_user_analytics_user_id ON user_analytics(user_id);
CREATE INDEX idx_user_analytics_period ON user_analytics(period);
CREATE INDEX idx_analytics_reports_user_id ON analytics_reports(user_id);
CREATE INDEX idx_analytics_reports_status ON analytics_reports(status);
```

**Оцінка**: 6 годин

---

### ANALYTICS-003: Інтеграція з Upwork API для збору даних

**Опис**: Створити сервіс для збору даних з Upwork API.

**Критерії прийняття**:
- [ ] Реалізований збір профілю користувача
- [ ] Реалізований збір пропозицій
- [ ] Реалізований збір контрактів
- [ ] Обробка помилок API

**Інструкції виконання**:

```python
class UpworkDataCollector(BaseDataCollector):
    def __init__(self):
        super().__init__()
        self.upwork_client = UpworkAPIClient()
        self.security = AnalyticsSecurity()
    
    async def collect_user_profile(self, user_id: str) -> dict:
        """Збирає профіль користувача"""
        try:
            profile = await self.upwork_client.get_user_profile(user_id)
            return self.security.anonymize_sensitive_data(profile)
        except Exception as e:
            self.logger.error(f"Error collecting profile for {user_id}: {e}")
            raise AnalyticsError("Failed to collect user profile")
    
    async def collect_user_proposals(self, user_id: str) -> dict:
        """Збирає пропозиції користувача"""
        try:
            proposals = await self.upwork_client.get_user_proposals(user_id)
            return self.security.anonymize_sensitive_data(proposals)
        except Exception as e:
            self.logger.error(f"Error collecting proposals for {user_id}: {e}")
            raise AnalyticsError("Failed to collect user proposals")
    
    async def collect_user_contracts(self, user_id: str) -> dict:
        """Збирає контракти користувача"""
        try:
            contracts = await self.upwork_client.get_user_contracts(user_id)
            return self.security.anonymize_sensitive_data(contracts)
        except Exception as e:
            self.logger.error(f"Error collecting contracts for {user_id}: {e}")
            raise AnalyticsError("Failed to collect user contracts")
```

**Оцінка**: 12 годин

---

### ANALYTICS-004: Реалізація обчислення метрик

**Опис**: Створити систему для обчислення різних метрик користувачів.

**Критерії прийняття**:
- [ ] Обчислення базових метрик (пропозиції, виграші, доходи)
- [ ] Обчислення трендів та зростання
- [ ] Кешування обчислених метрик
- [ ] Валідація результатів

**Інструкції виконання**:

```python
class MetricsCalculator:
    def __init__(self):
        self.cache = RedisCache()
    
    def calculate_basic_metrics(self, profile: dict, proposals: dict, contracts: dict) -> dict:
        """Обчислює базові метрики"""
        total_proposals = len(proposals.get('proposals', []))
        won_proposals = len([p for p in proposals.get('proposals', []) 
                           if p.get('status') == 'hired'])
        
        total_earnings = sum([c.get('total_amount', 0) 
                            for c in contracts.get('contracts', [])])
        
        return {
            'proposals_sent': total_proposals,
            'proposals_won': won_proposals,
            'win_rate': won_proposals / total_proposals if total_proposals > 0 else 0,
            'total_earnings': total_earnings,
            'average_rate': profile.get('hourly_rate', 0),
            'active_contracts': len([c for c in contracts.get('contracts', []) 
                                   if c.get('status') == 'active'])
        }
    
    def calculate_trends(self, historical_metrics: list) -> dict:
        """Обчислює тренди"""
        if len(historical_metrics) < 2:
            return {}
        
        current = historical_metrics[-1]
        previous = historical_metrics[-2]
        
        return {
            'earnings_growth': self._calculate_growth(
                current['total_earnings'], previous['total_earnings']
            ),
            'win_rate_change': current['win_rate'] - previous['win_rate'],
            'proposals_growth': self._calculate_growth(
                current['proposals_sent'], previous['proposals_sent']
            )
        }
    
    def _calculate_growth(self, current: float, previous: float) -> float:
        """Обчислює відсоток зростання"""
        if previous == 0:
            return 0
        return (current - previous) / previous
```

**Оцінка**: 10 годин

---

### ANALYTICS-005: Реалізація аналізу конкурентів

**Опис**: Створити систему для аналізу конкурентів на ринку.

**Критерії прийняття**:
- [ ] Пошук конкурентів за категорією
- [ ] Аналіз цін конкурентів
- [ ] Порівняння з користувачем
- [ ] Генерація рекомендацій

**Інструкції виконання**:

```python
class CompetitorAnalyzer:
    def __init__(self):
        self.upwork_client = UpworkAPIClient()
        self.cache = RedisCache()
    
    async def analyze_competitors(self, category: str, budget_range: str, skills: list) -> dict:
        """Аналізує конкурентів в категорії"""
        cache_key = f"competitors:{category}:{budget_range}:{','.join(skills)}"
        
# Перевіряємо кеш
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
# Збираємо дані конкурентів
        competitors = await self.upwork_client.search_freelancers(
            category=category,
            budget_range=budget_range,
            skills=skills
        )
        
# Аналізуємо дані
        analysis = self._analyze_competitor_data(competitors)
        
# Зберігаємо в кеш на 1 годину
        await self.cache.set(cache_key, analysis, expire=3600)
        
        return analysis
    
    def _analyze_competitor_data(self, competitors: list) -> dict:
        """Аналізує дані конкурентів"""
        if not competitors:
            return {'competitor_count': 0}
        
        rates = [c.get('hourly_rate', 0) for c in competitors if c.get('hourly_rate')]
        
        return {
            'competitor_count': len(competitors),
            'average_rate': sum(rates) / len(rates) if rates else 0,
            'rate_distribution': self._calculate_rate_distribution(rates),
            'top_competitors': self._get_top_competitors(competitors),
            'market_position': self._determine_market_position(rates)
        }
    
    def _calculate_rate_distribution(self, rates: list) -> dict:
        """Обчислює розподіл цін"""
        if not rates:
            return {'low': 0, 'medium': 0, 'high': 0}
        
        avg_rate = sum(rates) / len(rates)
        
        low_count = len([r for r in rates if r < avg_rate * 0.8])
        high_count = len([r for r in rates if r > avg_rate * 1.2])
        medium_count = len(rates) - low_count - high_count
        
        total = len(rates)
        return {
            'low': low_count / total,
            'medium': medium_count / total,
            'high': high_count / total
        }
```

**Оцінка**: 16 годин

---

### ANALYTICS-006: Створення API endpoints

**Опис**: Створити REST API для доступу до аналітичних даних.

**Критерії прийняття**:
- [ ] Endpoint для отримання метрик користувача
- [ ] Endpoint для аналізу конкурентів
- [ ] Endpoint для генерації звітів
- [ ] Валідація вхідних даних

**Інструкції виконання**:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["analytics"])

class MetricsRequest(BaseModel):
    period: str = "monthly"
    include_trends: bool = True

class CompetitorAnalysisRequest(BaseModel):
    category: str
    budget_range: str
    skills: list[str]

@router.get("/metrics/{user_id}")
async def get_user_metrics(
    user_id: str,
    request: MetricsRequest = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Отримує метрики користувача"""
# Перевіряємо права доступу
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        metrics_service = MetricsService()
        metrics = await metrics_service.get_user_metrics(user_id, request.period)
        
        if request.include_trends:
            trends = await metrics_service.get_user_trends(user_id)
            metrics['trends'] = trends
        
        return {
            "success": True,
            "data": metrics,
            "period": request.period
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/competitors/analyze")
async def analyze_competitors(
    request: CompetitorAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Аналізує конкурентів"""
    try:
        analyzer = CompetitorAnalyzer()
        analysis = await analyzer.analyze_competitors(
            request.category,
            request.budget_range,
            request.skills
        )
        
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reports/generate")
async def generate_report(
    report_type: str,
    user_id: str,
    period: str = "monthly",
    current_user: User = Depends(get_current_user)
):
    """Генерує звіт"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        report_service = ReportService()
        report_id = await report_service.generate_report(
            user_id, report_type, period
        )
        
        return {
            "success": True,
            "report_id": report_id,
            "status": "generating"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Оцінка**: 14 годин

---

### ANALYTICS-007: Реалізація системи безпеки

**Опис**: Створити систему безпеки для аналітичних даних.

**Критерії прийняття**:
- [ ] Шифрування аналітичних даних
- [ ] Анонімізація чутливих даних
- [ ] Валідація прав доступу
- [ ] Rate limiting

**Інструкції виконання**:

```python
class AnalyticsSecurity:
    def __init__(self):
        self.encryption_key = os.getenv('ANALYTICS_ENCRYPTION_KEY')
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_data(self, data: dict) -> str:
        """Шифрує дані"""
        json_data = json.dumps(data)
        encrypted = self.cipher.encrypt(json_data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> dict:
        """Розшифровує дані"""
        encrypted = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
    
    def anonymize_data(self, data: dict) -> dict:
        """Анонімізує чутливі дані"""
        anonymized = data.copy()
        
# Анонімізуємо імена клієнтів
        if 'client_name' in anonymized:
            anonymized['client_name'] = f"Client_{hash(anonymized['client_name'])}"
        
# Видаляємо контактну інформацію
        if 'project_description' in anonymized:
            anonymized['project_description'] = self._remove_contact_info(
                anonymized['project_description']
            )
        
        return anonymized
    
    def _remove_contact_info(self, text: str) -> str:
        """Видаляє контактну інформацію з тексту"""
# Видаляємо email адреси
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
# Видаляємо телефонні номери
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        return text
```

**Оцінка**: 8 годин

---

### ANALYTICS-008: Створення дашбордів

**Опис**: Створити інтерактивні дашборди для відображення аналітики.

**Критерії прийняття**:
- [ ] Дашборд з основними метриками
- [ ] Графіки трендів
- [ ] Аналіз конкурентів
- [ ] Адаптивний дизайн

**Інструкції виконання**:

```typescript
// React компонент для дашборду
interface DashboardProps {
  userId: string;
}

const AnalyticsDashboard: React.FC<DashboardProps> = ({ userId }) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchMetrics();
  }, [userId]);
  
  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/analytics/metrics/${userId}`);
      const data = await response.json();
      setMetrics(data.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return (
    <div className="analytics-dashboard">
      <h1>Аналітика продуктивності</h1>
      
      <div className="metrics-grid">
        <MetricCard
          title="Загальний дохід"
          value={`$${metrics?.total_earnings?.toLocaleString()}`}
          trend={metrics?.trends?.earnings_growth}
        />
        
        <MetricCard
          title="Відсоток успішності"
          value={`${(metrics?.win_rate * 100).toFixed(1)}%`}
          trend={metrics?.trends?.win_rate_change}
        />
        
        <MetricCard
          title="Активні контракти"
          value={metrics?.active_contracts}
        />
      </div>
      
      <div className="charts-section">
        <EarningsChart data={metrics?.earnings_timeline} />
        <ProposalsChart data={metrics?.proposals_timeline} />
      </div>
    </div>
  );
};

// Компонент для відображення метрики
interface MetricCardProps {
  title: string;
  value: string | number;
  trend?: number;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, trend }) => {
  return (
    <div className="metric-card">
      <h3>{title}</h3>
      <div className="metric-value">{value}</div>
      {trend !== undefined && (
        <div className={`metric-trend ${trend >= 0 ? 'positive' : 'negative'}`}>
          {trend >= 0 ? '↗' : '↘'} {Math.abs(trend * 100).toFixed(1)}%
        </div>
      )}
    </div>
  );
};
```

**Оцінка**: 20 годин

---

## Критерії прийняття

### Загальні критерії
- [ ] Всі unit тести проходять
- [ ] Всі integration тести проходять
- [ ] Код відповідає стандартам якості
- [ ] Документація оновлена
- [ ] Безпека перевірена

### Критерії продуктивності
- [ ] Час відповіді API < 500ms
- [ ] Кешування працює ефективно
- [ ] База даних оптимізована
- [ ] Rate limiting налаштований

### Критерії безпеки
- [ ] Всі дані зашифровані
- [ ] Чутливі дані анонімізовані
- [ ] Права доступу валідуються
- [ ] Логування налаштоване

---

## 🧪 Тестування

### Unit тести
```python
class TestAnalyticsModule:
    def test_metrics_calculation(self):
        """Тест обчислення метрик"""
        calculator = MetricsCalculator()
        
        profile = {'hourly_rate': 50}
        proposals = {'proposals': [
            {'status': 'hired'},
            {'status': 'rejected'},
            {'status': 'hired'}
        ]}
        contracts = {'contracts': [
            {'total_amount': 1000, 'status': 'active'},
            {'total_amount': 500, 'status': 'completed'}
        ]}
        
        metrics = calculator.calculate_basic_metrics(profile, proposals, contracts)
        
        assert metrics['proposals_sent'] == 3
        assert metrics['proposals_won'] == 2
        assert metrics['win_rate'] == 2/3
        assert metrics['total_earnings'] == 1500
        assert metrics['active_contracts'] == 1
    
    def test_data_anonymization(self):
        """Тест анонімізації даних"""
        security = AnalyticsSecurity()
        
        data = {
            'client_name': 'John Smith',
            'project_description': 'Contact me at john@email.com',
            'earnings': 1000
        }
        
        anonymized = security.anonymize_data(data)
        
        assert 'John Smith' not in str(anonymized)
        assert 'john@email.com' not in str(anonymized)
        assert anonymized['earnings'] == 1000
```

### Integration тести
```python
class TestAnalyticsIntegration:
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self):
        """Тест API endpoint для метрик"""
        client = TestClient(app)
        
        response = client.get("/analytics/metrics/test_user")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'data' in data
    
    @pytest.mark.asyncio
    async def test_competitor_analysis(self):
        """Тест аналізу конкурентів"""
        client = TestClient(app)
        
        response = client.post("/analytics/competitors/analyze", json={
            "category": "web_development",
            "budget_range": "1000-5000",
            "skills": ["React", "Node.js"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'data' in data
```

---

## Моніторинг

### Метрики для відстеження
- Кількість запитів до аналітики
- Час відповіді API
- Кількість згенерованих звітів
- Помилки збору даних
- Використання кешу

### Алерти
- Високий час відповіді (> 1 секунда)
- Високий рівень помилок (> 5%)
- Проблеми з Upwork API
- Перевищення rate limits

---

## Розклад

### Спринт 1 (Тижні 1-2)
- ANALYTICS-001: Базова структура (8 годин)
- ANALYTICS-002: База даних (6 годин)
- ANALYTICS-003: Upwork API інтеграція (12 годин)
- **Всього**: 26 годин

### Спринт 2 (Тижні 3-4)
- ANALYTICS-004: Обчислення метрик (10 годин)
- ANALYTICS-005: Аналіз конкурентів (16 годин)
- ANALYTICS-006: API endpoints (14 годин)
- **Всього**: 40 годин

### Спринт 3 (Тижні 5-6)
- ANALYTICS-007: Безпека (8 годин)
- ANALYTICS-008: Дашборди (20 годин)
- Тестування та оптимізація (12 годин)
- **Всього**: 40 годин

**Загальна тривалість**: 106 годин (≈ 13.25 робочих днів)

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 16:00  
**Статус**: В розробці 