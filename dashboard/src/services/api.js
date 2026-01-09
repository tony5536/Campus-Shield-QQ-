/**
 * Hardened API client with retry logic, timeout, and error recovery.
 * All calls include proper error handling and logging.
 */

import axios from 'axios';

// Load API configuration from environment variables
// REACT_APP_* variables are injected by react-scripts from .env file
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';
const API_PATH = '/api';
const API_BASE = `${API_BASE_URL.replace(/\/$/, '')}${API_PATH}`;
const REQUEST_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '30000', 10);
const MAX_RETRIES = 3;

// Log API configuration on module load (only in development)
if (process.env.REACT_APP_ENV === 'development') {
  console.log(`[API] Initialized with base URL: ${API_BASE}`);
}

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request logging
apiClient.interceptors.request.use(
  config => {
    const startTime = Date.now();
    config.metadata = { startTime };
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response logging with latency
apiClient.interceptors.response.use(
  response => {
    const duration = Date.now() - response.config.metadata.startTime;
    console.log(`[API] ${response.status} ${response.config.url} [${duration}ms]`);
    return response;
  },
  error => {
    if (error.config?.metadata) {
      const duration = Date.now() - error.config.metadata.startTime;
      console.error(`[API] ERROR ${error.response?.status || 'TIMEOUT'} ${error.config.url} [${duration}ms]`);
    }
    return Promise.reject(error);
  }
);

/**
 * Retry wrapper with exponential backoff
 */
async function withRetry(fn, maxRetries = MAX_RETRIES) {
  let lastError;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Don't retry on client errors (4xx)
      if (error.response?.status >= 400 && error.response?.status < 500) {
        throw error;
      }

      // Exponential backoff
      if (i < maxRetries - 1) {
        const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s
        console.warn(`[API] Retry ${i + 1}/${maxRetries} after ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

/**
 * Safe GET request with error handling
 */
export async function get(url, config = {}) {
  try {
    return await withRetry(() => apiClient.get(url, config));
  } catch (error) {
    console.error(`[API] GET ${url} failed:`, error.message);
    throw error;
  }
}

/**
 * Safe POST request
 */
export async function post(url, data = {}, config = {}) {
  try {
    return await withRetry(() => apiClient.post(url, data, config));
  } catch (error) {
    console.error(`[API] POST ${url} failed:`, error.message);
    throw error;
  }
}

/**
 * Safe PUT request
 */
export async function put(url, data = {}, config = {}) {
  try {
    return await withRetry(() => apiClient.put(url, data, config));
  } catch (error) {
    console.error(`[API] PUT ${url} failed:`, error.message);
    throw error;
  }
}

/**
 * Safe DELETE request
 */
export async function del(url, config = {}) {
  try {
    return await withRetry(() => apiClient.delete(url, config));
  } catch (error) {
    console.error(`[API] DELETE ${url} failed:`, error.message);
    throw error;
  }
}

// ========================================
// Incident API
// ========================================

export const incidentsAPI = {
  /**
   * Get all incidents with filters
   */
  async list(skip = 0, limit = 50, filters = {}) {
    try {
      const params = new URLSearchParams({
        offset: skip,  // v1 API expects 'offset', not 'skip'
        limit,
        ...filters
      });

      const response = await get(`/v1/incidents?${params}`);
      return {
        total: response.data?.total || 0,
        incidents: response.data?.incidents || []
      };
    } catch (error) {
      console.error('[API] Failed to fetch incidents:', error);
      return { total: 0, incidents: [] }; // Fallback
    }
  },

  /**
   * Get single incident
   */
  async get(id) {
    try {
      const response = await get(`/v1/incidents/${id}`);
      return response.data;
    } catch (error) {
      console.error(`[API] Failed to fetch incident ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create incident
   */
  async create(data) {
    try {
      const response = await post('/v1/incidents', data);
      return response.data;
    } catch (error) {
      console.error('[API] Failed to create incident:', error);
      throw error;
    }
  },

  /**
   * Update incident
   */
  async update(id, data) {
    try {
      const response = await put(`/v1/incidents/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`[API] Failed to update incident ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get recent incidents
   */
  async getRecent(hours = 24) {
    try {
      const response = await get(`/v1/incidents/recent/${hours}`);
      return response.data || [];
    } catch (error) {
      console.error('[API] Failed to fetch recent incidents:', error);
      return [];
    }
  }
};

// ========================================
// AI Assistant API
// ========================================

export const assistantAPI = {
  /**
   * Send chat message
   */
  async chat(query, history = []) {
    try {
      const response = await post('/v1/ai/chat', {
        query,
        history
      });

      return {
        reply: response.data?.reply || 'No response',
        confidence: response.data?.confidence ?? 0.5,
        sources: response.data?.sources || []
      };
    } catch (error) {
      console.error('[API] Chat error:', error);

      // Fallback response
      return {
        reply: 'AI Assistant is currently unavailable. Please try again.',
        confidence: 0.0,
        sources: []
      };
    }
  },

  /**
   * Analyze incident
   */
  async analyzeIncident(incident) {
    try {
      const response = await post('/v1/ai/analyze-incident', {
        incident_type: incident.incident_type,
        location: incident.location,
        description: incident.description,
        severity: incident.severity
      });

      return response.data;
    } catch (error) {
      console.error('[API] Analysis error:', error);
      return {
        reply: 'Unable to analyze incident',
        confidence: 0.0,
        sources: []
      };
    }
  },

  /**
   * Health check
   */
  async health() {
    try {
      const response = await get('/v1/ai/health');
      return response.data;
    } catch (error) {
      console.warn('[API] AI health check failed:', error.message);
      return { status: 'unhealthy', error: error.message };
    }
  }
};

// ========================================
// Dashboard API
// ========================================

export const dashboardAPI = {
  /**
   * Get dashboard metrics (canonical endpoint)
   * GET /api/v1/dashboard/metrics
   * Returns: { active_alerts, total_incidents, cameras_online, avg_response_time }
   */
  async getMetrics() {
    try {
      const response = await get('/v1/dashboard/metrics');
      return {
        active_alerts: response.data?.active_alerts || 0,
        total_incidents: response.data?.total_incidents || 0,
        cameras_online: response.data?.cameras_online || 0,
        avg_response_time: response.data?.avg_response_time || '0m'
      };
    } catch (error) {
      console.error('[API] Failed to fetch dashboard metrics:', error);
      throw error;
    }
  }
};

// ========================================
// Camera API
// ========================================

export const cameraAPI = {
  /**
   * Get all cameras
   */
  async list() {
    try {
      const response = await get('/v1/cameras');
      return response.data || [];
    } catch (error) {
      console.error('[API] Failed to fetch cameras:', error);
      return [];
    }
  }
};

// ========================================
// System Health
// ========================================

export async function getSystemHealth() {
  try {
    const [ai, incidents] = await Promise.allSettled([
      assistantAPI.health(),
      get('/v1/incidents?limit=1')
    ]);

    return {
      ai: ai.status === 'fulfilled' ? ai.value : { status: 'failed' },
      incidents: incidents.status === 'fulfilled',
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('[API] Health check failed:', error);
    return {
      ai: { status: 'unknown' },
      incidents: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

// ========================================
// Default Export (Unified API Client)
// ========================================

const api = {
  // Low-level methods
  client: apiClient,
  get,
  post,
  put,
  delete: del,
  withRetry,

  // High-level API groups
  incidents: incidentsAPI,
  assistant: assistantAPI,
  dashboard: dashboardAPI,
  cameras: cameraAPI,
  health: getSystemHealth,

  // Convenience methods (backward compatibility)
  async getMetrics() {
    return dashboardAPI.getMetrics();
  },

  async getCameras() {
    return cameraAPI.list();
  },

  async getIncidents(skip = 0, limit = 50, filters = {}) {
    return incidentsAPI.list(skip, limit, filters);
  },

  async getIncident(id) {
    return incidentsAPI.get(id);
  },

  async createIncident(data) {
    return incidentsAPI.create(data);
  },

  async updateIncident(id, data) {
    return incidentsAPI.update(id, data);
  },

  async aiAssist(query) {
    try {
      return await post('/v1/ai/analyze', { query });
    } catch (error) {
      console.error('[API] AI assist error:', error);
      throw error;
    }
  },

  async aiChat(query, history = []) {
    return assistantAPI.chat(query, history);
  },

  async aiAnalyzeIncident(incident) {
    return assistantAPI.analyzeIncident(incident);
  }
};

export default api;
