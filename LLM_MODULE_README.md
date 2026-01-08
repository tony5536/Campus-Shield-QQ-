# 🚀 CampusShield AI - Advanced LLM Integration Module

## Overview

This module provides a **futuristic, production-ready LLM integration** for the CampusShield AI system, enabling:

✨ **Multi-turn Chat** - Context-aware conversations with historical incident retrieval
📊 **Incident Summarization** - Generate concise summaries of security incidents
📄 **Report Generation** - Professional daily/weekly security reports
🔍 **Anomaly Explanation** - AI-powered analysis of detected anomalies
📚 **Historical Retrieval** - Vector-based semantic search of past incidents
⚙️ **Configurable LLM** - Dynamic model switching and parameter tuning

---

## Architecture

### Backend Components

#### 1. **Core LLM Module** (`ai/llm_utils.py`)
- `LLMChainManager`: Manages LangChain chains and model configuration
- `MultiTurnChat`: Handles conversation context and memory
- `IncidentSummarizer`: Generates concise incident summaries
- `ReportGenerator`: Creates professional security reports
- `AnomalyExplainer`: Explains detected anomalies with context
- `LLMService`: Unified service for all LLM operations

#### 2. **Vector Store** (`ai/vector_store.py`)
- **FAISS Backend**: Local, lightweight vector database
- **Memory Backend**: For development and testing
- **Pinecone/Weaviate**: Ready for integration
- Semantic similarity search for historical incidents
- Configurable embedding models (OpenAI embeddings)

#### 3. **Prompt Templates** (`ai/prompts.py`)
- Chat and FAQ templates
- Summarization prompts
- Daily/weekly report templates
- Anomaly explanation prompts
- Helper functions for formatting data

#### 4. **FastAPI Routes** (`Backend/app/api/routes/llm.py`)
- `/api/llm/health` - Service health check
- `/api/llm/chat` - Multi-turn chat endpoint
- `/api/llm/chat/history/{conversation_id}` - Chat history retrieval
- `/api/llm/summarize` - Incident summarization
- `/api/llm/report` - Report generation
- `/api/llm/explain-anomaly` - Anomaly explanation
- `/api/llm/historical-incidents` - Historical incident retrieval
- `/api/llm/config` - Get/update LLM configuration
- `/api/llm/models` - List available models

### Frontend Components

#### **LLMInsights Component** (`dashboard/src/pages/LLMInsights.jsx`)

Multi-tab interface with:
- **💬 Chat Tab**: Real-time multi-turn conversations
- **📊 Summarize Tab**: Period-based incident summarization
- **📄 Reports Tab**: Professional report generation
- **🔍 Anomaly Tab**: Anomaly detection analysis
- **📚 History Tab**: Semantic search of historical incidents
- **⚙️ Config Tab**: Dynamic LLM configuration

---

## Installation & Setup

### 1. Backend Dependencies

```bash
# Install required packages
pip install -r Backend/requirements.txt
```

Key dependencies:
```
langchain==0.1.20
langchain-openai==0.0.11
openai==1.21.0
faiss-cpu==1.7.4
numpy==1.24.3
```

### 2. Environment Configuration

Create `.env` file in backend root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here

# LLM Configuration (Optional)
LLM_MODEL=gpt-4              # or gpt-4-turbo, gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1500
LLM_TOP_P=0.95

# Vector Store Configuration
VECTOR_STORE_TYPE=faiss      # or memory, pinecone
VECTOR_STORE_PATH=./data/faiss_index
```

### 3. Frontend Integration

Add the LLMInsights component to your React app:

```jsx
import LLMInsights from './pages/LLMInsights';

function App() {
  return (
    <Routes>
      <Route path="/llm-insights" element={<LLMInsights />} />
    </Routes>
  );
}
```

Update `dashboard/src/config.js`:
```javascript
export const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';
```

Set environment variable:
```bash
REACT_APP_API_BASE=http://localhost:8000
```

### 4. Initialize Vector Store

```python
from ai.vector_store import get_vector_store
from ai.llm_utils import get_llm_service

# Initialize vector store
vector_store = get_vector_store("faiss")

# Store incidents from database
# vector_store.store_incidents(incidents)

# Get LLM service
service = get_llm_service()
```

---

## API Endpoints

### Health Check

```bash
GET /api/llm/health
```

Response:
```json
{
  "status": "healthy",
  "service": "LLM Module",
  "model": "gpt-4"
}
```

### Multi-Turn Chat

```bash
POST /api/llm/chat
```

Request:
```json
{
  "user_input": "What are the recent security incidents?",
  "conversation_id": "conv_123456",
  "use_context": true
}
```

Response:
```json
{
  "response": "Based on recent data...",
  "conversation_id": "conv_123456",
  "chat_history": [
    {
      "role": "user",
      "content": "What are the recent security incidents?",
      "timestamp": "2025-01-15T10:30:00.000Z"
    },
    {
      "role": "assistant",
      "content": "Based on recent data...",
      "timestamp": "2025-01-15T10:30:05.000Z"
    }
  ]
}
```

### Incident Summarization

```bash
POST /api/llm/summarize
```

Request:
```json
{
  "period": "day",
  "focus_area": "Security"
}
```

Response:
```json
{
  "summary": "Today's security summary...",
  "incident_count": 5,
  "generated_at": "2025-01-15T10:30:00.000Z"
}
```

### Report Generation

```bash
POST /api/llm/report
```

Request:
```json
{
  "report_type": "daily",
  "start_date": "2025-01-15",
  "include_recommendations": true
}
```

Response:
```json
{
  "report": "DAILY SECURITY REPORT...",
  "report_type": "daily",
  "generated_at": "2025-01-15T10:30:00.000Z"
}
```

### Anomaly Explanation

```bash
POST /api/llm/explain-anomaly
```

Request:
```json
{
  "anomaly_score": 0.85,
  "anomaly_type": "Unauthorized Access Attempt",
  "affected_area": "Building A - Server Room",
  "threshold": 0.7
}
```

Response:
```json
{
  "explanation": "This anomaly represents an unusual access pattern...",
  "risk_level": "High",
  "recommendations": [
    "Review access logs immediately",
    "Verify user identity and authorization",
    "Consider temporary access restriction"
  ]
}
```

### Historical Incident Retrieval

```bash
POST /api/llm/historical-incidents
```

Request:
```json
{
  "query": "unauthorized access",
  "top_k": 5,
  "min_severity": 0.5
}
```

Response:
```json
{
  "incidents": [
    {
      "incident_id": "123",
      "type": "Unauthorized Access",
      "location": "Building A",
      "severity": 0.8,
      "timestamp": "2025-01-14T15:30:00.000Z",
      "similarity_score": 0.95
    }
  ],
  "query": "unauthorized access",
  "count": 1
}
```

### Configuration Management

**Get Config:**
```bash
GET /api/llm/config
```

**Update Config:**
```bash
PUT /api/llm/config
```

Request:
```json
{
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1500,
  "top_p": 0.95
}
```

---

## Usage Examples

### Python Backend Usage

```python
from ai.llm_utils import get_llm_service, LLMConfig
from ai.vector_store import get_vector_store

# Initialize service
service = get_llm_service()

# ===== MULTI-TURN CHAT =====
response = service.chat.chat(
    user_input="What happened today?",
    conversation_id="admin_1"
)
print(response)

# Get chat history
history = service.chat.get_history()

# ===== SUMMARIZATION =====
summary = service.summarizer.summarize_incidents(
    incidents=[
        {
            'id': 1,
            'incident_type': 'Unauthorized Access',
            'location': 'Lab B',
            'severity': 0.8,
            'description': 'Failed login attempts detected'
        }
    ],
    focus="Security"
)
print(summary)

# ===== REPORT GENERATION =====
report = service.reporter.generate_daily_report(
    incidents=daily_incidents,
    report_date="2025-01-15"
)
print(report)

# ===== ANOMALY EXPLANATION =====
explanation = service.explainer.explain_anomaly(
    anomaly_score=0.85,
    anomaly_type="Unusual Network Traffic",
    affected_area="Campus Network",
    threshold=0.7
)
print(explanation)

# ===== CONFIGURATION UPDATE =====
new_config = LLMConfig(
    model="gpt-4-turbo",
    temperature=0.5,
    max_tokens=2000
)
service.update_config(new_config)
```

### JavaScript/React Usage

```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// Send chat message
async function sendMessage(userInput) {
  const response = await axios.post(`${API_BASE}/api/llm/chat`, {
    user_input: userInput,
    conversation_id: 'user_123',
    use_context: true
  });
  return response.data.response;
}

// Generate report
async function generateReport(type) {
  const response = await axios.post(`${API_BASE}/api/llm/report`, {
    report_type: type,
    include_recommendations: true
  });
  return response.data.report;
}

// Search historical incidents
async function searchIncidents(query) {
  const response = await axios.post(
    `${API_BASE}/api/llm/historical-incidents`,
    {
      query: query,
      top_k: 5
    }
  );
  return response.data.incidents;
}
```

---

## Advanced Features

### 1. Context-Aware Chat

The chat system automatically:
- Maintains conversation history
- Retrieves relevant historical incidents
- Uses embeddings for semantic similarity
- Provides contextual responses

### 2. Vector Store Operations

```python
from ai.vector_store import get_vector_store

vs = get_vector_store("faiss")

# Store incidents
vs.store_incidents([
    {
        'id': 1,
        'incident_type': 'Breach',
        'location': 'Lab',
        'severity': 0.9,
        'description': 'Data breach detected',
        'timestamp': '2025-01-15'
    }
])

# Retrieve similar incidents
similar = vs.retrieve_similar_incidents(
    query="security breach",
    top_k=5,
    filters={
        'min_severity': 0.7,
        'location': 'Lab'
    }
)
```

### 3. Dynamic Model Configuration

```python
from ai.llm_utils import LLMConfig, get_llm_service

# Switch to a faster model
config = LLMConfig(
    model="gpt-3.5-turbo",
    temperature=0.3,
    max_tokens=1000
)
service = get_llm_service(config)

# Or update existing service
service.update_config(config)
```

### 4. Custom Prompt Templates

```python
from langchain.prompts import PromptTemplate

custom_prompt = PromptTemplate(
    input_variables=["incident_data"],
    template="""Analyze this campus incident:
{incident_data}

Provide a security assessment."""
)
```

---

## Performance Optimization

### 1. Vector Store Caching

```python
# FAISS index is cached on disk
# Subsequent calls load from cache automatically
vector_store = get_vector_store("faiss")
```

### 2. Conversation Memory

Default: 10 messages per conversation
```python
chat = MultiTurnChat(
    chain_manager=manager,
    max_history=20  # Increase if needed
)
```

### 3. Model Selection

- **gpt-4**: Most capable, slower, higher cost
- **gpt-4-turbo**: Balanced, faster
- **gpt-3.5-turbo**: Fastest, most economical

---

## Troubleshooting

### Issue: OpenAI API Key Not Found

```bash
# Verify environment variable
echo $OPENAI_API_KEY

# Set if missing
export OPENAI_API_KEY=sk-your-key
```

### Issue: Vector Store Not Initializing

```python
# Check FAISS installation
python -c "import faiss; print(faiss.__version__)"

# Reinstall if needed
pip install --upgrade faiss-cpu
```

### Issue: Chat Not Returning Context

```python
# Verify vector store has incidents
vs = get_vector_store()
incidents = vs.retrieve_similar_incidents("test", top_k=1)
print(len(incidents))  # Should be > 0
```

### Issue: Slow Response Times

```python
# Switch to faster model
config = LLMConfig(
    model="gpt-3.5-turbo",
    temperature=0.5,  # Reduce for consistency
    max_tokens=1000  # Reduce token limit
)
```

---

## Security Considerations

1. **API Key Management**: Never commit `.env` files
2. **Rate Limiting**: Implement rate limiting on endpoints
3. **Input Validation**: All user inputs are validated
4. **Error Handling**: Errors don't expose sensitive data
5. **Vector Store Privacy**: Store incidents securely

---

## Future Enhancements

- [ ] Streaming responses for real-time chat
- [ ] Fine-tuned models for campus-specific incidents
- [ ] Multi-language support
- [ ] Advanced RAG with document chunking
- [ ] Pinecone/Weaviate integration
- [ ] Persistent conversation database
- [ ] Analytics and audit logging
- [ ] Custom system prompts per user role

---

## Example Prompts for Chat

```
1. "What are the top security incidents this week?"
2. "How many unauthorized access attempts occurred in Building A?"
3. "Generate a summary of all critical incidents from the last month"
4. "What patterns have you noticed in security breaches?"
5. "Explain the anomaly detected in the network traffic"
6. "Compare incident trends between this week and last week"
7. "What preventive measures would reduce similar incidents?"
8. "Show me all incidents related to unauthorized access"
```

---

## File Structure

```
CampusShield-AI/
├── ai/
│   ├── llm_utils.py           # Core LLM service
│   ├── vector_store.py        # Vector database
│   └── prompts.py             # Prompt templates
│
├── Backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── llm.py         # FastAPI routes
│   │   └── services/
│   │       ├── advanced_llm_service.py
│   │       └── vector_store_service.py
│   └── requirements.txt        # Dependencies
│
└── dashboard/
    └── src/pages/
        ├── LLMInsights.jsx     # React component
        └── LLMInsights.css     # Styling
```

---

## Contributing

For bug reports, feature requests, or improvements:
1. Create an issue with detailed description
2. Submit PR with clear commit messages
3. Follow existing code style and patterns

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues or questions:
- 📧 Email: support@campusshield-ai.com
- 💬 Discord: [Community Server]
- 📖 Docs: [Full Documentation]

---

**Last Updated**: January 2025
**Version**: 1.0.0
**Status**: Production Ready ✅
