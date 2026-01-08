# 🔧 LLM Module - Copy-Paste Code Snippets

Ready-to-use code snippets for common tasks. Just copy and adapt!

---

## Backend Python Snippets

### 1. Initialize LLM Service

```python
from ai.llm_utils import get_llm_service, LLMConfig
from ai.vector_store import get_vector_store

# Basic initialization
service = get_llm_service()

# With custom configuration
config = LLMConfig(
    model="gpt-4",
    temperature=0.7,
    max_tokens=1500,
    top_p=0.95
)
service = get_llm_service(config)

# Access components
chat = service.chat
summarizer = service.summarizer
reporter = service.reporter
explainer = service.explainer
```

### 2. Multi-Turn Chat

```python
# Send a message
response = service.chat.chat(
    user_input="What happened yesterday?",
    conversation_id="user_123"
)
print(response)

# Get conversation history
history = service.chat.get_history()
for msg in history:
    print(f"{msg['role']}: {msg['content']}")

# Clear conversation
service.chat.clear_history()
```

### 3. Summarize Incidents

```python
incidents = [
    {
        'id': 1,
        'incident_type': 'Unauthorized Access',
        'location': 'Building A',
        'severity': 0.8,
        'description': 'Failed login attempts',
        'timestamp': '2025-01-15T10:30:00'
    },
    # ... more incidents
]

summary = service.summarizer.summarize_incidents(
    incidents=incidents,
    focus="Security"
)
print(summary)
```

### 4. Generate Daily Report

```python
from datetime import datetime

incidents = [...]  # Get from database

report = service.reporter.generate_daily_report(
    incidents=incidents,
    report_date=datetime.now().strftime("%Y-%m-%d")
)
print(report)
```

### 5. Generate Weekly Report

```python
from datetime import datetime, timedelta

start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
incidents = [...]  # Get from database

report = service.reporter.generate_weekly_report(
    incidents=incidents,
    week_start=start_date
)
print(report)
```

### 6. Explain Anomaly

```python
explanation = service.explainer.explain_anomaly(
    anomaly_score=0.85,
    anomaly_type="Unusual Network Activity",
    affected_area="Campus Network - Building A",
    threshold=0.7,
    comparisons=[
        {
            'name': 'Traffic Rate',
            'value': '2500 MB/s',
            'normal_range': '500-1500 MB/s'
        }
    ]
)
print(explanation)
```

### 7. Analyze Pattern

```python
incidents = [...]  # Related incidents

pattern_analysis = service.explainer.analyze_pattern(
    pattern_description="Recurring access attempts at specific times",
    incidents=incidents,
    frequency="daily"
)
print(pattern_analysis)
```

### 8. Store Incidents in Vector Database

```python
from ai.vector_store import get_vector_store

vs = get_vector_store("faiss")

incidents = [
    {
        'id': 1,
        'incident_type': 'Breach',
        'location': 'Lab',
        'severity': 0.9,
        'description': 'Data breach detected',
        'timestamp': '2025-01-15'
    }
]

# Store incidents
vs.store_incidents(incidents)

# Retrieve similar incidents
similar = vs.retrieve_similar_incidents(
    query="security breach",
    top_k=5
)

for incident in similar:
    print(f"{incident['type']}: {incident['location']} (Score: {incident['similarity_score']})")
```

### 9. Update LLM Configuration

```python
# Create new config
config = LLMConfig(
    model="gpt-3.5-turbo",
    temperature=0.5,
    max_tokens=1000,
    top_p=0.9
)

# Apply it
service.update_config(config)
```

### 10. Custom Prompt Template

```python
from langchain.prompts import PromptTemplate

custom_prompt = PromptTemplate(
    input_variables=["incident_data", "location"],
    template="""Analyze this incident in {location}:

{incident_data}

Provide security assessment and recommendations."""
)

# Use in chain
chain = service.chain_manager._get_or_create_chain(
    "custom_analyzer",
    custom_prompt
)

result = chain.run(
    incident_data="...",
    location="Building A"
)
```

---

## FastAPI Integration Snippets

### 1. In Your Route Handler

```python
from fastapi import APIRouter
from backend.services.advanced_llm_service import get_llm_service

router = APIRouter()

@router.post("/custom-endpoint")
async def custom_endpoint(data: dict):
    service = get_llm_service()
    
    # Use LLM service
    response = service.chat.chat(
        user_input=data['query'],
        conversation_id=data.get('conv_id', 'default')
    )
    
    return {"response": response}
```

### 2. Database Integration

```python
from sqlalchemy.orm import Session
from backend.models.incident import Incident

@router.post("/llm/analyze-incidents")
async def analyze_incidents(db: Session):
    # Get incidents from database
    incidents = db.query(Incident).filter(
        Incident.severity > 0.5
    ).all()
    
    # Convert to dict
    incident_data = [
        {
            'id': i.id,
            'incident_type': i.incident_type,
            'location': i.location,
            'severity': i.severity,
            'description': i.description,
            'timestamp': i.timestamp.isoformat()
        }
        for i in incidents
    ]
    
    # Analyze
    service = get_llm_service()
    summary = service.summarizer.summarize_incidents(incident_data)
    
    return {"summary": summary}
```

---

## Frontend JavaScript/React Snippets

### 1. Basic Chat Request

```javascript
const axios = require('axios');

async function sendChatMessage(userInput) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/llm/chat',
      {
        user_input: userInput,
        conversation_id: 'user_123',
        use_context: true
      }
    );
    
    console.log('Response:', response.data.response);
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data?.detail);
  }
}

// Usage
sendChatMessage('What are recent incidents?');
```

### 2. Report Generation

```javascript
async function generateReport(type = 'daily') {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/llm/report',
      {
        report_type: type,
        include_recommendations: true
      }
    );
    
    console.log('Report:', response.data.report);
    return response.data.report;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
const report = await generateReport('weekly');
```

### 3. Historical Incident Search

```javascript
async function searchIncidents(query) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/llm/historical-incidents',
      {
        query: query,
        top_k: 10,
        min_severity: 0.5
      }
    );
    
    return response.data.incidents;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
const incidents = await searchIncidents('unauthorized access');
incidents.forEach(inc => {
  console.log(`${inc.type} - ${inc.location} (${inc.severity})`);
});
```

### 4. Anomaly Explanation

```javascript
async function explainAnomaly(score, type, area) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/llm/explain-anomaly',
      {
        anomaly_score: parseFloat(score),
        anomaly_type: type,
        affected_area: area,
        threshold: 0.7
      }
    );
    
    return {
      explanation: response.data.explanation,
      risk: response.data.risk_level,
      recommendations: response.data.recommendations
    };
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
const analysis = await explainAnomaly(0.85, 'Unauthorized Access', 'Building A');
console.log(`Risk Level: ${analysis.risk}`);
console.log(`Explanation: ${analysis.explanation}`);
```

### 5. React Hook for Chat

```javascript
import { useState } from 'react';
import axios from 'axios';

function useChat(conversationId = `conv_${Date.now()}`) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (userInput) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        'http://localhost:8000/api/llm/chat',
        {
          user_input: userInput,
          conversation_id: conversationId,
          use_context: true
        }
      );

      setMessages(response.data.chat_history);
      return response.data.response;
    } catch (err) {
      setError(err.response?.data?.detail || 'Error');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const clearMessages = () => setMessages([]);

  return { messages, loading, error, sendMessage, clearMessages };
}

// Usage in component
function ChatComponent() {
  const { messages, sendMessage, loading } = useChat();

  return (
    <div>
      {messages.map(msg => (
        <div key={msg.timestamp} className={msg.role}>
          {msg.content}
        </div>
      ))}
      <button onClick={() => sendMessage('Hello!')}>Send</button>
    </div>
  );
}
```

### 6. Update Configuration

```javascript
async function updateLLMConfig(config) {
  try {
    const response = await axios.put(
      'http://localhost:8000/api/llm/config',
      {
        model: config.model,
        temperature: config.temperature,
        max_tokens: config.maxTokens,
        top_p: config.topP
      }
    );
    
    console.log('Config updated:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
updateLLMConfig({
  model: 'gpt-3.5-turbo',
  temperature: 0.5,
  maxTokens: 1000,
  topP: 0.95
});
```

---

## Testing Snippets

### 1. cURL Test - Chat

```bash
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "What are recent security incidents?",
    "conversation_id": "test_123",
    "use_context": true
  }'
```

### 2. cURL Test - Report

```bash
curl -X POST http://localhost:8000/api/llm/report \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "daily",
    "include_recommendations": true
  }'
```

### 3. cURL Test - Anomaly

```bash
curl -X POST http://localhost:8000/api/llm/explain-anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "anomaly_score": 0.85,
    "anomaly_type": "Unusual Access Pattern",
    "affected_area": "Campus Network"
  }'
```

### 4. cURL Test - Historical Search

```bash
curl -X POST http://localhost:8000/api/llm/historical-incidents \
  -H "Content-Type: application/json" \
  -d '{
    "query": "unauthorized access",
    "top_k": 5
  }'
```

### 5. Python Unit Test Example

```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_llm_health():
    response = client.get("/api/llm/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat():
    response = client.post("/api/llm/chat", json={
        "user_input": "Hello",
        "conversation_id": "test",
        "use_context": True
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

---

## Environment Setup Snippets

### .env File Template

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here

# LLM Configuration
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1500
LLM_TOP_P=0.95

# Vector Store
VECTOR_STORE_TYPE=faiss
VECTOR_STORE_PATH=./data/faiss_index

# Application
DEBUG=True
ENVIRONMENT=development
```

### Docker Environment

```dockerfile
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LLM_MODEL=gpt-4
ENV VECTOR_STORE_TYPE=faiss
```

### Production Setup

```bash
export OPENAI_API_KEY=sk-prod-key
export LLM_MODEL=gpt-4-turbo
export VECTOR_STORE_TYPE=pinecone
export PINECONE_API_KEY=your-key
```

---

## Quick Reference

| Task | Endpoint | Method |
|------|----------|--------|
| Health Check | `/api/llm/health` | GET |
| Chat | `/api/llm/chat` | POST |
| Summarize | `/api/llm/summarize` | POST |
| Report | `/api/llm/report` | POST |
| Anomaly | `/api/llm/explain-anomaly` | POST |
| History | `/api/llm/historical-incidents` | POST |
| Config Get | `/api/llm/config` | GET |
| Config Set | `/api/llm/config` | PUT |
| Models | `/api/llm/models` | GET |

---

## Tips & Tricks

1. **Test in Swagger**: http://localhost:8000/docs
2. **Check Logs**: Add logging to track execution
3. **Cache Results**: Store frequently used reports
4. **Batch Operations**: Process multiple incidents together
5. **Monitor Costs**: Track OpenAI API usage
6. **Profile Performance**: Measure response times
7. **Version Control**: Track prompt changes
8. **A/B Test**: Compare model outputs

---

**Happy coding! 🚀**
