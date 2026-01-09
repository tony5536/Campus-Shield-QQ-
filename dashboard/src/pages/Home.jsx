import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

export default function Home() {
  const [stats, setStats] = useState({
    totalIncidents: 0,
    activeAlerts: 0,
    camerasOnline: 0,
    avgResponseTime: '0m',
  });
  const [recentIncidents, setRecentIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch dashboard metrics from canonical endpoint
      const metricsData = await api.dashboard.getMetrics();
      
      // Fetch real incidents for recent list
      let incidents = [];
      try {
        const incidentsRes = await api.incidents.list(0, 5);
        incidents = incidentsRes.incidents || [];
      } catch (incErr) {
        console.warn('Failed to fetch incidents:', incErr);
      }
      
      // Set stats from real backend data - never use placeholders
      setStats({
        totalIncidents: metricsData.total_incidents ?? 0,
        activeAlerts: metricsData.active_alerts ?? 0,
        camerasOnline: metricsData.cameras_online ?? 0,
        avgResponseTime: metricsData.avg_response_time ?? '0m',
      });
      
      setRecentIncidents(incidents.slice(0, 5));
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      const status = err.response?.status || 'Error';
      const message = err.response?.data?.detail || err.message || 'Unable to load dashboard data';
      setError(`${status} - ${message}`);
      // Clear stats on error (don't show stale data)
      setStats({
        totalIncidents: 0,
        activeAlerts: 0,
        camerasOnline: 0,
        avgResponseTime: '0m',
      });
      setRecentIncidents([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading dashboard data...</div>;

  return (
    <div className="home-page">
      <h2>Dashboard Overview</h2>
      
      {error && <div className="error" style={{color: '#c0392b', padding: '12px', backgroundColor: '#fadbd8', borderRadius: '4px', marginBottom: '20px'}}>❌ {error}</div>}

      {/* Stats Cards */}
      <div className="dashboard-grid">
        <div className="card danger">
          <div className="stat-label">Active Alerts</div>
          <div className="stat-number">{stats.activeAlerts}</div>
          <p>Requires immediate attention</p>
        </div>

        <div className="card">
          <div className="stat-label">Total Incidents</div>
          <div className="stat-number">{stats.totalIncidents}</div>
          <p>This week</p>
        </div>

        <div className="card success">
          <div className="stat-label">Cameras Online</div>
          <div className="stat-number">{stats.camerasOnline}</div>
          <p>Actively monitoring</p>
        </div>

        <div className="card">
          <div className="stat-label">Avg Response Time</div>
          <div className="stat-number">{stats.avgResponseTime}</div>
          <p>From detection to alert</p>
        </div>
      </div>

      {/* Recent Incidents */}
      <div style={{ marginTop: '40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>📋 Recent Incidents</h3>
          <Link to="/incidents" className="btn btn-primary">View All</Link>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Location</th>
                <th>Timestamp</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recentIncidents.length > 0 ? (
                recentIncidents.map((incident) => (
                  <tr key={incident.incident_id}>
                    <td>{incident.incident_type || 'Unknown'}</td>
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
                    <td>
                      <Link to={`/incident/${incident.incident_id}`} className="btn btn-primary" style={{ fontSize: '12px', padding: '6px 12px' }}>
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', color: '#95a5a6' }}>
                    No incidents recorded
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{ marginTop: '40px', padding: '24px', background: 'white', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0,0,0,0.08)' }}>
        <h3>🎯 Quick Actions</h3>
        <div style={{ display: 'flex', gap: '16px', marginTop: '16px', flexWrap: 'wrap' }}>
          <Link to="/live-view" className="btn btn-primary">Start Live Monitoring</Link>
          <Link to="/incidents" className="btn btn-primary">View Incident History</Link>
          <button className="btn btn-danger" onClick={() => alert('Initiating emergency protocol...')}>
            🚨 Emergency Alert
          </button>
        </div>
      </div>
    </div>
  );
}
