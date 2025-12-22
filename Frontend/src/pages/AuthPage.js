import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  IconButton,
  InputAdornment,
  Alert,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Psychology as BrainIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { usersApi } from '../services/api';

function AuthPage() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });

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
        localStorage.setItem('token', response.data.token);
        navigate('/chat');
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError('Пароли не совпадают');
          setIsLoading(false);
          return;
        }
        const response = await usersApi.register({
          email: formData.email,
          password: formData.password,
          name: formData.name,
        });
        localStorage.setItem('token', response.data.token);
        navigate('/chat');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка');
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
            {isLogin ? 'Log in' : 'Sign up'}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            {isLogin
              ? 'Welcome back! Please enter your details.'
              : 'Create your account to get started.'}
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
                    Name
                  </Typography>
                  <TextField
                    fullWidth
                    placeholder="Enter your name"
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
                  placeholder="Enter your email"
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
                    Confirm Password
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
                    Forgot password
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
                {isLogin ? 'Sign in' : 'Sign up'}
              </Button>

              <Typography
                variant="body2"
                textAlign="center"
                color="text.secondary"
                sx={{ mt: 1 }}
              >
                {isLogin ? "Don't have an account?" : 'Already have an account?'}{' '}
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
                  {isLogin ? 'Sign up' : 'Log in'}
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
                Skip Auth (Dev Mode)
              </Button>
            </Box>
          </form>
        </Box>
      </Box>
    </Box>
  );
}

export default AuthPage;
