import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '30000');

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptors for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Status endpoint
export const fetchStatus = async () => {
  const response = await api.get('/api/status');
  return response.data;
};

// Email endpoints
export const getEmails = async () => {
  const response = await api.get('/api/emails');
  return response.data;
};

export const getEmailDetail = async (id: number) => {
  const response = await api.get(`/api/emails/${id}`);
  return response.data;
};

export const summarizeEmail = async (id: number) => {
  const response = await api.post(`/api/emails/${id}/summarize`);
  return response.data;
};

export const getEmailActions = async (id: number) => {
  const response = await api.get(`/api/emails/${id}/actions`);
  return response.data;
};

// Data endpoints
export const getData = async () => {
  const response = await api.get('/api/data');
  return response.data;
};

export const queryData = async (query: string) => {
  const response = await api.post('/api/data/query', { query });
  return response.data;
};

// Response endpoints
export const getResponses = async () => {
  const response = await api.get('/api/responses');
  return response.data;
};

export const sendResponse = async (id: number, response: string) => {
  const res = await api.post(`/api/responses/${id}/send`, { response });
  return res.data;
};

export default api;
