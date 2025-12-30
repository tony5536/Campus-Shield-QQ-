import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

export default function Home() {
  const [stats, setStats] = useState({
    totalIncidents: 0,
    activeAlerts: 0,
    camerasOnline: 0,
    avgResponseTime: '0s',
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
      
      // Fetch incidents
      const incidentsRes = await api.getIncidents();
      const incidents = incidentsRes.data || [];
      
      // Fetch cameras
      const camerasRes = await api.getCameras();
      const cameras = camerasRes.data || [];
      
      // Calculate stats
      const activeIncidents = incidents.filter(i => i.status === 'active').length;
      const closedIncidents = incidents.filter(i => i.status === 'closed').length;
      
      setStats({
        totalIncidents: incidents.length,
        activeAlerts: activeIncidents,
        camerasOnline: cameras.filter(c => c.status === 'online').length,
        avgResponseTime: '2m 34s',
      });
      
      setRecentIncidents(incidents.slice(0, 5));
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Using demo data.');
      
      // Demo data fallback
      setStats({
        totalIncidents: 12,
        activeAlerts: 3,
        camerasOnline: 24,
        avgResponseTime: '2m 34s',
      });
      
      setRecentIncidents([
        {
          id: 1,
          title: 'Unauthorized Entry - Building A',
          timestamp: new Date(Date.now() - 15 * 60000).toLocaleString(),
          severity: 'critical',
          status: 'active',
        },
        {
          id: 2,
          title: 'Unusual Activity - Campus Grounds',
          timestamp: new Date(Date.now() - 45 * 60000).toLocaleString(),
          severity: 'high',
          status: 'active',
        },
        {
          id: 3,
          title: 'Crowd Gathering - Main Hall',
          timestamp: new Date(Date.now() - 120 * 60000).toLocaleString(),
          severity: 'medium',
          status: 'resolved',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading dashboard data</div>;

  return (
    <div className="home-page">
      <h2>Dashboard Overview</h2>
      
      {error && <div className="error">⚠️ {error}</div>}

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
                <th>Incident</th>
                <th>Timestamp</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recentIncidents.length > 0 ? (
                recentIncidents.map((incident) => (
                  <tr key={incident.id}>
                    <td>{incident.title}</td>
                    <td>{incident.timestamp}</td>
                    <td>
                      <span className={`badge ${incident.severity?.toLowerCase() || 'medium'}`}>
                        {incident.severity === 'critical' || incident.severity === 'high' ? '🔴' : 
                         incident.severity === 'medium' ? '🟠' : '🟢'} {incident.severity || 'Medium'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${incident.status === 'active' ? 'active' : 'low'}`}>
                        {incident.status}
                      </span>
                    </td>
                    <td>
                      <Link to={`/incident/${incident.id}`} className="btn btn-primary" style={{ fontSize: '12px', padding: '6px 12px' }}>
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', color: '#95a5a6' }}>
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
