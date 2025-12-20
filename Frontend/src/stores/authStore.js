import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { usersApi } from '../services/api';

const useAuthStore = create(
  persist(
    (set, get) => ({

      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await usersApi.login({ email, password });
          const { user, token } = response.data;
          
          localStorage.setItem('token', token);
          
          set({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
          
          return { success: true };
        } catch (error) {
          set({
            error: error.response?.data?.detail || 'Ошибка входа',
            isLoading: false,
          });
          return { success: false, error: error.response?.data?.detail };
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await usersApi.register(userData);
          const { user, token } = response.data;
          
          localStorage.setItem('token', token);
          
          set({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
          
          return { success: true };
        } catch (error) {
          set({
            error: error.response?.data?.detail || 'Ошибка регистрации',
            isLoading: false,
          });
          return { success: false, error: error.response?.data?.detail };
        }
      },

      logout: () => {
        localStorage.removeItem('token');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      fetchProfile: async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        set({ isLoading: true });
        try {
          const response = await usersApi.getProfile();
          set({
            user: response.data,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          if (error.response?.status === 401) {
            get().logout();
          }
        }
      },

      updateProfile: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await usersApi.updateProfile(data);
          set({
            user: response.data,
            isLoading: false,
          });
          return { success: true };
        } catch (error) {
          set({
            error: error.response?.data?.detail || 'Ошибка обновления',
            isLoading: false,
          });
          return { success: false };
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
