import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  IconButton,
  Alert,
  InputAdornment,
  Tooltip,
} from '@mui/material';
import {
  Psychology as BrainIcon,
  Visibility,
  VisibilityOff,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { usersApi } from '../services/api';

function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem('darkMode') === 'true' || false
  );

  useEffect(() => {
    if (!token) {
      setError('Недействительная или отсутствующая ссылка для сброса пароля.');
    }
  }, [token]);

  const handleToggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', newMode.toString());
    window.location.reload();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if (password.length < 8) {
      setError('Пароль должен содержать минимум 8 символов');
      return;
    }

    setIsLoading(true);

    try {
      await usersApi.resetPassword({ 
        token: token,
        new_password: password 
      });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка. Возможно, ссылка устарела.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        minHeight: '100vh',
        width: '100%',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: 32,
          WebkitAppRegion: 'drag',
          backgroundColor: 'background.default',
          borderBottom: '1px solid',
          borderColor: 'divider',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 1,
        }}
      >
        <Box sx={{ WebkitAppRegion: 'no-drag' }}>
          <Tooltip title={darkMode ? 'Светлая тема' : 'Тёмная тема'}>
            <IconButton
              size="small"
              onClick={handleToggleDarkMode}
              sx={{
                width: 32,
                height: 24,
                borderRadius: 0,
              }}
            >
              {darkMode ? <LightModeIcon fontSize="small" /> : <DarkModeIcon fontSize="small" />}
            </IconButton>
          </Tooltip>
        </Box>
        <Box
          sx={{
            display: 'flex',
            gap: 0.5,
            WebkitAppRegion: 'no-drag',
          }}
        >
          <IconButton
            size="small"
            onClick={() => window.electronAPI?.minimize()}
            sx={{
              width: 32,
              height: 24,
              borderRadius: 0,
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.05)',
              },
            }}
          >
            <Box sx={{ fontSize: 16 }}>−</Box>
          </IconButton>
          <IconButton
            size="small"
            onClick={() => window.electronAPI?.maximize()}
            sx={{
              width: 32,
              height: 24,
              borderRadius: 0,
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.05)',
              },
            }}
          >
            <Box sx={{ fontSize: 14 }}>□</Box>
          </IconButton>
          <IconButton
            size="small"
            onClick={() => window.electronAPI?.close()}
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
            <Box sx={{ fontSize: 16 }}>×</Box>
          </IconButton>
        </Box>
      </Box>

      <Box
        sx={{
          display: 'flex',
          width: '100%',
          height: '100vh',
          paddingTop: '32px',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: 'background.default',
        }}
      >
        <Box sx={{ width: '100%', maxWidth: 440 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 4 }}>
            <BrainIcon sx={{ fontSize: 40, color: 'primary.main' }} />
            <Typography variant="h5" fontWeight={700} color="primary.main">
              SOCIAL COACH
            </Typography>
          </Box>

          <Typography variant="h4" fontWeight={700} gutterBottom>
            Новый пароль
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            {success
              ? 'Ваш пароль успешно изменён!'
              : 'Введите новый пароль для вашего аккаунта.'}
          </Typography>

          {success ? (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }}>
                Пароль успешно изменён! Теперь вы можете войти с новым паролем.
              </Alert>
              <Button
                variant="contained"
                fullWidth
                onClick={() => navigate('/auth')}
                sx={{
                  py: 1.5,
                  fontSize: '1rem',
                  fontWeight: 600,
                  textTransform: 'none',
                }}
              >
                Перейти к входу
              </Button>
            </Box>
          ) : (
            <form onSubmit={handleSubmit}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                {error && (
                  <Alert severity="error" sx={{ mb: 1 }}>
                    {error}
                  </Alert>
                )}

                <Box>
                  <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
                    Новый пароль
                  </Typography>
                  <TextField
                    fullWidth
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Минимум 8 символов"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    disabled={!token}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                </Box>

                <Box>
                  <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
                    Подтвердите пароль
                  </Typography>
                  <TextField
                    fullWidth
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Повторите пароль"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    disabled={!token}
                  />
                </Box>

                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={isLoading || !token}
                  sx={{
                    py: 1.5,
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    mt: 1,
                  }}
                >
                  {isLoading ? 'Сохранение...' : 'Сохранить пароль'}
                </Button>

                <Button
                  variant="text"
                  onClick={() => navigate('/auth')}
                  sx={{
                    textTransform: 'none',
                    color: 'text.secondary',
                  }}
                >
                  Вернуться к входу
                </Button>
              </Box>
            </form>
          )}
        </Box>
      </Box>
    </Box>
  );
}

export default ResetPasswordPage;
