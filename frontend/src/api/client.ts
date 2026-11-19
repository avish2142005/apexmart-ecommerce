import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Return structured error message
    const msg = error.response?.data?.detail || error.response?.data?.error || error.message;
    return Promise.reject(new Error(typeof msg === 'object' ? JSON.stringify(msg) : msg));
  }
);

export default api;
