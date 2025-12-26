import { create } from 'zustand';
import { chatsApi } from '../services/api';

const useChatStore = create((set, get) => ({

  chats: [],
  currentChat: null,
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,

  fetchChats: async () => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await chatsApi.getAll();
      set({ 
        chats: response.data || [],
        isLoading: false 
      });
    } catch (error) {
      console.error('Error fetching chats:', error);
      set({ 
        chats: [],
        isLoading: false,
        error: error.response?.data?.detail || 'Ошибка загрузки диалогов'
      });
    }
  },

  fetchChat: async (chatId) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await chatsApi.getById(chatId);
      set({
        currentChat: response.data,
        messages: response.data.messages || [],
        isLoading: false,
      });
    } catch (error) {
      console.error('Error fetching chat:', error);
      const { chats } = get();
      const chat = chats.find(c => c.id === parseInt(chatId));
      if (chat) {
        set({
          currentChat: chat,
          messages: chat.messages || [],
          isLoading: false,
        });
      } else {
        set({ 
          isLoading: false,
          error: error.response?.data?.detail || 'Диалог не найден'
        });
      }
    }
  },

  createChat: async (scenario = null) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await chatsApi.create({
        title: 'Новый диалог',
        type: scenario || 'conversation'
      });
      
      const newChat = response.data;
      
      set((state) => ({
        chats: [newChat, ...state.chats],
        currentChat: newChat,
        messages: [],
        isLoading: false,
      }));
      
      return { success: true, chat: newChat };
    } catch (error) {
      console.error('Error creating chat:', error);
      set({ 
        isLoading: false,
        error: error.response?.data?.detail || 'Ошибка создания диалога'
      });
      return { success: false, error: error.message };
    }
  },

  sendMessage: async (content) => {
    const { currentChat } = get();
    if (!currentChat) return { success: false };

    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isSending: true,
    }));

    try {
      // Отправка сообщения на Backend
      const response = await chatsApi.sendMessage(currentChat.id, content);
      
      // Добавление ответа AI
      const aiMessage = {
        id: response.data.id || `ai-${Date.now()}`,
        role: 'assistant',
        content: response.data.ai_message || response.data.content || response.data.response || 'Ответ не получен',
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, aiMessage],
        isSending: false,
      }));

      return { success: true };
    } catch (error) {
      console.error('Error sending message:', error);
      set({ 
        isSending: false,
        error: error.response?.data?.detail || 'Ошибка отправки сообщения'
      });
      return { success: false, error: error.message };
    }
  },

  deleteChat: async (chatId) => {
    set((state) => ({
      chats: state.chats.filter(c => c.id !== chatId),
      currentChat: state.currentChat?.id === chatId ? null : state.currentChat,
      messages: state.currentChat?.id === chatId ? [] : state.messages,
    }));
    return { success: true };
  },

  setCurrentChat: (chat) => {
    set({
      currentChat: chat,
      messages: chat?.messages || [],
    });
  },

  clearError: () => set({ error: null }),
  
  clearChat: () => set({
    currentChat: null,
    messages: [],
  }),
}));

export default useChatStore;
