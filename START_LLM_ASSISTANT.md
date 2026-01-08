# 🚀 Start LLM Assistant - Quick Guide

## ✅ Setup Complete!

I've analyzed all `.md` files and prepared your LLM assistant. Here's what's ready:

### ✅ Dependencies Installed
All required packages are installed and verified.

### ✅ Environment Configuration
Added LLM configuration to `Backend/.env`:
- `OPENAI_API_KEY=sk-your-api-key-here` (⚠️ **YOU NEED TO SET THIS**)
- `LLM_PROVIDER=openai`
- `OPENAI_MODEL=gpt-4o-mini`

---

## 🔑 Step 1: Set Your OpenAI API Key

**IMPORTANT**: You need to add your actual OpenAI API key to the `.env` file.

1. Get your API key from: https://platform.openai.com/api-keys
2. Edit `Backend/.env` file
3. Replace `sk-your-api-key-here` with your actual key:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
   ```

**Alternative**: Set it as an environment variable:
```powershell
$env:OPENAI_API_KEY = "sk-your-actual-key-here"
```

---

## 🚀 Step 2: Start the Backend Server

### Option A: From Project Root
```powershell
cd C:\Dev\CampusShield-AI
python app.py
```

### Option B: Using Uvicorn Directly
```powershell
cd C:\Dev\CampusShield-AI\Backend
uvicorn app.main:app --reload
```

### Option C: From Backend Directory
```powershell
cd C:\Dev\CampusShield-AI\Backend
python -m uvicorn app.main:app --reload
```

The server will start on: **http://localhost:8000**

---

## 🧪 Step 3: Test the LLM Assistant

### Test 1: Health Check
```powershell
curl http://localhost:8000/health
```

### Test 2: Simple AI Assistant
```powershell
curl -X POST http://localhost:8000/api/ai/assist `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"Unauthorized person detected in building A after hours\"}'
```

### Test 3: Admin Assistant Query
```powershell
curl -X POST http://localhost:8000/api/ai/assistant `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What are the most common incident types?\"}'
```

### Test 4: View API Documentation
Open in browser: **http://localhost:8000/docs**

---

## 📍 Available LLM Endpoints

### Simple LLM Service (`/api/ai/*`):
- ✅ `POST /api/ai/assist` - AI-powered incident analysis
- ✅ `POST /api/ai/assistant` - Admin assistant queries  
- ✅ `POST /api/ai/explain-incident` - Incident explanations
- ✅ `POST /api/ai/generate-report` - Report generation
- ✅ `GET /api/ai/assistant/stats` - Assistant statistics

### Advanced LLM Module (`/api/llm/*`):
- `GET /api/llm/health` - Health check
- `POST /api/llm/chat` - Multi-turn chat
- `POST /api/llm/summarize` - Incident summarization
- `POST /api/llm/report` - Report generation
- `POST /api/llm/explain-anomaly` - Anomaly explanation

---

## 🎯 Quick Start Commands

### Start Server (PowerShell):
```powershell
# Navigate to project root
cd C:\Dev\CampusShield-AI

# Start server
python app.py
```

### Test in Browser:
1. Open: http://localhost:8000/docs
2. Try the `/api/ai/assist` endpoint
3. Enter a test query like: "Unauthorized access detected"

---

## 📚 Documentation Files Analyzed

I've analyzed these documentation files:
- ✅ QUICKSTART_LLM.md
- ✅ LLM_MODULE_README.md  
- ✅ LLM_DOCUMENTATION_INDEX.md
- ✅ README.md
- ✅ HACKATHON_DEMO_GUIDE.md
- ✅ DEPLOYMENT_CHECKLIST.md
- ✅ And more...

See `LLM_STARTUP_GUIDE.md` for complete analysis.

---

## ⚠️ Troubleshooting

### Issue: "OPENAI_API_KEY not found"
**Solution**: Set your API key in `Backend/.env` file or as environment variable.

### Issue: Port 8000 already in use
**Solution**: Use a different port:
```powershell
uvicorn app.main:app --reload --port 8001
```

### Issue: Import errors
**Solution**: Make sure you're in the correct directory and dependencies are installed:
```powershell
cd Backend
python check_dependencies.py
```

---

## 🎉 You're Ready!

1. ✅ Set your `OPENAI_API_KEY` in `Backend/.env`
2. ✅ Start the server with `python app.py`
3. ✅ Test at http://localhost:8000/docs
4. ✅ Use the LLM assistant endpoints!

**Need help?** Check `LLM_STARTUP_GUIDE.md` for detailed information.

