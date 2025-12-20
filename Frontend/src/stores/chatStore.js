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
    set({ 
      chats: [],
      isLoading: false 
    });
  },

  fetchChat: async (chatId) => {
    const { chats } = get();
    const chat = chats.find(c => c.id === parseInt(chatId));
    if (chat) {
      set({
        currentChat: chat,
        messages: chat.messages || [],
        isLoading: false,
      });
    }
  },

  createChat: async (scenario = null) => {
    const newChat = {
      id: Date.now(),
      title: 'Новый диалог',
      scenario,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    
    set((state) => ({
      chats: [newChat, ...state.chats],
      currentChat: newChat,
      messages: [],
      isLoading: false,
    }));
    
    return { success: true, chat: newChat };
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
      isSending: false,
    }));

    return { success: true };
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
