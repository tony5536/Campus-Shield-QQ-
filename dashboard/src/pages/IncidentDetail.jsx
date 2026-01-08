import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

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
      const response = await api.getIncident(id);
      setIncident(response.data);
    } catch (err) {
      console.error('Error fetching incident:', err);
      // Demo data fallback
      setIncident({
        id: parseInt(id),
        title: 'Unauthorized Entry - Building A',
        description: 'Motion detected at rear entrance after hours. Potential security breach.',
        location: 'Building A, 2nd Floor, East Wing',
        timestamp: new Date(Date.now() - 15 * 60000).toLocaleString(),
        severity: 'critical',
        status: 'active',
        assignedTo: 'Security Team 1',
        cameras: ['CAM-001', 'CAM-002'],
        aiAnalysis: {
          objectsDetected: ['person', 'backpack'],
          threatScore: 0.87,
          confidence: 0.94,
          summary: 'Unauthorized personnel detected with suspicious behavior patterns.',
        },
        timeline: [
          { time: '15:35:42', event: 'Motion detected', status: 'alert' },
          { time: '15:35:55', event: 'Person identified', status: 'warning' },
          { time: '15:36:10', event: 'Alert sent to security team', status: 'info' },
          { time: '15:37:30', event: 'Security team en route', status: 'info' },
        ],
      });
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
  // Defensive defaults for optional fields returned by the backend
  const cameras = Array.isArray(incident.cameras) ? incident.cameras : [];
  const timeline = Array.isArray(incident.timeline) ? incident.timeline : [];
  const ai = incident.aiAnalysis || {};
  const objectsDetected = Array.isArray(ai.objectsDetected) ? ai.objectsDetected : [];
  const threatScore = typeof ai.threatScore === 'number' ? ai.threatScore : null;
  const confidence = typeof ai.confidence === 'number' ? ai.confidence : null;
  return (
    <div className="incident-detail-page">
      <button className="btn btn-primary" onClick={() => navigate('/incidents')} style={{ marginBottom: '24px' }}>
        ← Back to Incidents
      </button>

      {/* Header */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div>
            <h2>{incident.title}</h2>
            <p style={{ color: '#7f8c8d', marginTop: '8px' }}>{incident.description}</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            {(() => {
              const sev = (incident?.severity ?? 'LOW').toString().toLowerCase();
              return (
                <span className={`badge ${sev || 'medium'}`} style={{ marginRight: '8px' }}>
                  {sev === 'critical' || sev === 'high' ? '🔴' : sev === 'medium' ? '🟠' : '🟢'} {incident.severity ?? 'Medium'}
                </span>
              );
            })()}
            {(() => {
              const statusLower = (incident?.status ?? 'ACTIVE').toString().toLowerCase();
              return (
                <span className={`badge ${statusLower === 'active' ? 'active' : 'low'}`}>
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
          <div className="stat-label">Location</div>
          <p style={{ fontWeight: '600', marginTop: '12px' }}>{incident.location}</p>
        </div>

        <div className="card">
          <div className="stat-label">Timestamp</div>
          <p style={{ fontWeight: '600', marginTop: '12px' }}>{incident.timestamp}</p>
        </div>

        <div className="card">
          <div className="stat-label">Assigned To</div>
          <p style={{ fontWeight: '600', marginTop: '12px' }}>{incident.assignedTo}</p>
        </div>

        <div className="card">
          <div className="stat-label">Cameras Involved</div>
          <p style={{ fontWeight: '600', marginTop: '12px' }}>
            {cameras.length > 0 ? cameras.join(', ') : 'N/A'}
          </p>
        </div>
      </div>

      {/* AI Analysis */}
      {incident.aiAnalysis && (
        <div className="card" style={{ marginBottom: '24px', background: '#f8f9fa' }}>
          <h3>🤖 AI Analysis Results</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '16px' }}>
            <div>
              <div className="stat-label">Threat Score</div>
              <div className="stat-number" style={{ color: threatScore !== null && threatScore > 0.7 ? '#e74c3c' : '#27ae60' }}>
                {threatScore !== null ? `${(threatScore * 100).toFixed(0)}%` : 'N/A'}
              </div>
            </div>
            <div>
              <div className="stat-label">Confidence</div>
              <div className="stat-number" style={{ color: '#3498db' }}>
                {confidence !== null ? `${(confidence * 100).toFixed(0)}%` : 'N/A'}
              </div>
            </div>
          </div>
          <div style={{ marginTop: '16px' }}>
            <p>
              <strong>Objects Detected:</strong> {objectsDetected.length > 0 ? objectsDetected.join(', ') : 'N/A'}
            </p>
            <p style={{ marginTop: '8px' }}>
              <strong>Summary:</strong> {incident.aiAnalysis.summary}
            </p>
          </div>
        </div>
      )}

      {/* Timeline */}
      {timeline.length > 0 && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <h3>📅 Incident Timeline</h3>
          <div style={{ marginTop: '16px' }}>
            {timeline.map((item, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  gap: '16px',
                  padding: '12px 0',
                  borderBottom: idx < timeline.length - 1 ? '1px solid #ecf0f1' : 'none',
                }}
              >
                <div style={{ fontWeight: '600', color: '#3498db', minWidth: '80px' }}>
                  {item.time}
                </div>
                <div>
                  <span className={`badge ${item.status}`}>{item.status}</span>
                  <p style={{ marginTop: '4px' }}>{item.event}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="card">
        <h3>Actions</h3>
        <div style={{ marginTop: '16px' }}>
          {(incident?.status ?? 'ACTIVE').toString().toLowerCase() === 'active' && (
            <div style={{ marginBottom: '16px' }}>
              <label htmlFor="status-select" style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>
                Update Status:
              </label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <select
                  id="status-select"
                  value={updateStatus}
                  onChange={(e) => setUpdateStatus(e.target.value)}
                  style={{
                    padding: '8px 12px',
                    border: '1px solid #bdc3c7',
                    borderRadius: '6px',
                    flex: 1,
                  }}
                >
                  <option value="">Select new status...</option>
                  <option value="resolved">Resolved</option>
                  <option value="pending">Pending</option>
                  <option value="investigating">Investigating</option>
                </select>
                <button
                  className="btn btn-success"
                  onClick={() => handleStatusUpdate(updateStatus)}
                  disabled={!updateStatus}
                >
                  Update
                </button>
              </div>
            </div>
          )}

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
