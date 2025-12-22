import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Checkbox,
  IconButton,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Check as CheckIcon,
  Timer as TimerIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { exercisesApi } from '../services/api';

const MOCK_EXERCISES = [
  {
    id: 1,
    title: 'Знакомство с новым коллегой',
    description: 'Практика первого впечатления и установления контакта в профессиональной среде',
    difficulty: 'easy',
    duration: 5,
    scenario: 'Вы первый день на новой работе. К вам подходит коллега и хочет познакомиться.',
    category: 'networking',
  },
  {
    id: 2,
    title: 'Просьба о помощи',
    description: 'Учимся корректно просить помощь у других людей, не создавая неловкости',
    difficulty: 'easy',
    duration: 5,
    scenario: 'Вам нужна помощь с задачей, которую вы не можете решить самостоятельно.',
    category: 'communication',
  },
  {
    id: 3,
    title: 'Разрешение конфликта',
    description: 'Навыки дипломатичного разрешения споров и недопониманий',
    difficulty: 'medium',
    duration: 10,
    scenario: 'Возник конфликт с другом из-за недопонимания. Нужно урегулировать ситуацию.',
    category: 'conflict',
  },
  {
    id: 4,
    title: 'Публичное выступление',
    description: 'Подготовка и проведение короткой презентации перед аудиторией',
    difficulty: 'hard',
    duration: 15,
    scenario: 'Вам нужно представить свой проект команде из 10 человек.',
    category: 'public_speaking',
  },
  {
    id: 5,
    title: 'Отказ без обиды',
    description: 'Учимся вежливо отказывать, сохраняя хорошие отношения',
    difficulty: 'medium',
    duration: 7,
    scenario: 'Друг просит вас помочь с переездом, но у вас уже есть планы.',
    category: 'boundaries',
  },
  {
    id: 6,
    title: 'Активное слушание',
    description: 'Практика техник активного слушания и эмпатии',
    difficulty: 'easy',
    duration: 5,
    scenario: 'Человек рассказывает вам о своей проблеме. Покажите, что вы его слушаете.',
    category: 'empathy',
  },
];

function ExercisesPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  
  const [addedExercises, setAddedExercises] = useState(() => {
    const saved = localStorage.getItem('addedExercises');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [completedExercises, setCompletedExercises] = useState(() => {
    const saved = localStorage.getItem('completedExercises');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('addedExercises', JSON.stringify(addedExercises));
  }, [addedExercises]);

  useEffect(() => {
    localStorage.setItem('completedExercises', JSON.stringify(completedExercises));
  }, [completedExercises]);

  useEffect(() => {
    localStorage.setItem('completedExercises', JSON.stringify(completedExercises));
  }, [completedExercises]);

  const handleAddExercise = (exerciseId) => {
    if (!addedExercises.includes(exerciseId)) {
      setAddedExercises([...addedExercises, exerciseId]);
      setActiveTab(1);
    }
  };

  const handleRemoveExercise = (exerciseId) => {
    setAddedExercises(addedExercises.filter(id => id !== exerciseId));
  };

  const isExerciseAdded = (exerciseId) => {
    return addedExercises.includes(exerciseId);
  };

  const isExerciseCompleted = (exerciseId) => {
    return completedExercises.includes(exerciseId);
  };

  const handleStartExercise = (exercise) => {
    setSelectedExercise(exercise);
    setUserAnswer('');
    setResult(null);
  };

  const handleSubmitAnswer = async () => {
    if (!userAnswer.trim()) return;
    
    setIsSubmitting(true);
    
    setTimeout(() => {
      const mockFeedback = {
        feedback: 'Отличный ответ! Вы проявили эмпатию и использовали правильные техники коммуникации. Продолжайте в том же духе!',
        score: Math.floor(Math.random() * 20) + 80,
      };
      
      setResult(mockFeedback);
      
      if (!completedExercises.includes(selectedExercise.id)) {
        setCompletedExercises([...completedExercises, selectedExercise.id]);
      }
      
      setAddedExercises(addedExercises.filter(id => id !== selectedExercise.id));
      
      setIsSubmitting(false);
    }, 1500);
  };

  const handleCloseDialog = () => {
    setSelectedExercise(null);
    setUserAnswer('');
    setResult(null);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  const getDifficultyLabel = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'Легкий';
      case 'medium': return 'Средний';
      case 'hard': return 'Сложный';
      default: return difficulty;
    }
  };

  const getFilteredExercises = () => {
    if (activeTab === 0) {
      return MOCK_EXERCISES.filter(ex => !completedExercises.includes(ex.id));
    } else if (activeTab === 1) {
      return MOCK_EXERCISES.filter(ex => 
        addedExercises.includes(ex.id) && !completedExercises.includes(ex.id)
      );
    } else {
      return MOCK_EXERCISES.filter(ex => completedExercises.includes(ex.id));
    }
  };

  const filteredExercises = getFilteredExercises();

  const totalExercises = MOCK_EXERCISES.length;
  const completedCount = completedExercises.length;
  const progressPercentage = totalExercises > 0 ? (completedCount / totalExercises) * 100 : 0;

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Упражнения
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Практикуйтесь в различных коммуникативных сценариях
        </Typography>
      </Box>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Общий прогресс
              </Typography>
              <LinearProgress
                variant="determinate"
                value={progressPercentage}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700} color="primary.main">
                {completedCount}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Выполнено
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700}>
                {totalExercises}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Всего
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Tabs
        value={activeTab}
        onChange={(_, v) => setActiveTab(v)}
        sx={{ mb: 3 }}
      >
        <Tab label="Все" />
        <Tab 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              Не выполнены
              {addedExercises.filter(id => !completedExercises.includes(id)).length > 0 && (
                <Chip 
                  label={addedExercises.filter(id => !completedExercises.includes(id)).length}
                  size="small"
                  color="primary"
                  sx={{ height: 20, minWidth: 20, '& .MuiChip-label': { px: 0.75, fontSize: '0.75rem' } }}
                />
              )}
            </Box>
          }
        />
        <Tab label="Выполнены" />
      </Tabs>

      <Grid container spacing={3}>
        {filteredExercises.map((exercise) => {
          const isAdded = isExerciseAdded(exercise.id);
          const isCompleted = isExerciseCompleted(exercise.id);
          
          return (
            <Grid item xs={12} sm={6} md={4} key={exercise.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  opacity: isCompleted ? 0.85 : 1,
                  position: 'relative',
                }}
              >
                <CardContent sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    <Chip
                      label={getDifficultyLabel(exercise.difficulty)}
                      size="small"
                      color={getDifficultyColor(exercise.difficulty)}
                    />
                    {isCompleted && (
                      <Chip
                        icon={<CheckIcon />}
                        label="Выполнено"
                        size="small"
                        color="success"
                        variant="outlined"
                      />
                    )}
                  </Box>
                  
                  <Typography variant="h6" gutterBottom>
                    {exercise.title}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {exercise.description?.substring(0, 120)}...
                  </Typography>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
                    <TimerIcon fontSize="small" />
                    <Typography variant="caption">
                      ~{exercise.duration} мин
                    </Typography>
                  </Box>
                </CardContent>
                
                {activeTab === 0 && !isCompleted && (
                  <CardActions sx={{ p: 2, pt: 0 }}>
                    {isAdded ? (
                      <Button
                        fullWidth
                        variant="outlined"
                        color="success"
                        startIcon={<CheckIcon />}
                        disabled
                      >
                        Добавлено
                      </Button>
                    ) : (
                      <Button
                        fullWidth
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={() => handleAddExercise(exercise.id)}
                      >
                        Добавить
                      </Button>
                    )}
                  </CardActions>
                )}
                
                {activeTab === 1 && (
                  <CardActions sx={{ p: 2, pt: 0 }}>
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={<StartIcon />}
                      onClick={() => handleStartExercise(exercise)}
                    >
                      Начать
                    </Button>
                  </CardActions>
                )}
                
                {activeTab === 2 && (
                  <CardActions sx={{ p: 2, pt: 0 }}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<CheckIcon />}
                      onClick={() => handleStartExercise(exercise)}
                    >
                      Повторить
                    </Button>
                  </CardActions>
                )}
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {filteredExercises.length === 0 && (
        <Box
          sx={{
            textAlign: 'center',
            py: 8,
          }}
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {activeTab === 1 && 'Нет добавленных упражнений'}
            {activeTab === 2 && 'Нет выполненных упражнений'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {activeTab === 1 && 'Добавьте упражнения из вкладки "Все"'}
            {activeTab === 2 && 'Выполните упражнения, чтобы увидеть их здесь'}
          </Typography>
        </Box>
      )}

      <Dialog
        open={!!selectedExercise}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        {selectedExercise && (
          <>
            <DialogTitle>
              <Typography variant="h5" fontWeight={600}>
                {selectedExercise.title}
              </Typography>
            </DialogTitle>
            
            <DialogContent>
              <Typography variant="body1" sx={{ mb: 3 }}>
                {selectedExercise.description}
              </Typography>
              
              {selectedExercise.scenario && (
                <Box
                  sx={{
                    p: 2,
                    mb: 3,
                    backgroundColor: 'background.paper',
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                >
                  <Typography variant="subtitle2" color="primary.main" gutterBottom>
                    Сценарий:
                  </Typography>
                  <Typography variant="body2">
                    {selectedExercise.scenario}
                  </Typography>
                </Box>
              )}

              {!result ? (
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  placeholder="Напишите ваш ответ..."
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  disabled={isSubmitting}
                />
              ) : (
                <Box>
                  <Typography variant="subtitle2" color="success.main" gutterBottom>
                    Обратная связь:
                  </Typography>
                  <Typography variant="body2">
                    {result.feedback}
                  </Typography>
                  {result.score && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Оценка: {result.score}/100
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </DialogContent>
            
            <DialogActions sx={{ p: 2 }}>
              <Button onClick={handleCloseDialog}>
                {result ? 'Отлично!' : 'Закрыть'}
              </Button>
              {!result && (
                <Button
                  variant="contained"
                  onClick={handleSubmitAnswer}
                  disabled={!userAnswer.trim() || isSubmitting}
                >
                  {isSubmitting ? <CircularProgress size={20} /> : 'Отправить'}
                </Button>
              )}
              {result && (
                <Button
                  variant="contained"
                  onClick={handleCloseDialog}
                >
                  Завершить
                </Button>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}

export default ExercisesPage;
