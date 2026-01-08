# CampusShield AI v2.0 - Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the `Backend` directory:

```bash
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Optional: Other LLM providers
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

# RAG Configuration
VECTOR_STORE_TYPE=faiss
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ML Configuration
ML_MODEL_PATH=./models
RISK_PREDICTION_ENABLED=true

# Security
CS_SECRET_KEY=your-secret-key-change-in-production
CS_DEBUG=true

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./backend.db
```

### 3. Initialize Database

```bash
python -c "from Backend.app.db.base import init_db; init_db()"
```

Or use the existing init script:
```bash
python init_db.py
```

### 4. Start the Server

```bash
uvicorn Backend.app.main:app --reload
```

The server will start at `http://localhost:8000`

### 5. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing the New Features

### Test Incident Intelligence Engine

```bash
# First, create an incident (or use existing one)
curl -X POST "http://localhost:8000/api/v1/incidents/" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "Intrusion",
    "severity": 0.8,
    "description": "Unauthorized person detected in building A after hours",
    "location": "Building A"
  }'

# Then analyze it
curl -X POST "http://localhost:8000/api/v1/intelligence/analyze?incident_id=1"
```

### Test RAG Q&A

```bash
# First, index some documents or incidents
curl -X POST "http://localhost:8000/api/v1/documents/index-incident?incident_id=1"

# Then ask questions
curl -X POST "http://localhost:8000/api/v1/ai/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the most common incident types?"
  }'
```

### Test Risk Forecasting

```bash
curl "http://localhost:8000/api/v1/forecast/risk?zones=Building%20A&time_horizon=7d"
```

### Upload a Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@path/to/your/document.pdf"
```

## 📊 API Endpoints Summary

### New v1 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/intelligence/analyze` | POST | Analyze incident with AI |
| `/api/v1/ai/ask` | POST | Ask questions with RAG |
| `/api/v1/documents/upload` | POST | Upload and index documents |
| `/api/v1/documents/index-incident` | POST | Index an incident |
| `/api/v1/forecast/risk` | GET | Get risk predictions |
| `/api/v1/incidents/` | GET/POST | List/create incidents |
| `/api/v1/incidents/{id}` | GET | Get specific incident |
| `/api/v1/alerts/` | GET | List alerts |

### Legacy Endpoints (Still Work)

- `/api/incidents/*` - Original incident endpoints
- `/api/alerts/*` - Original alert endpoints
- `/api/ai/*` - Original AI endpoints

## 🔍 Key Features

1. **AI Incident Intelligence**: Automatic analysis of every incident
2. **RAG System**: Ask questions about your campus security data
3. **Multi-Agent AI**: Coordinated AI agents for comprehensive analysis
4. **Risk Forecasting**: ML-powered predictions with AI explanations
5. **Document Indexing**: Upload policies, reports, and documents

## 🐛 Troubleshooting

### Import Errors

If you see import errors, make sure you're running from the project root:
```bash
# Correct
python -m Backend.app.main

# Or
cd Backend
python -m app.main
```

### LLM API Errors

- Check your API keys in `.env`
- Verify the LLM provider is set correctly
- Check API rate limits

### Vector Store Errors

- FAISS requires `faiss-cpu` and `sentence-transformers`
- First-time embedding model download may take time
- Ensure sufficient disk space for vector store

### Database Errors

- Ensure database is initialized: `python init_db.py`
- Check database file permissions
- For PostgreSQL, ensure connection string is correct

## 📚 Next Steps

1. **Read Architecture Docs**: See `ARCHITECTURE_V2.md`
2. **Review Implementation**: See `IMPLEMENTATION_SUMMARY.md`
3. **Explore APIs**: Use Swagger UI at `/docs`
4. **Index Documents**: Upload campus policies and reports
5. **Train ML Models**: Use historical incident data

## 💡 Tips

- Start with a few test incidents to see intelligence in action
- Index campus policy documents for better RAG answers
- Use the forecasting API to identify high-risk zones
- Monitor logs for AI agent decisions and confidence scores

---

**Need Help?** Check the documentation files or review the code structure in `Backend/app/`

