/**
 * Incident data contract and type safety utilities for React frontend.
 * Ensures all data matches backend schema - no missing fields, no undefined errors.
 */

/**
 * Canonical Incident schema - MUST match backend IncidentResponse
 */
export const INCIDENT_SCHEMA = {
  incident_id: "number (required)",
  incident_type: "string (required)",
  location: "string (required)",
  zone: "string (optional)",
  source: "string (optional)",
  severity: "string enum: LOW|MEDIUM|HIGH (required)",
  description: "string (required, may be empty)",
  status: "string enum: ACTIVE|RESOLVED (required)",
  timestamp: "string ISO 8601 UTC (required)"
};

/**
 * Validate incident object against schema
 * Returns { valid: boolean, errors: string[] }
 */
export function validateIncident(incident) {
  const errors = [];

  if (!incident || typeof incident !== 'object') {
    return { valid: false, errors: ['Incident must be an object'] };
  }

  // Required fields
  if (typeof incident.incident_id !== 'number') {
    errors.push('incident_id must be a number');
  }
  if (typeof incident.incident_type !== 'string') {
    errors.push('incident_type must be a string');
  }
  if (typeof incident.location !== 'string') {
    errors.push('location must be a string');
  }
  if (typeof incident.description !== 'string') {
    errors.push('description must be a string');
  }

  // Severity validation
  const validSeverities = ['LOW', 'MEDIUM', 'HIGH'];
  if (!validSeverities.includes(String(incident.severity || '').toUpperCase())) {
    errors.push(`severity must be one of: ${validSeverities.join(', ')}`);
  }

  // Status validation
  const validStatuses = ['ACTIVE', 'RESOLVED'];
  if (!validStatuses.includes(String(incident.status || '').toUpperCase())) {
    errors.push(`status must be one of: ${validStatuses.join(', ')}`);
  }

  // Timestamp validation
  if (!incident.timestamp || isNaN(Date.parse(incident.timestamp))) {
    errors.push('timestamp must be a valid ISO 8601 date');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Normalize incident data with safe defaults
 * Ensures no undefined values propagate to UI
 */
export function normalizeIncident(incident) {
  if (!incident || typeof incident !== 'object') {
    return createEmptyIncident();
  }

  return {
    incident_id: incident.incident_id ?? 0,
    incident_type: String(incident.incident_type ?? 'Unknown'),
    location: String(incident.location ?? 'Unknown'),
    zone: incident.zone ? String(incident.zone) : null,
    source: incident.source ? String(incident.source) : null,
    severity: normalizeSeverity(incident.severity),
    description: String(incident.description ?? ''),
    status: normalizeStatus(incident.status),
    timestamp: normalizeTimestamp(incident.timestamp)
  };
}

/**
 * Create empty incident with valid defaults
 */
export function createEmptyIncident() {
  return {
    incident_id: 0,
    incident_type: 'Unknown',
    location: 'Unknown',
    zone: null,
    source: null,
    severity: 'LOW',
    description: '',
    status: 'ACTIVE',
    timestamp: new Date().toISOString()
  };
}

/**
 * Normalize severity to canonical values
 */
export function normalizeSeverity(value) {
  if (!value) return 'LOW';
  
  const upper = String(value).toUpperCase();
  if (['CRITICAL', 'HIGH'].includes(upper)) return 'HIGH';
  if (['MEDIUM', 'MED'].includes(upper)) return 'MEDIUM';
  if (['LOW', 'MINOR'].includes(upper)) return 'LOW';
  
  // Numeric severity (0-1)
  try {
    const num = parseFloat(value);
    if (!isNaN(num)) {
      return num >= 0.66 ? 'HIGH' : num >= 0.33 ? 'MEDIUM' : 'LOW';
    }
  } catch (e) {
    console.warn('Unable to parse severity:', value);
  }
  
  return 'LOW';
}

/**
 * Normalize status to canonical values
 */
export function normalizeStatus(value) {
  if (!value) return 'ACTIVE';
  
  const upper = String(value).toUpperCase();
  return ['RESOLVED', 'CLOSED', 'DONE'].includes(upper) ? 'RESOLVED' : 'ACTIVE';
}

/**
 * Normalize timestamp to ISO format
 */
export function normalizeTimestamp(value) {
  if (!value) return new Date().toISOString();
  
  try {
    const date = new Date(value);
    if (isNaN(date.getTime())) {
      console.warn('Invalid timestamp:', value);
      return new Date().toISOString();
    }
    return date.toISOString();
  } catch (e) {
    console.warn('Error parsing timestamp:', value, e);
    return new Date().toISOString();
  }
}

/**
 * Get human-readable severity color
 */
export function getSeverityColor(severity) {
  const normalized = normalizeSeverity(severity);
  return {
    'HIGH': '#ff3333',
    'MEDIUM': '#ff9933',
    'LOW': '#33cc33'
  }[normalized] || '#999999';
}

/**
 * Get human-readable severity label
 */
export function getSeverityLabel(severity) {
  const normalized = normalizeSeverity(severity);
  return {
    'HIGH': '🔴 High',
    'MEDIUM': '🟠 Medium',
    'LOW': '🟢 Low'
  }[normalized] || 'Unknown';
}

/**
 * Format timestamp for display
 */
export function formatTimestamp(timestamp) {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  } catch (e) {
    console.warn('Error formatting timestamp:', timestamp);
    return 'Invalid date';
  }
}

/**
 * Format incident for display (safe access to all fields)
 */
export function formatIncidentDisplay(incident) {
  const normalized = normalizeIncident(incident);
  
  return {
    ...normalized,
    severityColor: getSeverityColor(normalized.severity),
    severityLabel: getSeverityLabel(normalized.severity),
    formattedTime: formatTimestamp(normalized.timestamp),
    displayName: `${normalized.incident_type} at ${normalized.location}`,
    displayDescription: normalized.description || '(No description)'
  };
}
