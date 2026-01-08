# CampusShield AI v2.0 - Architecture Documentation

## 🎯 Overview

CampusShield AI has been upgraded to an **industry-level AI security platform** with clean architecture, multi-agent AI systems, RAG (Retrieval-Augmented Generation), and predictive risk forecasting.

## 📁 Clean Architecture Structure

```
Backend/app/
├── main.py                    # FastAPI application entrypoint
├── api/
│   ├── v1/                    # New v1 API routes (clean architecture)
│   │   ├── incidents.py       # Incident management
│   │   ├── alerts.py          # Alert management
│   │   ├── ai.py              # RAG-based Q&A
│   │   ├── intelligence.py   # Incident Intelligence Engine
│   │   ├── forecasting.py     # Risk prediction APIs
│   │   └── documents.py       # Document upload & indexing
│   └── routes/                 # Legacy routes (backward compatible)
├── ai/
│   ├── llm/                   # LLM abstraction layer
│   │   ├── base.py            # Base LLM interface
│   │   ├── openai.py          # OpenAI implementation
│   │   ├── local.py           # Local/Ollama implementation
│   │   └── prompts.py         # Prompt templates
│   ├── rag/                   # RAG system
│   │   ├── vector_store.py    # Vector store abstraction (FAISS)
│   │   ├── indexer.py         # Document indexing
│   │   ├── retriever.py       # Similarity search
│   │   └── qa_chain.py        # RAG Q&A chain
│   └── agents/                # Multi-agent system
│       ├── analyst_agent.py   # Security analyst
│       ├── policy_agent.py    # Policy compliance
│       ├── forecasting_agent.py  # Risk forecasting
│       ├── report_agent.py    # Report generation
│       └── orchestrator.py   # Agent coordination
├── ml/                        # Machine Learning
│   ├── feature_engineering.py # Feature extraction
│   ├── risk_model.py          # ML risk prediction model
│   ├── predictor.py           # Risk predictor service
│   └── trainer.py             # Model training
├── core/                      # Core infrastructure
│   ├── config.py              # Centralized configuration
│   ├── security.py            # Auth & security utilities
│   └── logging.py             # Logging configuration
├── services/                  # Business logic services
├── models/                    # SQLAlchemy models
└── db/                        # Database initialization
```

## 🔥 Key Features Implemented

### Phase 1: Clean Architecture ✅
- **Modular structure** with clear separation of concerns
- **API versioning** (v1) with backward compatibility
- **Core infrastructure** (config, security, logging)
- **No business logic in routes** - all in services/agents

### Phase 2: AI Incident Intelligence Engine ✅
- **Automatic incident analysis** with:
  - Severity classification (Low/Medium/High/Critical)
  - Root cause inference
  - Pattern matching with historical incidents
  - AI-generated recommendations
  - Confidence scoring

**API**: `POST /api/v1/intelligence/analyze`

### Phase 3: Full RAG System ✅
- **Document indexing** (PDF, TXT, DOCX)
- **Vector store** (FAISS with sentence-transformers)
- **Intelligent chunking** with overlap
- **Retrieval QA** with source citations
- **Confidence-based refusal** if context insufficient

**APIs**:
- `POST /api/v1/ai/ask` - RAG-based Q&A
- `POST /api/v1/documents/upload` - Document upload
- `POST /api/v1/documents/index-incident` - Index incidents

### Phase 4: Multi-Agent AI System ✅
- **Security Analyst Agent** - Incident analysis
- **Policy Agent** - Compliance checking
- **Forecasting Agent** - Risk prediction with explanations
- **Report Agent** - Professional report generation
- **Agent Orchestrator** - Coordinates multiple agents

### Phase 5: Predictive Risk Forecasting ✅
- **ML models** (RandomForest, GradientBoosting)
- **Feature engineering** from incident data
- **Zone-wise risk prediction**
- **Time-based forecasting**
- **AI explanations** of predictions

**API**: `GET /api/v1/forecast/risk`

## 🛡️ Prompt Safety & Guardrails (Phase 6)

Implemented in RAG QA Chain:
- ✅ **Context-only answers** - AI only uses retrieved context
- ✅ **Confidence thresholds** - Refuses if confidence < 0.3
- ✅ **Source citations** - All answers cite sources
- ✅ **Hallucination prevention** - "Insufficient data" response when needed

## 📊 API Endpoints

### New v1 Endpoints

#### Intelligence
- `POST /api/v1/intelligence/analyze?incident_id={id}` - Analyze incident

#### AI & RAG
- `POST /api/v1/ai/ask` - Ask questions with RAG
- `POST /api/v1/documents/upload` - Upload documents
- `POST /api/v1/documents/index-incident?incident_id={id}` - Index incident

#### Forecasting
- `GET /api/v1/forecast/risk?zones={zone1,zone2}&time_horizon=7d` - Predict risks

#### Incidents (v1)
- `GET /api/v1/incidents/` - List incidents
- `POST /api/v1/incidents/` - Create incident
- `GET /api/v1/incidents/{id}` - Get incident

### Legacy Endpoints (Backward Compatible)
- All existing `/api/incidents`, `/api/alerts`, `/api/ai/*` endpoints still work

## 🔧 Configuration

Environment variables (`.env`):

```bash
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini

# RAG Configuration
VECTOR_STORE_TYPE=faiss
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ML Configuration
ML_MODEL_PATH=./models
RISK_PREDICTION_ENABLED=true

# Security
CS_SECRET_KEY=your-secret-key
CS_DEBUG=false
```

## 🚀 Getting Started

1. **Install dependencies**:
```bash
pip install -r Backend/requirements.txt
```

2. **Set environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Initialize database**:
```bash
python Backend/app/db/base.py  # Creates tables
```

4. **Start server**:
```bash
uvicorn Backend.app.main:app --reload
```

5. **Access API docs**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📈 Next Steps (Phases 7-9)

### Phase 7: Frontend Enhancements
- AI Chat interface with streaming
- Document upload UI
- Risk dashboard with heatmaps
- Real-time predictions display

### Phase 8: Security & Observability
- RBAC (Role-Based Access Control)
- Rate limiting
- Audit logs
- LLM usage metrics
- Prompt injection protection

### Phase 9: Documentation
- System architecture diagrams
- AI decision flow documentation
- RAG pipeline documentation
- Risk forecasting methodology

## 🎓 Architecture Principles

1. **Clean Architecture**: Separation of concerns, dependency inversion
2. **API Versioning**: v1 for new features, legacy routes maintained
3. **Modularity**: Each component is independently testable
4. **AI Safety**: Guardrails prevent hallucination, require citations
5. **Scalability**: Vector stores support cloud providers (Pinecone, Weaviate)
6. **Production-Ready**: Error handling, logging, configuration management

## 📝 Notes

- **Backward Compatibility**: All existing endpoints continue to work
- **Gradual Migration**: Can migrate to v1 endpoints incrementally
- **Extensibility**: Easy to add new agents, models, or vector stores
- **Testing**: Structure supports unit and integration testing

---

**Version**: 2.0.0  
**Status**: Core features complete (Phases 1-5)  
**Next**: Frontend integration and security hardening

