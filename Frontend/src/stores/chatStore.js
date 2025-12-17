import { create } from 'zustand';
import { chatsApi } from '../services/api';

const useChatStore = create((set, get) => ({
  // State
  chats: [],
  currentChat: null,
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,

  // Actions
  fetchChats: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await chatsApi.getAll();
      set({ chats: response.data, isLoading: false });
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Ошибка загрузки чатов',
        isLoading: false,
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
      set({
        error: error.response?.data?.detail || 'Ошибка загрузки чата',
        isLoading: false,
      });
    }
  },

  createChat: async (scenario = null) => {
    set({ isLoading: true, error: null });
    try {
      const response = await chatsApi.create({ scenario });
      const newChat = response.data;
      
      set((state) => ({
        chats: [newChat, ...state.chats],
        currentChat: newChat,
        messages: newChat.messages || [],
        isLoading: false,
      }));
      
      return { success: true, chat: newChat };
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Ошибка создания чата',
        isLoading: false,
      });
      return { success: false };
    }
  },

  sendMessage: async (content) => {
    const { currentChat } = get();
    if (!currentChat) return { success: false };

    // Optimistic update - add user message immediately
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
      const response = await chatsApi.sendMessage(currentChat.id, content);
      const aiMessage = response.data;

      set((state) => ({
        messages: [...state.messages.filter(m => m.id !== userMessage.id), 
          { ...userMessage, id: aiMessage.user_message_id || userMessage.id },
          aiMessage
        ],
        isSending: false,
      }));

      return { success: true };
    } catch (error) {
      // Remove optimistic message on error
      set((state) => ({
        messages: state.messages.filter(m => m.id !== userMessage.id),
        error: error.response?.data?.detail || 'Ошибка отправки',
        isSending: false,
      }));
      return { success: false };
    }
  },

  deleteChat: async (chatId) => {
    try {
      await chatsApi.delete(chatId);
      set((state) => ({
        chats: state.chats.filter(c => c.id !== chatId),
        currentChat: state.currentChat?.id === chatId ? null : state.currentChat,
        messages: state.currentChat?.id === chatId ? [] : state.messages,
      }));
      return { success: true };
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Ошибка удаления' });
      return { success: false };
    }
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
