import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  EmojiEvents as TrophyIcon,
  Timer as TimerIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import { usersApi, analysisApi } from '../services/api';

function StatCard({ icon, title, value, subtitle, color = 'primary.main' }) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              backgroundColor: `${color}15`,
              color: color,
            }}
          >
            {icon}
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
            <Typography variant="h4" fontWeight={700}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

function SkillCard({ name, level, progress }) {
  const getColor = (level) => {
    if (level >= 80) return 'success';
    if (level >= 50) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" fontWeight={500}>
          {name}
        </Typography>
        <Chip
          label={`${level}%`}
          size="small"
          color={getColor(level)}
        />
      </Box>
      <LinearProgress
        variant="determinate"
        value={progress}
        color={getColor(level)}
        sx={{ height: 8, borderRadius: 4 }}
      />
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
      // Set mock data for demo
      setProgress({
        totalChats: 12,
        totalExercises: 8,
        practiceTime: 245,
        currentStreak: 5,
        skills: [
          { name: 'Активное слушание', level: 75, progress: 75 },
          { name: 'Эмпатия', level: 60, progress: 60 },
          { name: 'Разрешение конфликтов', level: 45, progress: 45 },
          { name: 'Публичные выступления', level: 30, progress: 30 },
          { name: 'Переговоры', level: 55, progress: 55 },
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
    <Box sx={{ height: '100%', overflow: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Ваш прогресс
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Отслеживайте развитие коммуникативных навыков
        </Typography>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<ChatIcon />}
            title="Диалогов"
            value={progress?.totalChats || 0}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<TrophyIcon />}
            title="Упражнений"
            value={progress?.totalExercises || 0}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<TimerIcon />}
            title="Время практики"
            value={`${progress?.practiceTime || 0}`}
            subtitle="минут"
            color="warning.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<TrendingUpIcon />}
            title="Серия дней"
            value={progress?.currentStreak || 0}
            subtitle="подряд"
            color="error.main"
          />
        </Grid>
      </Grid>

      <Grid container spacing={4}>
        {/* Skills */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Навыки
              </Typography>
              
              {progress?.skills?.map((skill, index) => (
                <SkillCard
                  key={index}
                  name={skill.name}
                  level={skill.level}
                  progress={skill.progress}
                />
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Рекомендации
              </Typography>
              
              {recommendations.length > 0 ? (
                recommendations.map((rec, index) => (
                  <Box
                    key={index}
                    sx={{
                      p: 2,
                      mb: 2,
                      borderRadius: 2,
                      backgroundColor: 'background.default',
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                      {rec.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {rec.description}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Box sx={{ py: 4, textAlign: 'center' }}>
                  <Typography color="text.secondary">
                    Продолжайте практиковаться, чтобы получить персональные рекомендации
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default ProgressPage;
