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

function sanitizeIncident(raw) {
  if (!raw || typeof raw !== 'object') return {
    id: null,
    incident_type: '',
    description: '',
    location: '',
    timestamp: null,
    severity: null,
    status: 'ACTIVE',
    cameras: [],
    aiAnalysis: {},
  };

  // Normalize fields
  const safe = (v, d = '') => (typeof v === 'string' ? v : v == null ? d : String(v));
  const safeNum = (v, d = 0) => (typeof v === 'number' ? v : v == null ? d : Number(v));

  // Normalize severity into string values (LOW/MEDIUM/HIGH)
  const normalizeSeverity = (s) => {
    if (s == null) return 'LOW';
    if (typeof s === 'string') {
      const sval = s.trim().toLowerCase();
      if (sval === 'critical' || sval === 'high') return 'HIGH';
      if (sval === 'medium' || sval === 'med') return 'MEDIUM';
      if (sval === 'low' || sval === 'minor') return 'LOW';
      // Try numeric-like string
      const n2 = Number(sval);
      if (!Number.isNaN(n2)) {
        if (n2 >= 0.66) return 'HIGH';
        if (n2 >= 0.33) return 'MEDIUM';
        return 'LOW';
      }
      return s.toUpperCase();
    }
    const n = Number(s);
    if (!Number.isNaN(n)) {
      if (n >= 0.66) return 'HIGH';
      if (n >= 0.33) return 'MEDIUM';
      return 'LOW';
    }
    return String(s).toUpperCase();
  };

  const out = {
    id: raw.id ?? null,
    incident_id: raw.incident_id ?? null,
    camera_id: raw.camera_id ?? null,
    incident_type: safe(raw.incident_type, ''),
    severity: normalizeSeverity(raw.severity),
    status: (raw.status && String(raw.status)) || 'ACTIVE',
    description: safe(raw.description, ''),
    location: safe(raw.location, ''),
    zone: safe(raw.zone, ''),
    source: safe(raw.source, ''),
    assigned_team: safe(raw.assigned_team, ''),
    timestamp: raw.timestamp || null,
    // Preserve any frontend-expected arrays, default to []
    cameras: Array.isArray(raw.cameras) ? raw.cameras : [],
    tags: Array.isArray(raw.tags) ? raw.tags : [],
    aiAnalysis: raw.aiAnalysis && typeof raw.aiAnalysis === 'object' ? raw.aiAnalysis : raw.ai_analysis || {},
  };
  return out;
}

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
  getIncidents: () =>
    client.get('/api/incidents').then((res) => {
      // sanitize list
      if (Array.isArray(res.data)) {
        res.data = res.data.map(sanitizeIncident);
      }
      return res;
    }),
  getIncident: (id) =>
    client.get(`/api/incidents/${id}`).then((res) => {
      res.data = sanitizeIncident(res.data || {});
      return res;
    }),
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
