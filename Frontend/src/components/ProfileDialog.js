import React, { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  Box,
  Typography,
  TextField,
  Button,
  Avatar,
  IconButton,
  Divider,
  Grid,
  Slide,
} from '@mui/material';
import {
  PhotoCamera as PhotoCameraIcon,
  Close as CloseIcon,
  Save as SaveIcon,
} from '@mui/icons-material';

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

function ProfileDialog({ open, onClose }) {
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    bio: '',
    avatar: '',
  });
  
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (open) {
      setProfile({
        name: localStorage.getItem('userName') || 'Пользователь',
        email: localStorage.getItem('userEmail') || 'user@example.com',
        bio: localStorage.getItem('userBio') || '',
        avatar: localStorage.getItem('userAvatar') || '',
      });
    }
  }, [open]);

  const handleChange = (field) => (event) => {
    setProfile({ ...profile, [field]: event.target.value });
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        alert('Размер файла не должен превышать 5 МБ');
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        setProfile({ ...profile, avatar: reader.result });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSave = () => {
    localStorage.setItem('userName', profile.name);
    localStorage.setItem('userEmail', profile.email);
    localStorage.setItem('userBio', profile.bio);
    localStorage.setItem('userAvatar', profile.avatar);
    
    window.dispatchEvent(new Event('storage'));
    
    onClose();
  };

  const handleRemoveAvatar = () => {
    setProfile({ ...profile, avatar: '' });
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      TransitionComponent={Transition}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          minHeight: '60vh',
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          p: 2.5,
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Typography variant="h6" fontWeight={600}>
          Профиль пользователя
        </Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      <DialogContent sx={{ p: 3 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box sx={{ position: 'relative', display: 'inline-block' }}>
            <Avatar
              src={profile.avatar}
              sx={{
                width: 120,
                height: 120,
                fontSize: '3rem',
                bgcolor: 'primary.main',
                margin: '0 auto',
              }}
            >
              {!profile.avatar && profile.name.charAt(0).toUpperCase()}
            </Avatar>
            <IconButton
              onClick={handleAvatarClick}
              sx={{
                position: 'absolute',
                bottom: 0,
                right: 0,
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
              }}
              size="small"
            >
              <PhotoCameraIcon fontSize="small" />
            </IconButton>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              hidden
              onChange={handleAvatarChange}
            />
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2, mb: 1 }}>
            Рекомендуемый размер: 400x400px
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<PhotoCameraIcon />}
              onClick={handleAvatarClick}
            >
              Изменить фото
            </Button>
            {profile.avatar && (
              <Button
                variant="outlined"
                size="small"
                color="error"
                onClick={handleRemoveAvatar}
              >
                Удалить
              </Button>
            )}
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Личная информация
          </Typography>
          
          <Grid container spacing={2.5} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
                Имя
              </Typography>
              <TextField
                fullWidth
                value={profile.name}
                onChange={handleChange('name')}
                placeholder="Введите ваше имя"
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
                О себе
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                value={profile.bio}
                onChange={handleChange('bio')}
                placeholder="Расскажите немного о себе..."
              />
            </Grid>
          </Grid>
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Box>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Статистика
          </Typography>
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="primary.main">
                  0
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Диалогов
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="primary.main">
                  0
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Упражнений
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="primary.main">
                  0
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Дней
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>

      <Box
        sx={{
          p: 2.5,
          borderTop: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: 2,
        }}
      >
        <Button variant="outlined" onClick={onClose}>
          Отмена
        </Button>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSave}
        >
          Сохранить
        </Button>
      </Box>
    </Dialog>
  );
}

export default ProfileDialog;
