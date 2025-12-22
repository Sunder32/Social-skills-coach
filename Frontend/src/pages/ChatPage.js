import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Paper } from '@mui/material';
import useChatStore from '../stores/chatStore';
import ChatList from '../components/ChatList';
import ChatWindow from '../components/ChatWindow';

function ChatPage() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  
  const {
    chats,
    currentChat,
    messages,
    isLoading,
    isSending,
    fetchChats,
    fetchChat,
    createChat,
    sendMessage,
    deleteChat,
    setCurrentChat,
  } = useChatStore();

  useEffect(() => {
    fetchChats();
  }, []);

  useEffect(() => {
    if (chatId) {
      fetchChat(chatId);
    }
  }, [chatId]);

  const handleSelectChat = (chat) => {
    setCurrentChat(chat);
    navigate(`/chat/${chat.id}`);
  };

  const handleNewChat = async () => {
    const result = await createChat();
    if (result.success) {
      navigate(`/chat/${result.chat.id}`);
    }
  };

  const handleDeleteChat = async (id) => {
    await deleteChat(id);
    if (currentChat?.id === id) {
      navigate('/chat');
    }
  };

  const handleSendMessage = async (content) => {
    if (!currentChat) {
      const result = await createChat();
      if (result.success) {
        navigate(`/chat/${result.chat.id}`);
        setTimeout(() => {
          sendMessage(content);
        }, 100);
      }
    } else {
      await sendMessage(content);
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100%' }}>
      <Paper
        elevation={0}
        sx={{
          width: 320,
          borderRight: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.paper',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <ChatList
          chats={chats}
          currentChatId={currentChat?.id}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
          onNewChat={handleNewChat}
        />
      </Paper>

      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <ChatWindow
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading && !!chatId}
          isSending={isSending}
        />
      </Box>
    </Box>
  );
}

export default ChatPage;
