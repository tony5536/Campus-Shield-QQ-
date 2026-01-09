/* Frontend configuration for CampusShield AI Dashboard */

// Load from environment variables with fallback defaults
// VITE_* or REACT_APP_* variables are injected by the build system
const API_BASE_URL = process.env.VITE_API_BASE_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API_PATH = '/api';

// Ensure no double slashes in base URL
const normalizedBaseUrl = API_BASE_URL.replace(/\/$/, '');

// API endpoints
export const API_ENDPOINTS = {
  // Health
  HEALTH: `${normalizedBaseUrl}/health`,
  STATUS: `${normalizedBaseUrl}/status`,
  
  // Auth
  LOGIN: `${normalizedBaseUrl}${API_PATH}/auth/login`,
  
  // Cameras
  CAMERAS: `${normalizedBaseUrl}${API_PATH}/cameras`,
  CAMERA_DETAIL: (id) => `${normalizedBaseUrl}${API_PATH}/cameras/${id}`,
  
  // Incidents
  INCIDENTS: `${normalizedBaseUrl}${API_PATH}/incidents`,
  INCIDENT_DETAIL: (id) => `${normalizedBaseUrl}${API_PATH}/incidents/${id}`,
  INCIDENTS_V1: `${normalizedBaseUrl}${API_PATH}/v1/incidents`,
  INCIDENT_V1_DETAIL: (id) => `${normalizedBaseUrl}${API_PATH}/v1/incidents/${id}`,
  
  // Alerts
  ALERTS: `${normalizedBaseUrl}${API_PATH}/alerts`,
  ACKNOWLEDGE_ALERT: (id) => `${normalizedBaseUrl}${API_PATH}/alerts/${id}/ack`,
  ALERTS_V1: `${normalizedBaseUrl}${API_PATH}/v1/alerts`,
  
  // AI
  AI_EXPLAIN_INCIDENT: `${normalizedBaseUrl}${API_PATH}/ai/explain-incident`,
  AI_GENERATE_REPORT: `${normalizedBaseUrl}${API_PATH}/ai/generate-report`,
  AI_ASSIST: `${normalizedBaseUrl}${API_PATH}/ai/assist`,
  AI_ASSISTANT: `${normalizedBaseUrl}${API_PATH}/ai/assistant`,
  AI_ASSISTANT_STATS: `${normalizedBaseUrl}${API_PATH}/ai/assistant/stats`,
  
  // Dashboard (canonical endpoints)
  DASHBOARD_METRICS: `${normalizedBaseUrl}${API_PATH}/v1/dashboard/metrics`,
  DASHBOARD_OVERVIEW: `${normalizedBaseUrl}${API_PATH}/v1/dashboard/overview`,
  DASHBOARD_RECENT: `${normalizedBaseUrl}${API_PATH}/v1/dashboard/incidents/recent`,
  
  // Video
  VIDEO_STREAM: `${normalizedBaseUrl}${API_PATH}/video/stream`,
  VIDEO_HEALTH: `${normalizedBaseUrl}${API_PATH}/video/health`,
  
  // WebSocket
  WS_ALERTS: `${process.env.VITE_ALERTS_WS_URL || process.env.REACT_APP_ALERTS_WS_URL || 'ws://127.0.0.1:8000/ws/alerts'}`,
};

export default API_ENDPOINTS;
