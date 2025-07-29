# План імплементації модуля веб-інтерфейсу

> **Детальний план розробки веб-інтерфейсу з конкретними завданнями та інструкціями**

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
Створити сучасний, зручний та функціональний веб-інтерфейс для всіх модулів системи.

### Тривалість
- **Загальна тривалість**: 8 тижнів
- **Кількість спринтів**: 4 спринти по 2 тижні

### Команда
- **Frontend Developer**: 1 особа
- **UI/UX Designer**: 0.5 особи
- **Backend Developer**: 0.5 особи
- **QA Engineer**: 0.5 особи

---

## Етапи розробки

### Етап 1: Базова інфраструктура (Тижні 1-2)
- Налаштування React проекту
- Базова архітектура компонентів
- Система маршрутизації
- Базові UI компоненти

### Етап 2: Основні сторінки (Тижні 3-4)
- Дашборд користувача
- Сторінка пропозицій
- Сторінка аналітики
- Профіль користувача

### Етап 3: Інтерактивність (Тижні 5-6)
- Реальний час оновлення
- Інтерактивні графіки
- Система сповіщень
- Адаптивний дизайн

### Етап 4: Оптимізація (Тижні 7-8)
- Оптимізація продуктивності
- Тестування
- Документація
- Розгортання

---

## Детальні завдання

### WEB-001: Налаштування React проекту

**Опис**: Створити базову структуру React проекту з необхідними залежностями.

**Критерії прийняття**:
- [ ] Створений React проект з TypeScript
- [ ] Налаштовані залежності (Material-UI, React Query, Zustand)
- [ ] Налаштована система збірки
- [ ] Базові конфігурації

**Інструкції виконання**:

```bash
# Створення проекту
npx create-react-app upwork-ai-assistant --template typescript

# Встановлення залежностей
npm install @mui/material @emotion/react @emotion/styled
npm install @tanstack/react-query zustand
npm install react-router-dom axios
npm install recharts @mui/x-charts
npm install @mui/icons-material
```

```typescript
// Структура проекту
src/
├── components/
│   ├── common/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── LoadingSpinner.tsx
│   ├── dashboard/
│   │   ├── Dashboard.tsx
│   │   └── MetricCard.tsx
│   └── forms/
│       ├── LoginForm.tsx
│       └── ProfileForm.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── Proposals.tsx
│   ├── Analytics.tsx
│   └── Profile.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useApi.ts
│   └── useNotifications.ts
├── store/
│   ├── authStore.ts
│   └── uiStore.ts
├── services/
│   ├── api.ts
│   └── websocket.ts
└── utils/
    ├── constants.ts
    └── helpers.ts
```

**Оцінка**: 8 годин

---

### WEB-002: Базова архітектура компонентів

**Опис**: Створити базові компоненти та систему маршрутизації.

**Критерії прийняття**:
- [ ] Створені базові компоненти (Header, Sidebar, Layout)
- [ ] Налаштована маршрутизація
- [ ] Створена тема Material-UI
- [ ] Базові хуки

**Інструкції виконання**:

```typescript
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from './theme';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Proposals from './pages/Proposals';
import Analytics from './pages/Analytics';
import Profile from './pages/Profile';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/proposals" element={<Proposals />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
```

```typescript
// Layout.tsx
import { Box, Container } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Box sx={{ display: 'flex' }}>
      <Header />
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: { sm: 30 }
        }}
      >
        <Container maxWidth="xl">
          {children}
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;
```

**Оцінка**: 12 годин

---

### WEB-003: Система аутентифікації

**Опис**: Створити систему аутентифікації та управління станом користувача.

**Критерії прийняття**:
- [ ] Форма входу
- [ ] Зберігання токену
- [ ] Захищені маршрути
- [ ] Автоматичне оновлення токену

**Інструкції виконання**:

```typescript
// authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: async (email: string, password: string) => {
        try {
          const response = await api.post('/auth/login', { email, password });
          const { user, token } = response.data;
          
          set({
            user,
            token,
            isAuthenticated: true
          });
          
          // Зберігаємо токен в localStorage
          localStorage.setItem('token', token);
        } catch (error) {
          throw new Error('Login failed');
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false
        });
        localStorage.removeItem('token');
      },
      
      updateUser: (user: User) => {
        set({ user });
      }
    }),
    {
      name: 'auth-storage'
    }
  )
);
```

```typescript
// LoginForm.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert
} from '@mui/material';
import { useAuthStore } from '../store/authStore';

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const login = useAuthStore(state => state.login);
  const navigate = useNavigate();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      await login(email, password);
      navigate('/');
    } catch (error) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        maxWidth: 400,
        mx: 'auto',
        mt: 8
      }}
    >
      <Typography variant="h4" align="center">
        Sign In
      </Typography>
      
      {error && <Alert severity="error">{error}</Alert>}
      
      <TextField
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      
      <Button
        type="submit"
        variant="contained"
        disabled={loading}
        sx={{ mt: 2 }}
      >
        {loading ? 'Signing in...' : 'Sign In'}
      </Button>
    </Box>
  );
};

export default LoginForm;
```

**Оцінка**: 16 годин

---

### WEB-004: Дашборд користувача

**Опис**: Створити головний дашборд з основними метриками та графіками.

**Критерії прийняття**:
- [ ] Відображення основних метрик
- [ ] Інтерактивні графіки
- [ ] Оновлення в реальному часі
- [ ] Адаптивний дизайн

**Інструкції виконання**:

```typescript
// Dashboard.tsx
import { useEffect } from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import MetricCard from '../components/dashboard/MetricCard';
import EarningsChart from '../components/dashboard/EarningsChart';
import ProposalsChart from '../components/dashboard/ProposalsChart';
import { api } from '../services/api';

const Dashboard: React.FC = () => {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => api.get('/analytics/metrics/user/current'),
    refetchInterval: 30000 // Оновлюємо кожні 30 секунд
  });
  
  const { data: earningsData } = useQuery({
    queryKey: ['earnings-chart'],
    queryFn: () => api.get('/analytics/earnings/timeline'),
    refetchInterval: 60000 // Оновлюємо кожну хвилину
  });
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Метрики */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Earnings"
            value={`$${metrics?.total_earnings?.toLocaleString()}`}
            trend={metrics?.trends?.earnings_growth}
            icon="attach_money"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Win Rate"
            value={`${(metrics?.win_rate * 100).toFixed(1)}%`}
            trend={metrics?.trends?.win_rate_change}
            icon="trending_up"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Contracts"
            value={metrics?.active_contracts}
            icon="work"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Proposals Sent"
            value={metrics?.proposals_sent}
            trend={metrics?.trends?.proposals_growth}
            icon="send"
          />
        </Grid>
        
        {/* Графіки */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Earnings Timeline
            </Typography>
            <EarningsChart data={earningsData} />
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Proposals Status
            </Typography>
            <ProposalsChart data={metrics?.proposals_status} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
```

```typescript
// MetricCard.tsx
import { Card, CardContent, Typography, Box } from '@mui/material';
import { Icon } from '@mui/icons-material';

interface MetricCardProps {
  title: string;
  value: string | number;
  trend?: number;
  icon?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, trend, icon }) => {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4">
              {value}
            </Typography>
            {trend !== undefined && (
              <Typography
                variant="body2"
                color={trend >= 0 ? 'success.main' : 'error.main'}
              >
                {trend >= 0 ? '↗' : '↘'} {Math.abs(trend * 100).toFixed(1)}%
              </Typography>
            )}
          </Box>
          {icon && (
            <Icon sx={{ fontSize: 40, color: 'primary.main' }}>
              {icon}
            </Icon>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default MetricCard;
```

**Оцінка**: 20 годин

---

### WEB-005: Сторінка пропозицій

**Опис**: Створити сторінку для управління пропозиціями та контрактами.

**Критерії прийняття**:
- [ ] Список пропозицій з фільтрами
- [ ] Детальна інформація про пропозицію
- [ ] Статус пропозицій
- [ ] Пошук та сортування

**Інструкції виконання**:

```typescript
// Proposals.tsx
import { useState } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

const Proposals: React.FC = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  
  const { data: proposals, isLoading } = useQuery({
    queryKey: ['proposals', page, rowsPerPage, search, statusFilter],
    queryFn: () => api.get('/upwork/proposals', {
      params: {
        page: page + 1,
        limit: rowsPerPage,
        search,
        status: statusFilter !== 'all' ? statusFilter : undefined
      }
    })
  });
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'hired': return 'success';
      case 'interviewing': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Proposals
      </Typography>
      
      {/* Фільтри */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <TextField
          label="Search proposals"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ minWidth: 300 }}
        />
        
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            label="Status"
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="interviewing">Interviewing</MenuItem>
            <MenuItem value="hired">Hired</MenuItem>
            <MenuItem value="rejected">Rejected</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
      {/* Таблиця */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Job Title</TableCell>
              <TableCell>Client</TableCell>
              <TableCell>Budget</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {proposals?.data?.map((proposal: any) => (
              <TableRow key={proposal.id}>
                <TableCell>{proposal.job_title}</TableCell>
                <TableCell>{proposal.client_name}</TableCell>
                <TableCell>${proposal.budget}</TableCell>
                <TableCell>
                  <Chip
                    label={proposal.status}
                    color={getStatusColor(proposal.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(proposal.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Button size="small" onClick={() => handleViewDetails(proposal.id)}>
                    View
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        
        <TablePagination
          component="div"
          count={proposals?.total || 0}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>
    </Box>
  );
};

export default Proposals;
```

**Оцінка**: 18 годин

---

### WEB-006: Система сповіщень

**Опис**: Створити систему сповіщень для користувачів.

**Критерії прийняття**:
- [ ] Toast сповіщення
- [ ] Центр сповіщень
- [ ] Real-time сповіщення
- [ ] Налаштування сповіщень

**Інструкції виконання**:

```typescript
// NotificationProvider.tsx
import { createContext, useContext, useState, useEffect } from 'react';
import { Snackbar, Alert, Badge, IconButton, Menu, MenuItem } from '@mui/material';
import { Notifications as NotificationsIcon } from '@mui/icons-material';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  timestamp: Date;
  read: boolean;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');
  const [currentType, setCurrentType] = useState<'success' | 'error' | 'warning' | 'info'>('info');
  
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    };
    
    setNotifications(prev => [newNotification, ...prev]);
    
    // Показуємо toast
    setCurrentMessage(notification.message);
    setCurrentType(notification.type);
    setOpen(true);
  };
  
  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };
  
  const clearAll = () => {
    setNotifications([]);
  };
  
  return (
    <NotificationContext.Provider value={{
      notifications,
      addNotification,
      markAsRead,
      clearAll
    }}>
      {children}
      
      {/* Toast сповіщення */}
      <Snackbar
        open={open}
        autoHideDuration={6000}
        onClose={() => setOpen(false)}
      >
        <Alert
          onClose={() => setOpen(false)}
          severity={currentType}
          sx={{ width: '100%' }}
        >
          {currentMessage}
        </Alert>
      </Snackbar>
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};
```

**Оцінка**: 14 годин

---

### WEB-007: Адаптивний дизайн

**Опис**: Забезпечити повну адаптивність інтерфейсу для всіх пристроїв.

**Критерії прийняття**:
- [ ] Mobile-first підхід
- [ ] Responsive таблиці
- [ ] Адаптивні графіки
- [ ] Touch-friendly інтерфейс

**Інструкції виконання**:

```typescript
// ResponsiveTable.tsx
import { useTheme, useMediaQuery } from '@mui/material';
import { useState } from 'react';

interface ResponsiveTableProps {
  data: any[];
  columns: any[];
}

const ResponsiveTable: React.FC<ResponsiveTableProps> = ({ data, columns }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  if (isMobile) {
    return (
      <Box>
        {data.map((row, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              {columns.map((column) => (
                <Box key={column.field} sx={{ mb: 1 }}>
                  <Typography variant="caption" color="textSecondary">
                    {column.headerName}
                  </Typography>
                  <Typography variant="body2">
                    {row[column.field]}
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }
  
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell key={column.field}>{column.headerName}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row, index) => (
            <TableRow key={index}>
              {columns.map((column) => (
                <TableCell key={column.field}>
                  {row[column.field]}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
```

**Оцінка**: 12 годин

---

### WEB-008: Оптимізація продуктивності

**Опис**: Оптимізувати продуктивність веб-інтерфейсу.

**Критерії прийняття**:
- [ ] Lazy loading компонентів
- [ ] Оптимізація зображень
- [ ] Кешування даних
- [ ] Bundle optimization

**Інструкції виконання**:

```typescript
// Lazy loading компонентів
import { lazy, Suspense } from 'react';
import { CircularProgress } from '@mui/material';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Proposals = lazy(() => import('./pages/Proposals'));

const LoadingFallback = () => (
  <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
    <CircularProgress />
  </Box>
);

// App.tsx з lazy loading
function App() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/proposals" element={<Proposals />} />
      </Routes>
    </Suspense>
  );
}
```

```typescript
// Оптимізація зображень
import { LazyLoadImage } from 'react-lazy-load-image-component';

const OptimizedImage: React.FC<{ src: string; alt: string }> = ({ src, alt }) => {
  return (
    <LazyLoadImage
      src={src}
      alt={alt}
      effect="blur"
      placeholderSrc="/placeholder.png"
      style={{ width: '100%', height: 'auto' }}
    />
  );
};
```

**Оцінка**: 10 годин

---

## Критерії прийняття

### Загальні критерії
- [ ] Всі компоненти працюють коректно
- [ ] Адаптивний дизайн для всіх пристроїв
- [ ] Продуктивність оптимізована
- [ ] Accessibility відповідає стандартам

### Критерії продуктивності
- [ ] Час завантаження < 3 секунди
- [ ] Bundle size < 2MB
- [ ] Lighthouse score > 90
- [ ] Real-time оновлення працює

### Критерії UX
- [ ] Інтуїтивний інтерфейс
- [ ] Швидка навігація
- [ ] Зрозумілі повідомлення
- [ ] Responsive дизайн

---

## 🧪 Тестування

### Unit тести
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LoginForm from '../components/LoginForm';

const queryClient = new QueryClient();

describe('LoginForm', () => {
  it('should render login form', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <LoginForm />
      </QueryClientProvider>
    );
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });
  
  it('should show error on invalid login', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <LoginForm />
      </QueryClientProvider>
    );
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'invalid@email.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' }
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    expect(await screen.findByText(/invalid email or password/i)).toBeInTheDocument();
  });
});
```

### E2E тести
```typescript
import { test, expect } from '@playwright/test';

test('user can login and view dashboard', async ({ page }) => {
  await page.goto('/login');
  
  await page.fill('[data-testid="email-input"]', 'user@example.com');
  await page.fill('[data-testid="password-input"]', 'password123');
  await page.click('[data-testid="login-button"]');
  
  await expect(page).toHaveURL('/');
  await expect(page.locator('h1')).toContainText('Dashboard');
});
```

---

## Моніторинг

### Метрики для відстеження
- Час завантаження сторінок
- Кількість помилок JavaScript
- Використання пам'яті
- Кількість активних користувачів

### Алерти
- Високий час завантаження
- Багато помилок JavaScript
- Проблеми з API
- Проблеми з WebSocket

---

## Розклад

### Спринт 1 (Тижні 1-2)
- WEB-001: Налаштування проекту (8 годин)
- WEB-002: Базова архітектура (12 годин)
- **Всього**: 20 годин

### Спринт 2 (Тижні 3-4)
- WEB-003: Аутентифікація (16 годин)
- WEB-004: Дашборд (20 годин)
- **Всього**: 36 годин

### Спринт 3 (Тижні 5-6)
- WEB-005: Сторінка пропозицій (18 годин)
- WEB-006: Система сповіщень (14 годин)
- **Всього**: 32 години

### Спринт 4 (Тижні 7-8)
- WEB-007: Адаптивний дизайн (12 годин)
- WEB-008: Оптимізація (10 годин)
- **Всього**: 22 години

**Загальна тривалість**: 110 годин (≈ 13.75 робочих днів)

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 16:10  
**Статус**: В розробці 