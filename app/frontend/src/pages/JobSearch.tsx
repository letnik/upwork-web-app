import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { Search as SearchIcon, FilterList as FilterIcon } from '@mui/icons-material';
import { upworkService, Job, JobFilters } from '../services/upwork';
import { analyticsService } from '../services/analytics';

const JobSearch: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<JobFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const [budgetRange, setBudgetRange] = useState<[number, number]>([0, 20000]);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async (searchParams?: { query?: string; filters?: JobFilters }) => {
    try {
      setLoading(true);
      setError(null);

      let jobsData;
      if (searchParams?.query) {
        // Пошук вакансій
        const searchResult = await upworkService.searchJobs({
          query: searchParams.query,
          limit: 50
        });
        jobsData = searchResult.jobs;
        
        // Відстежуємо пошук
        analyticsService.trackJobSearch(searchParams.query, searchResult.total);
      } else {
        // Отримання всіх вакансій з фільтрами
        const result = await upworkService.getJobs({
          limit: 50,
          ...searchParams?.filters
        });
        jobsData = result.jobs;
      }

      setJobs(jobsData);
    } catch (err) {
      setError('Помилка завантаження вакансій');
      console.error('Job loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      loadJobs({ query: searchQuery.trim() });
    } else {
      loadJobs({ filters });
    }
  };

  const handleFilterChange = (key: keyof JobFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleApplyFilters = () => {
    loadJobs({ filters });
  };

  const handleJobClick = (job: Job) => {
    // Відстежуємо перегляд вакансії
    upworkService.trackJobView(job.id);
    // Тут можна додати навігацію до деталей вакансії
    console.log('Job clicked:', job.id);
  };

  const formatBudget = (budget: Job['budget']) => {
    return `$${budget.min.toLocaleString()} - $${budget.max.toLocaleString()}`;
  };

  const formatPostedTime = (postedTime: string) => {
    const date = new Date(postedTime);
    const now = new Date();
    const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'Щойно';
    if (diffHours < 24) return `${diffHours} год. тому`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} дн. тому`;
  };

  return (
    <>
      <Typography variant="h4" component="h1" gutterBottom>
        Пошук вакансій
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Знайдіть ідеальну вакансію на Upwork з допомогою AI
      </Typography>

      {/* Пошук */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Пошук вакансій"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Наприклад: React developer, Python backend..."
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={loading}
            >
              Пошук
            </Button>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => setShowFilters(!showFilters)}
            >
              Фільтри
            </Button>
          </Grid>
        </Grid>

        {/* Фільтри */}
        {showFilters && (
          <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="h6" gutterBottom>
              Фільтри пошуку
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="Навички"
                  value={filters.skills || ''}
                  onChange={(e) => handleFilterChange('skills', e.target.value)}
                  placeholder="React, Python, AWS..."
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="Локація"
                  value={filters.location || ''}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                  placeholder="United States, Canada..."
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography gutterBottom>Бюджет (USD)</Typography>
                <Slider
                  value={budgetRange}
                  onChange={(_, value) => setBudgetRange(value as [number, number])}
                  valueLabelDisplay="auto"
                  min={0}
                  max={20000}
                  step={500}
                />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption">${budgetRange[0].toLocaleString()}</Typography>
                  <Typography variant="caption">${budgetRange[1].toLocaleString()}</Typography>
                </Box>
              </Grid>
            </Grid>
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                onClick={handleApplyFilters}
                disabled={loading}
              >
                Застосувати фільтри
              </Button>
            </Box>
          </Box>
        )}
      </Paper>

      {/* Результати */}
      <Box sx={{ mt: 3 }}>
        {loading && (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {!loading && !error && jobs.length === 0 && (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              Вакансії не знайдено
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Спробуйте змінити критерії пошуку
            </Typography>
          </Paper>
        )}

        {!loading && !error && jobs.length > 0 && (
          <>
            <Typography variant="h6" gutterBottom>
              Знайдено {jobs.length} вакансій
            </Typography>
            <Grid container spacing={2}>
              {jobs.map((job) => (
                <Grid item xs={12} key={job.id}>
                  <Card 
                    sx={{ cursor: 'pointer', '&:hover': { boxShadow: 3 } }}
                    onClick={() => handleJobClick(job)}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6" component="h2" sx={{ flex: 1 }}>
                          {job.title}
                        </Typography>
                        <Typography variant="h6" color="primary">
                          {formatBudget(job.budget)}
                        </Typography>
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {job.description.length > 200 
                          ? `${job.description.substring(0, 200)}...` 
                          : job.description}
                      </Typography>

                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                        {job.skills.slice(0, 5).map((skill) => (
                          <Chip key={skill} label={skill} size="small" />
                        ))}
                        {job.skills.length > 5 && (
                          <Chip label={`+${job.skills.length - 5}`} size="small" variant="outlined" />
                        )}
                      </Box>

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {job.client.name} • {job.location}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            ⭐ {job.client.rating} • ${job.client.total_spent.toLocaleString()} витрачено
                          </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography variant="body2" color="text.secondary">
                            {formatPostedTime(job.posted_time)}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {job.proposals_count} пропозицій • {job.hire_rate}% наймають
                          </Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </>
        )}
      </Box>
    </>
  );
};

export default JobSearch; 