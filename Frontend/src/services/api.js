import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const usersApi = {
  register: (data) => api.post('/api/users/register', data),
  login: (data) => api.post('/api/users/login', data),
  getProgress: () => api.get('/api/users/me/progress'),
  verifyEmail: (data) => api.post('/api/users/verify-email', data),
  resendVerification: (data) => api.post('/api/users/resend-verification', data),
  forgotPassword: (data) => api.post('/api/users/forgot-password', data),
  resetPassword: (data) => api.post('/api/users/reset-password', data),
};

export const chatsApi = {
  getAll: () => api.get('/api/chats'),
  getById: (id) => api.get(`/api/chats/${id}`),
  create: (data) => api.post('/api/chats', data),
  sendMessage: (chatId, message) => 
    api.post(`/api/chats/${chatId}/messages`, { content: message }),
  delete: (id) => api.delete(`/api/chats/${id}`),
  getHistory: (chatId) => api.get(`/api/chats/${chatId}/history`),
};

export const analysisApi = {
  getRecommendations: () => api.get('/api/analysis/recommendations'),
};

export const libraryApi = {
  getTopics: () => api.get('/api/library/topics'),
  getTopic: (id) => api.get(`/api/library/topics/${id}`),
  getTechniques: (topicId = null) => 
    api.get('/api/library/techniques', { params: { topic_id: topicId } }),
  getTechnique: (id) => api.get(`/api/library/techniques/${id}`),
  search: (query) => api.get('/api/library/search', { params: { q: query } }),
};

export const exercisesApi = {
  submit: (id, answer) => api.post(`/api/exercises/${id}/submit`, { answer }),
  getProgress: () => api.get('/api/exercises/progress'),
};

export default api;
