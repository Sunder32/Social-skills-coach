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
import useLibraryStore from '../stores/libraryStore';

function LibraryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTopic, setSelectedTopic] = useState(null);
  
  const {
    topics,
    techniques,
    searchResults,
    isLoading,
    fetchTopics,
    fetchTechniques,
    search,
    clearSearch,
  } = useLibraryStore();

  useEffect(() => {
    fetchTopics();
    fetchTechniques();
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      const timer = setTimeout(() => {
        search(searchQuery);
      }, 300);
      return () => clearTimeout(timer);
    } else {
      clearSearch();
    }
  }, [searchQuery]);

  const handleTopicSelect = (topic) => {
    setSelectedTopic(topic);
    fetchTechniques(topic.id);
  };

  const displayedTechniques = selectedTopic
    ? techniques.filter(t => t.topicId === selectedTopic.id)
    : techniques;

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

      {searchQuery.trim() && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Результаты поиска
          </Typography>
          {isLoading ? (
            <CircularProgress />
          ) : searchResults.length > 0 ? (
            <Grid container spacing={2}>
              {searchResults.map((result) => (
                <Grid item xs={12} md={6} key={result.id}>
                  <Card>
                    <CardActionArea sx={{ p: 2 }}>
                      <Typography variant="subtitle1" fontWeight={600}>
                        {result.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {result.description?.substring(0, 150)}...
                      </Typography>
                    </CardActionArea>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography color="text.secondary">Ничего не найдено</Typography>
          )}
          <Divider sx={{ my: 4 }} />
        </Box>
      )}

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BookIcon /> Темы
          </Typography>
          <Card>
            <List disablePadding>
              <ListItemButton
                selected={!selectedTopic}
                onClick={() => {
                  setSelectedTopic(null);
                  fetchTechniques();
                }}
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
                    secondary={`${topic.techniqueCount || 0} техник`}
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
          
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2}>
              {displayedTechniques.map((technique) => (
                <Grid item xs={12} sm={6} key={technique.id}>
                  <Card sx={{ height: '100%' }}>
                    <CardActionArea sx={{ p: 2, height: '100%' }}>
                      <CardContent sx={{ p: 0 }}>
                        <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                          <Chip
                            label={technique.difficulty || 'Базовый'}
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
                          {technique.description?.substring(0, 100)}...
                        </Typography>
                      </CardContent>
                    </CardActionArea>
                  </Card>
                </Grid>
              ))}
              {displayedTechniques.length === 0 && (
                <Grid item xs={12}>
                  <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                    Техники не найдены
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}

export default LibraryPage;
