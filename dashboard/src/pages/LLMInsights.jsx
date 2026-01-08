import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './LLMInsights.css';

/**
 * LLMInsights Component
 * 
 * Advanced multi-tab interface for:
 * - Multi-turn Chatbot with context awareness
 * - Incident Summarization
 * - Report Generation
 * - Anomaly Explanation
 * - Historical Incident Retrieval
 */

const LLMInsights = () => {
  // ========================================================================
  // STATE MANAGEMENT
  // ========================================================================

  const [activeTab, setActiveTab] = useState('chat');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [config, setConfig] = useState({
    model: 'gpt-4',
    temperature: 0.7,
    max_tokens: 1500,
    top_p: 0.95,
  });

  // Chat state
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [conversationId] = useState(`conv_${Date.now()}`);
  const chatEndRef = useRef(null);

  // Summarization state
  const [summarizeInput, setSummarizeInput] = useState('');
  const [summarizeResult, setSummarizeResult] = useState('');
  const [summarizePeriod, setSummarizePeriod] = useState('day');

  // Report state
  const [reportType, setReportType] = useState('daily');
  const [reportResult, setReportResult] = useState('');
  const [reportStartDate, setReportStartDate] = useState('');

  // Anomaly state
  const [anomalyScore, setAnomalyScore] = useState(0.5);
  const [anomalyType, setAnomalyType] = useState('');
  const [anomalyArea, setAnomalyArea] = useState('');
  const [anomalyResult, setAnomalyResult] = useState('');

  // Historical incidents state
  const [historyQuery, setHistoryQuery] = useState('');
  const [historyResults, setHistoryResults] = useState([]);
  const [historyTopK, setHistoryTopK] = useState(5);

  // ========================================================================
  // API BASE URL
  // ========================================================================

  const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

  // ========================================================================
  // UTILITY FUNCTIONS
  // ========================================================================

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const handleError = (err) => {
    console.error('Error:', err);
    const errorMsg =
      err.response?.data?.detail ||
      err.message ||
      'An error occurred. Please try again.';
    setError(errorMsg);
  };

  // ========================================================================
  // LLM CONFIGURATION MANAGEMENT
  // ========================================================================

  const fetchConfig = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/llm/config`);
      setConfig(response.data);
    } catch (err) {
      console.warn('Could not fetch config:', err.message);
    }
  };

  const updateConfig = async (newConfig) => {
    try {
      setLoading(true);
      const response = await axios.put(`${API_BASE}/api/llm/config`, newConfig);
      setConfig(response.data);
      setError(null);
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  // ========================================================================
  // CHAT FUNCTIONS
  // ========================================================================

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = {
      role: 'user',
      content: chatInput,
      timestamp: new Date().toISOString(),
    };

    setChatHistory((prev) => [...prev, userMessage]);
    setChatInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE}/api/llm/chat`, {
        user_input: chatInput,
        conversation_id: conversationId,
        use_context: true,
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
      };

      setChatHistory((prev) => [...prev, assistantMessage]);
    } catch (err) {
      handleError(err);
      setChatHistory((prev) => prev.slice(0, -1)); // Remove user message on error
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await axios.delete(
        `${API_BASE}/api/llm/chat/history/${conversationId}`
      );
      setChatHistory([]);
      setError(null);
    } catch (err) {
      handleError(err);
    }
  };

  // ========================================================================
  // SUMMARIZATION FUNCTIONS
  // ========================================================================

  const summarizeIncidents = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${API_BASE}/api/llm/summarize`,
        {
          period: summarizePeriod,
          focus_area: summarizeInput || undefined,
        }
      );

      setSummarizeResult(response.data.summary);
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  // ========================================================================
  // REPORT GENERATION FUNCTIONS
  // ========================================================================

  const generateReport = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE}/api/llm/report`, {
        report_type: reportType,
        start_date: reportStartDate || undefined,
        include_recommendations: true,
      });

      setReportResult(response.data.report);
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  // ========================================================================
  // ANOMALY EXPLANATION FUNCTIONS
  // ========================================================================

  const explainAnomaly = async () => {
    if (!anomalyType.trim() || !anomalyArea.trim()) {
      setError('Please fill in all anomaly fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${API_BASE}/api/llm/explain-anomaly`,
        {
          anomaly_score: parseFloat(anomalyScore),
          anomaly_type: anomalyType,
          affected_area: anomalyArea,
          threshold: 0.7,
        }
      );

      // Defensive: ensure recommendations is an array
      const recommendations = Array.isArray(response.data.recommendations)
        ? response.data.recommendations
        : [];

      setAnomalyResult(
        `<strong>Risk Level: ${response.data.risk_level}</strong>\n\n${response.data.explanation}\n\n<strong>Recommendations:</strong>\n${recommendations.join('\n')}`
      );
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  // ========================================================================
  // HISTORICAL INCIDENTS FUNCTIONS
  // ========================================================================

  const searchHistoricalIncidents = async () => {
    if (!historyQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${API_BASE}/api/llm/historical-incidents`,
        {
          query: historyQuery,
          top_k: historyTopK,
        }
      );

      setHistoryResults(response.data.incidents);
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  // ========================================================================
  // RENDER FUNCTIONS FOR EACH TAB
  // ========================================================================

  const renderChatTab = () => (
    <div className="llm-tab-content chat-tab">
      <div className="chat-header">
        <h2>Campus Shield AI Chatbot</h2>
        <p>Ask questions about incidents, security patterns, and campus safety</p>
      </div>

      <div className="chat-messages">
        {chatHistory.length === 0 && (
          <div className="chat-welcome">
            <h3>👋 Welcome to Campus Shield AI</h3>
            <p>Ask me about:</p>
            <ul>
              <li>Recent incidents and patterns</li>
              <li>Security recommendations</li>
              <li>Historical incident analysis</li>
              <li>Campus safety trends</li>
            </ul>
          </div>
        )}

        {chatHistory.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <p>{msg.content}</p>
              <span className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
          placeholder="Type your question..."
          disabled={loading}
          className="chat-input"
        />
        <button
          onClick={sendChatMessage}
          disabled={loading || !chatInput.trim()}
          className="btn btn-primary"
        >
          {loading ? '⏳' : '📤'} Send
        </button>
        <button onClick={clearChat} className="btn btn-secondary">
          🗑️ Clear
        </button>
      </div>
    </div>
  );

  const renderSummarizeTab = () => (
    <div className="llm-tab-content summarize-tab">
      <div className="section-header">
        <h2>Incident Summarization</h2>
        <p>Generate concise summaries of security incidents</p>
      </div>

      <div className="form-group">
        <label>Time Period</label>
        <select
          value={summarizePeriod}
          onChange={(e) => setSummarizePeriod(e.target.value)}
          className="form-input"
        >
          <option value="day">Daily</option>
          <option value="week">Weekly</option>
          <option value="month">Monthly</option>
        </select>
      </div>

      <div className="form-group">
        <label>Focus Area (Optional)</label>
        <input
          type="text"
          value={summarizeInput}
          onChange={(e) => setSummarizeInput(e.target.value)}
          placeholder="e.g., Security, Health & Safety, Infrastructure"
          className="form-input"
        />
      </div>

      <button
        onClick={summarizeIncidents}
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? '⏳ Generating...' : '📊 Generate Summary'}
      </button>

      {summarizeResult && (
        <div className="result-box">
          <h3>Summary Result</h3>
          <div className="result-content">{summarizeResult}</div>
          <button
            onClick={() =>
              navigator.clipboard.writeText(summarizeResult)
            }
            className="btn btn-outline"
          >
            📋 Copy
          </button>
        </div>
      )}
    </div>
  );

  const renderReportTab = () => (
    <div className="llm-tab-content report-tab">
      <div className="section-header">
        <h2>Report Generation</h2>
        <p>Create professional security reports with insights and recommendations</p>
      </div>

      <div className="form-group">
        <label>Report Type</label>
        <select
          value={reportType}
          onChange={(e) => setReportType(e.target.value)}
          className="form-input"
        >
          <option value="daily">Daily Report</option>
          <option value="weekly">Weekly Report</option>
        </select>
      </div>

      <div className="form-group">
        <label>Start Date (Optional)</label>
        <input
          type="date"
          value={reportStartDate}
          onChange={(e) => setReportStartDate(e.target.value)}
          className="form-input"
        />
      </div>

      <button
        onClick={generateReport}
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? '⏳ Generating...' : '📄 Generate Report'}
      </button>

      {reportResult && (
        <div className="result-box">
          <h3>Generated Report</h3>
          <div className="result-content">{reportResult}</div>
          <div className="button-group">
            <button
              onClick={() =>
                navigator.clipboard.writeText(reportResult)
              }
              className="btn btn-outline"
            >
              📋 Copy
            </button>
            <button
              onClick={() => {
                const element = document.createElement('a');
                element.setAttribute(
                  'href',
                  'data:text/plain;charset=utf-8,' +
                    encodeURIComponent(reportResult)
                );
                element.setAttribute('download', `report_${Date.now()}.txt`);
                element.style.display = 'none';
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
              }}
              className="btn btn-outline"
            >
              ⬇️ Download
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const renderAnomalyTab = () => (
    <div className="llm-tab-content anomaly-tab">
      <div className="section-header">
        <h2>Anomaly Explanation</h2>
        <p>Understand detected anomalies with AI-powered analysis</p>
      </div>

      <div className="form-group">
        <label>Anomaly Score (0-1)</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={anomalyScore}
          onChange={(e) => setAnomalyScore(e.target.value)}
          className="form-input range-input"
        />
        <span className="score-display">Score: {parseFloat(anomalyScore).toFixed(1)}</span>
      </div>

      <div className="form-group">
        <label>Anomaly Type</label>
        <input
          type="text"
          value={anomalyType}
          onChange={(e) => setAnomalyType(e.target.value)}
          placeholder="e.g., Unauthorized Access, Unusual Traffic Pattern"
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label>Affected Area/Location</label>
        <input
          type="text"
          value={anomalyArea}
          onChange={(e) => setAnomalyArea(e.target.value)}
          placeholder="e.g., Building A, North Campus"
          className="form-input"
        />
      </div>

      <button
        onClick={explainAnomaly}
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? '⏳ Analyzing...' : '🔍 Explain Anomaly'}
      </button>

      {anomalyResult && (
        <div className="result-box anomaly-result">
          <h3>Analysis Result</h3>
          <div
            className="result-content"
            dangerouslySetInnerHTML={{
              __html: anomalyResult.replace(/\n/g, '<br/>'),
            }}
          />
          <button
            onClick={() =>
              navigator.clipboard.writeText(anomalyResult)
            }
            className="btn btn-outline"
          >
            📋 Copy
          </button>
        </div>
      )}
    </div>
  );

  const renderHistoryTab = () => (
    <div className="llm-tab-content history-tab">
      <div className="section-header">
        <h2>Historical Incident Retrieval</h2>
        <p>Search similar incidents from historical data</p>
      </div>

      <div className="form-group">
        <label>Search Query</label>
        <input
          type="text"
          value={historyQuery}
          onChange={(e) => setHistoryQuery(e.target.value)}
          placeholder="e.g., Unauthorized access, DDoS attack"
          className="form-input"
          onKeyPress={(e) =>
            e.key === 'Enter' && searchHistoricalIncidents()
          }
        />
      </div>

      <div className="form-group">
        <label>Results to Return</label>
        <input
          type="number"
          min="1"
          max="20"
          value={historyTopK}
          onChange={(e) => setHistoryTopK(parseInt(e.target.value))}
          className="form-input"
        />
      </div>

      <button
        onClick={searchHistoricalIncidents}
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? '⏳ Searching...' : '🔎 Search'}
      </button>

      {historyResults.length > 0 && (
        <div className="result-box">
          <h3>Found {historyResults.length} Similar Incidents</h3>
          <div className="incidents-list">
            {historyResults.map((incident, idx) => (
              <div key={idx} className="incident-card">
                <div className="incident-header">
                  <span className="incident-type">
                    {incident.type}
                  </span>
                  <span
                    className={`incident-severity severity-${
                      incident.severity > 0.7
                        ? 'high'
                        : incident.severity > 0.4
                        ? 'medium'
                        : 'low'
                    }`}
                  >
                    Severity: {(incident.severity * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="incident-details">
                  <p>
                    <strong>Location:</strong> {incident.location}
                  </p>
                  <p>
                    <strong>Time:</strong> {new Date(incident.timestamp).toLocaleString()}
                  </p>
                  <p>
                    <strong>Similarity:</strong> {(incident.similarity_score * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderConfigTab = () => (
    <div className="llm-tab-content config-tab">
      <div className="section-header">
        <h2>LLM Configuration</h2>
        <p>Customize model behavior and parameters</p>
      </div>

      <div className="config-grid">
        <div className="config-item">
          <label>Model</label>
          <select
            value={config.model}
            onChange={(e) =>
              updateConfig({
                ...config,
                model: e.target.value,
              })
            }
            className="form-input"
          >
            <option value="gpt-4">GPT-4 (Advanced)</option>
            <option value="gpt-4-turbo">GPT-4 Turbo</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
          </select>
        </div>

        <div className="config-item">
          <label>Temperature ({config.temperature})</label>
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={config.temperature}
            onChange={(e) =>
              updateConfig({
                ...config,
                temperature: parseFloat(e.target.value),
              })
            }
            className="form-input range-input"
          />
          <small>Higher = more creative</small>
        </div>

        <div className="config-item">
          <label>Max Tokens ({config.max_tokens})</label>
          <input
            type="range"
            min="100"
            max="4000"
            step="100"
            value={config.max_tokens}
            onChange={(e) =>
              updateConfig({
                ...config,
                max_tokens: parseInt(e.target.value),
              })
            }
            className="form-input range-input"
          />
        </div>

        <div className="config-item">
          <label>Top-P ({config.top_p})</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={config.top_p}
            onChange={(e) =>
              updateConfig({
                ...config,
                top_p: parseFloat(e.target.value),
              })
            }
            className="form-input range-input"
          />
        </div>
      </div>
    </div>
  );

  // ========================================================================
  // MAIN RENDER
  // ========================================================================

  return (
    <div className="llm-insights-container">
      <div className="llm-header">
        <h1>🚀 Campus Shield AI - Advanced Insights</h1>
        <p>Powered by LangChain & GPT-4 • Multi-turn conversations with context awareness</p>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button
            onClick={() => setError(null)}
            className="close-btn"
          >
            ✕
          </button>
        </div>
      )}

      <div className="tabs-container">
        <div className="tabs-header">
          <button
            className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`tab-button ${activeTab === 'summarize' ? 'active' : ''}`}
            onClick={() => setActiveTab('summarize')}
          >
            📊 Summarize
          </button>
          <button
            className={`tab-button ${activeTab === 'report' ? 'active' : ''}`}
            onClick={() => setActiveTab('report')}
          >
            📄 Reports
          </button>
          <button
            className={`tab-button ${activeTab === 'anomaly' ? 'active' : ''}`}
            onClick={() => setActiveTab('anomaly')}
          >
            🔍 Anomalies
          </button>
          <button
            className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            📚 History
          </button>
          <button
            className={`tab-button ${activeTab === 'config' ? 'active' : ''}`}
            onClick={() => setActiveTab('config')}
          >
            ⚙️ Config
          </button>
        </div>

        <div className="tabs-content">
          {activeTab === 'chat' && renderChatTab()}
          {activeTab === 'summarize' && renderSummarizeTab()}
          {activeTab === 'report' && renderReportTab()}
          {activeTab === 'anomaly' && renderAnomalyTab()}
          {activeTab === 'history' && renderHistoryTab()}
          {activeTab === 'config' && renderConfigTab()}
        </div>
      </div>
    </div>
  );
};

export default LLMInsights;
