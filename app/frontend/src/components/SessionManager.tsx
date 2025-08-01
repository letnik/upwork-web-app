import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Computer as ComputerIcon,
  Smartphone as SmartphoneIcon,
  Tablet as TabletIcon
} from '@mui/icons-material';
import { useSession } from '../hooks/useSession';

const SessionManager: React.FC = () => {
  const {
    sessions,
    total,
    loading,
    error,
    refreshSessions,
    deactivateSession,
    deactivateAllSessions
  } = useSession();

  const getDeviceIcon = (userAgent: string | null) => {
    if (!userAgent) return <ComputerIcon />;
    
    const ua = userAgent.toLowerCase();
    if (ua.includes('mobile') || ua.includes('android') || ua.includes('iphone')) {
      return <SmartphoneIcon />;
    } else if (ua.includes('tablet') || ua.includes('ipad')) {
      return <TabletIcon />;
    } else {
      return <ComputerIcon />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('uk-UA', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDeactivateSession = async (sessionId: number) => {
    const success = await deactivateSession(sessionId);
    if (success) {
      // Сесії автоматично оновляться через useSession
    }
  };

  const handleDeactivateAllSessions = async () => {
    if (window.confirm('Ви впевнені, що хочете деактивувати всі сесії? Це вимкне всі активні сесії.')) {
      const success = await deactivateAllSessions();
      if (success) {
        // Сесії автоматично оновляться через useSession
      }
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h6">
          Активні сесії ({total})
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={refreshSessions}
            sx={{ mr: 1 }}
          >
            Оновити
          </Button>
          {total > 1 && (
            <Button
              variant="outlined"
              color="error"
              onClick={handleDeactivateAllSessions}
            >
              Деактивувати всі
            </Button>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {sessions.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" textAlign="center">
              Активних сесій не знайдено
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {sessions.map((session) => (
            <Grid item xs={12} key={session.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box display="flex" alignItems="center" sx={{ flex: 1 }}>
                      {getDeviceIcon(session.user_agent)}
                      <Box sx={{ ml: 2, flex: 1 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          {session.ip_address || 'Невідома IP адреса'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {session.user_agent || 'Невідомий браузер'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Створено: {formatDate(session.created_at)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          Закінчується: {formatDate(session.expires_at)}
                        </Typography>
                      </Box>
                    </Box>
                    
                    <Box display="flex" alignItems="center" gap={1}>
                      {session.is_current && (
                        <Chip
                          label="Поточна"
                          color="primary"
                          size="small"
                        />
                      )}
                      {!session.is_current && (
                        <Tooltip title="Деактивувати сесію">
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => handleDeactivateSession(session.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {sessions.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="body2" color="text.secondary">
            💡 Порада: Деактивуйте незнайомі сесії для підвищення безпеки вашого акаунту
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SessionManager; 