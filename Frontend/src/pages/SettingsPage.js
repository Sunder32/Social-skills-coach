import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Save as SaveIcon,
  RestartAlt as ResetIcon,
} from '@mui/icons-material';

function SettingsPage() {
  const [settings, setSettings] = useState({
    apiUrl: 'http://localhost:8000',
    theme: 'dark',
    language: 'ru',
    notifications: true,
    soundEffects: true,
    autoSave: true,
    fontSize: 'medium',
  });
  const [saved, setSaved] = useState(false);

  const handleChange = (field) => (event) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setSettings({ ...settings, [field]: value });
  };

  const handleSave = () => {
    localStorage.setItem('appSettings', JSON.stringify(settings));
    setSaved(true);
  };

  const handleReset = () => {
    setSettings({
      apiUrl: 'http://localhost:8000',
      theme: 'dark',
      language: 'ru',
      notifications: true,
      soundEffects: true,
      autoSave: true,
      fontSize: 'medium',
    });
  };

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Настройки
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Настройте приложение под себя
        </Typography>
      </Box>

      <Box sx={{ maxWidth: 800 }}>
        {/* Connection settings */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Подключение
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <TextField
              fullWidth
              label="URL сервера API"
              value={settings.apiUrl}
              onChange={handleChange('apiUrl')}
              helperText="Адрес Backend сервера"
              sx={{ mb: 2 }}
            />
          </CardContent>
        </Card>

        {/* Appearance */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Внешний вид
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Тема</InputLabel>
              <Select
                value={settings.theme}
                label="Тема"
                onChange={handleChange('theme')}
              >
                <MenuItem value="dark">Тёмная</MenuItem>
                <MenuItem value="light">Светлая</MenuItem>
                <MenuItem value="system">Системная</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Язык</InputLabel>
              <Select
                value={settings.language}
                label="Язык"
                onChange={handleChange('language')}
              >
                <MenuItem value="ru">Русский</MenuItem>
                <MenuItem value="en">English</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Размер шрифта</InputLabel>
              <Select
                value={settings.fontSize}
                label="Размер шрифта"
                onChange={handleChange('fontSize')}
              >
                <MenuItem value="small">Маленький</MenuItem>
                <MenuItem value="medium">Средний</MenuItem>
                <MenuItem value="large">Большой</MenuItem>
              </Select>
            </FormControl>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Уведомления
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications}
                  onChange={handleChange('notifications')}
                />
              }
              label="Уведомления"
              sx={{ mb: 2, display: 'block' }}
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={settings.soundEffects}
                  onChange={handleChange('soundEffects')}
                />
              }
              label="Звуковые эффекты"
              sx={{ display: 'block' }}
            />
          </CardContent>
        </Card>

        {/* Data */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Данные
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <FormControlLabel
              control={
                <Switch
                  checked={settings.autoSave}
                  onChange={handleChange('autoSave')}
                />
              }
              label="Автосохранение диалогов"
            />
          </CardContent>
        </Card>

        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
          >
            Сохранить
          </Button>
          <Button
            variant="outlined"
            startIcon={<ResetIcon />}
            onClick={handleReset}
          >
            Сбросить
          </Button>
        </Box>
      </Box>

      <Snackbar
        open={saved}
        autoHideDuration={3000}
        onClose={() => setSaved(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert severity="success" onClose={() => setSaved(false)}>
          Настройки сохранены
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default SettingsPage;
