/* Frontend configuration for CampusShield AI Dashboard */

// API base URL - load from environment variable
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API endpoints
export const API_ENDPOINTS = {
  // Health
  HEALTH: `${API_BASE_URL}/health`,
  
  // Auth
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  
  // Cameras
  CAMERAS: `${API_BASE_URL}/api/cameras`,
  CAMERA_DETAIL: (id) => `${API_BASE_URL}/api/cameras/${id}`,
  
  // Incidents
  INCIDENTS: `${API_BASE_URL}/api/incidents`,
  INCIDENT_DETAIL: (id) => `${API_BASE_URL}/api/incidents/${id}`,
  
  // Alerts
  ALERTS: `${API_BASE_URL}/api/alerts`,
  ACKNOWLEDGE_ALERT: (id) => `${API_BASE_URL}/api/alerts/${id}/ack`,
  
  // AI
  AI_EXPLAIN_INCIDENT: `${API_BASE_URL}/api/ai/explain-incident`,
  AI_GENERATE_REPORT: `${API_BASE_URL}/api/ai/generate-report`,
  AI_ASSISTANT: `${API_BASE_URL}/api/ai/assistant`,
  AI_ASSISTANT_STATS: `${API_BASE_URL}/api/ai/assistant/stats`,
  
  // WebSocket
  WS_ALERTS: `${API_BASE_URL.replace('http', 'ws')}/ws/alerts`,
};

export default API_ENDPOINTS;
