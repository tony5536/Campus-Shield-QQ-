import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

export default function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [filteredIncidents, setFilteredIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');

  useEffect(() => {
    fetchIncidents();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [incidents, filterStatus, filterSeverity]);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const response = await api.incidents.list(0, 500);
      const data = response.incidents || [];
      setIncidents(data);
    } catch (err) {
      console.error('Error fetching incidents:', err);
      const status = err.response?.status || 'Error';
      const message = err.response?.data?.detail || err.message || 'Unable to load incidents';
      console.error(`HTTP ${status} - ${message}`);
      // Do NOT use demo data - show the error instead
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = incidents;

    if (filterStatus !== 'all') {
      filtered = filtered.filter((i) => (i.status || '').toString().toLowerCase() === filterStatus);
    }

    if (filterSeverity !== 'all') {
      filtered = filtered.filter((i) => {
        const sev = (i.severity || 'low').toString().toLowerCase();
        if (filterSeverity === 'critical') return sev === 'critical' || sev === 'high';
        return sev === filterSeverity;
      });
    }

    setFilteredIncidents(filtered);
  };

  if (loading) return <div className="loading">Loading incidents</div>;

  return (
    <div className="incidents-page">
      <h2>📋 Incident Management</h2>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <div>
            <label htmlFor="status-filter" style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#2c3e50' }}>
              Filter by Status:
            </label>
            <select
              id="status-filter"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid #bdc3c7',
                borderRadius: '6px',
                fontSize: '14px',
              }}
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="resolved">Resolved</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <div>
            <label htmlFor="severity-filter" style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#2c3e50' }}>
              Filter by Severity:
            </label>
            <select
              id="severity-filter"
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid #bdc3c7',
                borderRadius: '6px',
                fontSize: '14px',
              }}
            >
              <option value="all">All Severity</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <button
            onClick={fetchIncidents}
            className="btn btn-primary"
            style={{ marginTop: 'auto' }}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Incident</th>
              <th>Location</th>
              <th>Timestamp</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Assigned To</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredIncidents.length > 0 ? (
              filteredIncidents.map((incident) => (
                <tr key={incident.incident_id}>
                  <td style={{ fontWeight: '600' }}>{incident.incident_type || 'Unknown'}</td>
                  <td>{incident.location || 'Unknown'}</td>
                  <td>{new Date(incident.timestamp).toLocaleString()}</td>
                  <td>
                    {(() => {
                      const sev = (incident.severity || 'low').toString().toLowerCase();
                      return (
                        <span className={`badge ${sev}`}>
                          {sev === 'high' ? '🔴' : sev === 'medium' ? '🟠' : '🟢'} {sev}
                        </span>
                      );
                    })()}
                  </td>
                  <td>
                    {(() => {
                      const statusLower = (incident.status || 'ACTIVE').toString().toLowerCase();
                      return (
                        <span className={`badge ${statusLower === 'active' ? 'active' : 'resolved'}`}>
                          {incident.status}
                        </span>
                      );
                    })()}
                  </td>
                  <td>{incident.source || 'N/A'}</td>
                  <td>
                    <Link
                      to={`/incident/${incident.incident_id}`}
                      className="btn btn-primary"
                      style={{ fontSize: '12px', padding: '6px 12px' }}
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', color: '#95a5a6' }}>
                  No incidents found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Summary Stats */}
      <div className="dashboard-grid" style={{ marginTop: '40px' }}>
        <div className="card danger">
          <div className="stat-label">Active Incidents</div>
          <div className="stat-number">
            {filteredIncidents.filter((i) => (i.status || '').toString().toLowerCase() === 'active').length}
          </div>
        </div>

        <div className="card warning">
          <div className="stat-label">High Severity</div>
          <div className="stat-number">
            {filteredIncidents.filter((i) => {
              const sev = (i.severity || 'low').toString().toLowerCase();
              return sev === 'high';
            }).length}
          </div>
        </div>

        <div className="card success">
          <div className="stat-label">Resolved</div>
          <div className="stat-number">
            {filteredIncidents.filter((i) => (i.status || '').toString().toLowerCase() === 'resolved').length}
          </div>
        </div>
      </div>
    </div>
  );
}
