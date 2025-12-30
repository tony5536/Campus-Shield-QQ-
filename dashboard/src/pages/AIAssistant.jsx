import React, { useState, useEffect, useRef } from 'react';
import api from '../api';
import '../App.css';

export default function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastAnalysis, setLastAnalysis] = useState(null);

  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const getSeverityClass = (severity) => {
    const sev = severity?.toLowerCase() || 'medium';
    if (sev === 'high') return 'high';
    if (sev === 'medium') return 'medium';
    if (sev === 'low') return 'low';
    return 'medium';
  };

  const getSeverityEmoji = (severity) => {
    const sev = severity?.toLowerCase() || 'medium';
    if (sev === 'high') return '🔴';
    if (sev === 'medium') return '🟠';
    if (sev === 'low') return '🟢';
    return '🟠';
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const queryText = inputValue.trim();
    setInputValue('');
    setLoading(true);
    setError(null);
    setLastAnalysis(null);

    try {
      // Use the new /api/ai/assist endpoint for hackathon demo
      const response = await api.aiAssist(queryText);
      
      const analysis = response.data?.analysis || {};
      setLastAnalysis(analysis);

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: analysis.summary || 'Analysis completed.',
        analysis: analysis,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to get AI response. Please try again.';
      setError(errorMsg);
      
      // Fallback response - NEVER crash during demo
      const fallbackAnalysis = {
        summary: 'AI analysis temporarily unavailable. Please review the incident manually.',
        severity: 'Medium',
        recommended_action: 'Follow standard security protocols.',
        confidence: 'N/A'
      };
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: fallbackAnalysis.summary,
        analysis: fallbackAnalysis,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
      setLastAnalysis(fallbackAnalysis);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleQuickAction = (query) => {
    setInputValue(query);
    // Auto-submit after a brief delay
    setTimeout(() => {
      const form = document.querySelector('.chat-input-form');
      if (form) {
        const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
        form.dispatchEvent(submitEvent);
      }
    }, 100);
  };

  return (
    <div className="ai-assistant-page">
      <div className="card" style={{ marginBottom: '24px' }}>
        <h2>🤖 AI Incident Analyzer</h2>
        <p style={{ color: '#7f8c8d', marginTop: '8px' }}>
          Describe any incident or security concern. AI will analyze severity and recommend immediate actions.
        </p>
      </div>

      {/* Quick Demo Actions */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h3 style={{ marginBottom: '12px', fontSize: '16px' }}>Quick Demo Queries</h3>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary"
            onClick={() => handleQuickAction('Unauthorized person detected in building A after hours')}
            style={{ fontSize: '13px', padding: '8px 16px' }}
          >
            🔴 High Severity Demo
          </button>
          <button
            className="btn btn-primary"
            onClick={() => handleQuickAction('Suspicious activity near parking lot')}
            style={{ fontSize: '13px', padding: '8px 16px' }}
          >
            🟠 Medium Severity Demo
          </button>
          <button
            className="btn btn-primary"
            onClick={() => handleQuickAction('Vehicle parked in wrong zone')}
            style={{ fontSize: '13px', padding: '8px 16px' }}
          >
            🟢 Low Severity Demo
          </button>
        </div>
      </div>

      {/* Last Analysis Result Card - VISUAL IMPACT */}
      {lastAnalysis && (
        <div className="card" style={{ 
          marginBottom: '24px', 
          borderLeft: `5px solid ${
            lastAnalysis.severity?.toLowerCase() === 'high' ? '#e74c3c' :
            lastAnalysis.severity?.toLowerCase() === 'medium' ? '#f39c12' : '#27ae60'
          }`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <span className={`severity-badge ${getSeverityClass(lastAnalysis.severity)}`}>
              {getSeverityEmoji(lastAnalysis.severity)} {lastAnalysis.severity || 'Medium'}
            </span>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>
              Confidence: {lastAnalysis.confidence || 'N/A'}
            </span>
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <h4 style={{ color: '#2c3e50', marginBottom: '8px' }}>📋 Summary</h4>
            <p style={{ color: '#34495e', lineHeight: '1.6' }}>{lastAnalysis.summary}</p>
          </div>
          
          <div style={{ 
            padding: '16px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px',
            borderLeft: `4px solid ${
              lastAnalysis.severity?.toLowerCase() === 'high' ? '#e74c3c' :
              lastAnalysis.severity?.toLowerCase() === 'medium' ? '#f39c12' : '#27ae60'
            }`
          }}>
            <h4 style={{ color: '#2c3e50', marginBottom: '8px' }}>💡 Recommended Action</h4>
            <p style={{ color: '#34495e', lineHeight: '1.6', fontWeight: '500' }}>
              {lastAnalysis.recommended_action}
            </p>
          </div>
        </div>
      )}

      {/* Chat Container */}
      <div className="card" style={{ padding: 0, height: '500px', display: 'flex', flexDirection: 'column' }}>
        {/* Messages Area */}
        <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#95a5a6', marginTop: '100px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🛡️</div>
              <h3 style={{ color: '#2c3e50', marginBottom: '8px' }}>AI-Powered Incident Analysis</h3>
              <p>Describe any security incident and get instant AI analysis with severity assessment.</p>
              <p style={{ marginTop: '16px', fontSize: '14px' }}>
                Try: "Unauthorized entry detected" or "Suspicious activity in parking lot"
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.role}`}
                style={{
                  marginBottom: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: message.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <div
                  className="message-bubble"
                  style={{
                    maxWidth: '70%',
                    padding: '12px 16px',
                    borderRadius: '18px',
                    backgroundColor:
                      message.role === 'user'
                        ? '#3498db'
                        : '#ecf0f1',
                    color:
                      message.role === 'user'
                        ? 'white'
                        : '#2c3e50',
                    wordWrap: 'break-word',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {message.content}
                </div>
                <div
                  style={{
                    fontSize: '11px',
                    color: '#95a5a6',
                    marginTop: '4px',
                    padding: '0 4px',
                  }}
                >
                  {formatTime(message.timestamp)}
                </div>
              </div>
            ))
          )}
          
          {loading && (
            <div className="message assistant" style={{ marginBottom: '16px' }}>
              <div
                className="message-bubble"
                style={{
                  padding: '12px 16px',
                  borderRadius: '18px',
                  backgroundColor: '#ecf0f1',
                  color: '#2c3e50',
                }}
              >
                <span style={{ marginRight: '8px' }}>Analyzing incident...</span>
                <span className="loading" style={{ display: 'inline-block' }}></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div
          style={{
            borderTop: '1px solid #ecf0f1',
            padding: '16px 20px',
            backgroundColor: '#f8f9fa',
          }}
        >
          {error && (
            <div
              className="error"
              style={{
                marginBottom: '12px',
                padding: '12px',
                fontSize: '14px',
              }}
            >
              ⚠️ {error}
            </div>
          )}
          
          <form onSubmit={sendMessage} className="chat-input-form">
            <div style={{ display: 'flex', gap: '12px' }}>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Describe an incident: e.g., 'Unauthorized entry detected in Building A'..."
                disabled={loading}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '1px solid #bdc3c7',
                  borderRadius: '24px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.3s',
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#3498db';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#bdc3c7';
                }}
              />
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !inputValue.trim()}
                style={{
                  padding: '12px 24px',
                  borderRadius: '24px',
                  fontSize: '14px',
                  cursor: loading || !inputValue.trim() ? 'not-allowed' : 'pointer',
                  opacity: loading || !inputValue.trim() ? 0.6 : 1,
                }}
              >
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
