import { create } from 'zustand';
import { libraryApi } from '../services/api';

const useLibraryStore = create((set) => ({
  // State
  topics: [],
  techniques: [],
  currentTopic: null,
  currentTechnique: null,
  searchResults: [],
  isLoading: false,
  error: null,

  // Actions
  fetchTopics: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await libraryApi.getTopics();
      set({ topics: response.data, isLoading: false });
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Ошибка загрузки тем',
        isLoading: false,
      });
    }
  },

  fetchTopic: async (topicId) => {
    set({ isLoading: true, error: null });
    try {
      const response = await libraryApi.getTopic(topicId);
      set({ currentTopic: response.data, isLoading: false });
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Ошибка загрузки темы',
        isLoading: false,
      });
    }
  },

  fetchTechniques: async (topicId = null) => {
    set({ isLoading: true, error: null });
    try {
      const response = await libraryApi.getTechniques(topicId);
      set({ techniques: response.data, isLoading: false });
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Ошибка загрузки техник',
        isLoading: false,
      });
    }
  },

  fetchTechnique: async (techniqueId) => {
    set({ isLoading: true, error: null });
    try {
      const response = await libraryApi.getTechnique(techniqueId);
      set({ currentTechnique: response.data, isLoading: false });
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Ошибка загрузки техники',
        isLoading: false,
      });
    }
  },

  search: async (query) => {
    if (!query.trim()) {
      set({ searchResults: [] });
      return;
    }
    
    set({ isLoading: true, error: null });
    try {
      const response = await libraryApi.search(query);
      set({ searchResults: response.data, isLoading: false });
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Ошибка поиска',
        isLoading: false,
      });
    }
  },

  clearSearch: () => set({ searchResults: [] }),
  clearError: () => set({ error: null }),
}));

export default useLibraryStore;
