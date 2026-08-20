import axios from 'axios';
import { env } from '../config/env';
import i18n from '../../i18n/i18n';

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach token and active language
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('arkidi_access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  config.headers['Accept-Language'] = i18n.language || 'en';
  return config;
});

// Response interceptor: handle 401 unauth / redirect to login
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('arkidi_access_token');
      localStorage.removeItem('arkidi_refresh_token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
