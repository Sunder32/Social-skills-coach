import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Send as SendIcon,
  AttachFile as AttachIcon,
  Close as CloseIcon,
  InsertDriveFile as FileIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

function MessageBubble({ message, isUser }) {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
        animation: 'slideUp 0.3s ease-out',
      }}
    >
      <Paper
        elevation={0}
        sx={{
          maxWidth: '70%',
          p: 2,
          px: 2.5,
          borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
          backgroundColor: isUser ? 'primary.main' : 'background.paper',
          color: isUser ? 'white' : 'text.primary',
          border: isUser ? 'none' : '1px solid rgba(0,0,0,0.08)',
        }}
      >
        {isUser ? (
          <Typography variant="body1">{message.content}</Typography>
        ) : (
          <Box
            sx={{
              '& p': { m: 0, mb: 1, '&:last-child': { mb: 0 } },
              '& ul, & ol': { pl: 2, m: 0, mb: 1 },
              '& code': {
                backgroundColor: 'rgba(0,0,0,0.2)',
                px: 0.5,
                borderRadius: 0.5,
                fontSize: '0.9em',
              },
            }}
          >
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </Box>
        )}
        <Typography
          variant="caption"
          sx={{
            display: 'block',
            mt: 1,
            opacity: 0.7,
            textAlign: 'right',
          }}
        >
          {new Date(message.timestamp).toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Typography>
      </Paper>
    </Box>
  );
}

function TypingIndicator() {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
      <Paper
        elevation={0}
        sx={{
          p: 2,
          px: 3,
          borderRadius: '16px 16px 16px 4px',
          backgroundColor: 'background.paper',
          border: '1px solid rgba(0,0,0,0.08)',
          display: 'flex',
          gap: 0.5,
        }}
      >
        {[0, 1, 2].map((i) => (
          <Box
            key={i}
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: 'text.secondary',
              animation: 'pulse 1.5s infinite',
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </Paper>
    </Box>
  );
}

function ChatWindow({ messages, onSendMessage, isLoading, isSending }) {
  const [inputValue, setInputValue] = useState('');
  const [attachedFile, setAttachedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSend = () => {
    if ((inputValue.trim() || fileContent) && !isSending) {
      let messageContent = inputValue.trim();
      
      // Если есть прикрепленный файл, добавляем его содержимое
      if (fileContent && attachedFile) {
        const fileHeader = `📎 Файл: ${attachedFile.name}\n\`\`\`\n${fileContent}\n\`\`\`\n\n`;
        messageContent = fileHeader + messageContent;
      }
      
      onSendMessage(messageContent);
      setInputValue('');
      setAttachedFile(null);
      setFileContent('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Проверка размера файла (макс 1MB)
      if (file.size > 1024 * 1024) {
        alert('Файл слишком большой. Максимальный размер: 1 МБ');
        e.target.value = '';
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target.result;
        // Ограничиваем содержимое до 50000 символов
        const truncatedContent = content.length > 50000 
          ? content.substring(0, 50000) + '\n... (файл обрезан, показано 50000 символов)'
          : content;
        setFileContent(truncatedContent);
        setAttachedFile(file);
      };
      reader.onerror = () => {
        alert('Ошибка при чтении файла');
      };
      reader.readAsText(file, 'UTF-8');
      e.target.value = '';
    }
  };

  const handleRemoveFile = () => {
    setAttachedFile(null);
    setFileContent('');
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: 'background.default',
      }}
    >

      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {isLoading ? (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              flex: 1,
            }}
          >
            <CircularProgress />
          </Box>
        ) : messages.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              flex: 1,
              opacity: 0.6,
            }}
          >
            <Typography variant="h6" gutterBottom>
              Начните диалог
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Напишите сообщение, чтобы начать практику
            </Typography>
          </Box>
        ) : (
          <>
            {messages.map((message, index) => (
              <MessageBubble
                key={message.id || index}
                message={message}
                isUser={message.role === 'user'}
              />
            ))}
            {isSending && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </Box>

      <Box
        sx={{
          p: 2,
          pt: 0,
          borderTop: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.default',
        }}
      >
        {/* Отображение прикрепленного файла */}
        {attachedFile && (
          <Box sx={{ mb: 1, px: 1 }}>
            <Chip
              icon={<FileIcon />}
              label={`${attachedFile.name} (${(attachedFile.size / 1024).toFixed(1)} КБ)`}
              onDelete={handleRemoveFile}
              deleteIcon={<CloseIcon />}
              color="primary"
              variant="outlined"
              sx={{ maxWidth: '100%' }}
            />
          </Box>
        )}
        <Paper
          elevation={0}
          sx={{
            display: 'flex',
            alignItems: 'flex-end',
            gap: 1,
            p: 1,
            backgroundColor: 'background.paper',
            borderRadius: 3,
            border: '1px solid rgba(0,0,0,0.12)',
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            hidden
            onChange={handleFileChange}
            accept=".txt,.md,.json,.csv,.xml,.yaml,.yml,.ini,.cfg,.py,.js,.html,.css,.log"
          />
          <Tooltip title="Прикрепить файл">
            <IconButton 
              size="small" 
              sx={{ color: attachedFile ? 'primary.main' : 'text.secondary' }}
              onClick={handleFileClick}
              disabled={isSending}
            >
              <AttachIcon />
            </IconButton>
          </Tooltip>

          <TextField
            ref={inputRef}
            fullWidth
            multiline
            maxRows={4}
            placeholder={attachedFile ? "Добавьте комментарий к файлу..." : "Напишите сообщение..."}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isSending}
            variant="standard"
            InputProps={{
              disableUnderline: true,
              sx: { fontSize: '1rem' },
            }}
            sx={{
              '& .MuiInputBase-root': {
                py: 0.5,
              },
            }}
          />

          <Tooltip title="Отправить">
            <span>
              <IconButton
                onClick={handleSend}
                disabled={(!inputValue.trim() && !attachedFile) || isSending}
                sx={{
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '&.Mui-disabled': {
                    backgroundColor: 'action.disabledBackground',
                  },
                }}
              >
                {isSending ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  <SendIcon />
                )}
              </IconButton>
            </span>
          </Tooltip>
        </Paper>
      </Box>
    </Box>
  );
}

export default ChatWindow;
