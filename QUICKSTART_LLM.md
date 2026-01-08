# LLM Module Integration Guide

## Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### Step 2: Set Environment Variables
```bash
# .env file in Backend directory
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
```

### Step 3: Start Backend
```bash
cd Backend
uvicorn app.main:app --reload
```

### Step 4: Access LLM Endpoints
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/llm/health
- Chat: POST http://localhost:8000/api/llm/chat

### Step 5: Integrate React Component
```jsx
import LLMInsights from './pages/LLMInsights';

// Add to your routing
<Route path="/insights" element={<LLMInsights />} />
```

---

## Testing the Module

### Test 1: Health Check
```bash
curl http://localhost:8000/api/llm/health
```

### Test 2: Send Chat Message
```bash
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "What are recent incidents?",
    "conversation_id": "test_1",
    "use_context": true
  }'
```

### Test 3: Generate Report
```bash
curl -X POST http://localhost:8000/api/llm/report \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "daily",
    "include_recommendations": true
  }'
```

### Test 4: Explain Anomaly
```bash
curl -X POST http://localhost:8000/api/llm/explain-anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "anomaly_score": 0.85,
    "anomaly_type": "Unauthorized Access",
    "affected_area": "Building A"
  }'
```

---

## Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| ImportError: No module named 'langchain' | Run `pip install -r Backend/requirements.txt` |
| OPENAI_API_KEY not found | Add key to .env file and restart |
| FAISS import error | Run `pip install faiss-cpu` |
| Port 8000 already in use | Use `uvicorn ... --port 8001` |
| React component not rendering | Check import path and API_BASE URL |

---

## API Response Examples

### Successful Chat Response
```json
{
  "response": "Based on the recent incident data...",
  "conversation_id": "conv_123",
  "chat_history": [...]
}
```

### Successful Report Response
```json
{
  "report": "DAILY SECURITY REPORT\n\nExecutive Summary...",
  "report_type": "daily",
  "generated_at": "2025-01-15T10:30:00"
}
```

### Error Response
```json
{
  "detail": "Chat error: [specific error message]"
}
```

---

## Production Deployment

### Render.com Deployment
1. Add to `Procfile`:
   ```
   web: cd Backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. Set environment variables in Render dashboard

3. Deploy via Git push

### Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY Backend/requirements.txt .
RUN pip install -r requirements.txt

COPY Backend/app app/
COPY ai/ ai/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Performance Tips

1. **Cache Vector Store**: FAISS index persists to disk
2. **Use gpt-3.5-turbo**: For faster, cheaper responses
3. **Limit max_tokens**: Reduces latency
4. **Batch Operations**: Process multiple incidents at once
5. **Monitor API Usage**: Track OpenAI costs

---

## Common Use Cases

### For Admin Dashboard
- Daily security reports
- Anomaly explanations
- Historical incident search
- Configurable alerts

### For Student Portal
- Safety FAQ chatbot
- Incident timeline summaries
- Location-based incident history
- General campus security Q&A

### For Security Team
- Multi-turn investigation assistant
- Pattern analysis
- Risk assessment
- Automated response recommendations

---

## Next Steps

After integration:
1. ✅ Test all endpoints
2. ✅ Connect to database
3. ✅ Load historical incidents into vector store
4. ✅ Customize system prompts
5. ✅ Monitor API usage
6. ✅ Collect user feedback
7. ✅ Iterate on features

---

**Ready to deploy? Start with Step 1 above!**
