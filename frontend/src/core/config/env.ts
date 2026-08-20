export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  appName: import.meta.env.VITE_APP_NAME || 'Arkidi Platform',
  defaultLanguage: import.meta.env.VITE_DEFAULT_LANGUAGE || 'en',
};
