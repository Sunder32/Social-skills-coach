import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  TextField,
  InputAdornment,
  Chip,
  List,
  ListItemButton,
  ListItemText,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  MenuBook as BookIcon,
  Psychology as TechniqueIcon,
} from '@mui/icons-material';

const TOPICS = [
  {
    id: 1,
    name: 'Управление конфликтами',
    description: 'Методы и техники разрешения конфликтных ситуаций',
  },
  {
    id: 2,
    name: 'Публичное выступление',
    description: 'Навыки эффективной презентации и ораторского мастерства',
  },
  {
    id: 3,
    name: 'Деловое общение',
    description: 'Коммуникация в профессиональной среде',
  },
  {
    id: 4,
    name: 'Невербальные средства общения',
    description: 'Язык тела, жесты и мимика в коммуникации',
  },
  {
    id: 5,
    name: 'Активное слушание',
    description: 'Техники эффективного восприятия информации',
  },
];

const TECHNIQUES = {
  1: [
    { id: 101, name: 'Техника "Я-сообщения"', description: 'Выражение своих чувств и потребностей без обвинений', difficulty: 'basic' },
    { id: 102, name: 'Метод "Пяти почему"', description: 'Определение истинной причины конфликта', difficulty: 'intermediate' },
    { id: 103, name: 'Компромисс', description: 'Поиск взаимовыгодного решения', difficulty: 'basic' },
    { id: 104, name: 'Медиация', description: 'Привлечение третьей стороны для разрешения спора', difficulty: 'advanced' },
  ],
  2: [
    { id: 201, name: 'Правило трёх', description: 'Структурирование речи в три части', difficulty: 'basic' },
    { id: 202, name: 'Storytelling', description: 'Использование историй для убеждения', difficulty: 'intermediate' },
    { id: 203, name: 'Работа с визуальными материалами', description: 'Эффективное использование презентаций', difficulty: 'basic' },
    { id: 204, name: 'Управление голосом', description: 'Техники модуляции и интонации', difficulty: 'intermediate' },
  ],
  3: [
    { id: 301, name: 'Деловая переписка', description: 'Правила составления эффективных писем', difficulty: 'basic' },
    { id: 302, name: 'Сетевое взаимодействие', description: 'Построение профессиональных связей', difficulty: 'intermediate' },
    { id: 303, name: 'Этикет переговоров', description: 'Протокол и культура делового общения', difficulty: 'basic' },
    { id: 304, name: 'Фасилитация встреч', description: 'Эффективное ведение совещаний', difficulty: 'advanced' },
  ],
  4: [
    { id: 401, name: 'Чтение языка тела', description: 'Интерпретация невербальных сигналов', difficulty: 'intermediate' },
    { id: 402, name: 'Зеркалирование', description: 'Копирование жестов для установления раппорта', difficulty: 'basic' },
    { id: 403, name: 'Контроль дистанции', description: 'Управление личным пространством', difficulty: 'basic' },
    { id: 404, name: 'Мимика и эмоции', description: 'Распознавание эмоций по лицу', difficulty: 'intermediate' },
  ],
  5: [
    { id: 501, name: 'Парафразирование', description: 'Переформулирование слов собеседника', difficulty: 'basic' },
    { id: 502, name: 'Открытые вопросы', description: 'Задавание вопросов для углубления диалога', difficulty: 'basic' },
    { id: 503, name: 'Эмпатическое присутствие', description: 'Полное внимание к собеседнику', difficulty: 'intermediate' },
    { id: 504, name: 'Резюмирование', description: 'Подведение итогов разговора', difficulty: 'basic' },
  ],
};

function LibraryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [topics] = useState(TOPICS);
  const [techniques, setTechniques] = useState([]);

  useEffect(() => {
    if (selectedTopic) {
      setTechniques(TECHNIQUES[selectedTopic.id] || []);
    } else {
      const allTechniques = Object.values(TECHNIQUES).flat();
      setTechniques(allTechniques);
    }
  }, [selectedTopic]);

  const handleTopicSelect = (topic) => {
    setSelectedTopic(topic);
  };

  const filteredTechniques = techniques.filter((technique) =>
    technique.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    technique.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Библиотека знаний
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Изучайте техники эффективной коммуникации
        </Typography>
      </Box>

      <TextField
        fullWidth
        placeholder="Поиск техник и материалов..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon color="action" />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 4 }}
      />

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BookIcon /> Темы
          </Typography>
          <Card>
            <List disablePadding>
              <ListItemButton
                selected={!selectedTopic}
                onClick={() => setSelectedTopic(null)}
              >
                <ListItemText primary="Все темы" />
              </ListItemButton>
              <Divider />
              {topics.map((topic) => (
                <ListItemButton
                  key={topic.id}
                  selected={selectedTopic?.id === topic.id}
                  onClick={() => handleTopicSelect(topic)}
                >
                  <ListItemText
                    primary={topic.name}
                    secondary={topic.description}
                  />
                </ListItemButton>
              ))}
            </List>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TechniqueIcon /> 
            {selectedTopic ? `Техники: ${selectedTopic.name}` : 'Все техники'}
          </Typography>
          
          <Grid container spacing={2}>
            {filteredTechniques.map((technique) => (
              <Grid item xs={12} sm={6} key={technique.id}>
                <Card sx={{ height: '100%' }}>
                  <CardActionArea sx={{ p: 2, height: '100%' }}>
                    <CardContent sx={{ p: 0 }}>
                      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                        <Chip
                          label={
                            technique.difficulty === 'advanced' ? 'Продвинутый' :
                            technique.difficulty === 'intermediate' ? 'Средний' :
                            'Базовый'
                          }
                          size="small"
                          color={
                            technique.difficulty === 'advanced' ? 'error' :
                            technique.difficulty === 'intermediate' ? 'warning' :
                            'success'
                          }
                        />
                      </Box>
                      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                        {technique.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {technique.description}
                      </Typography>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))}
            {filteredTechniques.length === 0 && (
              <Grid item xs={12}>
                <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  Техники не найдены
                </Typography>
              </Grid>
            )}
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}

export default LibraryPage;
