# Running CampusShield AI Server

## ✅ Correct Way to Run the Server

### Option 1: From Project Root (Recommended)

```powershell
# 1. Navigate to project root
cd C:\Dev\CampusShield-AI

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Run server
uvicorn Backend.app.main:app --reload
```

### Option 2: Use the Start Script

**PowerShell:**
```powershell
cd C:\Dev\CampusShield-AI
.\start_server.ps1
```

**Batch File:**
```cmd
cd C:\Dev\CampusShield-AI
start_server.bat
```

## ❌ Common Mistakes

### Wrong: Running from `backend` directory
```powershell
cd C:\Dev\CampusShield-AI\backend  # ❌ Wrong!
uvicorn Backend.app.main:app --reload  # This will fail
```

**Error**: `ModuleNotFoundError: No module named 'Backend'`

### Wrong: Using wrong import path
```powershell
uvicorn app.main:app --reload  # ❌ Wrong!
```

## ✅ Correct Import Path

The correct import path is: `Backend.app.main:app`

This means:
- `Backend` = the `Backend` directory at project root
- `app` = the `app` subdirectory inside `Backend`
- `main` = the `main.py` file
- `app` = the FastAPI app instance

## 📍 Directory Structure

```
C:\Dev\CampusShield-AI\          ← Run from HERE
├── Backend\                      ← This is the module
│   └── app\
│       └── main.py              ← Contains the FastAPI app
├── .venv\                       ← Virtual environment
└── start_server.ps1            ← Helper script
```

## 🔍 Verify You're in the Right Place

Check that you can see:
- ✅ `Backend` directory (uppercase)
- ✅ `Backend\app\main.py` file exists
- ✅ `.venv` directory exists

## 🚀 Quick Test

```powershell
# From project root
python -c "from Backend.app.main import app; print('✅ Import successful')"
```

If this works, you're ready to run the server!

## 📝 Environment Variables

Before starting, make sure you have a `.env` file in the `Backend` directory:

```bash
# Backend/.env
OPENAI_API_KEY=your_key_here
CS_DEBUG=true
DATABASE_URL=sqlite:///./backend.db
```

## 🌐 Access the Server

Once running:
- **API**: http://127.0.0.1:8000
- **Docs**: http://127.0.0.1:8000/docs
- **Health**: http://127.0.0.1:8000/health

---

**Remember**: Always run from `C:\Dev\CampusShield-AI` (project root), not from `backend` subdirectory!

