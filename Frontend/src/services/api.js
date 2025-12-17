import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
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

// Response interceptor
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

// ==================== Users API ====================
export const usersApi = {
  register: (data) => api.post('/api/users/register', data),
  login: (data) => api.post('/api/users/login', data),
  getProfile: () => api.get('/api/users/me'),
  updateProfile: (data) => api.put('/api/users/me', data),
  getProgress: () => api.get('/api/users/me/progress'),
};

// ==================== Chats API ====================
export const chatsApi = {
  getAll: () => api.get('/api/chats'),
  getById: (id) => api.get(`/api/chats/${id}`),
  create: (data) => api.post('/api/chats', data),
  sendMessage: (chatId, message) => 
    api.post(`/api/chats/${chatId}/messages`, { content: message }),
  delete: (id) => api.delete(`/api/chats/${id}`),
  getHistory: (chatId) => api.get(`/api/chats/${chatId}/history`),
};

// ==================== Analysis API ====================
export const analysisApi = {
  analyzeChat: (chatId) => api.get(`/api/analysis/chat/${chatId}`),
  getPatterns: (chatId) => api.get(`/api/analysis/chat/${chatId}/patterns`),
  getSentiment: (chatId) => api.get(`/api/analysis/chat/${chatId}/sentiment`),
  getRecommendations: () => api.get('/api/analysis/recommendations'),
  analyzeText: (text) => api.post('/api/analysis/text', { text }),
};

// ==================== Library API ====================
export const libraryApi = {
  getTopics: () => api.get('/api/library/topics'),
  getTopic: (id) => api.get(`/api/library/topics/${id}`),
  getTechniques: (topicId = null) => 
    api.get('/api/library/techniques', { params: { topic_id: topicId } }),
  getTechnique: (id) => api.get(`/api/library/techniques/${id}`),
  search: (query) => api.get('/api/library/search', { params: { q: query } }),
};

// ==================== Exercises API ====================
export const exercisesApi = {
  getAll: (topicId = null) => 
    api.get('/api/exercises', { params: { topic_id: topicId } }),
  getById: (id) => api.get(`/api/exercises/${id}`),
  start: (id) => api.post(`/api/exercises/${id}/start`),
  submit: (id, answer) => api.post(`/api/exercises/${id}/submit`, { answer }),
  getProgress: () => api.get('/api/exercises/progress'),
  getHistory: () => api.get('/api/exercises/history'),
};

export default api;
