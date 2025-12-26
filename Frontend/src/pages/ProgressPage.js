import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  EmojiEvents as TrophyIcon,
  Timer as TimerIcon,
  CheckCircle as CheckIcon,
  Star as StarIcon,
  Lightbulb as TipIcon,
  School as LearnIcon,
  FitnessCenter as ExerciseIcon,
  ArrowForward as ArrowIcon,
  Visibility as ViewIcon,
  AutoAwesome as GenerateIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

// Карточка статистики
function StatCard({ icon, value, label, color = 'primary.main' }) {
  return (
    <Card>
      <CardContent sx={{ textAlign: 'center', py: 3 }}>
        <Box sx={{ color, mb: 1 }}>
          {icon}
        </Box>
        <Typography variant="h3" fontWeight={700}>
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
      </CardContent>
    </Card>
  );
}

// Полоса навыка
function SkillBar({ name, level, color }) {
  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="body2" fontWeight={500}>{name}</Typography>
        <Typography variant="body2" color="text.secondary">{level}%</Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={level}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: 'action.hover',
          '& .MuiLinearProgress-bar': {
            backgroundColor: color,
            borderRadius: 4,
          },
        }}
      />
    </Box>
  );
}

// Рекомендации по умолчанию
const DEFAULT_RECOMMENDATIONS = [
  {
    type: 'exercise',
    title: 'Практика активного слушания',
    description: 'Пройдите упражнение "Активное слушание" для улучшения навыков эмпатии',
    action: 'exercises',
    priority: 'high'
  },
  {
    type: 'lesson',
    title: 'Изучите технику "Я-сообщения"',
    description: 'Эта техника поможет вам выражать недовольство без обвинений',
    action: 'library',
    priority: 'medium'
  },
  {
    type: 'practice',
    title: 'Попрактикуйтесь в комплиментах',
    description: 'Давайте искренние конкретные комплименты 3 людям сегодня',
    action: 'exercises',
    priority: 'low'
  }
];

// Названия навыков
const SKILL_NAMES = {
  communication: 'Общение',
  conflict: 'Разрешение конфликтов',
  public_speaking: 'Публичные выступления',
  boundaries: 'Личные границы',
  empathy: 'Эмпатия',
  networking: 'Нетворкинг',
  active_listening: 'Активное слушание',
  feedback: 'Обратная связь',
  negotiation: 'Переговоры'
};

// Цвета навыков
const SKILL_COLORS = {
  communication: '#4caf50',
  conflict: '#ff9800',
  public_speaking: '#9c27b0',
  boundaries: '#2196f3',
  empathy: '#e91e63',
  networking: '#00bcd4',
  active_listening: '#8bc34a',
  feedback: '#ff5722',
  negotiation: '#673ab7'
};

function ProgressPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [skills, setSkills] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [generatingRecs, setGeneratingRecs] = useState(false);
  
  // Загрузка данных из localStorage
  useEffect(() => {
    calculateProgress();
  }, []);

  const calculateProgress = () => {
    setLoading(true);
    
    try {
      // Получаем данные из localStorage
      const completedExercises = JSON.parse(localStorage.getItem('completedExercises') || '{}');
      const exerciseResults = JSON.parse(localStorage.getItem('exerciseResults') || '{}');
      const chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');
      const firstVisit = localStorage.getItem('firstVisitDate');
      
      // Устанавливаем дату первого визита, если ещё нет
      if (!firstVisit) {
        localStorage.setItem('firstVisitDate', new Date().toISOString());
      }

      // Подсчёт статистики
      const exercisesCompleted = Object.keys(completedExercises).length;
      
      // Дни активности
      const startDate = firstVisit ? new Date(firstVisit) : new Date();
      const today = new Date();
      const daysActive = Math.max(1, Math.ceil((today - startDate) / (1000 * 60 * 60 * 24)));
      
      // Время обучения (примерно 5 минут на упражнение)
      const totalMinutes = exercisesCompleted * 5 + chatHistory.length * 2;
      const hoursLearning = Math.round(totalMinutes / 60 * 10) / 10;
      
      // Средний результат
      let totalScore = 0;
      let scoreCount = 0;
      Object.values(completedExercises).forEach(ex => {
        if (ex.score) {
          totalScore += ex.score;
          scoreCount++;
        }
      });
      const averageResult = scoreCount > 0 ? Math.round(totalScore / scoreCount) : 0;

      setStats({
        daysActive,
        exercisesCompleted,
        hoursLearning,
        averageResult
      });

      // Расчёт навыков по категориям упражнений
      const skillScores = {};
      Object.entries(completedExercises).forEach(([id, data]) => {
        // Определяем категорию по id упражнения (примерно)
        let category = 'communication';
        if (id === '1') category = 'communication';
        if (id === '2') category = 'conflict';
        if (id === '3') category = 'public_speaking';
        if (id === '4') category = 'boundaries';
        if (id === '5') category = 'empathy';
        if (id === '6') category = 'communication';

        if (!skillScores[category]) {
          skillScores[category] = { total: 0, count: 0 };
        }
        skillScores[category].total += data.score || 0;
        skillScores[category].count += 1;
      });

      // Преобразуем в массив для отображения
      const calculatedSkills = Object.entries(skillScores).map(([key, value]) => ({
        name: SKILL_NAMES[key] || key,
        level: Math.round(value.total / value.count),
        color: SKILL_COLORS[key] || '#4caf50'
      }));

      // Добавляем базовые навыки с нулевым прогрессом, если нет данных
      if (calculatedSkills.length === 0) {
        setSkills([
          { name: 'Общение', level: 0, color: '#4caf50' },
          { name: 'Эмпатия', level: 0, color: '#e91e63' },
          { name: 'Разрешение конфликтов', level: 0, color: '#ff9800' },
          { name: 'Публичные выступления', level: 0, color: '#9c27b0' },
          { name: 'Личные границы', level: 0, color: '#2196f3' },
        ]);
      } else {
        setSkills(calculatedSkills.sort((a, b) => b.level - a.level));
      }

      // Генерация рекомендаций на основе данных
      generateRecommendations(skillScores, exercisesCompleted);

    } catch (error) {
      console.error('Error calculating progress:', error);
      // Fallback на нулевые значения
      setStats({
        daysActive: 1,
        exercisesCompleted: 0,
        hoursLearning: 0,
        averageResult: 0
      });
      setSkills([
        { name: 'Общение', level: 0, color: '#4caf50' },
        { name: 'Эмпатия', level: 0, color: '#e91e63' },
        { name: 'Разрешение конфликтов', level: 0, color: '#ff9800' },
      ]);
      setRecommendations(DEFAULT_RECOMMENDATIONS);
    }
    
    setLoading(false);
  };

  const generateRecommendations = (skillScores, exercisesCompleted) => {
    const recs = [];
    
    // Если ещё не прошёл ни одного упражнения
    if (exercisesCompleted === 0) {
      recs.push({
        type: 'exercise',
        title: 'Начните с простого упражнения',
        description: 'Рекомендуем начать с упражнения "Просьба о помощи" — оно лёгкое и полезное',
        action: 'exercises',
        priority: 'high'
      });
      recs.push({
        type: 'lesson',
        title: 'Изучите основы',
        description: 'Познакомьтесь с библиотекой техник общения',
        action: 'library',
        priority: 'medium'
      });
    } else {
      // Находим слабые навыки
      const weakSkills = Object.entries(skillScores)
        .filter(([_, v]) => v.total / v.count < 70)
        .map(([key]) => key);

      // Находим непройденные категории
      const allCategories = ['communication', 'conflict', 'public_speaking', 'boundaries', 'empathy'];
      const uncovered = allCategories.filter(cat => !skillScores[cat]);

      if (uncovered.length > 0) {
        const cat = uncovered[0];
        recs.push({
          type: 'exercise',
          title: `Попробуйте новое направление`,
          description: `Вы ещё не практиковались в навыке "${SKILL_NAMES[cat]}". Попробуйте!`,
          action: 'exercises',
          priority: 'high'
        });
      }

      if (weakSkills.length > 0) {
        const weak = weakSkills[0];
        recs.push({
          type: 'practice',
          title: `Улучшите "${SKILL_NAMES[weak]}"`,
          description: `Ваш результат в этом навыке ниже 70%. Повторите упражнения этой категории`,
          action: 'exercises',
          priority: 'medium'
        });
      }

      // Общие рекомендации
      recs.push({
        type: 'lesson',
        title: 'Изучите продвинутые техники',
        description: 'В библиотеке есть много полезных техник для углубления навыков',
        action: 'library',
        priority: 'low'
      });
    }

    setRecommendations(recs.length > 0 ? recs : DEFAULT_RECOMMENDATIONS);
  };

  const handleGenerateAIRecommendations = async () => {
    setGeneratingRecs(true);
    
    // Имитация генерации AI-рекомендаций
    setTimeout(() => {
      const aiRecs = [
        {
          type: 'exercise',
          title: 'Фокус на активном слушании',
          description: 'На основе вашего прогресса, рекомендую сосредоточиться на техниках парафраза и отражения чувств. Это фундаментальные навыки эмпатии.',
          action: 'exercises',
          priority: 'high'
        },
        {
          type: 'lesson',
          title: 'Изучите невербальную коммуникацию',
          description: '65% общения происходит невербально. Изучите техники чтения языка тела в библиотеке.',
          action: 'library',
          priority: 'high'
        },
        {
          type: 'practice',
          title: 'Ежедневная практика',
          description: 'Попробуйте каждый день давать хотя бы один конкретный комплимент. Это тренирует внимательность и позитивное мышление.',
          action: 'exercises',
          priority: 'medium'
        },
        {
          type: 'tip',
          title: 'Совет: Ведите дневник',
          description: 'Записывайте сложные социальные ситуации и анализируйте их. Что получилось хорошо? Что можно улучшить?',
          priority: 'low'
        }
      ];
      
      setRecommendations(aiRecs);
      setGeneratingRecs(false);
      setShowRecommendations(true);
    }, 1500);
  };

  const handleActionClick = (action) => {
    setShowRecommendations(false);
    if (action === 'exercises') {
      navigate('/exercises');
    } else if (action === 'library') {
      navigate('/library');
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getPriorityLabel = (priority) => {
    switch (priority) {
      case 'high': return 'Важно';
      case 'medium': return 'Средний';
      case 'low': return 'Низкий';
      default: return priority;
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'exercise': return <ExerciseIcon />;
      case 'lesson': return <LearnIcon />;
      case 'practice': return <TrophyIcon />;
      case 'tip': return <TipIcon />;
      default: return <StarIcon />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Мой прогресс
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Отслеживайте развитие своих социальных навыков
        </Typography>
      </Box>

      {/* Статистика */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={6} md={3}>
          <StatCard
            icon={<CalendarIcon sx={{ fontSize: 40 }} />}
            value={stats?.daysActive || 0}
            label="Дней обучения"
            color="primary.main"
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatCard
            icon={<CheckIcon sx={{ fontSize: 40 }} />}
            value={stats?.exercisesCompleted || 0}
            label="Упражнений"
            color="success.main"
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatCard
            icon={<TimerIcon sx={{ fontSize: 40 }} />}
            value={`${stats?.hoursLearning || 0}ч`}
            label="Время обучения"
            color="info.main"
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatCard
            icon={<TrophyIcon sx={{ fontSize: 40 }} />}
            value={stats?.averageResult ? `${stats.averageResult}%` : '—'}
            label="Средний результат"
            color="warning.main"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Навыки */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <TrendingUpIcon color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Уровень навыков
                </Typography>
              </Box>
              
              {skills.length > 0 ? (
                skills.map((skill, index) => (
                  <SkillBar key={index} {...skill} />
                ))
              ) : (
                <Alert severity="info">
                  Пройдите упражнения, чтобы увидеть свой прогресс по навыкам
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Рекомендации */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TipIcon color="primary" />
                  <Typography variant="h6" fontWeight={600}>
                    Рекомендации
                  </Typography>
                </Box>
                <Button
                  size="small"
                  startIcon={<ViewIcon />}
                  onClick={() => setShowRecommendations(true)}
                >
                  Подробнее
                </Button>
              </Box>

              {recommendations.slice(0, 3).map((rec, index) => (
                <Box 
                  key={index}
                  sx={{ 
                    p: 2, 
                    mb: 2, 
                    backgroundColor: 'action.hover', 
                    borderRadius: 2,
                    cursor: rec.action ? 'pointer' : 'default',
                    '&:hover': rec.action ? { backgroundColor: 'action.selected' } : {}
                  }}
                  onClick={() => rec.action && handleActionClick(rec.action)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    {getTypeIcon(rec.type)}
                    <Typography variant="subtitle2" fontWeight={600}>
                      {rec.title}
                    </Typography>
                    <Chip 
                      label={getPriorityLabel(rec.priority)} 
                      size="small" 
                      color={getPriorityColor(rec.priority)}
                      sx={{ ml: 'auto' }}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {rec.description}
                  </Typography>
                </Box>
              ))}

              <Button
                fullWidth
                variant="outlined"
                startIcon={generatingRecs ? <CircularProgress size={20} /> : <GenerateIcon />}
                onClick={handleGenerateAIRecommendations}
                disabled={generatingRecs}
                sx={{ mt: 1 }}
              >
                {generatingRecs ? 'Генерация...' : 'Получить AI-рекомендации'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Достижения */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <TrophyIcon color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Достижения
            </Typography>
          </Box>
          
          <Grid container spacing={2}>
            {[
              { 
                title: 'Первые шаги', 
                desc: 'Завершите первое упражнение',
                achieved: (stats?.exercisesCompleted || 0) >= 1
              },
              { 
                title: 'На пути к мастерству', 
                desc: 'Завершите 3 упражнения',
                achieved: (stats?.exercisesCompleted || 0) >= 3
              },
              { 
                title: 'Отличник', 
                desc: 'Получите 90%+ в упражнении',
                achieved: (stats?.averageResult || 0) >= 90
              },
              { 
                title: 'Постоянство', 
                desc: 'Занимайтесь 7 дней',
                achieved: (stats?.daysActive || 0) >= 7
              },
              { 
                title: 'Мастер общения', 
                desc: 'Завершите все упражнения',
                achieved: (stats?.exercisesCompleted || 0) >= 6
              },
              { 
                title: 'Перфекционист', 
                desc: 'Средний балл 80%+',
                achieved: (stats?.averageResult || 0) >= 80
              },
            ].map((achievement, index) => (
              <Grid item xs={6} sm={4} md={2} key={index}>
                <Box 
                  sx={{ 
                    textAlign: 'center',
                    p: 2,
                    borderRadius: 2,
                    backgroundColor: achievement.achieved ? 'primary.main' : 'action.hover',
                    color: achievement.achieved ? 'white' : 'text.secondary',
                    opacity: achievement.achieved ? 1 : 0.6,
                    transition: 'all 0.3s'
                  }}
                >
                  <TrophyIcon sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="body2" fontWeight={600}>
                    {achievement.title}
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'block', opacity: 0.8 }}>
                    {achievement.desc}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Диалог с рекомендациями */}
      <Dialog 
        open={showRecommendations} 
        onClose={() => setShowRecommendations(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TipIcon color="primary" />
            Персональные рекомендации
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <List>
            {recommendations.map((rec, index) => (
              <React.Fragment key={index}>
                <ListItem 
                  button={!!rec.action}
                  onClick={() => rec.action && handleActionClick(rec.action)}
                  sx={{ borderRadius: 2 }}
                >
                  <ListItemIcon sx={{ color: getPriorityColor(rec.priority) + '.main' }}>
                    {getTypeIcon(rec.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {rec.title}
                        <Chip 
                          label={getPriorityLabel(rec.priority)} 
                          size="small" 
                          color={getPriorityColor(rec.priority)}
                        />
                      </Box>
                    }
                    secondary={rec.description}
                  />
                  {rec.action && <ArrowIcon color="action" />}
                </ListItem>
                {index < recommendations.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRecommendations(false)}>
            Закрыть
          </Button>
          <Button 
            variant="contained" 
            startIcon={<ExerciseIcon />}
            onClick={() => handleActionClick('exercises')}
          >
            К упражнениям
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ProgressPage;
