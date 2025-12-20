import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  LocalFireDepartment as FireIcon,
  FitnessCenter as ExerciseIcon,
  Schedule as TimeIcon,
  Star as StarIcon,
  Lightbulb as LightbulbIcon,
} from '@mui/icons-material';
import { usersApi, analysisApi } from '../services/api';

function StatCard({ icon, title, value, color = 'primary.main' }) {
  return (
    <Card
      sx={{
        border: '2px solid',
        borderColor: 'primary.main',
        borderRadius: 3,
        boxShadow: 'none',
        textAlign: 'center',
      }}
    >
      <CardContent sx={{ py: 3 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            mb: 1,
            color: 'primary.main',
          }}
        >
          {icon}
        </Box>
        <Typography variant="h3" fontWeight={700} sx={{ mb: 0.5 }}>
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );
}

function SkillBar({ name, level }) {
  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" fontWeight={500} color="text.primary">
          {name}
        </Typography>
        <Typography variant="body2" fontWeight={600} color="text.primary">
          {level}%
        </Typography>
      </Box>
      <Box sx={{ position: 'relative', height: 12, borderRadius: 2, backgroundColor: 'rgba(223, 37, 49, 0.1)' }}>
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            height: '100%',
            width: `${level}%`,
            backgroundColor: 'primary.main',
            borderRadius: 2,
            transition: 'width 0.5s ease-in-out',
          }}
        />
      </Box>
    </Box>
  );
}

function ProgressPage() {
  const [progress, setProgress] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [progressRes, recsRes] = await Promise.all([
        usersApi.getProgress(),
        analysisApi.getRecommendations(),
      ]);
      setProgress(progressRes.data);
      setRecommendations(recsRes.data || []);
    } catch (error) {
      console.error('Error loading progress:', error);
      setProgress({
        daysActive: 24,
        exercisesCompleted: 47,
        hoursLearning: 18,
        averageResult: 92,
        skills: [
          { name: 'Активное слушание', level: 85 },
          { name: 'Эмпатия', level: 72 },
          { name: 'Убеждение', level: 68 },
          { name: 'Управление конфликтами', level: 79 },
          { name: 'Невербальная коммуникация', level: 91 },
          { name: 'Уверенность в общении', level: 78 },
        ],
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 4, backgroundColor: 'background.default' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Ваш прогресс
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Отслеживайте развитие коммуникативных навыков
          </Typography>
        </Box>
        <Button
          variant="outlined"
          color="primary"
          sx={{
            borderRadius: 2,
            textTransform: 'none',
            fontWeight: 600,
            borderWidth: 2,
            '&:hover': { borderWidth: 2 },
          }}
        >
          Посмотреть рекомендации
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<FireIcon sx={{ fontSize: 32 }} />}
            title="Дней активности"
            value={progress?.daysActive || 24}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<ExerciseIcon sx={{ fontSize: 32 }} />}
            title="Упражнений завершено"
            value={progress?.exercisesCompleted || 47}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<TimeIcon sx={{ fontSize: 32 }} />}
            title="Часов обучения"
            value={progress?.hoursLearning || 18}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<StarIcon sx={{ fontSize: 32 }} />}
            title="Средний результат"
            value={`${progress?.averageResult || 92}%`}
          />
        </Grid>
      </Grid>

      <Card sx={{ borderRadius: 3, boxShadow: 'none' }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" fontWeight={600}>
              Навыки
            </Typography>
            <Button
              variant="text"
              color="primary"
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              Улучшить навыки
            </Button>
          </Box>
          
          {progress?.skills?.map((skill, index) => (
            <SkillBar
              key={index}
              name={skill.name}
              level={skill.level}
            />
          ))}
        </CardContent>
      </Card>

      <Box
        sx={{
          mt: 4,
          p: 4,
          backgroundColor: 'rgba(223, 37, 49, 0.05)',
          borderRadius: 3,
          textAlign: 'center',
        }}
      >
        <Box
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 48,
            height: 48,
            borderRadius: '50%',
            backgroundColor: 'primary.main',
            mb: 2,
          }}
        >
          <LightbulbIcon sx={{ color: 'white', fontSize: 24 }} />
        </Box>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Персональные рекомендации
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 500, mx: 'auto' }}>
          Получите индивидуальные советы по развитию коммуникативных навыков на основе вашего прогресса и активности
        </Typography>
        <Button
          variant="contained"
          color="primary"
          size="large"
          sx={{
            borderRadius: 2,
            textTransform: 'none',
            fontWeight: 600,
            px: 4,
          }}
        >
          Получить рекомендации
        </Button>
      </Box>
    </Box>
  );
}

export default ProgressPage;
