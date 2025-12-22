import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  IconButton,
  Alert,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Psychology as BrainIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      setSuccess(true);
    } catch (err) {
      setError('Произошла ошибка. Попробуйте позже.');
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
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/auth')}
            sx={{
              mb: 3,
              textTransform: 'none',
              color: 'text.secondary',
            }}
          >
            Назад к входу
          </Button>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 4 }}>
            <BrainIcon sx={{ fontSize: 40, color: 'primary.main' }} />
            <Typography variant="h5" fontWeight={700} color="primary.main">
              SOCIAL COACH
            </Typography>
          </Box>

          <Typography variant="h4" fontWeight={700} gutterBottom>
            Forgot password?
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            {success
              ? 'Мы отправили инструкции по сбросу пароля на вашу почту.'
              : 'Введите ваш email, и мы отправим инструкции по восстановлению пароля.'}
          </Typography>

          {success ? (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }}>
                Письмо успешно отправлено! Проверьте свою почту.
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
                Вернуться к входу
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
                    Email
                  </Typography>
                  <TextField
                    fullWidth
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </Box>

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
                  {isLoading ? 'Отправка...' : 'Отправить инструкции'}
                </Button>
              </Box>
            </form>
          )}
        </Box>
      </Box>
    </Box>
  );
}

export default ForgotPasswordPage;
