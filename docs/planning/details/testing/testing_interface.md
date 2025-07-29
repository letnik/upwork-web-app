# 🧪 Веб-інтерфейс для тестування

> **Окрема сторінка додатку для тестування всіх функцій системи**

---

## Зміст

1. [Призначення](#призначення)
2. [Архітектура тестового інтерфейсу](#архітектура-тестового-інтерфейсу)
3. [Реалізація](#реалізація)
4. [Моніторинг тестів](#моніторинг-тестів)
5. [Безпека тестового інтерфейсу](#безпека-тестового-інтерфейсу)
6. [Розгортання](#розгортання)

---

## Призначення

Веб-інтерфейс для тестування забезпечує:
- Тестування всіх API endpoints
- Перевірку функціональності модулів
- Валідацію безпеки системи
- Тестування продуктивності
- Демонстрацію можливостей системи

---

## Архітектура тестового інтерфейсу

### Структура сторінок

```
/testing/
├── /auth/                    # Тестування авторизації
│   ├── login                 # Тест входу
│   ├── register             # Тест реєстрації
│   ├── oauth                # Тест OAuth flow
│   └── mfa                  # Тест MFA
├── /api/                     # Тестування API
│   ├── endpoints            # Тест всіх endpoints
│   ├── validation           # Тест валідації
│   └── errors              # Тест обробки помилок
├── /upwork/                  # Тестування Upwork інтеграції
│   ├── sync                 # Тест синхронізації
│   ├── jobs                 # Тест роботи з вакансіями
│   └── proposals           # Тест пропозицій
├── /ai/                      # Тестування AI функцій
│   ├── analysis            # Тест аналізу вакансій
│   ├── generation          # Тест генерації пропозицій
│   └── optimization        # Тест оптимізації
├── /security/               # Тестування безпеки
│   ├── encryption          # Тест шифрування
│   ├── rate-limiting       # Тест обмежень
│   └── monitoring          # Тест моніторингу
└── /performance/            # Тестування продуктивності
    ├── load                # Навантажувальні тести
    ├── stress              # Стрес-тести
    └── monitoring          # Моніторинг метрик
```

---

## Реалізація

### React компоненти

```typescript
// src/pages/Testing/index.tsx
import React from 'react';
import { Box, Tabs, Tab, Typography } from '@mui/material';
import AuthTesting from './AuthTesting';
import ApiTesting from './ApiTesting';
import UpworkTesting from './UpworkTesting';
import AiTesting from './AiTesting';
import SecurityTesting from './SecurityTesting';
import PerformanceTesting from './PerformanceTesting';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`testing-tabpanel-${index}`}
      aria-labelledby={`testing-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default function TestingInterface() {
  const [value, setValue] = React.useState(0);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" gutterBottom>
        🧪 Тестове середовище
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="testing tabs">
          <Tab label="Авторизація" />
          <Tab label="API" />
          <Tab label="Upwork" />
          <Tab label="AI" />
          <Tab label="Безпека" />
          <Tab label="Продуктивність" />
        </Tabs>
      </Box>
      
      <TabPanel value={value} index={0}>
        <AuthTesting />
      </TabPanel>
      <TabPanel value={value} index={1}>
        <ApiTesting />
      </TabPanel>
      <TabPanel value={value} index={2}>
        <UpworkTesting />
      </TabPanel>
      <TabPanel value={value} index={3}>
        <AiTesting />
      </TabPanel>
      <TabPanel value={value} index={4}>
        <SecurityTesting />
      </TabPanel>
      <TabPanel value={value} index={5}>
        <PerformanceTesting />
      </TabPanel>
    </Box>
  );
}
```

### Тестування авторизації

```typescript
// src/pages/Testing/AuthTesting.tsx
import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Card,
  CardContent,
  Alert,
  CircularProgress
} from '@mui/material';

interface TestResult {
  name: string;
  status: 'success' | 'error' | 'pending';
  message: string;
  duration?: number;
}

export default function AuthTesting() {
  const [results, setResults] = useState<TestResult[]>([]);
  const [loading, setLoading] = useState(false);

  const runAuthTests = async () => {
    setLoading(true);
    const newResults: TestResult[] = [];

    // Тест реєстрації
    try {
      const startTime = Date.now();
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'testuser',
          email: 'test@example.com',
          password: 'TestPassword123!'
        })
      });
      
      const duration = Date.now() - startTime;
      
      if (response.ok) {
        newResults.push({
          name: 'Реєстрація користувача',
          status: 'success',
          message: 'Користувач успішно зареєстрований',
          duration
        });
      } else {
        newResults.push({
          name: 'Реєстрація користувача',
          status: 'error',
          message: `Помилка: ${response.statusText}`,
          duration
        });
      }
    } catch (error) {
      newResults.push({
        name: 'Реєстрація користувача',
        status: 'error',
        message: `Помилка: ${error}`
      });
    }

    // Тест входу
    try {
      const startTime = Date.now();
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'testuser',
          password: 'TestPassword123!'
        })
      });
      
      const duration = Date.now() - startTime;
      
      if (response.ok) {
        newResults.push({
          name: 'Вхід користувача',
          status: 'success',
          message: 'Успішний вхід',
          duration
        });
      } else {
        newResults.push({
          name: 'Вхід користувача',
          status: 'error',
          message: `Помилка: ${response.statusText}`,
          duration
        });
      }
    } catch (error) {
      newResults.push({
        name: 'Вхід користувача',
        status: 'error',
        message: `Помилка: ${error}`
      });
    }

    setResults(newResults);
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Тестування авторизації
      </Typography>
      
      <Button
        variant="contained"
        onClick={runAuthTests}
        disabled={loading}
        sx={{ mb: 2 }}
      >
        {loading ? <CircularProgress size={24} /> : 'Запустити тести'}
      </Button>

      {results.map((result, index) => (
        <Card key={index} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {result.name}
            </Typography>
            
            <Alert severity={result.status}>
              {result.message}
              {result.duration && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Час виконання: {result.duration}ms
                </Typography>
              )}
            </Alert>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}
```

### Тестування API

```typescript
// src/pages/Testing/ApiTesting.tsx
import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Card,
  CardContent,
  Alert,
  Grid
} from '@mui/material';

interface ApiTest {
  name: string;
  endpoint: string;
  method: string;
  body?: any;
}

export default function ApiTesting() {
  const [results, setResults] = useState<any[]>([]);
  const [selectedTest, setSelectedTest] = useState<ApiTest | null>(null);

  const apiTests: ApiTest[] = [
    {
      name: 'Отримання профілю',
      endpoint: '/api/users/profile',
      method: 'GET'
    },
    {
      name: 'Отримання вакансій',
      endpoint: '/api/upwork/jobs',
      method: 'GET'
    },
    {
      name: 'Створення пропозиції',
      endpoint: '/api/upwork/proposals',
      method: 'POST',
      body: {
        job_id: 'test_job_123',
        cover_letter: 'Test proposal',
        bid_amount: 100
      }
    },
    {
      name: 'AI аналіз вакансії',
      endpoint: '/api/ai/analyze-job',
      method: 'POST',
      body: {
        job_id: 'test_job_123'
      }
    }
  ];

  const runApiTest = async (test: ApiTest) => {
    try {
      const startTime = Date.now();
      
      const options: RequestInit = {
        method: test.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      };

      if (test.body) {
        options.body = JSON.stringify(test.body);
      }

      const response = await fetch(test.endpoint, options);
      const duration = Date.now() - startTime;
      
      const result = {
        name: test.name,
        status: response.ok ? 'success' : 'error',
        statusCode: response.status,
        duration,
        data: await response.json()
      };

      setResults(prev => [...prev, result]);
    } catch (error) {
      setResults(prev => [...prev, {
        name: test.name,
        status: 'error',
        error: error.toString()
      }]);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Тестування API
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Доступні тести
          </Typography>
          
          {apiTests.map((test, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6">{test.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {test.method} {test.endpoint}
                </Typography>
                
                <Button
                  variant="outlined"
                  onClick={() => runApiTest(test)}
                  sx={{ mt: 1 }}
                >
                  Запустити тест
                </Button>
              </CardContent>
            </Card>
          ))}
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Результати тестів
          </Typography>
          
          {results.map((result, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6">{result.name}</Typography>
                
                <Alert severity={result.status} sx={{ mb: 1 }}>
                  Статус: {result.statusCode || 'Помилка'}
                  {result.duration && (
                    <Typography variant="body2">
                      Час: {result.duration}ms
                    </Typography>
                  )}
                </Alert>
                
                {result.data && (
                  <Typography variant="body2" component="pre" sx={{ fontSize: '0.8rem' }}>
                    {JSON.stringify(result.data, null, 2)}
                  </Typography>
                )}
              </CardContent>
            </Card>
          ))}
        </Grid>
      </Grid>
    </Box>
  );
}
```

---

## Моніторинг тестів

### Метрики тестування

```typescript
// src/utils/testMetrics.ts
export interface TestMetrics {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  averageResponseTime: number;
  successRate: number;
}

export class TestMetricsCollector {
  private metrics: TestMetrics = {
    totalTests: 0,
    passedTests: 0,
    failedTests: 0,
    averageResponseTime: 0,
    successRate: 0
  };

  addTestResult(success: boolean, responseTime: number) {
    this.metrics.totalTests++;
    
    if (success) {
      this.metrics.passedTests++;
    } else {
      this.metrics.failedTests++;
    }

    // Оновлення середнього часу відповіді
    const totalTime = this.metrics.averageResponseTime * (this.metrics.totalTests - 1) + responseTime;
    this.metrics.averageResponseTime = totalTime / this.metrics.totalTests;
    
    // Оновлення відсотка успішності
    this.metrics.successRate = (this.metrics.passedTests / this.metrics.totalTests) * 100;
  }

  getMetrics(): TestMetrics {
    return { ...this.metrics };
  }

  reset() {
    this.metrics = {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      averageResponseTime: 0,
      successRate: 0
    };
  }
}
```

---

## Безпека тестового інтерфейсу

### Обмеження доступу

```typescript
// src/middleware/testAccess.ts
export const requireTestAccess = (req: Request, res: Response, next: NextFunction) => {
  // Перевірка, чи користувач має права на тестування
  const user = req.user;
  
  if (!user || !user.roles.includes('tester')) {
    return res.status(403).json({
      error: 'Access denied. Testing interface requires tester role.'
    });
  }
  
  next();
};
```

### Логування тестів

```typescript
// src/utils/testLogger.ts
export class TestLogger {
  static logTest(testName: string, result: any) {
    console.log(`[TEST] ${testName}: ${result.status}`, {
      timestamp: new Date().toISOString(),
      testName,
      result,
      user: 'current_user_id'
    });
  }

  static logError(testName: string, error: any) {
    console.error(`[TEST ERROR] ${testName}:`, {
      timestamp: new Date().toISOString(),
      testName,
      error: error.toString(),
      user: 'current_user_id'
    });
  }
}
```

---

## Розгортання

### Конфігурація для різних середовищ

```typescript
// src/config/testing.ts
export const TESTING_CONFIG = {
  development: {
    enabled: true,
    allowDestructiveTests: true,
    mockData: true
  },
  staging: {
    enabled: true,
    allowDestructiveTests: false,
    mockData: false
  },
  production: {
    enabled: false,
    allowDestructiveTests: false,
    mockData: false
  }
};
```

---

**Версія**: 1.0.0 