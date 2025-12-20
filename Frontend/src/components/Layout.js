import React, { useState } from 'react';
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
} from '@mui/material';
import {
  Chat as ChatIcon,
  MenuBook as LibraryIcon,
  FitnessCenter as ExercisesIcon,
  TrendingUp as ProgressIcon,
  Settings as SettingsIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';

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

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (
    <Box sx={{ display: 'flex', width: '100%' }}>
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
          },
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: drawerOpen ? 'space-between' : 'center',
            p: 2,
            minHeight: 64,
          }}
        >
          {drawerOpen && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <PsychologyIcon sx={{ color: 'primary.main', fontSize: 32 }} />
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  color: 'primary.main',
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

        <Divider sx={{ opacity: 0.5 }} />

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

        <Divider sx={{ opacity: 0.5 }} />

        <List sx={{ px: 1, py: 1 }}>
          <Tooltip title={!drawerOpen ? 'Настройки' : ''} placement="right">
            <ListItemButton
              selected={location.pathname === '/settings'}
              onClick={() => navigate('/settings')}
              sx={{
                minHeight: 48,
                justifyContent: drawerOpen ? 'initial' : 'center',
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: drawerOpen ? 2 : 'auto',
                  justifyContent: 'center',
                }}
              >
                <SettingsIcon />
              </ListItemIcon>
              {drawerOpen && <ListItemText primary="Настройки" />}
            </ListItemButton>
          </Tooltip>
        </List>

        {drawerOpen && (
          <Box
            sx={{
              p: 2,
              borderTop: `1px solid ${theme.palette.divider}`,
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
            }}
          >
            <Avatar
              sx={{
                width: 36,
                height: 36,
                bgcolor: 'primary.main',
                fontSize: '0.9rem',
              }}
            >
              U
            </Avatar>
            <Box sx={{ overflow: 'hidden' }}>
              <Typography variant="body2" fontWeight={500} noWrap>
                Пользователь
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap>
                Уровень: Начинающий
              </Typography>
            </Box>
          </Box>
        )}
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: '100vh',
          overflow: 'hidden',
          backgroundColor: theme.palette.background.default,
        }}
      >
        {children}
      </Box>
    </Box>
  );
}

export default Layout;
