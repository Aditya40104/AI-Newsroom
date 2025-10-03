import axios from 'axios';

// Create axios instance with base URL and timeout
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000',
  timeout: 10000, // 10 seconds timeout to prevent infinite buffering
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors and timeouts
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout - server might be slow or down');
      error.message = 'Request timeout. Please check if the server is running and try again.';
    } else if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    } else if (!error.response) {
      console.error('Network error - server might be down');
      error.message = 'Cannot connect to server. Please check if the backend is running.';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  logout: () => api.post('/api/auth/logout'),
  getCurrentUser: () => api.get('/api/auth/me'),
};

// Article API
export const articleAPI = {
  getArticles: (params = {}) => api.get('/api/articles', { params }),
  getArticle: (id) => api.get(`/api/articles/${id}`),
  createArticle: (data) => api.post('/api/articles', data),
  updateArticle: (id, data) => api.put(`/api/articles/${id}`, data),
  deleteArticle: (id) => api.delete(`/api/articles/${id}`),
  getArticleVersions: (id) => api.get(`/api/articles/${id}/versions`),
  getArticleVersion: (id, version) => api.get(`/api/articles/${id}/versions/${version}`),
};

export default api;