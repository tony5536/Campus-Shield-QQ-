/**
 * Hardened Incidents component with:
 * - Strict data contract validation
 * - Real-time updates (WebSocket + polling fallback)
 * - Error recovery
 * - Loading states
 * - Empty states
 * - Null guards
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { validateIncident, normalizeIncident, formatIncidentDisplay } from '../schemas/incident';
import api from '../services/api';
import { connectWithAutoReconnect } from '../config/wsConfig';
import '../styles/Incidents.css';

export default function IncidentsHardened() {
  // State
  const [incidents, setIncidents] = useState([]);
  const [filteredIncidents, setFilteredIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filters
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [searchText, setSearchText] = useState('');
  
  // Real-time
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
  const wsRef = useRef(null);
  const pollIntervalRef = useRef(null);

  // ============================================
  // Fetch Incidents
  // ============================================

  const fetchIncidents = useCallback(async () => {
    try {
      setError(null);
      
      const filters = {};
      if (filterStatus !== 'all') filters.status = filterStatus;
      if (filterSeverity !== 'all') filters.severity = filterSeverity;

      const result = await api.incidents.list(0, 100, filters);
      
      // Validate and normalize all incidents
      const validIncidents = (result.incidents || [])
        .filter(inc => {
          const validation = validateIncident(inc);
          if (!validation.valid) {
            console.warn('Invalid incident:', inc, validation.errors);
          }
          return validation.valid;
        })
        .map(normalizeIncident);

      setIncidents(validIncidents);
      console.log(`Loaded ${validIncidents.length} incidents`);
    } catch (err) {
      console.error('Failed to fetch incidents:', err);
      setError('Failed to load incidents. Please try again.');
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  }, [filterStatus, filterSeverity]);

  // ============================================
  // WebSocket for Real-Time Updates
  // ============================================

  const setupWebSocket = useCallback(() => {
    // Skip if WebSocket already created
    if (wsRef.current) return;

    try {
      // Use centralized helper; default path is '/ws/alerts' (backend canonical)
      const manager = connectWithAutoReconnect('/ws/alerts', {
        onOpen: () => {
          console.log('WebSocket connected');
          setIsWebSocketConnected(true);
          // Stop polling when WebSocket works
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
        },
        onMessage: (event) => {
          try {
            const data = JSON.parse(event.data);

            if (data.type === 'new_incident') {
              const newIncident = normalizeIncident(data.incident);
              setIncidents(prev => [newIncident, ...prev].slice(0, 100));
              console.log('New incident received via WebSocket');
            } else if (data.type === 'incident_update') {
              const updatedIncident = normalizeIncident(data.incident);
              setIncidents(prev =>
                prev.map(inc =>
                  inc.incident_id === updatedIncident.incident_id ? updatedIncident : inc
                )
              );
              console.log('Incident updated via WebSocket');
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        },
        onError: (error) => {
          console.error('WebSocket error:', error);
          setIsWebSocketConnected(false);
          // Fall back to polling
          startPolling();
        },
        onClose: () => {
          console.log('WebSocket disconnected');
          setIsWebSocketConnected(false);
          wsRef.current = null;
          // Fall back to polling
          startPolling();
        }
      });

      wsRef.current = manager;
    } catch (err) {
      console.error('Failed to setup WebSocket:', err);
      setIsWebSocketConnected(false);
      startPolling();
    }
  }, []);

  // ============================================
  // Polling Fallback
  // ============================================

  const startPolling = useCallback(() => {
    if (pollIntervalRef.current) return;

    console.log('Starting polling for incidents...');
    pollIntervalRef.current = setInterval(fetchIncidents, 5000); // Poll every 5s
  }, [fetchIncidents]);

  // ============================================
  // Filtering
  // ============================================

  useEffect(() => {
    let filtered = incidents;

    // Status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(i => (i.status || '').toLowerCase() === filterStatus.toLowerCase());
    }

    // Severity filter
    if (filterSeverity !== 'all') {
      filtered = filtered.filter(i => (i.severity || 'LOW').toUpperCase() === filterSeverity.toUpperCase());
    }

    // Search filter
    if (searchText.trim()) {
      const search = searchText.toLowerCase();
      filtered = filtered.filter(i =>
        (i.incident_type || '').toLowerCase().includes(search) ||
        (i.location || '').toLowerCase().includes(search) ||
        (i.description || '').toLowerCase().includes(search)
      );
    }

    setFilteredIncidents(filtered);
  }, [incidents, filterStatus, filterSeverity, searchText]);

  // ============================================
  // Lifecycle
  // ============================================

  useEffect(() => {
    // Initial fetch
    fetchIncidents();

    // Setup WebSocket with fallback to polling
    setupWebSocket();

    // Cleanup
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [fetchIncidents, setupWebSocket]);

  // ============================================
  // Rendering
  // ============================================

  if (loading) {
    return (
      <div className="incidents-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading incidents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="incidents-page">
      {/* Header */}
      <div className="incidents-header">
        <h1>Campus Incidents</h1>
        <div className="connection-status">
          <span className={`status-badge ${isWebSocketConnected ? 'connected' : 'polling'}`}>
            {isWebSocketConnected ? '🔴 Live' : '🟡 Polling'}
          </span>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={fetchIncidents}>Retry</button>
        </div>
      )}

      {/* Controls */}
      <div className="incidents-controls">
        <input
          type="text"
          placeholder="Search incidents..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          className="search-input"
        />
        
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="resolved">Resolved</option>
        </select>

        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Severity</option>
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
        </select>

        <button onClick={fetchIncidents} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {/* Incidents List */}
      <div className="incidents-list">
        {filteredIncidents.length === 0 ? (
          <div className="empty-state">
            <p>No incidents found</p>
            <small>Adjust filters or create a new incident</small>
          </div>
        ) : (
          filteredIncidents.map((incident) => {
            // Format for display
            const display = formatIncidentDisplay(incident);

            return (
              <div
                key={incident.incident_id}
                className={`incident-card severity-${display.severity.toLowerCase()}`}
              >
                <div className="incident-header">
                  <div className="incident-title">
                    <span className="severity-badge">{display.severityLabel}</span>
                    <h3>{display.incident_type}</h3>
                  </div>
                  <span className={`status-badge status-${display.status.toLowerCase()}`}>
                    {display.status}
                  </span>
                </div>

                <div className="incident-details">
                  <p><strong>Location:</strong> {display.location}</p>
                  {display.zone && <p><strong>Zone:</strong> {display.zone}</p>}
                  {display.source && <p><strong>Source:</strong> {display.source}</p>}
                  <p><strong>Description:</strong> {display.displayDescription}</p>
                  <p><strong>Time:</strong> {display.formattedTime}</p>
                </div>

                <div className="incident-actions">
                  <button className="btn-primary">View Details</button>
                  <button className="btn-secondary">Edit</button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Stats */}
      <div className="incidents-stats">
        <div className="stat">
          <span className="stat-label">Total</span>
          <span className="stat-value">{incidents.length}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Active</span>
          <span className="stat-value">
            {incidents.filter(i => (i.status || 'ACTIVE').toUpperCase() === 'ACTIVE').length}
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">High Severity</span>
          <span className="stat-value">
            {incidents.filter(i => (i.severity || 'LOW').toUpperCase() === 'HIGH').length}
          </span>
        </div>
      </div>
    </div>
  );
}
