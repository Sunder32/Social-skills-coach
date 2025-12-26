import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Tooltip,
  useTheme,
  Switch,
} from '@mui/material';
import {
  Chat as ChatIcon,
  MenuBook as LibraryIcon,
  FitnessCenter as ExercisesIcon,
  TrendingUp as ProgressIcon,
  Person as PersonIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Psychology as PsychologyIcon,
  Minimize as MinimizeIcon,
  CheckBoxOutlineBlank as MaximizeIcon,
  Close as CloseIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
} from '@mui/icons-material';
import ProfileDialog from './ProfileDialog';

const DRAWER_WIDTH = 260;
const DRAWER_COLLAPSED_WIDTH = 72;

const menuItems = [
  { path: '/chat', label: 'Диалоги', icon: <ChatIcon /> },
  { path: '/library', label: 'Библиотека', icon: <LibraryIcon /> },
  { path: '/exercises', label: 'Упражнения', icon: <ExercisesIcon /> },
  { path: '/progress', label: 'Прогресс', icon: <ProgressIcon /> },
];

function Layout({ children }) {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [profileDialogOpen, setProfileDialogOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem('darkMode') === 'true' || false
  );
  
  const [userName, setUserName] = useState(localStorage.getItem('userName') || 'Пользователь');
  const [userAvatar, setUserAvatar] = useState(localStorage.getItem('userAvatar') || '');

  useEffect(() => {
    const handleStorageChange = () => {
      setUserName(localStorage.getItem('userName') || 'Пользователь');
      setUserAvatar(localStorage.getItem('userAvatar') || '');
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', newMode);
    window.dispatchEvent(new CustomEvent('themeChange', { detail: newMode }));
  };

  const handleMinimize = () => {
    if (window.electronAPI) {
      window.electronAPI.minimize();
    }
  };

  const handleMaximize = () => {
    if (window.electronAPI) {
      window.electronAPI.maximize();
    }
  };

  const handleClose = () => {
    if (window.electronAPI) {
      window.electronAPI.close();
    }
  };

  return (
    <Box sx={{ display: 'flex', width: '100%', height: '100vh' }}>
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: 32,
          WebkitAppRegion: 'drag',
          backgroundColor: theme.palette.background.paper,
          borderBottom: `1px solid ${theme.palette.divider}`,
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          px: 1,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            gap: 0.5,
            WebkitAppRegion: 'no-drag',
          }}
        >
          <IconButton
            size="small"
            onClick={handleMinimize}
            sx={{
              width: 32,
              height: 24,
              borderRadius: 0,
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.05)',
              },
            }}
          >
            <MinimizeIcon sx={{ fontSize: 16 }} />
          </IconButton>
          <IconButton
            size="small"
            onClick={handleMaximize}
            sx={{
              width: 32,
              height: 24,
              borderRadius: 0,
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.05)',
              },
            }}
          >
            <MaximizeIcon sx={{ fontSize: 14 }} />
          </IconButton>
          <IconButton
            size="small"
            onClick={handleClose}
            sx={{
              width: 32,
              height: 24,
              borderRadius: 0,
              '&:hover': {
                backgroundColor: '#df2531',
                color: 'white',
              },
            }}
          >
            <CloseIcon sx={{ fontSize: 16 }} />
          </IconButton>
        </Box>
      </Box>
      
      <Drawer
        variant="permanent"
        sx={{
          width: drawerOpen ? DRAWER_WIDTH : DRAWER_COLLAPSED_WIDTH,
          flexShrink: 0,
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          '& .MuiDrawer-paper': {
            width: drawerOpen ? DRAWER_WIDTH : DRAWER_COLLAPSED_WIDTH,
            boxSizing: 'border-box',
            backgroundColor: theme.palette.background.paper,
            borderRight: `1px solid ${theme.palette.divider}`,
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
            overflowX: 'hidden',
            paddingTop: '32px',
          },
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: drawerOpen ? 'space-between' : 'center',
            p: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
          }}
        >
          {drawerOpen && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Box 
                sx={{ 
                  width: 24,
                  height: 24,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <Box
                  component="img"
                  src="./assets/cors.png"
                  alt="Logo"
                  sx={{
                    width: 52,
                    height: 52,
                    objectFit: 'contain',
                  }}
                />
              </Box>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  color: 'primary.main',
                  lineHeight: '24px',
                }}
              >
                SOCIAL COACH
              </Typography>
            </Box>
          )}
          <IconButton onClick={toggleDrawer} size="small">
            {drawerOpen ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
        </Box>

        <List sx={{ px: 1, py: 2, flex: 1 }}>
          {menuItems.map((item) => (
            <Tooltip
              key={item.path}
              title={!drawerOpen ? item.label : ''}
              placement="right"
            >
              <ListItemButton
                selected={location.pathname.startsWith(item.path)}
                onClick={() => navigate(item.path)}
                sx={{
                  minHeight: 48,
                  justifyContent: drawerOpen ? 'initial' : 'center',
                  mb: 0.5,
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: drawerOpen ? 2 : 'auto',
                    justifyContent: 'center',
                    color: location.pathname.startsWith(item.path)
                      ? 'primary.main'
                      : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {drawerOpen && (
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{
                      fontWeight: location.pathname.startsWith(item.path) ? 600 : 400,
                    }}
                  />
                )}
              </ListItemButton>
            </Tooltip>
          ))}
        </List>

        <List sx={{ px: 1, py: 1 }}>
          <Tooltip title={!drawerOpen ? 'Тема' : ''} placement="right">
            <ListItemButton
              onClick={toggleDarkMode}
              sx={{
                minHeight: 48,
                justifyContent: drawerOpen ? 'initial' : 'center',
                mb: 0.5,
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: drawerOpen ? 2 : 'auto',
                  justifyContent: 'center',
                  color: 'text.secondary',
                }}
              >
                {darkMode ? <DarkModeIcon /> : <LightModeIcon />}
              </ListItemIcon>
              {drawerOpen && (
                <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, justifyContent: 'space-between' }}>
                  <ListItemText primary="Тема" />
                  <Switch
                    checked={darkMode}
                    onChange={toggleDarkMode}
                    size="small"
                    sx={{
                      '& .MuiSwitch-switchBase.Mui-checked': {
                        color: 'primary.main',
                      },
                      '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                        backgroundColor: 'primary.main',
                      },
                    }}
                  />
                </Box>
              )}
            </ListItemButton>
          </Tooltip>
        </List>

        <Box
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: drawerOpen ? 'flex-start' : 'center',
            gap: 1.5,
            cursor: 'pointer',
            '&:hover': {
              backgroundColor: 'rgba(0,0,0,0.04)',
            },
          }}
          onClick={() => setProfileDialogOpen(true)}
        >
          <Avatar
            src={userAvatar}
            sx={{
              width: 36,
              height: 36,
              bgcolor: 'primary.main',
              fontSize: '0.9rem',
            }}
          >
            {!userAvatar && userName.charAt(0).toUpperCase()}
          </Avatar>
          {drawerOpen && (
            <Box sx={{ overflow: 'hidden' }}>
              <Typography variant="body2" fontWeight={500} noWrap>
                {userName}
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap>
                Уровень: Начинающий
              </Typography>
            </Box>
          )}
        </Box>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: '100vh',
          overflow: 'hidden',
          backgroundColor: theme.palette.background.default,
          paddingTop: '32px',
        }}
      >
        {children}
      </Box>

      <ProfileDialog
        open={profileDialogOpen}
        onClose={() => setProfileDialogOpen(false)}
      />
    </Box>
  );
}

export default Layout;
