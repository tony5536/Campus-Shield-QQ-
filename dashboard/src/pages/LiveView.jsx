import React, { useState, useEffect } from 'react';
import api from '../api';

export default function LiveView() {
  const [cameras, setCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [loading, setLoading] = useState(true);
  const [streaming, setStreaming] = useState(false);

  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    try {
      setLoading(true);
      const response = await api.getCameras();
      const data = response.data || [];
      setCameras(data);
      if (data.length > 0) setSelectedCamera(data[0]);
    } catch (err) {
      console.error('Error fetching cameras:', err);
      // Demo data fallback
      const demoCameras = [
        {
          id: 'CAM-001',
          name: 'Building A - Entrance',
          location: 'Building A, Ground Floor',
          status: 'online',
          resolution: '1920x1080',
          fps: 30,
          lastUpdate: new Date().toLocaleString(),
        },
        {
          id: 'CAM-002',
          name: 'Building A - East Wing',
          location: 'Building A, 2nd Floor',
          status: 'online',
          resolution: '1920x1080',
          fps: 30,
          lastUpdate: new Date().toLocaleString(),
        },
        {
          id: 'CAM-003',
          name: 'Campus Grounds - North',
          location: 'Campus Grounds, North Section',
          status: 'online',
          resolution: '2560x1440',
          fps: 60,
          lastUpdate: new Date().toLocaleString(),
        },
        {
          id: 'CAM-004',
          name: 'Main Hall - Atrium',
          location: 'Main Hall, Ground Floor',
          status: 'offline',
          resolution: '1920x1080',
          fps: 30,
          lastUpdate: '2 hours ago',
        },
        {
          id: 'CAM-005',
          name: 'Parking Lot C',
          location: 'Parking Area C',
          status: 'online',
          resolution: '1920x1080',
          fps: 15,
          lastUpdate: new Date().toLocaleString(),
        },
      ];
      setCameras(demoCameras);
      setSelectedCamera(demoCameras[0]);
    } finally {
      setLoading(false);
    }
  };

  const startStream = () => {
    if (selectedCamera) {
      setStreaming(true);
      // In production, establish WebRTC/RTSP connection here
      alert(`Starting stream from ${selectedCamera.name}`);
    }
  };

  const stopStream = () => {
    setStreaming(false);
    alert('Stream stopped');
  };

  if (loading) return <div className="loading">Loading cameras</div>;

  return (
    <div className="live-view-page">
      <h2>📹 Live Camera View</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '24px' }}>
        {/* Main Stream */}
        <div>
          <div
            style={{
              background: streaming ? '#000' : '#ecf0f1',
              borderRadius: '12px',
              overflow: 'hidden',
              boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
              marginBottom: '24px',
            }}
          >
            {selectedCamera && (
              <div
                style={{
                  width: '100%',
                  paddingBottom: '56.25%', // 16:9 aspect ratio
                  position: 'relative',
                  background: '#2c3e50',
                }}
              >
                {streaming ? (
                  <div
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#fff',
                      fontSize: '24px',
                    }}
                  >
                    📹 LIVE STREAM - {selectedCamera.name}
                  </div>
                ) : (
                  <div
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#95a5a6',
                    }}
                  >
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '48px', marginBottom: '16px' }}>▶️</div>
                      <p>Click "Start Stream" to begin monitoring</p>
                    </div>
                  </div>
                )}

                {/* Camera Info Overlay */}
                <div
                  style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
                    color: '#fff',
                    padding: '16px',
                    fontSize: '14px',
                  }}
                >
                  <strong>{selectedCamera.name}</strong>
                  <div style={{ fontSize: '12px', color: '#bdc3c7', marginTop: '4px' }}>
                    {selectedCamera.location}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Stream Controls */}
          <div className="card">
            <h3>⚙️ Stream Controls</h3>
            <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
              {!streaming ? (
                <button className="btn btn-success" onClick={startStream}>
                  ▶️ Start Stream
                </button>
              ) : (
                <button className="btn btn-danger" onClick={stopStream}>
                  ⏹️ Stop Stream
                </button>
              )}
              <button className="btn btn-primary" onClick={() => alert('Taking snapshot...')}>
                📷 Snapshot
              </button>
              <button className="btn btn-primary" onClick={() => alert('Recording started...')}>
                ⏺️ Record
              </button>
            </div>

            {selectedCamera && (
              <div style={{ marginTop: '16px', fontSize: '14px' }}>
                <p>
                  <strong>Resolution:</strong> {selectedCamera.resolution}
                </p>
                <p>
                  <strong>FPS:</strong> {selectedCamera.fps}
                </p>
                <p>
                  <strong>Status:</strong>{' '}
                  <span className={`badge ${selectedCamera.status === 'online' ? 'success' : 'danger'}`}>
                    {selectedCamera.status}
                  </span>
                </p>
              </div>
            )}
          </div>

          {/* AI Analysis Panel */}
          <div className="card" style={{ marginTop: '24px' }}>
            <h3>🤖 Real-time AI Analysis</h3>
            <div style={{ marginTop: '16px' }}>
              <div>
                <strong>Objects Detected:</strong>
                <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {['person', 'backpack', 'phone'].map((obj) => (
                    <span key={obj} className="badge success">
                      {obj}
                    </span>
                  ))}
                </div>
              </div>
              <div style={{ marginTop: '16px' }}>
                <strong>Threat Assessment:</strong>
                <div
                  style={{
                    marginTop: '8px',
                    padding: '12px',
                    background: '#ecf0f1',
                    borderRadius: '6px',
                    fontSize: '14px',
                  }}
                >
                  ✅ Normal activity detected. No threats identified.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Camera List Sidebar */}
        <div>
          <div className="card">
            <h3>Cameras</h3>
            <div style={{ marginTop: '16px', maxHeight: '600px', overflowY: 'auto' }}>
              {cameras.map((camera) => (
                <div
                  key={camera.id}
                  onClick={() => setSelectedCamera(camera)}
                  style={{
                    padding: '12px',
                    marginBottom: '8px',
                    background: selectedCamera?.id === camera.id ? '#e3f2fd' : '#fff',
                    border:
                      selectedCamera?.id === camera.id
                        ? '2px solid #3498db'
                        : '1px solid #ecf0f1',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                  }}
                  onMouseEnter={(e) => {
                    if (selectedCamera?.id !== camera.id) {
                      e.currentTarget.style.background = '#f8f9fa';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedCamera?.id !== camera.id) {
                      e.currentTarget.style.background = '#fff';
                    }
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div>
                      <strong style={{ fontSize: '13px', display: 'block' }}>
                        {camera.name}
                      </strong>
                      <span className={`badge ${camera.status === 'online' ? 'success' : 'danger'}`} style={{ marginTop: '4px' }}>
                        {camera.status}
                      </span>
                    </div>
                  </div>
                  <div style={{ fontSize: '11px', color: '#95a5a6', marginTop: '4px' }}>
                    {camera.location}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="card" style={{ marginTop: '16px' }}>
            <h3>Stats</h3>
            <div style={{ marginTop: '16px', fontSize: '14px' }}>
              <p>
                <strong>Total Cameras:</strong> {cameras.length}
              </p>
              <p>
                <strong>Online:</strong>{' '}
                <span style={{ color: '#27ae60', fontWeight: 'bold' }}>
                  {cameras.filter((c) => c.status === 'online').length}
                </span>
              </p>
              <p>
                <strong>Offline:</strong>{' '}
                <span style={{ color: '#e74c3c', fontWeight: 'bold' }}>
                  {cameras.filter((c) => c.status === 'offline').length}
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
