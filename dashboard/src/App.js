import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Incidents from './pages/Incidents';
import IncidentDetail from './pages/IncidentDetail';
import LiveView from './pages/LiveView';
import AIAssistant from './pages/AIAssistant';
import './App.css';

export default function App() {
  const [alerts, setAlerts] = useState(0);

  return (
    <Router>
      <div className="app-container">
        {/* Navigation Header */}
        <header className="navbar">
          <div className="navbar-brand">
            <h1>🛡️ CampusShield AI</h1>
            <p>Smart Campus Safety & Emergency Response</p>
          </div>
          <nav className="nav-links">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/incidents" className="nav-link">Incidents</Link>
            <Link to="/live-view" className="nav-link">Live View</Link>
            <Link to="/ai-assistant" className="nav-link">AI Assistant</Link>
            <div className="alert-badge" title="Active Alerts">🔔 {alerts}</div>
          </nav>
        </header>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/incident/:id" element={<IncidentDetail />} />
            <Route path="/live-view" element={<LiveView />} />
            <Route path="/ai-assistant" element={<AIAssistant />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="footer">
          <p>&copy; 2025 CampusShield AI. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

