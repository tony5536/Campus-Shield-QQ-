# Installation Notes for CampusShield AI v2.0

## ⚠️ Important Installation Notes

### Dependency Installation

Some packages may have version conflicts. Here's the recommended installation order:

1. **Install core dependencies first**:
```bash
pip install fastapi uvicorn SQLAlchemy pydantic pydantic-settings
pip install python-jose[cryptography] passlib[bcrypt]
pip install aiofiles python-multipart python-dotenv httpx
```

2. **Install ML dependencies**:
```bash
pip install scikit-learn pandas scipy
```

3. **Install LLM dependencies**:
```bash
pip install langchain langchain-openai openai
```

4. **Install vector store**:
```bash
pip install faiss-cpu
```

5. **Install document processing**:
```bash
pip install PyPDF2 python-docx
```

6. **Install sentence-transformers (may require numpy downgrade)**:
```bash
# Option 1: If numpy 2.x is installed, you may need to downgrade temporarily
pip install "numpy<2.0" sentence-transformers
# Then upgrade numpy back if needed
pip install "numpy>=2.0" --upgrade

# Option 2: Use a version that supports numpy 2.x (if available)
pip install sentence-transformers --upgrade
```

### Windows-Specific Issues

- **scikit-learn**: Use version >= 1.4.0 which has pre-built wheels for Windows
- **FAISS**: Use faiss-cpu >= 1.9.0 for Windows compatibility
- **NumPy**: Version 2.x works fine, but some packages may require < 2.0

### Alternative: Use Pre-installed Versions

If you already have compatible versions installed, you can skip the problematic packages:

```bash
# Check what's installed
pip list | grep -E "sentence-transformers|numpy|scikit-learn"

# If versions are compatible, proceed with server startup
```

### Quick Test

After installation, test the imports:

```python
python -c "from Backend.app.ai.llm.openai import OpenAILLM; print('✅ LLM OK')"
python -c "from Backend.app.ai.rag.vector_store import get_vector_store; print('✅ RAG OK')"
python -c "from Backend.app.ml.risk_model import RiskPredictionModel; print('✅ ML OK')"
```

### Troubleshooting

1. **NumPy version conflicts**: 
   - Try: `pip install "numpy<2.0"` then install sentence-transformers
   - Or: Use a virtual environment with Python 3.11 or 3.12

2. **FAISS installation issues**:
   - Ensure you're using `faiss-cpu` not `faiss`
   - Windows: Use version >= 1.9.0

3. **scikit-learn build errors**:
   - Use pre-built wheels: `pip install scikit-learn>=1.4.0`
   - Or install Microsoft Visual C++ Build Tools if you need to build from source

### Minimal Installation (Core Features Only)

If you only need core features without RAG/ML:

```bash
pip install fastapi uvicorn SQLAlchemy pydantic pydantic-settings
pip install python-jose[cryptography] passlib[bcrypt]
pip install aiofiles python-multipart python-dotenv httpx
pip install openai langchain langchain-openai
```

This will allow:
- ✅ API endpoints
- ✅ LLM features
- ✅ Incident management
- ❌ RAG (requires sentence-transformers)
- ❌ ML predictions (requires scikit-learn)

---

**Note**: The system is designed to be modular. If a component fails to import, other features will still work.

