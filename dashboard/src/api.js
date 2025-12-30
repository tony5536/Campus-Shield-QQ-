/* API client service for CampusShield AI */
import axios from 'axios';
import { API_ENDPOINTS } from './config';

const client = axios.create({
  baseURL: API_ENDPOINTS.HEALTH.replace('/health', ''),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Methods
export const api = {
  // Health
  checkHealth: () => client.get('/health'),
  
  // Auth
  login: (username, password) =>
    client.post('/api/auth/login', { username, password }),
  
  // Cameras
  getCameras: () => client.get('/api/cameras'),
  getCamera: (id) => client.get(`/api/cameras/${id}`),
  createCamera: (data) => client.post('/api/cameras', data),
  
  // Incidents
  getIncidents: () => client.get('/api/incidents'),
  getIncident: (id) => client.get(`/api/incidents/${id}`),
  createIncident: (data) => client.post('/api/incidents', data),
  
  // Alerts
  getAlerts: () => client.get('/api/alerts'),
  acknowledgeAlert: (id, actor = 'guard') =>
    client.post(`/api/alerts/${id}/ack`, {}, { params: { actor } }),
  
  // AI
  explainIncident: (incidentId) =>
    client.post('/api/ai/explain-incident', { incident_id: incidentId }),
  generateReport: (incidentId, includeRecommendations = true) =>
    client.post('/api/ai/generate-report', {
      incident_id: incidentId,
      include_recommendations: includeRecommendations,
    }),
  assistantQuery: (query, context = null) =>
    client.post('/api/ai/assistant', { query, context }),
  aiAssist: (query) =>
    client.post('/api/ai/assist', { query }),
  getAssistantStats: () => client.get('/api/ai/assistant/stats'),
};

export default api;
