import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Container,
  Tooltip,
} from '@mui/material';
import {
  Work as WorkIcon,
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  ExitToApp as LogoutIcon,
  Menu as MenuIcon,
  Description as DescriptionIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Помилка виходу:', error);
    }
    handleMenuClose();
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <AppBar position="static" elevation={1} sx={{ backgroundColor: '#1976d2' }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          {/* Логотип та назва */}
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <WorkIcon sx={{ mr: 1, fontSize: 28 }} />
            <Typography
              variant="h6"
              noWrap
              component={RouterLink}
              to="/dashboard"
              sx={{
                textDecoration: 'none',
                color: 'inherit',
                fontWeight: 700,
                letterSpacing: '.1rem',
              }}
            >
              Upwork AI Assistant
            </Typography>
          </Box>

          {/* Навігаційні кнопки */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 1 }}>
            <Button
              component={RouterLink}
              to="/dashboard"
              startIcon={<DashboardIcon />}
              sx={{
                color: 'white',
                backgroundColor: isActive('/dashboard') ? 'rgba(255,255,255,0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              Дашборд
            </Button>
            
            <Button
              component={RouterLink}
              to="/jobs"
              startIcon={<WorkIcon />}
              sx={{
                color: 'white',
                backgroundColor: isActive('/jobs') ? 'rgba(255,255,255,0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              Вакансії
            </Button>
            
            <Button
              component={RouterLink}
              to="/profile"
              startIcon={<PersonIcon />}
              sx={{
                color: 'white',
                backgroundColor: isActive('/profile') ? 'rgba(255,255,255,0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              Профіль
            </Button>
            
            <Button
              component={RouterLink}
              to="/proposal-creator"
              startIcon={<DescriptionIcon />}
              sx={{
                color: 'white',
                backgroundColor: isActive('/proposal-creator') ? 'rgba(255,255,255,0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              Пропозиції
            </Button>
            
            <Button
              component={RouterLink}
              to="/analytics"
              startIcon={<AnalyticsIcon />}
              sx={{
                color: 'white',
                backgroundColor: isActive('/analytics') ? 'rgba(255,255,255,0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              Аналітика
            </Button>
          </Box>

          {/* Профіль користувача */}
          {user && (
            <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
              <Tooltip title="Меню користувача">
                <IconButton
                  onClick={handleMenuOpen}
                  sx={{ color: 'white' }}
                >
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      bgcolor: 'rgba(255,255,255,0.2)',
                      fontSize: '0.875rem',
                    }}
                  >
                    {(user.first_name || user.email)?.charAt(0).toUpperCase()}
                  </Avatar>
                </IconButton>
              </Tooltip>
              
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                PaperProps={{
                  sx: {
                    mt: 1,
                    minWidth: 200,
                  },
                }}
              >
                <MenuItem
                  component={RouterLink}
                  to="/profile"
                  onClick={handleMenuClose}
                  sx={{ py: 1.5 }}
                >
                  <PersonIcon sx={{ mr: 2, fontSize: 20 }} />
                  Профіль
                </MenuItem>
                
                <MenuItem
                  component={RouterLink}
                  to="/settings"
                  onClick={handleMenuClose}
                  sx={{ py: 1.5 }}
                >
                  <SettingsIcon sx={{ mr: 2, fontSize: 20 }} />
                  Налаштування
                </MenuItem>
                
                <MenuItem
                  onClick={handleLogout}
                  sx={{ py: 1.5, color: 'error.main' }}
                >
                  <LogoutIcon sx={{ mr: 2, fontSize: 20 }} />
                  Вийти
                </MenuItem>
              </Menu>
            </Box>
          )}

          {/* Мобільне меню */}
          <Box sx={{ display: { xs: 'flex', md: 'none' }, ml: 1 }}>
            <Tooltip title="Меню">
              <IconButton
                onClick={handleMenuOpen}
                sx={{ color: 'white' }}
              >
                <MenuIcon />
              </IconButton>
            </Tooltip>
            
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              PaperProps={{
                sx: {
                  mt: 1,
                  minWidth: 200,
                },
              }}
            >
              <MenuItem
                component={RouterLink}
                to="/dashboard"
                onClick={handleMenuClose}
                sx={{ py: 1.5 }}
              >
                <DashboardIcon sx={{ mr: 2, fontSize: 20 }} />
                Дашборд
              </MenuItem>
              
              <MenuItem
                component={RouterLink}
                to="/jobs"
                onClick={handleMenuClose}
                sx={{ py: 1.5 }}
              >
                <WorkIcon sx={{ mr: 2, fontSize: 20 }} />
                Вакансії
              </MenuItem>
              
              <MenuItem
                component={RouterLink}
                to="/profile"
                onClick={handleMenuClose}
                sx={{ py: 1.5 }}
              >
                <PersonIcon sx={{ mr: 2, fontSize: 20 }} />
                Профіль
              </MenuItem>
              
              <MenuItem
                onClick={handleLogout}
                sx={{ py: 1.5, color: 'error.main' }}
              >
                <LogoutIcon sx={{ mr: 2, fontSize: 20 }} />
                Вийти
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header; 