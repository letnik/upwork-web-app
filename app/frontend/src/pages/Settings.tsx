import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  Divider,
  Card,
  CardContent,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Security,
  Notifications,
  Palette,
  Person,
  Download,
  Visibility,
  VisibilityOff,
  Email,
  Phone,
  Language,
  DarkMode,
  LightMode,
  Delete,
  Edit,
  Save,
  Cancel,
} from '@mui/icons-material';
import MFASetup from '../components/MFASetup';
import SessionManager from '../components/SessionManager';

interface MFASettings {
  mfa_enabled: boolean;
  mfa_setup: boolean;
  backup_codes_count: number;
}

interface ProfileSettings {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  bio: string;
  skills: string[];
  hourly_rate: number;
  timezone: string;
  language: string;
}

interface NotificationSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  proposal_alerts: boolean;
  job_matches: boolean;
  payment_notifications: boolean;
  marketing_emails: boolean;
}

interface ThemeSettings {
  mode: 'light' | 'dark' | 'auto';
  primary_color: string;
  compact_mode: boolean;
}

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [mfaSettings, setMfaSettings] = useState<MFASettings | null>(null);
  const [profileSettings, setProfileSettings] = useState<ProfileSettings>({
    first_name: 'Іван',
    last_name: 'Петренко',
    email: 'ivan.petrenko@example.com',
    phone: '+380501234567',
    bio: 'Досвідчений веб-розробник з 5+ роками досвіду',
    skills: ['React', 'Node.js', 'Python', 'TypeScript'],
    hourly_rate: 25,
    timezone: 'Europe/Kiev',
    language: 'uk',
  });
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>({
    email_notifications: true,
    push_notifications: true,
    proposal_alerts: true,
    job_matches: true,
    payment_notifications: true,
    marketing_emails: false,
  });
  const [themeSettings, setThemeSettings] = useState<ThemeSettings>({
    mode: 'light',
    primary_color: '#1976d2',
    compact_mode: false,
  });
  const [showMFASetup, setShowMFASetup] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editProfile, setEditProfile] = useState(false);
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
    show_passwords: false,
  });

  // Завантажити налаштування MFA
  const loadMFASettings = async () => {
    try {
      const response = await fetch('/api/auth/mfa/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setMfaSettings(data);
      }
    } catch (err) {
      console.error('Помилка завантаження налаштувань MFA:', err);
    }
  };

  // Вимкнути MFA
  const disableMFA = async () => {
    setLoading(true);
    setError(null);

    try {
      const code = prompt('Введіть поточний MFA код для вимкнення:');
      if (!code) return;

      const response = await fetch('/api/auth/mfa/disable', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ code })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Помилка вимкнення MFA');
      }

      setSuccess('MFA успішно вимкнено');
      loadMFASettings();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Помилка вимкнення MFA');
    } finally {
      setLoading(false);
    }
  };

  // Регенерувати резервні коди
  const regenerateBackupCodes = async () => {
    setLoading(true);
    setError(null);

    try {
      const code = prompt('Введіть поточний MFA код для регенерації резервних кодів:');
      if (!code) return;

      const response = await fetch('/api/auth/mfa/regenerate-backup-codes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ code })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Помилка регенерації резервних кодів');
      }

      const data = await response.json();
      alert(`Нові резервні коди:\n${data.backup_codes.join('\n')}`);
      setSuccess('Резервні коди регенеровано');
      loadMFASettings();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Помилка регенерації резервних кодів');
    } finally {
      setLoading(false);
    }
  };

  // Змінити пароль
  const changePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('Нові паролі не співпадають');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          current_password: passwordData.current_password,
          new_password: passwordData.new_password,
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Помилка зміни паролю');
      }

      setSuccess('Пароль успішно змінено');
      setShowPasswordDialog(false);
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
        show_passwords: false,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Помилка зміни паролю');
    } finally {
      setLoading(false);
    }
  };

  // Експорт даних
  const exportData = () => {
    const data = {
      profile: profileSettings,
      notifications: notificationSettings,
      theme: themeSettings,
      export_date: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `upwork-settings-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    setSuccess('Дані експортовано');
  };

  // Зберегти налаштування профілю
  const saveProfile = () => {
    setEditProfile(false);
    setSuccess('Профіль успішно оновлено');
  };

  useEffect(() => {
    loadMFASettings();
  }, []);

  if (showMFASetup) {
    return (
      <Box sx={{ p: 3 }}>
        <MFASetup
          onSetupComplete={() => {
            setShowMFASetup(false);
            loadMFASettings();
            setSuccess('MFA успішно налаштовано!');
          }}
          onCancel={() => setShowMFASetup(false)}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Налаштування
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Таби */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab icon={<Person />} label="Профіль" />
          <Tab icon={<Security />} label="Безпека" />
          <Tab icon={<Notifications />} label="Сповіщення" />
          <Tab icon={<Palette />} label="Тема" />
          <Tab icon={<Download />} label="Експорт" />
        </Tabs>
      </Paper>

      {/* Контент табів */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    Інформація профілю
                  </Typography>
                  <Box>
                    {editProfile ? (
                      <>
                        <Button
                          variant="contained"
                          startIcon={<Save />}
                          onClick={saveProfile}
                          sx={{ mr: 1 }}
                        >
                          Зберегти
                        </Button>
                        <Button
                          variant="outlined"
                          startIcon={<Cancel />}
                          onClick={() => setEditProfile(false)}
                        >
                          Скасувати
                        </Button>
                      </>
                    ) : (
                      <Button
                        variant="outlined"
                        startIcon={<Edit />}
                        onClick={() => setEditProfile(true)}
                      >
                        Редагувати
                      </Button>
                    )}
                  </Box>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Ім'я"
                      value={profileSettings.first_name}
                      onChange={(e) => setProfileSettings({...profileSettings, first_name: e.target.value})}
                      disabled={!editProfile}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Прізвище"
                      value={profileSettings.last_name}
                      onChange={(e) => setProfileSettings({...profileSettings, last_name: e.target.value})}
                      disabled={!editProfile}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      value={profileSettings.email}
                      onChange={(e) => setProfileSettings({...profileSettings, email: e.target.value})}
                      disabled={!editProfile}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Телефон"
                      value={profileSettings.phone}
                      onChange={(e) => setProfileSettings({...profileSettings, phone: e.target.value})}
                      disabled={!editProfile}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="Біографія"
                      value={profileSettings.bio}
                      onChange={(e) => setProfileSettings({...profileSettings, bio: e.target.value})}
                      disabled={!editProfile}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Годинна ставка ($)"
                      type="number"
                      value={profileSettings.hourly_rate}
                      onChange={(e) => setProfileSettings({...profileSettings, hourly_rate: Number(e.target.value)})}
                      disabled={!editProfile}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth disabled={!editProfile}>
                      <InputLabel>Часовий пояс</InputLabel>
                      <Select
                        value={profileSettings.timezone}
                        onChange={(e) => setProfileSettings({...profileSettings, timezone: e.target.value})}
                        label="Часовий пояс"
                      >
                        <MenuItem value="Europe/Kiev">Київ (UTC+3)</MenuItem>
                        <MenuItem value="Europe/London">Лондон (UTC+0)</MenuItem>
                        <MenuItem value="America/New_York">Нью-Йорк (UTC-5)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                <Box mt={3}>
                  <Typography variant="subtitle1" gutterBottom>
                    Навички
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {profileSettings.skills.map((skill, index) => (
                      <Chip
                        key={index}
                        label={skill}
                        onDelete={editProfile ? () => {
                          const newSkills = profileSettings.skills.filter((_, i) => i !== index);
                          setProfileSettings({...profileSettings, skills: newSkills});
                        } : undefined}
                      />
                    ))}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Швидкі дії
                </Typography>
                <List>
                  <ListItem button onClick={() => setShowPasswordDialog(true)}>
                    <ListItemIcon>
                      <Security />
                    </ListItemIcon>
                    <ListItemText primary="Змінити пароль" />
                  </ListItem>
                  <ListItem button onClick={exportData}>
                    <ListItemIcon>
                      <Download />
                    </ListItemIcon>
                    <ListItemText primary="Експорт даних" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Двофакторна автентифікація (MFA)
                </Typography>
                
                <Divider sx={{ mb: 2 }} />

                {mfaSettings && (
                  <Box>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={mfaSettings.mfa_enabled}
                          onChange={() => {
                            if (mfaSettings.mfa_enabled) {
                              disableMFA();
                            } else {
                              setShowMFASetup(true);
                            }
                          }}
                          disabled={loading}
                        />
                      }
                      label={mfaSettings.mfa_enabled ? 'MFA увімкнено' : 'MFA вимкнено'}
                    />

                    {mfaSettings.mfa_enabled && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Резервних кодів: {mfaSettings.backup_codes_count}
                        </Typography>
                        
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={regenerateBackupCodes}
                          disabled={loading}
                          sx={{ mt: 1 }}
                        >
                          Регенерувати резервні коди
                        </Button>
                      </Box>
                    )}

                    {!mfaSettings.mfa_setup && !mfaSettings.mfa_enabled && (
                      <Button
                        variant="contained"
                        onClick={() => setShowMFASetup(true)}
                        sx={{ mt: 1 }}
                      >
                        Налаштувати MFA
                      </Button>
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Управління сесіями
                </Typography>
                
                <Divider sx={{ mb: 2 }} />

                <SessionManager />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Налаштування сповіщень
            </Typography>
            
            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.email_notifications}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        email_notifications: e.target.checked
                      })}
                    />
                  }
                  label="Email сповіщення"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.push_notifications}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        push_notifications: e.target.checked
                      })}
                    />
                  }
                  label="Push сповіщення"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.proposal_alerts}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        proposal_alerts: e.target.checked
                      })}
                    />
                  }
                  label="Сповіщення про пропозиції"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.job_matches}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        job_matches: e.target.checked
                      })}
                    />
                  }
                  label="Сповіщення про вакансії"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.payment_notifications}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        payment_notifications: e.target.checked
                      })}
                    />
                  }
                  label="Сповіщення про платежі"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.marketing_emails}
                      onChange={(e) => setNotificationSettings({
                        ...notificationSettings,
                        marketing_emails: e.target.checked
                      })}
                    />
                  }
                  label="Маркетингові email"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Тема інтерфейсу
                </Typography>
                
                <Divider sx={{ mb: 2 }} />

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Режим теми</InputLabel>
                  <Select
                    value={themeSettings.mode}
                    onChange={(e) => setThemeSettings({
                      ...themeSettings,
                      mode: e.target.value as 'light' | 'dark' | 'auto'
                    })}
                    label="Режим теми"
                  >
                    <MenuItem value="light">
                      <Box display="flex" alignItems="center">
                        <LightMode sx={{ mr: 1 }} />
                        Світла
                      </Box>
                    </MenuItem>
                    <MenuItem value="dark">
                      <Box display="flex" alignItems="center">
                        <DarkMode sx={{ mr: 1 }} />
                        Темна
                      </Box>
                    </MenuItem>
                    <MenuItem value="auto">Автоматично</MenuItem>
                  </Select>
                </FormControl>

                <FormControlLabel
                  control={
                    <Switch
                      checked={themeSettings.compact_mode}
                      onChange={(e) => setThemeSettings({
                        ...themeSettings,
                        compact_mode: e.target.checked
                      })}
                    />
                  }
                  label="Компактний режим"
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Кольорова схема
                </Typography>
                
                <Divider sx={{ mb: 2 }} />

                <Box display="flex" flexWrap="wrap" gap={1}>
                  {['#1976d2', '#dc004e', '#388e3c', '#f57c00', '#7b1fa2'].map((color) => (
                    <Tooltip key={color} title={color}>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          borderRadius: '50%',
                          backgroundColor: color,
                          cursor: 'pointer',
                          border: themeSettings.primary_color === color ? '3px solid #000' : 'none',
                        }}
                        onClick={() => setThemeSettings({
                          ...themeSettings,
                          primary_color: color
                        })}
                      />
                    </Tooltip>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 4 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Експорт та імпорт даних
            </Typography>
            
            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Експорт налаштувань
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Завантажте всі ваші налаштування у форматі JSON для резервного копіювання.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Download />}
                  onClick={exportData}
                >
                  Експортувати налаштування
                </Button>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Видалення акаунту
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Увага! Ця дія незворотна. Всі ваші дані будуть видалені назавжди.
                </Typography>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => {
                    if (confirm('Ви впевнені, що хочете видалити свій акаунт? Ця дія незворотна.')) {
                      // Логіка видалення акаунту
                      alert('Функція видалення акаунту буде реалізована в наступних версіях.');
                    }
                  }}
                >
                  Видалити акаунт
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Діалог зміни паролю */}
      <Dialog open={showPasswordDialog} onClose={() => setShowPasswordDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Зміна паролю</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type={passwordData.show_passwords ? 'text' : 'password'}
                label="Поточний пароль"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type={passwordData.show_passwords ? 'text' : 'password'}
                label="Новий пароль"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type={passwordData.show_passwords ? 'text' : 'password'}
                label="Підтвердження нового паролю"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={passwordData.show_passwords}
                    onChange={(e) => setPasswordData({...passwordData, show_passwords: e.target.checked})}
                  />
                }
                label="Показати паролі"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPasswordDialog(false)}>
            Скасувати
          </Button>
          <Button
            variant="contained"
            onClick={changePassword}
            disabled={loading || !passwordData.current_password || !passwordData.new_password || !passwordData.confirm_password}
          >
            Змінити пароль
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings; 