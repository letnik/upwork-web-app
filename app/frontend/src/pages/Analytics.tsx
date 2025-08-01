import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Schedule,
  Work,
  Star,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface AnalyticsData {
  earnings: {
    total: number;
    monthly: number;
    weekly: number;
    trend: number;
  };
  proposals: {
    sent: number;
    accepted: number;
    pending: number;
    successRate: number;
  };
  jobs: {
    applied: number;
    won: number;
    active: number;
    completed: number;
  };
  performance: {
    rating: number;
    responseTime: number;
    completionRate: number;
  };
  timeSeries: Array<{
    date: string;
    earnings: number;
    proposals: number;
    jobs: number;
  }>;
  categoryData: Array<{
    name: string;
    value: number;
    color: string;
  }>;
}

const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    // Імітація завантаження даних
    setTimeout(() => {
      const mockData: AnalyticsData = {
        earnings: {
          total: 15420,
          monthly: 3200,
          weekly: 850,
          trend: 12.5,
        },
        proposals: {
          sent: 45,
          accepted: 18,
          pending: 12,
          successRate: 40,
        },
        jobs: {
          applied: 67,
          won: 23,
          active: 8,
          completed: 15,
        },
        performance: {
          rating: 4.8,
          responseTime: 2.3,
          completionRate: 95,
        },
        timeSeries: [
          { date: 'Пн', earnings: 1200, proposals: 5, jobs: 3 },
          { date: 'Вт', earnings: 1800, proposals: 8, jobs: 4 },
          { date: 'Ср', earnings: 1400, proposals: 6, jobs: 2 },
          { date: 'Чт', earnings: 2200, proposals: 10, jobs: 5 },
          { date: 'Пт', earnings: 1900, proposals: 7, jobs: 3 },
          { date: 'Сб', earnings: 1600, proposals: 4, jobs: 2 },
          { date: 'Нд', earnings: 1100, proposals: 3, jobs: 1 },
        ],
        categoryData: [
          { name: 'Web Development', value: 45, color: '#8884d8' },
          { name: 'Mobile Development', value: 25, color: '#82ca9d' },
          { name: 'Design', value: 20, color: '#ffc658' },
          { name: 'Writing', value: 10, color: '#ff7300' },
        ],
      };
      setData(mockData);
      setLoading(false);
    }, 1500);
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    trend?: number;
    color?: string;
  }> = ({ title, value, icon, trend, color = 'primary' }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
              {value}
            </Typography>
            {trend !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                {trend > 0 ? (
                  <TrendingUp sx={{ color: 'success.main', fontSize: 16 }} />
                ) : (
                  <TrendingDown sx={{ color: 'error.main', fontSize: 16 }} />
                )}
                <Typography
                  variant="body2"
                  color={trend > 0 ? 'success.main' : 'error.main'}
                  sx={{ ml: 0.5 }}
                >
                  {Math.abs(trend)}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              backgroundColor: `${color}.light`,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!data) {
    return (
      <Box p={3}>
        <Alert severity="warning">Дані не знайдено</Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        📊 Аналітика
      </Typography>

      {/* Основні метрики */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Загальний заробіток"
            value={`$${data.earnings.total.toLocaleString()}`}
            icon={<AttachMoney sx={{ color: 'primary.main' }} />}
            trend={data.earnings.trend}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Пропозиції відправлено"
            value={data.proposals.sent}
            icon={<Work sx={{ color: 'secondary.main' }} />}
            trend={15}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Активні проекти"
            value={data.jobs.active}
            icon={<Schedule sx={{ color: 'info.main' }} />}
            trend={-5}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Рейтинг"
            value={data.performance.rating}
            icon={<Star sx={{ color: 'warning.main' }} />}
            trend={2}
          />
        </Grid>
      </Grid>

      {/* Таби для різних типів аналітики */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Заробіток" />
          <Tab label="Пропозиції" />
          <Tab label="Проекти" />
          <Tab label="Категорії" />
        </Tabs>
      </Paper>

      {/* Контент табів */}
      <Box>
        {activeTab === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3, height: 400 }}>
                <Typography variant="h6" gutterBottom>
                  Динаміка заробітку
                </Typography>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.timeSeries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="earnings" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <MetricCard
                    title="Заробіток цього місяця"
                    value={`$${data.earnings.monthly.toLocaleString()}`}
                    icon={<AttachMoney sx={{ color: 'success.main' }} />}
                    trend={8}
                  />
                </Grid>
                <Grid item xs={12}>
                  <MetricCard
                    title="Заробіток цього тижня"
                    value={`$${data.earnings.weekly.toLocaleString()}`}
                    icon={<AttachMoney sx={{ color: 'info.main' }} />}
                    trend={12}
                  />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        )}

        {activeTab === 1 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: 400 }}>
                <Typography variant="h6" gutterBottom>
                  Статистика пропозицій
                </Typography>
                <Box display="flex" flexDirection="column" gap={2}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography>Відправлено</Typography>
                    <Chip label={data.proposals.sent} color="primary" />
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography>Прийнято</Typography>
                    <Chip label={data.proposals.accepted} color="success" />
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography>В очікуванні</Typography>
                    <Chip label={data.proposals.pending} color="warning" />
                  </Box>
                  <Divider />
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="h6">Успішність</Typography>
                    <Typography variant="h6" color="success.main">
                      {data.proposals.successRate}%
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: 400 }}>
                <Typography variant="h6" gutterBottom>
                  Динаміка пропозицій
                </Typography>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.timeSeries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="proposals" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
          </Grid>
        )}

        {activeTab === 2 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3, height: 400 }}>
                <Typography variant="h6" gutterBottom>
                  Активність проектів
                </Typography>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.timeSeries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="jobs" stroke="#ffc658" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: 400 }}>
                <Typography variant="h6" gutterBottom>
                  Статистика проектів
                </Typography>
                <Box display="flex" flexDirection="column" gap={2}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography>Подано заявок</Typography>
                    <Chip label={data.jobs.applied} color="primary" />
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography>Виграно</Typography>
                    <Chip label={data.jobs.won} color="success" />
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography>Активні</Typography>
                    <Chip label={data.jobs.active} color="info" />
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography>Завершені</Typography>
                    <Chip label={data.jobs.completed} color="default" />
                  </Box>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        )}

        {activeTab === 3 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: 400 }}>
                <Typography variant="h6" gutterBottom>
                  Розподіл по категоріях
                </Typography>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(props: any) => 
                        props.percent ? `${props.name} ${(props.percent * 100).toFixed(0)}%` : props.name
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {data.categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: 400 }}>
                <Typography variant="h6" gutterBottom>
                  Деталі категорій
                </Typography>
                <Box display="flex" flexDirection="column" gap={2}>
                  {data.categoryData.map((category, index) => (
                    <Box key={index} display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            backgroundColor: category.color,
                          }}
                        />
                        <Typography>{category.name}</Typography>
                      </Box>
                      <Typography variant="h6">{category.value}%</Typography>
                    </Box>
                  ))}
                </Box>
              </Paper>
            </Grid>
          </Grid>
        )}
      </Box>
    </Box>
  );
};

export default Analytics; 