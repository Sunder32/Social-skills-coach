import React from 'react';
import {
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Box,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';

function ChatList({ chats, currentChatId, onSelectChat, onDeleteChat, onNewChat }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Вчера';
    } else if (diffDays < 7) {
      return date.toLocaleDateString('ru-RU', { weekday: 'short' });
    } else {
      return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    }
  };

  const getScenarioLabel = (scenario) => {
    const labels = {
      'small_talk': 'Беседа',
      'conflict': 'Конфликт',
      'negotiation': 'Переговоры',
      'feedback': 'Обратная связь',
      'request': 'Просьба',
    };
    return labels[scenario] || scenario;
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Typography variant="h6" fontWeight={600}>
          Диалоги
        </Typography>
        <Tooltip title="Новый диалог">
          <IconButton
            onClick={onNewChat}
            sx={{
              backgroundColor: 'primary.main',
              color: 'white',
              '&:hover': { backgroundColor: 'primary.dark' },
            }}
            size="small"
          >
            <AddIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <List sx={{ flex: 1, overflow: 'auto', p: 1 }}>
        {chats.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              opacity: 0.5,
              p: 3,
              textAlign: 'center',
            }}
          >
            <ChatIcon sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
            <Typography variant="body2">
              Нет диалогов
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Создайте новый диалог для практики
            </Typography>
          </Box>
        ) : (
          chats.map((chat) => (
            <ListItemButton
              key={chat.id}
              selected={chat.id === currentChatId}
              onClick={() => onSelectChat(chat)}
              sx={{
                mb: 0.5,
                borderRadius: 2,
                '&:hover .delete-button': {
                  opacity: 1,
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <ChatIcon
                  sx={{
                    color: chat.id === currentChatId ? 'primary.main' : 'text.secondary',
                  }}
                />
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography
                      variant="body2"
                      fontWeight={chat.id === currentChatId ? 600 : 400}
                      noWrap
                      sx={{ flex: 1 }}
                    >
                      {chat.title || `Диалог ${chat.id}`}
                    </Typography>
                    {chat.scenario && (
                      <Chip
                        label={getScenarioLabel(chat.scenario)}
                        size="small"
                        sx={{
                          height: 20,
                          fontSize: '0.65rem',
                          backgroundColor: 'rgba(223, 37, 49, 0.1)',
                          color: 'primary.main',
                        }}
                      />
                    )}
                  </Box>
                }
                secondary={
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    noWrap
                    component="span"
                  >
                    {chat.lastMessage || 'Нет сообщений'}
                  </Typography>
                }
              />
              <ListItemSecondaryAction>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(chat.updatedAt || chat.createdAt)}
                  </Typography>
                  <IconButton
                    className="delete-button"
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteChat(chat.id);
                    }}
                    sx={{
                      opacity: 0,
                      transition: 'opacity 0.2s',
                      '&:hover': {
                        color: 'error.main',
                      },
                    }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              </ListItemSecondaryAction>
            </ListItemButton>
          ))
        )}
      </List>
    </Box>
  );
}

export default ChatList;
