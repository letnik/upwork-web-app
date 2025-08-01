import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { 
  Search as SearchIcon, 
  Description as ProposalIcon,
  TrendingUp as AnalyticsIcon,
  Person as ProfileIcon 
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { analyticsService, DashboardData } from '../services/analytics';
import { aiService } from '../services/ai';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsService.getDashboardData();
      setDashboardData(data);
      
      // Відстежуємо перегляд дашборду
      analyticsService.trackUserAction('dashboard_viewed');
    } catch (err: any) {
      console.error('Dashboard loading error:', err);
      if (err.response?.status === 401) {
        setError('Потрібна авторизація. Будь ласка, увійдіть в систему.');
      } else if (err.response?.status === 500) {
        setError('Помилка сервера. Спробуйте пізніше.');
      } else if (err.message?.includes('Network error')) {
        setError('Помилка з\'єднання з сервером. Перевірте підключення до мережі.');
      } else {
        setError('Помилка завантаження даних дашборду');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    analyticsService.trackUserAction('quick_action', { action });
    
    switch (action) {
      case 'search_jobs':
        window.location.href = '/jobs';
        break;
      case 'generate_proposal':
        window.location.href = '/jobs';
        break;
      case 'view_analytics':
        // Можна додати сторінку аналітики
        break;
      case 'edit_profile':
        window.location.href = '/profile';
        break;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <>
      <Typography variant="h4" component="h1" gutterBottom>
        Ласкаво просимо, {user?.first_name || user?.email}!
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Це ваш основний дашборд для роботи з Upwork AI Assistant
      </Typography>

      <Grid container spacing={3}>
        {/* Статистика */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Знайдені вакансії
              </Typography>
              <Typography variant="h4">
                {dashboardData?.jobs?.applied || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Подано пропозицій
              </Typography>
              <Typography variant="h4">
                {dashboardData?.proposals?.sent || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Успішність
              </Typography>
              <Typography variant="h4">
                {dashboardData?.performance?.success_rate ? `${dashboardData.performance.success_rate}%` : '0%'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Зароблено
              </Typography>
              <Typography variant="h4">
                ${dashboardData?.earnings?.total || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Швидкі дії */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Швидкі дії
            </Typography>
            <Grid container spacing={2}>
              <Grid item>
                <Button
                  variant="contained"
                  startIcon={<SearchIcon />}
                  onClick={() => handleQuickAction('search_jobs')}
                >
                  Пошук робіт
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  startIcon={<ProposalIcon />}
                  onClick={() => handleQuickAction('generate_proposal')}
                >
                  Генерувати пропозицію
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  startIcon={<AnalyticsIcon />}
                  onClick={() => handleQuickAction('view_analytics')}
                >
                  Аналітика
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  startIcon={<ProfileIcon />}
                  onClick={() => handleQuickAction('edit_profile')}
                >
                  Профіль
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Останні активності */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Останні активності
            </Typography>
            {dashboardData?.time_series && dashboardData.time_series.length > 0 ? (
              <Box>
                {dashboardData.time_series.slice(0, 3).map((activity: any, index: number) => (
                  <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      {activity.date}
                    </Typography>
                    <Typography variant="body1">
                      Зароблено: ${activity.earnings} | Пропозицій: {activity.proposals}
                    </Typography>
                    <Chip 
                      label="активність" 
                      size="small" 
                      color="primary" 
                      sx={{ mt: 1 }}
                    />
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Поки що немає активностей. Почніть з пошуку робіт!
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* AI Рекомендації */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, bgcolor: 'primary.light', color: 'white' }}>
            <Typography variant="h6" gutterBottom>
              🤖 AI Рекомендації
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              На основі вашої активності, AI рекомендує:
            </Typography>
            <Box>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Оновіть свій профіль для кращого пошуку робіт
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Додайте більше ключових слів до пошуку
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Перегляньте останні пропозиції для покращення
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </>
  );
};

export default Dashboard; 