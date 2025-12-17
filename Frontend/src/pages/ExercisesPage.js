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
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Check as CheckIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import { exercisesApi } from '../services/api';

function ExercisesPage() {
  const [exercises, setExercises] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    loadExercises();
  }, []);

  const loadExercises = async () => {
    setIsLoading(true);
    try {
      const response = await exercisesApi.getAll();
      setExercises(response.data);
    } catch (error) {
      console.error('Error loading exercises:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartExercise = async (exercise) => {
    setSelectedExercise(exercise);
    setUserAnswer('');
    setResult(null);
  };

  const handleSubmitAnswer = async () => {
    if (!userAnswer.trim()) return;
    
    setIsSubmitting(true);
    try {
      const response = await exercisesApi.submit(selectedExercise.id, userAnswer);
      setResult(response.data);
    } catch (error) {
      console.error('Error submitting:', error);
    } finally {
      setIsSubmitting(false);
    }
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

  const filteredExercises = exercises.filter(ex => {
    if (activeTab === 0) return true;
    if (activeTab === 1) return !ex.completed;
    if (activeTab === 2) return ex.completed;
    return true;
  });

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
          Упражнения
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Практикуйтесь в различных коммуникативных сценариях
        </Typography>
      </Box>

      {/* Progress overview */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Общий прогресс
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(exercises.filter(e => e.completed).length / exercises.length) * 100 || 0}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700} color="primary.main">
                {exercises.filter(e => e.completed).length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Выполнено
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700}>
                {exercises.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Всего
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onChange={(_, v) => setActiveTab(v)}
        sx={{ mb: 3 }}
      >
        <Tab label="Все" />
        <Tab label="Не выполнены" />
        <Tab label="Выполнены" />
      </Tabs>

      {/* Exercises grid */}
      <Grid container spacing={3}>
        {filteredExercises.map((exercise) => (
          <Grid item xs={12} sm={6} md={4} key={exercise.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                opacity: exercise.completed ? 0.7 : 1,
              }}
            >
              <CardContent sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip
                    label={getDifficultyLabel(exercise.difficulty)}
                    size="small"
                    color={getDifficultyColor(exercise.difficulty)}
                  />
                  {exercise.completed && (
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
                    ~{exercise.duration || 5} мин
                  </Typography>
                </Box>
              </CardContent>
              
              <CardActions sx={{ p: 2, pt: 0 }}>
                <Button
                  fullWidth
                  variant={exercise.completed ? 'outlined' : 'contained'}
                  startIcon={exercise.completed ? <CheckIcon /> : <StartIcon />}
                  onClick={() => handleStartExercise(exercise)}
                >
                  {exercise.completed ? 'Повторить' : 'Начать'}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Exercise dialog */}
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
                Закрыть
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
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}

export default ExercisesPage;
