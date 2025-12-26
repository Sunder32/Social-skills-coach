import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  IconButton,
  InputAdornment,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Psychology as BrainIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { usersApi } from '../services/api';

function AuthPage() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showVerification, setShowVerification] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');
  const [registeredEmail, setRegisteredEmail] = useState('');
  const [savedPassword, setSavedPassword] = useState('');
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem('darkMode') === 'true' || false
  );
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });

  const handleToggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', newMode.toString());
    window.location.reload();
  };

  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (isLogin) {
        const response = await usersApi.login({
          email: formData.email,
          password: formData.password,
        });
        localStorage.setItem('token', response.data.access_token);
        window.location.hash = '#/chat';
        window.location.reload();
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError('Пароли не совпадают');
          setIsLoading(false);
          return;
        }
        await usersApi.register({
          email: formData.email,
          password: formData.password,
          name: formData.name,
        });
        setRegisteredEmail(formData.email);
        setSavedPassword(formData.password);
        setShowVerification(true);
        setError('');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Произошла ошибка';
      if (errorMessage.includes('Email не подтверждён') || errorMessage.includes('not verified')) {
        setRegisteredEmail(formData.email);
        setSavedPassword(formData.password);
        setShowVerification(true);
        setError('Email не подтверждён. Проверьте почту и введите код подтверждения.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerification = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await usersApi.verifyEmail({
        email: registeredEmail,
        code: verificationCode,
      });
      
      const loginResponse = await usersApi.login({
        email: registeredEmail,
        password: savedPassword,
      });
      localStorage.setItem('token', loginResponse.data.access_token);
      window.location.hash = '#/chat';
      window.location.reload();
    } catch (err) {
      setError(err.response?.data?.detail || 'Неверный код подтверждения');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setIsLoading(true);
    try {
      await usersApi.resendVerification({ email: registeredEmail });
      setError('');
      alert('Новый код отправлен на вашу почту');
    } catch (err) {
      setError('Ошибка при отправке кода');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSkipAuth = () => {
    localStorage.setItem('token', 'dev-token');
    navigate('/chat');
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setShowVerification(false);
    setVerificationCode('');
    setSavedPassword('');
    setFormData({
      email: '',
      password: '',
      confirmPassword: '',
      name: '',
    });
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

          {showVerification ? (
            <>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                Подтверждение Email
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                Мы отправили 6-значный код на <strong>{registeredEmail}</strong>. 
                Проверьте свою почту и введите код подтверждения.
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              <form onSubmit={handleVerification}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                  <Box>
                    <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
                      Код подтверждения
                    </Typography>
                    <TextField
                      fullWidth
                      placeholder="Введите 6-значный код"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      required
                      inputProps={{ maxLength: 6 }}
                      sx={{
                        '& input': {
                          fontSize: '1.5rem',
                          letterSpacing: '0.5rem',
                          textAlign: 'center',
                        },
                      }}
                    />
                  </Box>

                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    fullWidth
                    disabled={isLoading || verificationCode.length !== 6}
                    sx={{
                      py: 1.5,
                      fontSize: '1rem',
                      fontWeight: 600,
                      textTransform: 'none',
                      mt: 1,
                    }}
                  >
                    Подтвердить
                  </Button>

                  <Button
                    variant="text"
                    onClick={handleResendCode}
                    disabled={isLoading}
                    sx={{
                      textTransform: 'none',
                      fontWeight: 500,
                    }}
                  >
                    Отправить код повторно
                  </Button>

                  <Button
                    variant="text"
                    onClick={() => {
                      setShowVerification(false);
                      setVerificationCode('');
                      setError('');
                    }}
                    sx={{
                      textTransform: 'none',
                      fontSize: '0.875rem',
                      color: 'text.secondary',
                    }}
                  >
                    Вернуться к регистрации
                  </Button>
                </Box>
              </form>
            </>
          ) : (
            <>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                {isLogin ? 'Log in' : 'Sign up'}
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                {isLogin
                  ? 'С возвращением! Пожалуйста, введите ваши данные.'
                  : 'Создайте аккаунт, чтобы начать.'}
              </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
              {!isLogin && (
                <Box>
                  <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
                    Имя
                  </Typography>
                  <TextField
                    fullWidth
                    placeholder="Введите ваше имя"
                    value={formData.name}
                    onChange={handleChange('name')}
                    required={!isLogin}
                  />
                </Box>
              )}

              <Box>
                <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
                  Email
                </Typography>
                <TextField
                  fullWidth
                  type="email"
                  placeholder="Введите ваш email"
                  value={formData.email}
                  onChange={handleChange('email')}
                  required
                />
              </Box>

              <Box>
                <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
                  Password
                </Typography>
                <TextField
                  fullWidth
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange('password')}
                  required
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

              {!isLogin && (
                <Box>
                  <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
                    Подтвердите пароль
                  </Typography>
                  <TextField
                    fullWidth
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={handleChange('confirmPassword')}
                    required={!isLogin}
                  />
                </Box>
              )}

              {isLogin && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="text"
                    onClick={() => navigate('/forgot-password')}
                    sx={{ textTransform: 'none', fontWeight: 500, color: 'primary.main' }}
                  >
                    Забыли пароль?
                  </Button>
                </Box>
              )}

              <Button
                type="submit"
                variant="contained"
                size="large"
                fullWidth
                disabled={isLoading}
                sx={{
                  py: 1.5,
                  fontSize: '1rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  mt: 1,
                }}
              >
                {isLogin ? 'Войти' : 'Зарегистрироваться'}
              </Button>

              <Typography
                variant="body2"
                textAlign="center"
                color="text.secondary"
                sx={{ mt: 1 }}
              >
                {isLogin ? "Нет аккаунта?" : 'Уже есть аккаунт?'}{' '}
                <Button
                  variant="text"
                  onClick={toggleMode}
                  sx={{
                    textTransform: 'none',
                    fontWeight: 600,
                    p: 0,
                    minWidth: 'auto',
                    '&:hover': {
                      backgroundColor: 'transparent',
                      textDecoration: 'underline',
                    },
                  }}
                >
                  {isLogin ? 'Зарегистрироваться' : 'Войти'}
                </Button>
              </Typography>

              <Button
                variant="text"
                onClick={handleSkipAuth}
                sx={{
                  textTransform: 'none',
                  fontSize: '0.75rem',
                  color: 'text.disabled',
                  mt: 2,
                }}
              >
                Пропустить авторизацию (Режим разработки)
              </Button>
            </Box>
          </form>
          </>
          )}
        </Box>
      </Box>
    </Box>
  );
}

export default AuthPage;
