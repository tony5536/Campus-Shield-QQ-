import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updateStatus, setUpdateStatus] = useState('');

  useEffect(() => {
    fetchIncidentDetail();
  }, [id]);

  const fetchIncidentDetail = async () => {
    try {
      setLoading(true);
      const response = await api.incidents.get(parseInt(id));
      setIncident(response);
    } catch (err) {
      console.error('Error fetching incident:', err);
      // Show error instead of demo data
      setIncident(null);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    try {
      // Call API to update status (if available)
      await api.getIncidents(); // Placeholder
      setIncident({ ...incident, status: newStatus });
      setUpdateStatus('');
      alert(`Incident status updated to: ${newStatus}`);
    } catch (err) {
      console.error('Error updating incident:', err);
      alert('Failed to update incident status');
    }
  };

  if (loading) return <div className="loading">Loading incident details</div>;

  if (!incident) {
    return (
      <div className="error">
        ❌ Incident not found
        <br />
        <button className="btn btn-primary" onClick={() => navigate('/incidents')} style={{ marginTop: '16px' }}>
          Back to Incidents
        </button>
      </div>
    );
  }

  return (
    <div className="incident-detail-page">
      <button className="btn btn-primary" onClick={() => navigate('/incidents')} style={{ marginBottom: '24px' }}>
        ← Back to Incidents
      </button>

      {/* Header */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div>
            <h2>{incident.incident_type || 'Incident'}</h2>
            <p style={{ color: '#7f8c8d', marginTop: '8px' }}>{incident.description || 'No description provided'}</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            {(() => {
              const sev = (incident.severity || 'low').toString().toLowerCase();
              return (
                <span className={`badge ${sev}`} style={{ marginRight: '8px' }}>
                  {sev === 'high' ? '🔴' : sev === 'medium' ? '🟠' : '🟢'} {sev}
                </span>
              );
            })()}
            {(() => {
              const statusLower = (incident.status || 'ACTIVE').toString().toLowerCase();
              return (
                <span className={`badge ${statusLower === 'active' ? 'active' : 'resolved'}`}>
                  {incident.status}
                </span>
              );
            })()}
          </div>
        </div>
      </div>

      {/* Details Grid */}
      <div className="dashboard-grid" style={{ marginBottom: '24px' }}>
        <div className="card">
          <div className="stat-label">Incident ID</div>
          <p style={{ fontWeight: '600', marginTop: '12px' }}>{incident.incident_id}</p>
        </div>

        <div className="card">
          <div className="stat-label">Location</div>
          <p style={{ fontWeight: '600', marginTop: '12px' }}>{incident.location || 'Unknown'}</p>
        </div>

        <div className="card">
          <div className="stat-label">Zone</div>
          <p style={{ fontWeight: '600', marginTop: '12px' }}>{incident.zone || 'N/A'}</p>
        </div>

        <div className="card">
          <div className="stat-label">Source</div>
          <p style={{ fontWeight: '600', marginTop: '12px' }}>{incident.source || 'N/A'}</p>
        </div>

        <div className="card">
          <div className="stat-label">Timestamp</div>
          <p style={{ fontWeight: '600', marginTop: '12px' }}>
            {new Date(incident.timestamp).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="card">
        <h3>Actions</h3>
        <div style={{ marginTop: '16px' }}>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={() => alert('Opening video evidence...')}>
              📹 View Video Evidence
            </button>
            <button className="btn btn-primary" onClick={() => alert('Downloading report...')}>
              📄 Download Report
            </button>
            <button className="btn btn-danger" onClick={() => alert('Sending notification to responders...')}>
              📢 Notify Responders
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
