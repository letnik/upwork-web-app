# Модуль веб-інтерфейсу

> **Модуль для створення сучасного та зручного веб-інтерфейсу**

---

## Зміст

1. [Огляд модуля](#огляд-модуля)
2. [Архітектура модуля](#-архітектура-модуля)
3. [API Endpoints](#-api-endpoints)
4. [Аспекти безпеки](#аспекти-безпеки)
5. [Інтеграція](#інтеграція)
6. [Тестування](#тестування)
7. [Моніторинг](#моніторинг)

---

## Огляд модуля

### Призначення
- Створення інтерактивного веб-інтерфейсу
- Відображення дашбордів та аналітики
- Керування пропозиціями та контрактами
- Інтеграція з усіма модулями системи
- Забезпечення відповідності та зручності

### Основні функції
- Реактивний інтерфейс на React.js
- Реальний час оновлення даних
- Адаптивний дизайн
- Інтерактивні графіки та діаграми
- Система сповіщень

---

## Архітектура модуля

### Компоненти

```
┌─────────────────────────────────────────────────────────────┐
│                  Web Interface Module                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ React App   │  │ State Mgmt  │  │ Router      │        │
│  │             │  │ (Zustand)   │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Components  │  │ API Client  │  │ Real-time   │        │
│  │ (Material-UI)│  │ (React Query)│  │ (WebSocket) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Charts      │  │ Notifications│  │ Responsive  │        │
│  │ & Graphs    │  │ System      │  │ Design      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

**State Management:**
- **Zustand** для локального стану
- **React Query** для серверного стану та кешування
- **Material-UI** для компонентів інтерфейсу

### Взаємодія з іншими модулями

- **Auth Module**: Авторизація та аутентифікація
- **Analytics Module**: Відображення дашбордів
- **AI Module**: Інтеграція AI функцій
- **Upwork Integration**: Відображення даних з Upwork

---

## API Endpoints

### Керування користувачами

```python
# Отримання профілю користувача
GET /api/user/profile
Headers: Authorization: Bearer <token>
Response: {
    "user_id": "user_123",
    "email": "user@example.com",
    "upwork_profile": {
        "profile_id": "~0123456789",
        "hourly_rate": 85,
        "total_earnings": 15000,
        "success_rate": 0.85
    },
    "preferences": {
        "notifications": true,
        "theme": "dark",
        "language": "uk"
    }
}

# Оновлення профілю
PUT /api/user/profile
Headers: Authorization: Bearer <token>
Body: {
    "preferences": {
        "notifications": false,
        "theme": "light"
    }
}
Response: {
    "status": "success",
    "message": "Profile updated successfully"
}
```

### Дашборди та аналітика

```python
# Отримання головного дашборду
GET /api/dashboard/main
Headers: Authorization: Bearer <token>
Response: {
    "widgets": [
        {
            "id": "earnings_chart",
            "type": "line_chart",
            "title": "Доходи за місяць",
            "data": {
                "labels": ["Січ", "Лют", "Бер"],
                "datasets": [{
                    "label": "Доходи",
                    "data": [5000, 6500, 7200],
                    "borderColor": "#4CAF50"
                }]
            }
        },
        {
            "id": "proposals_status",
            "type": "pie_chart",
            "title": "Статус пропозицій",
            "data": {
                "labels": ["Очікування", "Інтерв'ю", "Прийнято", "Відхилено"],
                "datasets": [{
                    "data": [15, 8, 12, 25],
                    "backgroundColor": ["#FFC107", "#2196F3", "#4CAF50", "#F44336"]
                }]
            }
        }
    ],
    "summary": {
        "total_earnings": 18700,
        "active_contracts": 3,
        "win_rate": 0.27,
        "proposals_sent": 60
    }
}

# Отримання детальної аналітики
GET /api/analytics/detailed
Headers: Authorization: Bearer <token>
Query params: period, category, date_from, date_to
Response: {
    "period": "monthly",
    "metrics": {
        "earnings_by_category": {
            "web_development": 8500,
            "mobile_development": 6200,
            "design": 4000
        },
        "proposals_by_status": {
            "pending": 15,
            "interviewing": 8,
            "hired": 12,
            "rejected": 25
        },
        "top_skills": [
            {"skill": "React", "demand": 0.85},
            {"skill": "Node.js", "demand": 0.78},
            {"skill": "Python", "demand": 0.72}
        ]
    },
    "trends": {
        "earnings_growth": 0.15,
        "win_rate_change": 0.05,
        "proposals_growth": 0.20
    }
}
```

### Керування пропозиціями

```python
# Отримання списку пропозицій
GET /api/proposals
Headers: Authorization: Bearer <token>
Query params: status, category, page, limit
Response: {
    "proposals": [
        {
            "id": "proposal_123",
            "title": "E-commerce Website Development",
            "client": "Client Name",
            "budget": 5000,
            "status": "interviewing",
            "submitted_at": "2024-12-15T10:30:00Z",
            "category": "web_development",
            "ai_score": 0.85,
            "ai_suggestions": [
                "Додайте більше деталей про технології",
                "Включіть приклади робіт"
            ]
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 60,
        "pages": 3
    }
}

# Створення нової пропозиції
POST /api/proposals
Headers: Authorization: Bearer <token>
Body: {
    "title": "Mobile App Development",
    "description": "Professional mobile app development...",
    "budget": 3000,
    "timeline": "2 months",
    "skills": ["React Native", "Node.js", "MongoDB"],
    "use_ai_assistance": true
}
Response: {
    "proposal_id": "proposal_456",
    "ai_generated_content": {
        "proposal_text": "Професійний розробник з 5+ роками досвіду...",
        "cover_letter": "Дякую за можливість...",
        "score": 0.92
    },
    "status": "draft"
}
```

### Сповіщення

```python
# Отримання сповіщень
GET /api/notifications
Headers: Authorization: Bearer <token>
Query params: unread_only, limit
Response: {
    "notifications": [
        {
            "id": "notif_123",
            "type": "proposal_status",
            "title": "Пропозиція прийнята",
            "message": "Ваша пропозиція 'E-commerce Website' була прийнята",
            "data": {
                "proposal_id": "proposal_123",
                "client_name": "Client Name"
            },
            "read": false,
            "created_at": "2024-12-19T15:30:00Z"
        }
    ],
    "unread_count": 5
}

# Позначення сповіщення як прочитане
PUT /api/notifications/{notification_id}/read
Headers: Authorization: Bearer <token>
Response: {
    "status": "success",
    "message": "Notification marked as read"
}
```

---

## Аспекти безпеки

### Безпека веб-інтерфейсу

```python
class WebInterfaceSecurity:
    def __init__(self):
        self.csrf_protection = CSRFProtection()
        self.xss_protection = XSSProtection()
        self.content_security_policy = ContentSecurityPolicy()
        
    def validate_user_input(self, data: dict) -> bool:
        """Валідація вхідних даних користувача"""
# Перевірка на XSS
        for key, value in data.items():
            if isinstance(value, str) and self.xss_protection.contains_xss(value):
                return False
                
# Перевірка на SQL injection
        if self.contains_sql_injection(str(data)):
            return False
            
        return True
    
    def sanitize_output(self, data: dict) -> dict:
        """Очищення вихідних даних"""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.xss_protection.sanitize(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_output(value)
            else:
                sanitized[key] = value
        return sanitized
    
    def set_security_headers(self, response):
        """Встановлює заголовки безпеки"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = self.content_security_policy.get_policy()
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
```

### CORS та безпека

```python
class CORSManager:
    def __init__(self):
        self.allowed_origins = [
            'https://app.upwork-analyzer.com',
            'https://localhost:3000'
        ]
        self.allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.allowed_headers = [
            'Content-Type', 'Authorization', 'X-Requested-With'
        ]
        
    def validate_origin(self, origin: str) -> bool:
        """Перевіряє дозволене походження"""
        return origin in self.allowed_origins
    
    def set_cors_headers(self, response, origin: str):
        """Встановлює CORS заголовки"""
        if self.validate_origin(origin):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
            response.headers['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
            response.headers['Access-Control-Allow-Credentials'] = 'true'
```

---

## Інтеграція

### Інтеграція з React.js

```typescript
// Основна структура React додатку
interface AppState {
  user: User | null;
  dashboard: DashboardData | null;
  notifications: Notification[];
  theme: 'light' | 'dark';
}

class WebInterfaceManager {
  private apiClient: APIClient;
  private stateManager: StateManager;
  private realTimeClient: RealTimeClient;
  
  constructor() {
    this.apiClient = new APIClient();
    this.stateManager = new StateManager();
    this.realTimeClient = new RealTimeClient();
  }
  
  async initializeApp(): Promise<void> {
    try {
      // Завантажуємо дані користувача
      const user = await this.apiClient.getUserProfile();
      this.stateManager.setUser(user);
      
      // Завантажуємо дашборд
      const dashboard = await this.apiClient.getDashboard();
      this.stateManager.setDashboard(dashboard);
      
      // Підключаємося до real-time оновлень
      this.realTimeClient.connect();
      
    } catch (error) {
      console.error('Failed to initialize app:', error);
      throw error;
    }
  }
  
  async updateProposal(proposalId: string, data: Partial<Proposal>): Promise<void> {
    try {
      const updatedProposal = await this.apiClient.updateProposal(proposalId, data);
      this.stateManager.updateProposal(updatedProposal);
      
      // Оновлюємо дашборд
      const dashboard = await this.apiClient.getDashboard();
      this.stateManager.setDashboard(dashboard);
      
    } catch (error) {
      console.error('Failed to update proposal:', error);
      throw error;
    }
  }
}

// Компонент дашборду
class DashboardComponent extends React.Component<DashboardProps, DashboardState> {
  async componentDidMount() {
    try {
      const dashboard = await this.props.apiClient.getDashboard();
      this.setState({ dashboard, loading: false });
    } catch (error) {
      this.setState({ error: error.message, loading: false });
    }
  }
  
  render() {
    if (this.state.loading) {
      return <LoadingSpinner />;
    }
    
    if (this.state.error) {
      return <ErrorMessage message={this.state.error} />;
    }
    
    return (
      <div className="dashboard">
        <DashboardHeader summary={this.state.dashboard.summary} />
        <WidgetGrid widgets={this.state.dashboard.widgets} />
        <RecentActivity activities={this.state.dashboard.recentActivities} />
      </div>
    );
  }
}
```

### Інтеграція з API

```typescript
class APIClient {
  private baseURL: string;
  private authToken: string;
  
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.authToken = localStorage.getItem('auth_token') || '';
  }
  
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.authToken}`,
      ...options.headers
    };
    
    try {
      const response = await fetch(url, {
        ...options,
        headers
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          // Токен закінчився, перенаправляємо на логін
          window.location.href = '/login';
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }
  
  async getDashboard(): Promise<DashboardData> {
    return this.request<DashboardData>('/api/dashboard/main');
  }
  
  async getProposals(params: ProposalsParams): Promise<ProposalsResponse> {
    const queryString = new URLSearchParams(params).toString();
    return this.request<ProposalsResponse>(`/api/proposals?${queryString}`);
  }
  
  async createProposal(data: CreateProposalData): Promise<Proposal> {
    return this.request<Proposal>('/api/proposals', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  async getNotifications(unreadOnly: boolean = false): Promise<Notification[]> {
    return this.request<Notification[]>(`/api/notifications?unread_only=${unreadOnly}`);
  }
}
```

---

## 🧪 Тестування

### Unit Tests

```typescript
describe('WebInterfaceManager', () => {
  let manager: WebInterfaceManager;
  let mockApiClient: jest.Mocked<APIClient>;
  
  beforeEach(() => {
    mockApiClient = {
      getUserProfile: jest.fn(),
      getDashboard: jest.fn(),
      updateProposal: jest.fn()
    } as any;
    
    manager = new WebInterfaceManager();
    manager['apiClient'] = mockApiClient;
  });
  
  test('should initialize app successfully', async () => {
    const mockUser = { id: 'user_123', email: 'test@example.com' };
    const mockDashboard = { widgets: [], summary: {} };
    
    mockApiClient.getUserProfile.mockResolvedValue(mockUser);
    mockApiClient.getDashboard.mockResolvedValue(mockDashboard);
    
    await manager.initializeApp();
    
    expect(mockApiClient.getUserProfile).toHaveBeenCalled();
    expect(mockApiClient.getDashboard).toHaveBeenCalled();
  });
  
  test('should handle initialization error', async () => {
    mockApiClient.getUserProfile.mockRejectedValue(new Error('API Error'));
    
    await expect(manager.initializeApp()).rejects.toThrow('API Error');
  });
});

describe('APIClient', () => {
  let client: APIClient;
  
  beforeEach(() => {
    client = new APIClient();
    localStorage.clear();
  });
  
  test('should make authenticated requests', async () => {
    const mockToken = 'test_token';
    localStorage.setItem('auth_token', mockToken);
    
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ data: 'test' })
    });
    
    await client.getDashboard();
    
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/dashboard/main'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': `Bearer ${mockToken}`
        })
      })
    );
  });
});
```

### Integration Tests

```typescript
describe('Dashboard Integration', () => {
  test('should load and display dashboard data', async () => {
    const mockDashboard = {
      widgets: [
        {
          id: 'earnings_chart',
          type: 'line_chart',
          title: 'Доходи за місяць',
          data: { labels: [], datasets: [] }
        }
      ],
      summary: {
        total_earnings: 15000,
        active_contracts: 3
      }
    };
    
    // Мокаємо API
    jest.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockDashboard)
    } as Response);
    
    const { getByText, findByText } = render(<DashboardComponent />);
    
    // Перевіряємо завантаження
    expect(getByText('Loading...')).toBeInTheDocument();
    
    // Перевіряємо відображення даних
    await findByText('Доходи за місяць');
    expect(getByText('15000')).toBeInTheDocument();
  });
});
```

---

## Моніторинг

### Метрики веб-інтерфейсу

```typescript
class WebInterfaceMetrics {
  private analytics: Analytics;
  
  constructor() {
    this.analytics = new Analytics();
  }
  
  trackPageView(page: string): void {
    this.analytics.track('page_view', { page });
  }
  
  trackUserAction(action: string, data: any): void {
    this.analytics.track('user_action', { action, ...data });
  }
  
  trackError(error: Error, context: string): void {
    this.analytics.track('error', {
      message: error.message,
      stack: error.stack,
      context
    });
  }
  
  trackPerformance(metric: string, value: number): void {
    this.analytics.track('performance', { metric, value });
  }
}
```

### Логування веб-інтерфейсу

```typescript
class WebInterfaceLogger {
  private logger: Logger;
  
  constructor() {
    this.logger = new Logger('web_interface');
  }
  
  logUserAction(userId: string, action: string, data: any): void {
    this.logger.info('User action', {
      userId,
      action,
      data,
      timestamp: new Date().toISOString()
    });
  }
  
  logError(error: Error, context: string): void {
    this.logger.error('Web interface error', {
      message: error.message,
      stack: error.stack,
      context,
      timestamp: new Date().toISOString()
    });
  }
  
  logPerformance(metric: string, value: number): void {
    this.logger.info('Performance metric', {
      metric,
      value,
      timestamp: new Date().toISOString()
    });
  }
}
```

---

## Чек-лист реалізації

### Безпека
- [ ] Валідація вхідних даних
- [ ] Очищення вихідних даних
- [ ] CORS налаштування
- [ ] Заголовки безпеки
- [ ] Захист від XSS та CSRF

### Функціональність
- [ ] Реактивний інтерфейс на React.js
- [ ] State management
- [ ] Real-time оновлення
- [ ] Адаптивний дизайн
- [ ] Інтерактивні графіки

### Тестування
- [ ] Unit тести для компонентів
- [ ] Unit тести для API клієнта
- [ ] Integration тести для дашборду
- [ ] Тести продуктивності
- [ ] Тести доступності

### Моніторинг
- [ ] Метрики використання
- [ ] Метрики продуктивності
- [ ] Логування помилок
- [ ] Аналітика користувачів
- [ ] Відстеження помилок

---

**Версія**: 1.0.0 